# -*- coding: utf-8 -*-
"""
ODS Audit Analyzer - Integrates ODS handler with automated testing.

Connects the ODS file format with our automated accessibility tests.
Supports full RGAA 4.1.2 testing with all 106 criteria.
Optionally enhances criterion 10.7 with Playwright-based focus testing.
"""

import csv
import os
import sys
from typing import Dict, List, Optional
from .ods_handler import RGAAAuditODSHandler
from .ods_models import Status, Derogation, PageAudit, AuditCriterion
from .analyzer import AnalyseurRGAA, ResultatTest
from .crawler import Crawler
from .config import get_config
from .full_rgaa_tester import FullRGAATester, WebPageAnalyzer, TestResult

# Ensure criterion_10_7 package is importable (it lives alongside rgaa_tester/)
_parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _parent_dir not in sys.path:
    sys.path.insert(0, _parent_dir)

# Optional Playwright-based focus testing for criterion 10.7
PLAYWRIGHT_AVAILABLE = False
PLAYWRIGHT_IMPORT_ERROR = ""
try:
    from criterion_10_7.focus_tester import FocusTester, PageFocusResult
    from criterion_10_7.constants import FocusStatus
    PLAYWRIGHT_AVAILABLE = True
except ImportError as _e:
    PLAYWRIGHT_IMPORT_ERROR = str(_e)

# Optional Playwright-based image alt checking for criterion 1.1
IMAGE_ALT_CHECKER_AVAILABLE = False
IMAGE_ALT_CHECKER_IMPORT_ERROR = ""
try:
    from image_alt_checker import ImageAltChecker, audit_criterion_1_1
    IMAGE_ALT_CHECKER_AVAILABLE = True
