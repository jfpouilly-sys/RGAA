"""
Orchestrateur du test RGAA 10.7 — Visibilite du focus.
Coordonne la detection, l'analyse et la classification.

Usage :
    with FocusTester(headless=True) as tester:
        results = tester.test_urls(urls)
"""

from dataclasses import dataclass, field
from playwright.sync_api import sync_playwright, Page, Browser
from .focus_detector import FocusDetector, FocusableElement
from .css_analyzer import CSSFocusAnalyzer
from .constants import FocusStatus


@dataclass
class PageFocusResult:
    """Resultat complet de l'analyse d'une page."""
    url: str
    page_id: str
    total_focusable: int = 0
    total_visible: int = 0
    total_conforme: int = 0
    total_non_conforme: int = 0
    total_a_verifier: int = 0
    elements: list = field(default_factory=list)
    stylesheet_analysis: dict = field(default_factory=dict)
    suggested_status: str = ""
    confidence: str = ""
    details: str = ""

    def compute_suggested_status(self):
        """
        Determine le statut suggere pour la grille ODS.

        Logique :
        - Si au moins 1 NC et 0 A_VERIFIER -> NC (haute confiance)
        - Si 0 NC et 0 A_VERIFIER et >0 C -> C (haute confiance)
        - Si des A_VERIFIER existent -> NT ou C/NC selon proportions
        - Si 0 elements focusables -> NA
        """
        if self.total_focusable == 0 or self.total_visible == 0:
            self.suggested_status = FocusStatus.NON_APPLICABLE
            self.confidence = "haute"
            self.details = "Aucun element focusable visible detecte"
            return

        if self.total_non_conforme > 0 and self.total_a_verifier == 0:
            self.suggested_status = FocusStatus.NON_CONFORME
            self.confidence = "haute"
            self.details = (
                f"{self.total_non_conforme} element(s) avec outline supprime "
                f"sans compensation detectee"
            )
        elif self.total_non_conforme == 0 and self.total_a_verifier == 0:
            self.suggested_status = FocusStatus.CONFORME
            self.confidence = "haute"
            self.details = (
                f"Tous les {self.total_conforme} elements analyses ont un "
                f"indicateur de focus visible"
            )
        elif self.total_non_conforme > 0 and self.total_a_verifier > 0:
            self.suggested_status = FocusStatus.NON_CONFORME
            self.confidence = "moyenne"
            self.details = (
                f"{self.total_non_conforme} NC confirme(s), "
                f"{self.total_a_verifier} a verifier manuellement"
            )
        else:
            # Que des A_VERIFIER, pas de NC
            self.suggested_status = FocusStatus.A_VERIFIER
            self.confidence = "faible"
            self.details = (
                f"{self.total_a_verifier} element(s) necessitent une "
                f"verification manuelle"
            )


class FocusTester:
    """
    Testeur principal pour le critere RGAA 10.7.

    Usage :
        tester = FocusTester()
        results = tester.test_urls(urls, page_ids)
        tester.generate_report(results, output_path)
    """

    def __init__(self, headless: bool = True, browser_type: str = 'chromium'):
        self.headless = headless
        self.browser_type = browser_type
        self._browser: Browser | None = None
        self._playwright = None

    def __enter__(self):
        self._playwright = sync_playwright().start()
        browser_launcher = getattr(self._playwright, self.browser_type)
        self._browser = browser_launcher.launch(headless=self.headless)
        return self

    def __exit__(self, *args):
        if self._browser:
            self._browser.close()
        if self._playwright:
            self._playwright.stop()

    def test_page(self, url: str, page_id: str,
                  progress_callback=None) -> PageFocusResult:
        """
        Teste une page complete pour le critere 10.7.

        Args:
            url: URL de la page a tester
            page_id: Identifiant de la page (ex: "P01")
            progress_callback: Fonction optionnelle (message: str, percent: float)

        Returns:
            PageFocusResult avec tous les details
        """
        result = PageFocusResult(url=url, page_id=page_id)

        page = self._browser.new_page()
        try:
            # Charger la page
            if progress_callback:
                progress_callback(f"Chargement de {url}...", 0.0)

            page.goto(url, wait_until='networkidle', timeout=30000)
            page.wait_for_timeout(1000)

            # Etape 1 : Analyse des feuilles de style
            if progress_callback:
                progress_callback("Analyse des feuilles de style...", 0.1)

            analyzer = CSSFocusAnalyzer(page)
            result.stylesheet_analysis = analyzer.analyze_stylesheet_rules()

            # Etape 2 : Detecter les elements focusables
            if progress_callback:
                progress_callback(
                    "Detection des elements focusables...", 0.2
                )

            detector = FocusDetector(page)
            elements = detector.detect_all()
            result.total_focusable = len(elements)

            visible_elements = [e for e in elements if e.is_visible]
            result.total_visible = len(visible_elements)

            if not visible_elements:
                result.suggested_status = FocusStatus.NON_APPLICABLE
                result.confidence = "haute"
                result.details = "Aucun element focusable visible"
                return result

            # Etape 3 : Analyser chaque element
            for i, element in enumerate(visible_elements):
                if progress_callback:
                    pct = 0.2 + (0.7 * (i / len(visible_elements)))
                    progress_callback(
                        f"Analyse element {i+1}/{len(visible_elements)} : "
                        f"{element.identifier}",
                        pct
                    )

                analyzer.analyze_element(element)
                result.elements.append(element)

                # Compteurs
                if element.status == FocusStatus.CONFORME:
                    result.total_conforme += 1
                elif element.status == FocusStatus.NON_CONFORME:
                    result.total_non_conforme += 1
                elif element.status == FocusStatus.A_VERIFIER:
                    result.total_a_verifier += 1

            # Etape 4 : Calculer le statut suggere
            result.compute_suggested_status()

            if progress_callback:
                progress_callback("Analyse terminee", 1.0)

        except Exception as e:
            result.details = f"Erreur lors du test : {str(e)}"
            result.suggested_status = FocusStatus.A_VERIFIER
            result.confidence = "faible"
        finally:
            page.close()

        return result

    def test_urls(self, urls: list[tuple[str, str]],
                  progress_callback=None) -> list[PageFocusResult]:
        """
        Teste plusieurs pages.

        Args:
            urls: Liste de tuples (url, page_id)
            progress_callback: Callback de progression global

        Returns:
            Liste de PageFocusResult
        """
        results = []
        for i, (url, page_id) in enumerate(urls):
            if progress_callback:
                progress_callback(
                    f"Page {i+1}/{len(urls)} : {page_id}",
                    i / len(urls)
                )

            result = self.test_page(url, page_id, progress_callback=None)
            results.append(result)

        return results
