# -*- coding: utf-8 -*-
"""
ODS Audit Analyzer - Integrates ODS handler with automated testing.

Connects the ODS file format with our automated accessibility tests.
Supports full RGAA 4.1.2 testing with all 106 criteria.
"""

from typing import Dict, List, Optional
from .ods_handler import RGAAAuditODSHandler
from .ods_models import Status, Derogation, PageAudit, AuditCriterion
from .analyzer import AnalyseurRGAA, ResultatTest
from .crawler import Crawler
from .config import get_config
from .full_rgaa_tester import FullRGAATester, WebPageAnalyzer, TestResult


class ODSAuditAnalyzer:
    """Integrates ODS handler with automated testing."""

    def __init__(self, ods_handler: RGAAAuditODSHandler, config=None, full_rgaa_mode: bool = True):
        """
        Initialize the ODS analyzer.

        Args:
            ods_handler: RGAAAuditODSHandler instance
            config: Configuration object (optional)
            full_rgaa_mode: If True, run all 106 RGAA criteria (default). If False, only Section 2.
        """
        self.handler = ods_handler
        self.config = config or get_config()
        self.analyseur = AnalyseurRGAA(config)
        self.crawler = Crawler(config)
        self.full_rgaa_mode = full_rgaa_mode

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

        # Update criteria based on test results, but skip NA criteria
        for criterion_id, result in results.items():
            # Check if criterion is already marked as NA
            criterion = page_data.get_criterion(criterion_id)
            if criterion and criterion.status == Status.NOT_APPLICABLE:
                # Skip updating NA criteria - they remain NA
                if hasattr(self.crawler, '_callback_log') and self.crawler._callback_log:
                    self.crawler._callback_log(f"⊘ Critère {criterion_id} marqué NA - test ignoré")
                continue

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

        Supports full RGAA 4.1.2 testing (all 106 criteria) when full_rgaa_mode is True,
        or Section 2 (CADRES) only when False.

        Args:
            url: URL to test

        Returns:
            Dictionary with test results per criterion
        """
        results = {}

        try:
            # Fetch the page HTML first
            if hasattr(self.crawler, '_callback_log') and self.crawler._callback_log:
                self.crawler._callback_log(f"📡 Récupération de: {url}")

            page = self.crawler.crawl_page_unique(url)

            if not page:
                raise Exception("Impossible de récupérer la page - aucune réponse du serveur")

            if page.erreur:
                raise Exception(f"Erreur lors de la récupération: {page.erreur}")

            # Log page fetch success
            if hasattr(self.crawler, '_callback_log') and self.crawler._callback_log:
                self.crawler._callback_log(f"🔍 Analyse du HTML ({len(page.html)} caractères)...")

            # Run full RGAA tests if enabled
            if self.full_rgaa_mode:
                results = self._run_full_rgaa_tests(page.html, page.url)
            else:
                results = self._run_section2_tests(page.html, page.url)

        except Exception as e:
            # Log the error
            if hasattr(self.crawler, '_callback_log') and self.crawler._callback_log:
                self.crawler._callback_log(f"❌ Erreur: {str(e)}")

            # Mark as not tested if error occurs
            error_result = {
                'status': Status.NOT_TESTED,
                'modifications': '',
                'comments': f'Erreur lors du test automatique: {str(e)}'
            }

            if self.full_rgaa_mode:
                # Mark all 106 criteria as not tested
                for theme_criteria in [
                    ["1.1", "1.2", "1.3", "1.4", "1.5", "1.6", "1.7", "1.8", "1.9"],
                    ["2.1", "2.2"],
                    ["3.1", "3.2", "3.3"],
                    ["4.1", "4.2", "4.3", "4.4", "4.5", "4.6", "4.7", "4.8", "4.9", "4.10", "4.11", "4.12", "4.13"],
                    ["5.1", "5.2", "5.3", "5.4", "5.5", "5.6", "5.7", "5.8"],
                    ["6.1", "6.2"],
                    ["7.1", "7.2", "7.3", "7.4", "7.5"],
                    ["8.1", "8.2", "8.3", "8.4", "8.5", "8.6", "8.7", "8.8", "8.9", "8.10"],
                    ["9.1", "9.2", "9.3", "9.4"],
                    ["10.1", "10.2", "10.3", "10.4", "10.5", "10.6", "10.7", "10.8", "10.9", "10.10", "10.11", "10.12", "10.13", "10.14"],
                    ["11.1", "11.2", "11.3", "11.4", "11.5", "11.6", "11.7", "11.8", "11.9", "11.10", "11.11", "11.12", "11.13"],
                    ["12.1", "12.2", "12.3", "12.4", "12.5", "12.6", "12.7", "12.8", "12.9", "12.10", "12.11"],
                    ["13.1", "13.2", "13.3", "13.4", "13.5", "13.6", "13.7", "13.8", "13.9", "13.10", "13.11", "13.12"]
                ]:
                    for crit in theme_criteria:
                        results[crit] = error_result.copy()
            else:
                results["2.1"] = error_result.copy()
                results["2.2"] = error_result.copy()

            # Re-raise to let caller handle it
            raise

        return results

    def _run_full_rgaa_tests(self, html: str, url: str) -> Dict:
        """
        Run all 106 RGAA criteria tests.

        Args:
            html: HTML content of the page
            url: URL of the page

        Returns:
            Dictionary with test results per criterion
        """
        results = {}

        # Create web page analyzer with pre-fetched HTML
        analyzer = WebPageAnalyzer(url, html)
        analyzer.fetch()  # This will use the provided HTML

        # Create full RGAA tester
        tester = FullRGAATester(analyzer)

        # Run all tests
        test_results = tester.run_all_tests()

        # Convert TestResult objects to dictionaries compatible with ODS handler
        for criterion_id, result in test_results.items():
            # Build modifications text for column F
            # For NT/NC status, include the reason/recommendation
            modifications_text = result.modifications

            # If modifications is empty but we have issues or manual_check, use those
            if not modifications_text:
                if result.issues:
                    # Join issues into modifications text
                    modifications_text = "; ".join(result.issues[:5])
                elif result.manual_check:
                    # Use manual_check as the reason for NT status
                    modifications_text = result.manual_check

            # For NT status, prefix with indication that manual verification is needed
            if result.status == Status.NOT_TESTED and modifications_text:
                if not modifications_text.startswith("VÉRIFICATION"):
                    modifications_text = f"À VÉRIFIER: {modifications_text}"

            results[criterion_id] = {
                'status': result.status,
                'modifications': modifications_text,
                'comments': result.comments or result.manual_check
            }

        # Log summary
        if hasattr(self.crawler, '_callback_log') and self.crawler._callback_log:
            summary = tester.get_summary(test_results)
            auto_na = summary.get('auto_detected_na', 0)
            self.crawler._callback_log(
                f"✓ Analyse complète: {summary['conforme']}C/{summary['non_conforme']}NC/"
                f"{summary['non_applicable']}NA/{summary['non_teste']}NT "
                f"({summary['compliance_rate']}% conformité)"
            )
            if auto_na > 0:
                self.crawler._callback_log(
                    f"  ↳ {auto_na} critères NA auto-détectés (éléments absents de la page)"
                )

        return results

    def _run_section2_tests(self, html: str, url: str) -> Dict:
        """
        Run Section 2 (CADRES) tests only (legacy mode).

        Args:
            html: HTML content of the page
            url: URL of the page

        Returns:
            Dictionary with test results for criteria 2.1 and 2.2
        """
        results = {}

        resultat_page = self.analyseur.analyser_page(html, url)

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

        # Log analysis results
        if hasattr(self.crawler, '_callback_log') and self.crawler._callback_log:
            frames_info = f"{resultat_page.cadres_testes} cadre(s) détecté(s)"
            if resultat_page.cadres_testes > 0:
                conf_info = f", {resultat_page.cadres_testes - resultat_page.non_conformes_2_1} conforme(s)"
                self.crawler._callback_log(f"✓ Analyse terminée: {frames_info}{conf_info}")
            else:
                self.crawler._callback_log(f"✓ Analyse terminée: {frames_info}")

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

        if self.full_rgaa_mode:
            summary += "\n---\n\n*Rapport généré automatiquement par RGAA Audit Complet (106 critères)*\n"
        else:
            summary += "\n---\n\n*Rapport généré automatiquement par RGAA Section 2 Tester*\n"

        return summary
