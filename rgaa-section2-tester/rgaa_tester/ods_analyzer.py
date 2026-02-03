# -*- coding: utf-8 -*-
"""
ODS Audit Analyzer - Integrates ODS handler with automated testing.

Connects the ODS file format with our automated accessibility tests.
"""

from typing import Dict, List, Optional
from .ods_handler import RGAAAuditODSHandler
from .ods_models import Status, Derogation, PageAudit, AuditCriterion
from .analyzer import AnalyseurRGAA, ResultatTest
from .crawler import Crawler
from .config import get_config


class ODSAuditAnalyzer:
    """Integrates ODS handler with automated testing."""

    def __init__(self, ods_handler: RGAAAuditODSHandler, config=None):
        """
        Initialize the ODS analyzer.

        Args:
            ods_handler: RGAAAuditODSHandler instance
            config: Configuration object (optional)
        """
        self.handler = ods_handler
        self.config = config or get_config()
        self.analyseur = AnalyseurRGAA(config)
        self.crawler = Crawler(config)

    def analyze_page(self, page_id: str, run_automated_tests: bool = True) -> Optional[PageAudit]:
        """
        Run automated tests on a page and update results.

        Args:
            page_id: Page identifier (P01, P02, etc.)
            run_automated_tests: Whether to run automated tests

        Returns:
            Updated PageAudit object
        """
        page_data = self.handler.get_page_audit(page_id)
        if not page_data:
            return None

        url = page_data.url

        # Check if URL is valid
        if url in ["Absente", ""] or not url.startswith("http"):
            # Mark all criteria as NA for absent pages
            for criterion in page_data.criteria:
                criterion.status = Status.NOT_APPLICABLE
                self.handler.update_criterion(
                    page_id=page_id,
                    criterion_id=criterion.criterion_id,
                    status=Status.NOT_APPLICABLE
                )
            return page_data

        if not run_automated_tests:
            return page_data

        # Run automated tests
        results = self.run_automated_tests(url)

        # Update criteria based on test results
        for criterion_id, result in results.items():
            self.handler.update_criterion(
                page_id=page_id,
                criterion_id=criterion_id,
                status=result['status'],
                modifications=result.get('modifications', ''),
                comments=result.get('comments', '')
            )

        # Reload updated page data
        return self.handler.get_page_audit(page_id)

    def run_automated_tests(self, url: str) -> Dict:
        """
        Execute automated tests and return results.

        Currently supports Section 2 (CADRES) tests.

        Args:
            url: URL to test

        Returns:
            Dictionary with test results per criterion
        """
        results = {}

        # Test Section 2: CADRES (Frames)
        try:
            # Analyze the page
            resultat_page = self.analyseur.analyser_page(url)

            # Test criterion 2.1 (Frame titles present)
            if resultat_page.cadres_testes > 0:
                if resultat_page.non_conformes_2_1 == 0:
                    results["2.1"] = {
                        'status': Status.COMPLIANT,
                        'modifications': '',
                        'comments': f'Tous les {resultat_page.cadres_testes} cadres ont un titre.'
                    }
                else:
                    results["2.1"] = {
                        'status': Status.NON_COMPLIANT,
                        'modifications': f'{resultat_page.non_conformes_2_1} cadre(s) sans titre détecté(s). Ajouter un attribut title descriptif.',
                        'comments': f'{resultat_page.non_conformes_2_1}/{resultat_page.cadres_testes} cadres non conformes.'
                    }
            else:
                results["2.1"] = {
                    'status': Status.NOT_APPLICABLE,
                    'modifications': '',
                    'comments': 'Aucun cadre détecté sur cette page.'
                }

            # Test criterion 2.2 (Frame titles relevant)
            if resultat_page.cadres_testes > 0:
                # 2.2 requires manual verification
                alertes_count = resultat_page.a_verifier_2_2
                if alertes_count > 0:
                    results["2.2"] = {
                        'status': Status.NOT_TESTED,
                        'modifications': '',
                        'comments': f'⚠️ {alertes_count} cadre(s) signalé(s) pour vérification manuelle. La pertinence des titres doit être validée par un auditeur humain.'
                    }
                else:
                    results["2.2"] = {
                        'status': Status.NOT_TESTED,
                        'modifications': '',
                        'comments': f'Vérification manuelle requise pour {resultat_page.cadres_testes} cadre(s). Aucun titre suspect détecté automatiquement.'
                    }
            else:
                results["2.2"] = {
                    'status': Status.NOT_APPLICABLE,
                    'modifications': '',
                    'comments': 'Aucun cadre détecté sur cette page.'
                }

        except Exception as e:
            # Mark as not tested if error occurs
            results["2.1"] = {
                'status': Status.NOT_TESTED,
                'modifications': '',
                'comments': f'Erreur lors du test automatique: {str(e)}'
            }
            results["2.2"] = {
                'status': Status.NOT_TESTED,
                'modifications': '',
                'comments': f'Erreur lors du test automatique: {str(e)}'
            }

        return results

    def analyze_all_pages(self, progress_callback=None) -> Dict:
        """
        Analyze all pages in the audit file.

        Args:
            progress_callback: Optional callback function(page_id, progress, total)

        Returns:
            Dictionary with summary statistics
        """
        pages = self.handler.get_sample_pages()
        total = len(pages)

        for i, page_info in enumerate(pages):
            page_id = page_info['page_id']

            if progress_callback:
                progress_callback(page_id, i + 1, total)

            try:
                self.analyze_page(page_id, run_automated_tests=True)
            except Exception as e:
                print(f"Error analyzing {page_id}: {e}")

        # Return global statistics
        return self.handler.calculate_synthesis()

    def generate_report_summary(self) -> str:
        """
        Generate a text summary of the audit results.

        Returns:
            Markdown formatted summary
        """
        stats = self.handler.calculate_synthesis()

        summary = f"""# Résumé de l'audit RGAA

## Informations générales

- **Date** : {self.handler.audit_data.date}
- **Auditeur** : {self.handler.audit_data.auditor}
- **Contexte** : {self.handler.audit_data.context}
- **Site** : {self.handler.audit_data.site_url}

## Statistiques globales

- **Pages analysées** : {stats['total_pages']}
- **Critères totaux** : {stats['total_criteria']}
- **Conformes** : {stats['compliant']} ({stats['compliance_rate']:.1f}% des applicables)
- **Non conformes** : {stats['non_compliant']}
- **Non applicables** : {stats['not_applicable']}
- **Non testés** : {stats['not_tested']}
- **Dérogations** : {stats['derogations']}

## Taux de conformité

"""
        if stats['compliance_rate'] is not None:
            rate = stats['compliance_rate']
            if rate >= 100:
                summary += "✅ **100% conforme**\n"
            elif rate >= 50:
                summary += f"⚠️ **{rate:.1f}% conforme** - Améliorations nécessaires\n"
            else:
                summary += f"❌ **{rate:.1f}% conforme** - Travail important requis\n"
        else:
            summary += "ℹ️ Taux de conformité non calculable (aucun critère applicable testé)\n"

        summary += "\n---\n\n*Rapport généré automatiquement par RGAA Section 2 Tester*\n"

        return summary