except ImportError as _e:
    IMAGE_ALT_CHECKER_IMPORT_ERROR = str(_e)


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
        self.output_dir = "."  # Default output directory
        self.focus_test_enabled = False  # Playwright focus testing for 10.7
        self._focus_tester = None  # Shared FocusTester instance
        self.image_alt_test_enabled = False  # Playwright image alt testing for 1.1

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
            if hasattr(self.crawler, '_callback_log') and self.crawler._callback_log:
                self.crawler._callback_log(f"❌ Page {page_id} non trouvée dans les données")
            return None

        url = page_data.url

        # Log diagnostic info for debugging
        if hasattr(self.crawler, '_callback_log') and self.crawler._callback_log:
            self.crawler._callback_log(f"🔎 Page ID: {page_id} | Titre: {page_data.title}")
            self.crawler._callback_log(f"🔗 URL à analyser: {url}")

        # Check if URL is valid
        if url in ["Absente", ""] or not url.startswith("http"):
            # Log that page is absent
            if hasattr(self.crawler, '_callback_log') and self.crawler._callback_log:
                self.crawler._callback_log(f"⊘ Page {page_id} absente ou URL invalide - tous les critères marqués NA")
                self.crawler._callback_log(f"   Critère | Description | Statut")
                self.crawler._callback_log(f"   " + "-" * 60)

            # Mark all criteria as NA in memory (fast)
            for criterion in page_data.criteria:
                criterion.status = Status.NOT_APPLICABLE
                criterion.modifications = "Page absente ou URL invalide"
                # Log each criterion
                if hasattr(self.crawler, '_callback_log') and self.crawler._callback_log:
                    desc = criterion.description[:50] + "..." if len(criterion.description) > 50 else criterion.description
                    self.crawler._callback_log(f"   {criterion.criterion_id} | {desc} | ⊘ NA")

            # Save CSV for this page (use memory data since ODS not updated)
            csv_path = self.save_page_csv(page_id, output_dir=self.output_dir, use_memory_data=True)
            if csv_path and hasattr(self.crawler, '_callback_log') and self.crawler._callback_log:
                self.crawler._callback_log(f"💾 CSV sauvegardé: {csv_path}")

            return page_data

        if not run_automated_tests:
            return page_data

        # Run automated tests
        results = self.run_automated_tests(url)

        # Helper to get status symbol
        def status_symbol(status):
            symbols = {
                Status.COMPLIANT: "✓ C",
                Status.NON_COMPLIANT: "✗ NC",
                Status.NOT_APPLICABLE: "⊘ NA",
                Status.NOT_TESTED: "? NT"
            }
            return symbols.get(status, "? NT")

        # Log header for criteria list
        if hasattr(self.crawler, '_callback_log') and self.crawler._callback_log:
            self.crawler._callback_log(f"   Critère | Description | Statut")
            self.crawler._callback_log(f"   " + "-" * 60)

        # Update criteria based on test results, but skip NA criteria
        for criterion_id, result in results.items():
            # Get criterion info for logging
            criterion = page_data.get_criterion(criterion_id)
            description = criterion.description[:50] + "..." if criterion and len(criterion.description) > 50 else (criterion.description if criterion else "")

            if criterion and criterion.status == Status.NOT_APPLICABLE:
                # Skip updating NA criteria - they remain NA
                if hasattr(self.crawler, '_callback_log') and self.crawler._callback_log:
                    self.crawler._callback_log(f"   {criterion_id} | {description} | {status_symbol(Status.NOT_APPLICABLE)} (pré-marqué)")
                continue

            # Log criterion being tested with result
            if hasattr(self.crawler, '_callback_log') and self.crawler._callback_log:
                self.crawler._callback_log(f"   {criterion_id} | {description} | {status_symbol(result['status'])}")

            self.handler.update_criterion(
                page_id=page_id,
                criterion_id=criterion_id,
                status=result['status'],
                modifications=result.get('modifications', ''),
                comments=result.get('comments', '')
            )

        # Reload updated page data
        updated_page = self.handler.get_page_audit(page_id)

        # Save CSV file for this page (use memory data for correct results)
        csv_path = self.save_page_csv(page_id, output_dir=self.output_dir, use_memory_data=True)
        if csv_path and hasattr(self.crawler, '_callback_log') and self.crawler._callback_log:
            self.crawler._callback_log(f"💾 CSV sauvegardé: {csv_path}")

        return updated_page

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

    def _run_full_rgaa_tests(self, html: str, url: str,
                             media_detection_data: dict = None) -> Dict:
        """
        Run all 106 RGAA criteria tests.

        Args:
            html: HTML content of the page
            url: URL of the page
            media_detection_data: Optional Playwright-based media detection data
                                  from MediaDetector.detect_all_media()

        Returns:
            Dictionary with test results per criterion
        """
        results = {}

        # Create web page analyzer with pre-fetched HTML
        analyzer = WebPageAnalyzer(url, html)
        analyzer.fetch()  # This will use the provided HTML

        # Create full RGAA tester with optional media detection data
        tester = FullRGAATester(analyzer, media_detection_data=media_detection_data)

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

        # Enhance criterion 10.7 with Playwright dynamic analysis if enabled
        focus_10_7_status = "non demandé"
        if self.focus_test_enabled:
            if PLAYWRIGHT_AVAILABLE:
                focus_result, focus_error = self._run_focus_test(url)
                if focus_result:
                    results["10.7"] = focus_result
                    focus_10_7_status = f"exécuté ({focus_result['status'].value})"
                else:
                    focus_10_7_status = (
                        f"erreur — {focus_error}. "
                        f"Résultat statique conservé pour 10.7"
                    )
            else:
                focus_10_7_status = f"indisponible — {PLAYWRIGHT_IMPORT_ERROR}"
                if hasattr(self.crawler, '_callback_log') and self.crawler._callback_log:
                    self.crawler._callback_log(
                        f"   ⚠️ Critère 10.7 focus (Playwright): {focus_10_7_status}"
                    )
                    self.crawler._callback_log(
                        "      → Installer avec: pip install playwright && playwright install chromium"
                    )
        else:
            # Focus test not enabled — log the reason
            if not PLAYWRIGHT_AVAILABLE:
                focus_10_7_status = (
                    "désactivé (Playwright non installé). "
                    "Installer: pip install playwright && playwright install chromium"
                )
            else:
                focus_10_7_status = (
                    "désactivé (cocher 'Test focus 10.7' dans les options, "
                    "ou utiliser --focus en CLI)"
                )

        # Enhance criterion 1.1 with Playwright dynamic analysis if enabled
        image_alt_1_1_status = "non demandé"
        if self.image_alt_test_enabled:
            if IMAGE_ALT_CHECKER_AVAILABLE and PLAYWRIGHT_AVAILABLE:
                alt_result, alt_error = self._run_image_alt_test(url)
                if alt_result:
                    results["1.1"] = alt_result
                    image_alt_1_1_status = f"exécuté ({alt_result['status'].value})"
                else:
                    image_alt_1_1_status = (
                        f"erreur — {alt_error}. "
                        f"Résultat statique conservé pour 1.1"
                    )
            else:
                if not IMAGE_ALT_CHECKER_AVAILABLE:
                    image_alt_1_1_status = f"indisponible — {IMAGE_ALT_CHECKER_IMPORT_ERROR}"
                else:
                    image_alt_1_1_status = f"indisponible — {PLAYWRIGHT_IMPORT_ERROR}"
        else:
            if not IMAGE_ALT_CHECKER_AVAILABLE or not PLAYWRIGHT_AVAILABLE:
                image_alt_1_1_status = "désactivé (Playwright non installé)"
            else:
                image_alt_1_1_status = "désactivé (non activé dans les options)"

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
            # Always log criterion 10.7 focus test status
            self.crawler._callback_log(
                f"  ↳ Critère 10.7 focus (Playwright): {focus_10_7_status}"
            )
            # Log criterion 1.1 image alt test status
            self.crawler._callback_log(
                f"  ↳ Critère 1.1 images (Playwright): {image_alt_1_1_status}"
            )

        return results

    def start_focus_tester(self):
        """
        Start the shared Playwright browser for focus testing.
        Call this before analyzing pages when focus_test_enabled is True.
        The browser stays open for all pages, avoiding repeated launch overhead.
        """
        if not PLAYWRIGHT_AVAILABLE:
            if hasattr(self.crawler, '_callback_log') and self.crawler._callback_log:
                self.crawler._callback_log(
                    "⚠️ Playwright non disponible — test focus 10.7 désactivé. "
                    "Installer avec: pip install playwright && playwright install chromium"
                )
            return False

        try:
            self._focus_tester = FocusTester(headless=True)
            self._focus_tester.__enter__()
            if hasattr(self.crawler, '_callback_log') and self.crawler._callback_log:
                self.crawler._callback_log(
                    "🔎 Navigateur Playwright démarré pour test focus 10.7"
                )
            return True
        except Exception as e:
            error_msg = str(e)
            if hasattr(self.crawler, '_callback_log') and self.crawler._callback_log:
                self.crawler._callback_log(
                    f"⚠️ Impossible de démarrer Playwright: {error_msg}"
                )
                if "chromium" in error_msg.lower() or "executable" in error_msg.lower() or "browser" in error_msg.lower():
                    self.crawler._callback_log(
                        "   → Le navigateur Chromium n'est probablement pas installé."
                    )
                    self.crawler._callback_log(
                        "   → Exécuter: playwright install chromium"
                    )
            self._focus_tester = None
            return False

    def stop_focus_tester(self):
        """Stop the shared Playwright browser."""
        if self._focus_tester:
            try:
                self._focus_tester.__exit__(None, None, None)
            except Exception:
                pass
            self._focus_tester = None

    def _run_focus_test(self, url: str) -> tuple:
        """
        Run Playwright-based focus visibility test for criterion 10.7.

        Uses the shared FocusTester browser instance to analyze computed
        styles before/after focus on each focusable element.

        Args:
            url: URL to test

        Returns:
            Tuple (result_dict, error_message).
            result_dict is None on error, error_message is "" on success.
        """
        if not self._focus_tester:
            # No shared instance — try creating a temporary one
            try:
                with FocusTester(headless=True) as temp_tester:
                    return self._execute_focus_test(temp_tester, url)
            except Exception as e:
                error_msg = str(e)
                if hasattr(self.crawler, '_callback_log') and self.crawler._callback_log:
                    self.crawler._callback_log(
                        f"   ⚠️ Test focus 10.7 échoué (lancement navigateur): {error_msg}"
                    )
                    self.crawler._callback_log(
                        "      → Avez-vous exécuté: playwright install chromium ?"
                    )
                return None, error_msg
        else:
            return self._execute_focus_test(self._focus_tester, url)

    def _execute_focus_test(self, tester: 'FocusTester', url: str) -> tuple:
        """
        Execute the focus test and convert result to ODS-compatible dict.

        Args:
            tester: FocusTester instance with active browser
            url: URL to test

        Returns:
            Tuple (result_dict, error_message).
            result_dict is None on error, error_message is "" on success.
        """
        log = None
        if hasattr(self.crawler, '_callback_log') and self.crawler._callback_log:
            log = self.crawler._callback_log

        try:
            if log:
                log("   🔎 Test focus 10.7 (Playwright)...")

            def progress_cb(msg, pct):
                if log:
                    log(f"      {msg}")

            # page_id is not critical here — just for the result object
            result = tester.test_page(url, "focus", progress_callback=progress_cb)

            if log:
                log(
                    f"   🔎 Focus 10.7: {result.total_conforme}C / "
                    f"{result.total_non_conforme}NC / "
                    f"{result.total_a_verifier} à vérifier "
                    f"(confiance: {result.confidence})"
                )

            # Convert FocusStatus to ODS Status
            status_map = {
                FocusStatus.CONFORME: Status.COMPLIANT,
                FocusStatus.NON_CONFORME: Status.NON_COMPLIANT,
                FocusStatus.NON_APPLICABLE: Status.NOT_APPLICABLE,
                FocusStatus.A_VERIFIER: Status.NOT_TESTED,
            }
            ods_status = status_map.get(
                result.suggested_status, Status.NOT_TESTED
            )

            # Build modifications text
            prefix = "[FOCUS-AUTO]" if result.confidence == "haute" else "[FOCUS-PARTIEL]"
            modifications = (
                f"{prefix} {result.details}. "
                f"Éléments analysés: {result.total_visible}, "
                f"C={result.total_conforme}, NC={result.total_non_conforme}, "
                f"À vérifier={result.total_a_verifier}."
            )

            # Build detailed comments with NC elements
            comments_parts = []
            nc_elements = [
                e for e in result.elements
                if e.status == FocusStatus.NON_CONFORME
            ]
            if nc_elements:
                comments_parts.append(
                    f"NC: {', '.join(e.identifier for e in nc_elements[:5])}"
                )
            av_elements = [
                e for e in result.elements
                if e.status == FocusStatus.A_VERIFIER
            ]
            if av_elements:
                comments_parts.append(
                    f"À vérifier: {len(av_elements)} élément(s)"
                )
            if result.stylesheet_analysis.get('global_outline_none'):
                comments_parts.append(
                    "ALERTE: règle globale outline:none détectée"
                )
            comments = "; ".join(comments_parts) if comments_parts else ""

            return {
                'status': ods_status,
                'modifications': modifications,
                'comments': comments
            }, ""

        except Exception as e:
            error_msg = str(e)
            if log:
                log(f"   ⚠️ Erreur test focus 10.7: {error_msg}")
            return None, error_msg

    def _run_image_alt_test(self, url: str) -> tuple:
        """
        Run Playwright-based image alt text test for criterion 1.1.

        Uses a temporary Playwright browser to analyze all image elements
        and their accessible names according to RGAA algorithm.

        Args:
            url: URL to test

        Returns:
            Tuple (result_dict, error_message).
            result_dict is None on error, error_message is "" on success.
        """
        import asyncio

        log = None
        if hasattr(self.crawler, '_callback_log') and self.crawler._callback_log:
            log = self.crawler._callback_log

        try:
            if log:
                log("   🔎 Test images 1.1 (Playwright)...")

            async def _run():
                from playwright.async_api import async_playwright
                async with async_playwright() as pw:
                    browser = await pw.chromium.launch(headless=True)
                    page = await browser.new_page()
                    await page.goto(url, wait_until='domcontentloaded', timeout=30000)
                    audit_result = await audit_criterion_1_1(page)
                    await browser.close()
                    return audit_result

            # Run async code from sync context
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                loop = None

            if loop and loop.is_running():
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as pool:
                    audit_result = pool.submit(
                        lambda: asyncio.run(_run())
                    ).result()
            else:
                audit_result = asyncio.run(_run())

            if log:
                summary = audit_result['results']['summary']
                log(
                    f"   🔎 Images 1.1: {summary['with_alternative']} avec alt / "
                    f"{summary['without_alternative']} sans alt "
                    f"(total: {summary['total_images']})"
                )

            # Convert to ODS-compatible status
            status_str = audit_result['status']
            status_map = {'C': Status.COMPLIANT, 'NC': Status.NON_COMPLIANT, 'NA': Status.NOT_APPLICABLE}
            ods_status = status_map.get(status_str, Status.NOT_TESTED)

            summary = audit_result['results']['summary']
            prefix = "[IMAGE-ALT-AUTO]"
            modifications = (
                f"{prefix} {summary['total_images']} images analysées. "
                f"Avec alternative: {summary['with_alternative']}, "
                f"Sans alternative: {summary['without_alternative']}. "
                f"Erreurs: {summary['total_errors']}, "
                f"Avertissements: {summary['total_warnings']}. "
                f"Couverture automatique: 60%."
            )

            comments_parts = []
            if summary['without_alternative'] > 0:
                comments_parts.append(
                    f"{summary['without_alternative']} image(s) sans alternative textuelle"
                )
            if summary['total_warnings'] > 0:
                comments_parts.append(
                    f"{summary['total_warnings']} avertissement(s) à vérifier"
                )
            comments_parts.append(
                "Vérification manuelle requise: pertinence des alternatives (critère 1.3)"
            )
            comments = "; ".join(comments_parts)

            return {
                'status': ods_status,
                'modifications': modifications,
                'comments': comments
            }, ""

        except Exception as e:
            error_msg = str(e)
            if log:
                log(f"   ⚠️ Erreur test images 1.1: {error_msg}")
            return None, error_msg

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

    def analyze_all_pages(self, progress_callback=None, log_callback=None) -> Dict:
        """
        Analyze all pages in the audit file.

        Args:
            progress_callback: Optional callback function(page_id, progress, total)
            log_callback: Optional callback function(message) for logging

        Returns:
            Dictionary with summary statistics
        """
        pages = self.handler.get_sample_pages()
        total = len(pages)

        # Use crawler's log callback if not provided
        if log_callback is None and hasattr(self.crawler, '_callback_log'):
            log_callback = self.crawler._callback_log

        def _log(msg):
            if log_callback:
                log_callback(msg)
            else:
                print(msg)

        for i, page_info in enumerate(pages):
            page_id = page_info['page_id']

            if progress_callback:
                progress_callback(page_id, i + 1, total)

            try:
                self.analyze_page(page_id, run_automated_tests=True)
            except Exception as e:
                _log(f"⚠️ Erreur lors de l'analyse de {page_id}: {str(e)}")
                # Continue with next page instead of stopping

        # After all pages analyzed, generate complete audit.xlsx if input was xlsx/ods
        stats = self.handler.calculate_synthesis()
        self._populate_xlsx_audit(_log)
        return stats

    def _populate_xlsx_audit(self, log_callback=None):
        """
        Call populate_xlsx_audit to generate a complete audit.xlsx file
        based on the input xlsx file and generated CSV results.

        Only runs when the input file is xlsx or ods format.

        Args:
            log_callback: Optional callback for logging messages
        """
        def _log(msg):
            if log_callback:
                log_callback(msg)
            else:
                print(msg)

        # Check if the input file is xlsx or ods
        if not self.handler or not hasattr(self.handler, 'filepath'):
            return

        input_path = self.handler.filepath
        ext = os.path.splitext(input_path)[1].lower()

        if ext not in ['.xlsx', '.xlsm', '.xls', '.ods']:
            return

        try:
            from pathlib import Path
            _log("=" * 50)
            _log("Generation du fichier audit.xlsx complet...")

            # Import the populator
            # The populate_xlsx_audit.py script is in the parent directory
            script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            populate_module_path = os.path.join(script_dir, 'populate_xlsx_audit.py')

            if not os.path.exists(populate_module_path):
                _log(f"Script populate_xlsx_audit.py non trouve: {populate_module_path}")
                return

            # Import the module dynamically
            import importlib.util
            spec = importlib.util.spec_from_file_location("populate_xlsx_audit", populate_module_path)
            populate_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(populate_module)

            # Find the xlsx template file
            template_path = Path(input_path)

            # Look for CSV files in the output directory
            output_dir = self.output_dir or os.path.dirname(input_path)
            csv_pattern = os.path.join(output_dir, "P*.csv")

            import glob
            csv_files = sorted(glob.glob(csv_pattern))
            if not csv_files:
                _log("Aucun fichier CSV genere - impossible de populer le fichier audit.xlsx")
                return

            _log(f"Fichiers CSV trouves: {len(csv_files)}")

            # Determine output file path
            output_xlsx = Path(output_dir) / f"{template_path.stem}_audit_complete.xlsx"

            # Create populator and run
            populator = populate_module.XLSXAuditPopulator(
                xlsx_template=template_path,
                output_xlsx=output_xlsx
            )

            # Load all CSV files
            original_cwd = os.getcwd()
            try:
                os.chdir(output_dir)
                num_loaded = populator.load_csv_files("P*.csv")
            finally:
                os.chdir(original_cwd)

            if num_loaded > 0:
                success = populator.update_xlsx_file()
                if success:
                    _log(f"Fichier audit complet genere: {output_xlsx}")
                else:
                    _log("Erreur lors de la mise a jour du fichier XLSX")
            else:
                _log("Aucun fichier CSV charge - generation du fichier audit.xlsx ignoree")

        except Exception as e:
            _log(f"Erreur lors de la generation du fichier audit.xlsx: {str(e)}")

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

        # Criterion 10.7 focus testing status section
        summary += "\n## Critère 10.7 — Visibilité du focus\n\n"
        if self.focus_test_enabled and PLAYWRIGHT_AVAILABLE:
            summary += (
                "- **Test dynamique (Playwright)** : activé\n"
                "- Les résultats du critère 10.7 ont été enrichis par une analyse "
                "des computed styles CSS avant/après focus\n"
                "- Couverture estimée : ~60%\n"
            )
        elif self.focus_test_enabled and not PLAYWRIGHT_AVAILABLE:
            summary += (
                f"- **Test dynamique (Playwright)** : demandé mais indisponible\n"
                f"- Raison : {PLAYWRIGHT_IMPORT_ERROR}\n"
                "- Installation : `pip install playwright && playwright install chromium`\n"
                "- Le critère 10.7 a été testé en analyse statique uniquement (couverture ~50%)\n"
            )
        else:
            summary += (
                "- **Test dynamique (Playwright)** : désactivé\n"
            )
            if not PLAYWRIGHT_AVAILABLE:
                summary += (
                    f"- Playwright non installé ({PLAYWRIGHT_IMPORT_ERROR})\n"
                    "- Installation : `pip install playwright && playwright install chromium`\n"
                )
            else:
                summary += (
                    "- Pour activer : cocher 'Test focus 10.7' dans les options, "
                    "ou utiliser `--focus` en CLI\n"
                )
            summary += (
                "- Le critère 10.7 a été testé en analyse statique uniquement (couverture ~50%)\n"
            )

        if self.full_rgaa_mode:
            summary += "\n---\n\n*Rapport généré automatiquement par RGAA Audit Complet (106 critères)*\n"
        else:
            summary += "\n---\n\n*Rapport généré automatiquement par RGAA Section 2 Tester*\n"

        return summary

    def save_page_csv(self, page_id: str, output_dir: str = ".", use_memory_data: bool = False) -> str:
        """
        Save page test results to a CSV file.

        Exports the Pxx tab directly from ODS, preserving all rows
        with their current test results.

        Args:
            page_id: Page identifier (P01, P02, etc.)
            output_dir: Directory to save the CSV file (default: current directory)
            use_memory_data: If True, use in-memory data instead of ODS

        Returns:
            Path to the saved CSV file
        """
        # Create CSV filename
        csv_filename = f"{page_id}.csv"
        csv_path = os.path.join(output_dir, csv_filename)

        if use_memory_data:
            # Export from in-memory data (for absent pages)
            page_data = self.handler.get_page_audit(page_id)
            if not page_data:
                return ""

            with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile, delimiter=';', quoting=csv.QUOTE_MINIMAL)

                # Write header (including Page and URL columns for compatibility with populate_xlsx_audit.py)
                writer.writerow([
                    'Page',
                    'URL',
                    'Thématique',
                    'Critère',
                    'Description',
                    'Statut',
                    'Dérogation',
                    'Modifications',
                    'Commentaires',
                    'Date de modification'
                ])

                # Write criteria rows
                for criterion in page_data.criteria:
                    writer.writerow([
                        page_id,
                        page_data.url,
                        criterion.theme,
                        criterion.criterion_id,
                        criterion.description,
                        criterion.status.value,
                        criterion.derogation.value,
                        criterion.modifications,
                        criterion.comments,
                        criterion.modification_date
                    ])

            return csv_path
        else:
            # Export directly from ODS sheet (preserves all rows)
            success = self.handler.export_page_to_csv(page_id, csv_path)
            return csv_path if success else ""
