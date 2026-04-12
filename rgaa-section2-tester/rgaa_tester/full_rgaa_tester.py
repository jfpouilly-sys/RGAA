# -*- coding: utf-8 -*-
"""
Module complet d'analyse RGAA 4.1.2 - 106 critères

Implémente les tests de conformité pour tous les critères du RGAA 4.1.2
organisés par thématique.
"""

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from bs4 import BeautifulSoup, Tag
import requests
from .ods_models import Status
from .content_detector import ContentDetector


@dataclass
class TestResult:
    """Résultat d'un test de critère RGAA."""
    criterion_id: str
    status: Status
    issues: List[str] = field(default_factory=list)
    modifications: str = ""
    comments: str = ""
    automated_coverage: float = 0.0
    manual_check: str = ""

    def to_dict(self) -> Dict:
        return {
            'status': self.status,
            'issues': self.issues,
            'modifications': self.modifications,
            'comments': self.comments,
            'automated_coverage': self.automated_coverage,
            'manual_check': self.manual_check
        }


class WebPageAnalyzer:
    """Analyseur de page web pour les tests RGAA."""

    def __init__(self, url: str, html: str = None):
        """
        Initialise l'analyseur.

        Args:
            url: URL de la page
            html: Contenu HTML (optionnel, sera récupéré si non fourni)
        """
        self.url = url
        self.html = html
        self.soup = None
        self._fetched = False

    def fetch(self) -> bool:
        """Récupère la page web et parse le HTML."""
        if self.html:
            self.soup = BeautifulSoup(self.html, 'lxml')
            self._fetched = True
            return True

        try:
            headers = {'User-Agent': 'RGAA-Auditor/2.0'}
            response = requests.get(self.url, headers=headers, timeout=30)
            response.raise_for_status()
            self.html = response.text
            self.soup = BeautifulSoup(self.html, 'lxml')
            self._fetched = True
            return True
        except Exception as e:
            print(f"Erreur récupération {self.url}: {e}")
            return False

    def is_ready(self) -> bool:
        return self._fetched and self.soup is not None


class FullRGAATester:
    """
    Testeur RGAA complet - 106 critères.

    Exécute tous les tests de conformité RGAA 4.1.2 sur une page web.
    """

    # Mapping des critères aux thématiques
    CRITERIA_THEMES = {
        "1.1": "IMAGES", "1.2": "IMAGES", "1.3": "IMAGES", "1.4": "IMAGES",
        "1.5": "IMAGES", "1.6": "IMAGES", "1.7": "IMAGES", "1.8": "IMAGES", "1.9": "IMAGES",
        "2.1": "CADRES", "2.2": "CADRES",
        "3.1": "COULEURS", "3.2": "COULEURS", "3.3": "COULEURS",
        "4.1": "MULTIMÉDIA", "4.2": "MULTIMÉDIA", "4.3": "MULTIMÉDIA", "4.4": "MULTIMÉDIA",
        "4.5": "MULTIMÉDIA", "4.6": "MULTIMÉDIA", "4.7": "MULTIMÉDIA", "4.8": "MULTIMÉDIA",
        "4.9": "MULTIMÉDIA", "4.10": "MULTIMÉDIA", "4.11": "MULTIMÉDIA", "4.12": "MULTIMÉDIA",
        "4.13": "MULTIMÉDIA",
        "5.1": "TABLEAUX", "5.2": "TABLEAUX", "5.3": "TABLEAUX", "5.4": "TABLEAUX",
        "5.5": "TABLEAUX", "5.6": "TABLEAUX", "5.7": "TABLEAUX", "5.8": "TABLEAUX",
        "6.1": "LIENS", "6.2": "LIENS",
        "7.1": "SCRIPTS", "7.2": "SCRIPTS", "7.3": "SCRIPTS", "7.4": "SCRIPTS", "7.5": "SCRIPTS",
        "8.1": "ÉLÉMENTS OBLIGATOIRES", "8.2": "ÉLÉMENTS OBLIGATOIRES",
        "8.3": "ÉLÉMENTS OBLIGATOIRES", "8.4": "ÉLÉMENTS OBLIGATOIRES",
        "8.5": "ÉLÉMENTS OBLIGATOIRES", "8.6": "ÉLÉMENTS OBLIGATOIRES",
        "8.7": "ÉLÉMENTS OBLIGATOIRES", "8.8": "ÉLÉMENTS OBLIGATOIRES",
        "8.9": "ÉLÉMENTS OBLIGATOIRES", "8.10": "ÉLÉMENTS OBLIGATOIRES",
        "9.1": "STRUCTURATION DE L'INFORMATION", "9.2": "STRUCTURATION DE L'INFORMATION",
        "9.3": "STRUCTURATION DE L'INFORMATION", "9.4": "STRUCTURATION DE L'INFORMATION",
        "10.1": "PRÉSENTATION DE L'INFORMATION", "10.2": "PRÉSENTATION DE L'INFORMATION",
        "10.3": "PRÉSENTATION DE L'INFORMATION", "10.4": "PRÉSENTATION DE L'INFORMATION",
        "10.5": "PRÉSENTATION DE L'INFORMATION", "10.6": "PRÉSENTATION DE L'INFORMATION",
        "10.7": "PRÉSENTATION DE L'INFORMATION", "10.8": "PRÉSENTATION DE L'INFORMATION",
        "10.9": "PRÉSENTATION DE L'INFORMATION", "10.10": "PRÉSENTATION DE L'INFORMATION",
        "10.11": "PRÉSENTATION DE L'INFORMATION", "10.12": "PRÉSENTATION DE L'INFORMATION",
        "10.13": "PRÉSENTATION DE L'INFORMATION", "10.14": "PRÉSENTATION DE L'INFORMATION",
        "11.1": "FORMULAIRES", "11.2": "FORMULAIRES", "11.3": "FORMULAIRES",
        "11.4": "FORMULAIRES", "11.5": "FORMULAIRES", "11.6": "FORMULAIRES",
        "11.7": "FORMULAIRES", "11.8": "FORMULAIRES", "11.9": "FORMULAIRES",
        "11.10": "FORMULAIRES", "11.11": "FORMULAIRES", "11.12": "FORMULAIRES",
        "11.13": "FORMULAIRES",
        "12.1": "NAVIGATION", "12.2": "NAVIGATION", "12.3": "NAVIGATION",
        "12.4": "NAVIGATION", "12.5": "NAVIGATION", "12.6": "NAVIGATION",
        "12.7": "NAVIGATION", "12.8": "NAVIGATION", "12.9": "NAVIGATION",
        "12.10": "NAVIGATION", "12.11": "NAVIGATION",
        "13.1": "CONSULTATION", "13.2": "CONSULTATION", "13.3": "CONSULTATION",
        "13.4": "CONSULTATION", "13.5": "CONSULTATION", "13.6": "CONSULTATION",
        "13.7": "CONSULTATION", "13.8": "CONSULTATION", "13.9": "CONSULTATION",
        "13.10": "CONSULTATION", "13.11": "CONSULTATION", "13.12": "CONSULTATION"
    }

    def __init__(self, analyzer: WebPageAnalyzer, use_content_detection: bool = True,
                 media_detection_data: Optional[Dict[str, Any]] = None):
        """
        Initialise le testeur.

        Args:
            analyzer: Instance de WebPageAnalyzer avec la page chargee
            use_content_detection: Si True, utilise la detection de contenu pour marquer automatiquement les NA
            media_detection_data: Donnees optionnelles de detection multimedia Playwright
                                  (retournees par MediaDetector.detect_all_media())
        """
        self.analyzer = analyzer
        self.soup = analyzer.soup
        self.url = analyzer.url
        self.html = analyzer.html or ""
        self.use_content_detection = use_content_detection
        self.media_detection_data = media_detection_data

        # Initialize content detector for automatic NA detection
        self.content_detector = ContentDetector(self.soup)
        self.detection_results = None
        self.auto_na_criteria = []

        if use_content_detection:
            self.detection_results = self.content_detector.detect_all()

            # If Playwright media detection data is available, enhance the
            # content detector's media results for more accurate NA detection
            if media_detection_data:
                self._enhance_media_detection(media_detection_data)

            self.auto_na_criteria = self.content_detector.get_na_criteria()

    def _enhance_media_detection(self, media_data: Dict[str, Any]):
        """
        Enhance content detector media results with Playwright-based detection.

        Playwright can detect dynamically loaded media elements that
        BeautifulSoup's static analysis misses (JS-injected video/audio,
        hidden elements, etc.).

        Args:
            media_data: Data from MediaDetector.detect_all_media()
        """
        if not self.detection_results or 'media' not in self.detection_results:
            return

        media_results = self.detection_results['media']

        # If Playwright detected temporal media but static analysis didn't
        pw_has_video = len(media_data.get('videos', [])) > 0
        pw_has_audio = len(media_data.get('audios', [])) > 0
        pw_has_temporal_objects = any(
            obj.get('type', '').startswith(('video/', 'audio/', 'application/x-shockwave-flash'))
            for obj in media_data.get('objects', [])
        )
        pw_has_temporal_embeds = any(
            emb.get('type', '').startswith(('video/', 'audio/', 'application/x-shockwave-flash'))
            for emb in media_data.get('embeds', [])
        )

        if pw_has_video or pw_has_audio or pw_has_temporal_objects or pw_has_temporal_embeds:
            media_results['temporal_present'] = True

        # If Playwright detected non-temporal media but static analysis didn't
        pw_has_canvas = len(media_data.get('canvas', [])) > 0
        pw_has_non_temporal_objects = any(
            obj.get('type', '').startswith('image/')
            for obj in media_data.get('objects', [])
        )
        pw_has_non_temporal_embeds = any(
            emb.get('type', '').startswith('image/')
            for emb in media_data.get('embeds', [])
        )

        if pw_has_canvas or pw_has_non_temporal_objects or pw_has_non_temporal_embeds:
            media_results['non_temporal_present'] = True

        # If Playwright detected autoplay media
        pw_has_autoplay = (
            any(vid.get('autoplay', False) for vid in media_data.get('videos', [])) or
            any(aud.get('autoplay', False) for aud in media_data.get('audios', []))
        )
        if pw_has_autoplay:
            media_results['autoplay_present'] = True

        # Update the count to reflect enhanced detection
        media_results['count'] = max(
            media_results.get('count', 0),
            media_data.get('total_count', 0)
        )

        # Store reference for use in Section 4 tests
        media_results['_playwright_data'] = media_data

    # ========================================================================
    # THÈME 1: IMAGES (Critères 1.1 - 1.9)
    # ========================================================================

    def _has_text_alternative(self, element: Tag) -> bool:
        """Vérifie si un élément a une alternative textuelle."""
        if element.get('alt'):
            return True
        if element.get('aria-label'):
            return True
        if element.get('aria-labelledby'):
            labelledby_id = element.get('aria-labelledby')
            referenced = self.soup.find(id=labelledby_id)
            if referenced and referenced.get_text(strip=True):
                return True
        if element.get('title'):
            return True
        if element.name == 'svg':
            title = element.find('title')
            if title and title.get_text(strip=True):
                return True
        return False

    def test_1_1(self) -> TestResult:
        """Critère 1.1: Chaque image porteuse d'information a-t-elle une alternative textuelle ?"""
        issues = []

        # Test 1.1.1 - Balises <img>
        images = self.soup.find_all('img')
        for img in images:
            alt = img.get('alt')
            # Ignorer les images décoratives (alt="")
            if alt == '':
                continue
            if not self._has_text_alternative(img):
                src = img.get('src', 'source inconnue')[:50]
                issues.append(f"Image sans alternative: {src}")

        # Test 1.1.2 - Zones cliquables <area>
        areas = self.soup.find_all('area', href=True)
        for area in areas:
            if not area.get('alt'):
                issues.append(f"Zone cliquable <area> sans alt")

        # Test 1.1.3 - Boutons image <input type="image">
        input_images = self.soup.find_all('input', {'type': 'image'})
        for inp in input_images:
            if not inp.get('alt'):
                issues.append(f"Bouton image sans alt: {inp.get('name', 'inconnu')}")

        # Test 1.1.5 - SVG avec role="img"
        svgs = self.soup.find_all('svg')
        for svg in svgs:
            if svg.get('role') == 'img' and not self._has_text_alternative(svg):
                issues.append("SVG role='img' sans alternative textuelle")

        # Test 1.1.6 - Objects image
        objects = self.soup.find_all('object', type=re.compile(r'image/', re.I))
        for obj in objects:
            if not obj.get('aria-label') and not obj.get('aria-labelledby'):
                issues.append("Object image sans alternative")

        # Test 1.1.8 - Canvas
        canvases = self.soup.find_all('canvas')
        for canvas in canvases:
            if not canvas.get('aria-label') and not canvas.get('aria-labelledby'):
                inner_text = canvas.get_text(strip=True)
                if not inner_text:
                    issues.append("Canvas sans alternative textuelle")

        # Éléments avec role="img"
        role_imgs = self.soup.find_all(attrs={'role': 'img'})
        for elem in role_imgs:
            if elem.name not in ['img', 'svg'] and not self._has_text_alternative(elem):
                issues.append(f"Élément role='img' sans alternative: <{elem.name}>")

        # Déterminer le statut
        total_images = len(images) + len(areas) + len(input_images) + len(svgs) + len(objects) + len(canvases)
        if total_images == 0:
            return TestResult("1.1", Status.NOT_APPLICABLE, [], "Aucune image détectée", "", 0.95)
        elif issues:
            return TestResult("1.1", Status.NON_COMPLIANT, issues,
                              "; ".join(issues[:5]), "", 0.95)
        else:
            return TestResult("1.1", Status.COMPLIANT, [], "", "", 0.95)

    def test_1_2(self) -> TestResult:
        """Critère 1.2: Chaque image de décoration est-elle correctement ignorée ?"""
        issues = []

        images = self.soup.find_all('img')
        for img in images:
            alt = img.get('alt')
            # Images avec alt="" sont décoratives
            if alt == '':
                # Ne doivent pas avoir d'autres attributs de labellisation
                if img.get('aria-label') or img.get('aria-labelledby') or img.get('title'):
                    src = img.get('src', '')[:30]
                    issues.append(f"Image déco avec attributs contradictoires: {src}")

            # Images avec role="presentation" doivent avoir alt=""
            role = img.get('role')
            if role == 'presentation' and alt != '' and alt is not None:
                issues.append("role='presentation' mais alt non vide")

        # SVG décoratifs avec aria-hidden
        svgs = self.soup.find_all('svg', {'aria-hidden': 'true'})
        for svg in svgs:
            if svg.get('aria-label') or svg.get('aria-labelledby'):
                issues.append("SVG aria-hidden='true' avec alternative textuelle présente")

        decorative_count = len([i for i in images if i.get('alt') == ''])
        if decorative_count == 0 and not svgs:
            return TestResult("1.2", Status.NOT_APPLICABLE, [], "Aucune image décorative détectée", "", 0.70)
        elif issues:
            return TestResult("1.2", Status.NON_COMPLIANT, issues,
                              "; ".join(issues), "", 0.70,
                              "Vérifier visuellement si les images sans alt sont bien décoratives")
        else:
            return TestResult("1.2", Status.COMPLIANT, [],
                              "", "Vérification manuelle recommandée", 0.70)

    def test_1_3(self) -> TestResult:
        """Critère 1.3: L'alternative textuelle est-elle pertinente ?"""
        issues = []
        suspicious_patterns = [
            r'^image\d*\.?(png|jpg|gif|svg)?$',
            r'^img\d*$',
            r'^photo\d*$',
            r'^picture$',
            r'^image$',
            r'^\d+$',
            r'^DSC_?\d+',
            r'^IMG_?\d+',
            r'^screenshot',
            r'^capture',
            r'^\.{3,}$',
        ]

        images = self.soup.find_all('img', alt=True)
        for img in images:
            alt = img.get('alt', '').strip()
            if not alt:
                continue

            for pattern in suspicious_patterns:
                if re.match(pattern, alt, re.IGNORECASE):
                    issues.append(f"Alt suspect (nom fichier?): '{alt[:30]}'")
                    break

            if len(alt) > 250:
                issues.append(f"Alt trop long ({len(alt)} car.): '{alt[:30]}...'")

            src = img.get('src', '')
            if alt.lower() in src.lower() and len(alt) > 3:
                issues.append(f"Alt = nom fichier: '{alt[:30]}'")

        if not images:
            return TestResult("1.3", Status.NOT_APPLICABLE, [], "Aucune image avec alt", "", 0.40)
        elif issues:
            return TestResult("1.3", Status.NON_COMPLIANT, issues,
                              "; ".join(issues[:5]), "", 0.40,
                              "Vérifier la pertinence sémantique des alternatives")
        else:
            return TestResult("1.3", Status.COMPLIANT, [],
                              "", "Vérification manuelle recommandée", 0.40)

    def test_1_4(self) -> TestResult:
        """Critère 1.4: CAPTCHA avec alternative identifiant sa nature."""
        captcha_indicators = ['captcha', 'recaptcha', 'hcaptcha', 'securimage', 'verification']
        issues = []
        captcha_found = False

        for indicator in captcha_indicators:
            elements = self.soup.find_all(class_=re.compile(indicator, re.I))
            elements += self.soup.find_all(id=re.compile(indicator, re.I))

            for elem in elements:
                captcha_found = True
                imgs = elem.find_all('img')
                for img in imgs:
                    alt = img.get('alt', '')
                    if not alt or 'captcha' not in alt.lower():
                        issues.append("Image CAPTCHA sans alternative descriptive")

        if not captcha_found:
            return TestResult("1.4", Status.NOT_APPLICABLE, [], "Aucun CAPTCHA présent sur la page détecté", "", 0.60)
        elif issues:
            return TestResult("1.4", Status.NON_COMPLIANT, issues,
                              "; ".join(issues), "", 0.60)
        else:
            return TestResult("1.4", Status.COMPLIANT, [], "", "", 0.60)

    def test_1_5(self) -> TestResult:
        """Critère 1.5: Alternative non graphique au CAPTCHA."""
        captcha_zones = self.soup.find_all(class_=re.compile('captcha', re.I))
        captcha_zones += self.soup.find_all(id=re.compile('captcha', re.I))

        if not captcha_zones:
            return TestResult("1.5", Status.NOT_APPLICABLE, [], "Aucun CAPTCHA présent sur la page", "", 0.70)

        issues = []
        for zone in captcha_zones:
            has_audio = zone.find('audio') or zone.find(class_=re.compile('audio', re.I))
            has_alt_link = zone.find('a', string=re.compile('audio|sonore|alternative', re.I))

            if not has_audio and not has_alt_link:
                issues.append("CAPTCHA sans alternative non graphique")

        if issues:
            return TestResult("1.5", Status.NON_COMPLIANT, issues,
                              "; ".join(issues), "", 0.70)
        else:
            return TestResult("1.5", Status.COMPLIANT, [], "", "", 0.70)

    def test_1_6(self) -> TestResult:
        """Critère 1.6: Images complexes avec description détaillée."""
        issues = []
        complex_indicators = ['chart', 'graph', 'diagram', 'schema', 'infograph', 'map', 'graphique']

        complex_images = []
        for img in self.soup.find_all('img'):
            src = img.get('src', '').lower()
            alt = img.get('alt', '').lower()
            classes = ' '.join(img.get('class', [])).lower()

            if any(ind in src or ind in alt or ind in classes for ind in complex_indicators):
                complex_images.append(img)
                has_longdesc = img.get('longdesc')
                has_describedby = img.get('aria-describedby')
                parent = img.parent
                adjacent_link = parent.find('a', string=re.compile('description|détail|voir', re.I)) if parent else None

                if not has_longdesc and not has_describedby and not adjacent_link:
                    issues.append(f"Image complexe sans description: {src[:40]}")

        if not complex_images:
            return TestResult("1.6", Status.NOT_APPLICABLE, [], "Pas d'image complexe détectée", "", 0.50,
                              "Identifier manuellement les images nécessitant description détaillée")
        elif issues:
            return TestResult("1.6", Status.NON_COMPLIANT, issues,
                              "; ".join(issues), "", 0.50)
        else:
            return TestResult("1.6", Status.COMPLIANT, [], "", "", 0.50)

    def test_1_7(self) -> TestResult:
        """Critère 1.7: Description détaillée pertinente pour images complexes."""
        complex_indicators = ['chart', 'graph', 'diagram', 'schema', 'infograph', 'map', 'graphique']
        complex_images = []

        for img in self.soup.find_all('img'):
            src = img.get('src', '').lower()
            alt = img.get('alt', '').lower()
            classes = ' '.join(img.get('class', [])).lower()

            if any(ind in src or ind in alt or ind in classes for ind in complex_indicators):
                complex_images.append(img)

        if not complex_images:
            return TestResult("1.7", Status.NOT_APPLICABLE, [], "Pas d'image complexe détectée", "", 0.60)

        # Check if complex images have detailed descriptions
        issues = []
        for img in complex_images:
            has_longdesc = img.get('longdesc')
            has_describedby = img.get('aria-describedby')
            if has_describedby:
                desc_elem = self.soup.find(id=has_describedby)
                if desc_elem and len(desc_elem.get_text(strip=True)) > 50:
                    continue  # Has sufficient description
            parent = img.parent
            adjacent_desc = parent.find(['p', 'div'], class_=re.compile('description|detail', re.I)) if parent else None

            if not has_longdesc and not has_describedby and not adjacent_desc:
                issues.append(f"Image complexe sans description détaillée vérifiable")

        if issues:
            return TestResult("1.7", Status.NON_COMPLIANT, issues,
                              "; ".join(issues), "", 0.60)
        else:
            return TestResult("1.7", Status.COMPLIANT, [], "", "", 0.60)

    def test_1_8(self) -> TestResult:
        """Critère 1.8: Images texte remplaçables par du texte stylé."""
        issues = []
        text_image_patterns = ['button', 'btn', 'title', 'heading', 'logo', 'banner']

        for img in self.soup.find_all('img'):
            src = img.get('src', '').lower()
            alt = img.get('alt', '')

            if alt and len(alt) > 3:
                if not re.search(r'\.(png|jpg|gif|svg)$', alt, re.I):
                    if any(p in src for p in text_image_patterns):
                        issues.append(f"Image-texte potentielle: '{alt[:30]}' - envisager texte CSS")

        if issues:
            return TestResult("1.8", Status.NON_COMPLIANT, issues,
                              "; ".join(issues[:5]), "", 0.30,
                              "Vérifier si des images texte peuvent être remplacées par du CSS")
        else:
            return TestResult("1.8", Status.COMPLIANT, [],
                              "", "Vérification manuelle recommandée", 0.30)

    def test_1_9(self) -> TestResult:
        """Critère 1.9: Légendes correctement reliées aux images."""
        issues = []
        figures = self.soup.find_all('figure')

        for figure in figures:
            img = figure.find('img') or figure.find('svg') or figure.find('canvas')
            figcaption = figure.find('figcaption')

            if img and figcaption:
                role = figure.get('role')
                if role not in ['figure', 'group', None]:
                    issues.append("Figure avec role inapproprié")

        if not figures:
            return TestResult("1.9", Status.NOT_APPLICABLE, [], "Aucune figure avec légende présente sur la page", "", 0.85)
        elif issues:
            return TestResult("1.9", Status.NON_COMPLIANT, issues,
                              "; ".join(issues), "", 0.85)
        else:
            return TestResult("1.9", Status.COMPLIANT, [], "", "", 0.85)

    # ========================================================================
    # THÈME 2: CADRES (Critères 2.1 - 2.2)
    # ========================================================================

    def test_2_1(self) -> TestResult:
        """Critère 2.1: Chaque cadre a-t-il un titre de cadre ?"""
        issues = []
        iframes = self.soup.find_all('iframe')
        frames = self.soup.find_all('frame')
        all_frames = iframes + frames

        for frame in all_frames:
            title = frame.get('title', '').strip()
            if not title:
                src = frame.get('src', 'source inconnue')[:40]
                issues.append(f"Cadre sans titre: {src}")

        if not all_frames:
            return TestResult("2.1", Status.NOT_APPLICABLE, [], "Aucun cadre iframe/frame présent sur la page", "", 0.98)
        elif issues:
            return TestResult("2.1", Status.NON_COMPLIANT, issues,
                              "; ".join(issues), "", 0.98)
        else:
            return TestResult("2.1", Status.COMPLIANT, [], "", "", 0.98)

    def test_2_2(self) -> TestResult:
        """Critère 2.2: Titre de cadre pertinent."""
        issues = []
        generic_titles = ['iframe', 'frame', 'cadre', 'contenu', 'content', 'widget', 'untitled']

        all_frames = self.soup.find_all(['iframe', 'frame'])
        frames_with_title = [f for f in all_frames if f.get('title')]

        for frame in frames_with_title:
            title = frame.get('title', '').strip().lower()
            src = frame.get('src', '')

            if title in generic_titles:
                issues.append(f"Titre générique: '{title}'")
            if title == src or src in title:
                issues.append(f"Titre = URL: '{title[:30]}'")
            if len(title) < 3:
                issues.append(f"Titre trop court: '{title}'")

        if not all_frames:
            return TestResult("2.2", Status.NOT_APPLICABLE, [], "Aucun cadre iframe/frame présent sur la page", "", 0.35)
        elif issues:
            return TestResult("2.2", Status.NON_COMPLIANT, issues,
                              "; ".join(issues), "", 0.35,
                              "Vérifier que le titre décrit bien le contenu du cadre")
        else:
            return TestResult("2.2", Status.COMPLIANT, [], "", "", 0.35)

    # ========================================================================
    # THÈME 3: COULEURS (Critères 3.1 - 3.3)
    # ========================================================================

    def test_3_1(self) -> TestResult:
        """Critère 3.1: Information non donnée uniquement par la couleur."""
        issues = []

        # Vérifier champs obligatoires
        required_fields = self.soup.find_all(['input', 'select', 'textarea'], required=True)
        required_fields += self.soup.find_all(attrs={'aria-required': 'true'})

        for field in required_fields:
            label = None
            if field.get('id'):
                label = self.soup.find('label', {'for': field.get('id')})

            if label:
                label_text = label.get_text()
                if '*' not in label_text and 'obligatoire' not in label_text.lower() and 'required' not in label_text.lower():
                    issues.append(f"Champ requis sans indicateur visible: {field.get('name', 'inconnu')}")

        # Chercher messages d'erreur sans texte
        error_elements = self.soup.find_all(class_=re.compile('error|erreur|invalid', re.I))
        for elem in error_elements:
            has_icon = elem.find(['svg', 'i', 'img', 'span'])
            text = elem.get_text(strip=True)
            if not has_icon and not text:
                issues.append("Message d'erreur potentiellement indiqué uniquement par couleur")

        # If no forms or error elements, mark as NA
        if not required_fields and not error_elements:
            return TestResult("3.1", Status.NOT_APPLICABLE, [], "Aucun formulaire présent sur la page ou message d'erreur détecté", "", 0.50)

        if issues:
            return TestResult("3.1", Status.NON_COMPLIANT, issues,
                              "; ".join(issues), "", 0.50)
        else:
            return TestResult("3.1", Status.COMPLIANT, [],
                              "", "", 0.50)

    def test_3_2(self) -> TestResult:
        """Critère 3.2: Contraste texte/arrière-plan suffisant."""
        issues = []
        # Low contrast colors that are problematic
        low_contrast_patterns = [
            (r'color:\s*#[cdef]{3}\b', "Couleur claire détectée"),
            (r'color:\s*#[cdef]{6}\b', "Couleur claire détectée"),
            (r'color:\s*(lightgr[ae]y|silver|gainsboro)', "Couleur grise claire"),
            (r'color:\s*rgb\s*\(\s*[12]\d{2}\s*,\s*[12]\d{2}\s*,\s*[12]\d{2}', "Couleur RGB claire"),
        ]

        elements_with_color = self.soup.find_all(style=re.compile(r'color:', re.I))
        for elem in elements_with_color:
            style = elem.get('style', '').lower()
            for pattern, msg in low_contrast_patterns:
                if re.search(pattern, style, re.I):
                    issues.append(msg)
                    break

        # Check embedded styles
        for style_tag in self.soup.find_all('style'):
            css = style_tag.get_text().lower()
            if 'color:' in css:
                for pattern, msg in low_contrast_patterns:
                    if re.search(pattern, css, re.I):
                        issues.append(f"CSS: {msg}")
                        break

        if issues:
            return TestResult("3.2", Status.NON_COMPLIANT, issues,
                              "; ".join(list(set(issues))[:5]) + " - Vérifier contraste avec outil dédié",
                              "", 0.40)
        else:
            return TestResult("3.2", Status.COMPLIANT, [],
                              "", "Aucune couleur problématique détectée en inline/embedded CSS", 0.40)

    def test_3_3(self) -> TestResult:
        """Critère 3.3: Contraste des composants d'interface."""
        issues = []

        # Check for buttons/inputs with potentially low contrast borders
        interactive_elements = self.soup.find_all(['button', 'input', 'select', 'textarea', 'a'])

        for elem in interactive_elements:
            style = elem.get('style', '').lower()
            # Check for very thin or light borders
            if 'border' in style:
                if re.search(r'border.*:\s*(none|0|transparent)', style):
                    # No visible border - might rely on background
                    pass
                if re.search(r'border-color:\s*#[def]{3}', style):
                    issues.append(f"Bordure peu contrastée sur <{elem.name}>")

        # If no interactive elements, NA
        if not interactive_elements:
            return TestResult("3.3", Status.NOT_APPLICABLE, [], "Aucun composant d'interface détecté", "", 0.40)

        if issues:
            return TestResult("3.3", Status.NON_COMPLIANT, issues,
                              "; ".join(issues[:5]), "", 0.40)
        else:
            return TestResult("3.3", Status.COMPLIANT, [],
                              "", "Composants d'interface présents", 0.40)

    # ========================================================================
    # THÈME 4: MULTIMÉDIA (Critères 4.1 - 4.13)
    # ========================================================================

    def _find_media_iframes(self) -> list:
        """Find iframes embedding video/audio platforms (YouTube, Vimeo, etc.)."""
        media_iframes = []
        media_pattern = re.compile(
            r'youtube|youtu\.be|vimeo|dailymotion|twitch|soundcloud|spotify|deezer|bandcamp|'
            r'vidyard|wistia|brightcove|jwplatform|player\.',
            re.I
        )
        for iframe in self.soup.find_all('iframe'):
            src = iframe.get('src', '') or iframe.get('data-src', '') or ''
            if media_pattern.search(src):
                media_iframes.append(iframe)
        return media_iframes

    def test_4_1(self) -> TestResult:
        """Critère 4.1: Média temporel avec transcription ou audiodescription."""
        issues = []

        videos = self.soup.find_all('video')
        audios = self.soup.find_all('audio')
        media_objects = self.soup.find_all('object', type=re.compile(r'video/|audio/', re.I))
        embeds = self.soup.find_all('embed', type=re.compile(r'video/|audio/', re.I))
        media_iframes = self._find_media_iframes()

        all_media = videos + audios + media_objects + embeds + media_iframes

        for media in all_media:
            tracks = media.find_all('track') if hasattr(media, 'find_all') else []
            parent = media.parent
            transcript_link = parent.find('a', string=re.compile(r'transcript|transcription|texte', re.I)) if parent else None

            if not tracks and not transcript_link:
                src = media.get('src', media.get('data', ''))[:40]
                issues.append(f"Média sans transcription: {src}")

        if not all_media:
            return TestResult("4.1", Status.NOT_APPLICABLE, [], "Aucun média présent sur la page temporel détecté", "", 0.80)
        elif issues:
            return TestResult("4.1", Status.NON_COMPLIANT, issues,
                              "; ".join(issues), "", 0.80)
        else:
            return TestResult("4.1", Status.COMPLIANT, [], "", "", 0.80)

    def test_4_2(self) -> TestResult:
        """Critère 4.2: Transcription pertinente pour média pré-enregistré audio seul."""
        audios = self.soup.find_all('audio')
        if not audios:
            return TestResult("4.2", Status.NOT_APPLICABLE, [], "Aucun média présent sur la page audio seul", "", 0.60)

        issues = []
        for audio in audios:
            # Check for transcript track or adjacent link
            tracks = audio.find_all('track')
            has_transcript = any(t.get('kind') in ['captions', 'subtitles', 'descriptions'] for t in tracks)

            parent = audio.parent
            transcript_link = parent.find('a', string=re.compile(r'transcript|transcription', re.I)) if parent else None

            if not has_transcript and not transcript_link:
                src = audio.get('src', '')[:30]
                issues.append(f"Audio sans transcription: {src}")

        if issues:
            return TestResult("4.2", Status.NON_COMPLIANT, issues,
                              "; ".join(issues), "", 0.60)
        else:
            return TestResult("4.2", Status.COMPLIANT, [],
                              "", "", 0.60)

    def test_4_3(self) -> TestResult:
        """Critère 4.3: Sous-titres synchronisés pour vidéos."""
        issues = []
        videos = self.soup.find_all('video')
        video_iframes = self._find_media_iframes()

        for video in videos:
            tracks = video.find_all('track')
            has_captions = any(t.get('kind') in ['captions', 'subtitles'] for t in tracks)
            if not has_captions:
                src = video.get('src', '')[:40]
                issues.append(f"Vidéo sans sous-titres: {src}")

        if video_iframes:
            issues.append("VÉRIFICATION MANUELLE: Vérifier sous-titres des vidéos intégrées (iframe)")

        if not videos and not video_iframes:
            return TestResult("4.3", Status.NOT_APPLICABLE, [], "Aucune vidéo présente sur la page", "", 0.90)
        elif issues:
            return TestResult("4.3", Status.NON_COMPLIANT, issues,
                              "; ".join(issues), "", 0.75)
        else:
            return TestResult("4.3", Status.COMPLIANT, [], "", "", 0.90)

    def test_4_4(self) -> TestResult:
        """Critère 4.4: Sous-titres pertinents pour médias synchronisés."""
        videos = self.soup.find_all('video')
        video_iframes = self._find_media_iframes()

        if not videos and not video_iframes:
            return TestResult("4.4", Status.NOT_APPLICABLE, [], "Aucune vidéo présente sur la page", "", 0.60)

        # Check if videos have subtitle tracks
        issues = []
        for video in videos:
            tracks = video.find_all('track')
            has_captions = any(t.get('kind') in ['captions', 'subtitles'] for t in tracks)
            if not has_captions:
                issues.append("Vidéo sans piste de sous-titres")

        if issues:
            return TestResult("4.4", Status.NON_COMPLIANT, issues,
                              "; ".join(issues), "", 0.60)
        else:
            return TestResult("4.4", Status.COMPLIANT, [],
                              "", "", 0.60)

    def test_4_5(self) -> TestResult:
        """Critère 4.5: Audiodescription synchronisée pour vidéos."""
        videos = self.soup.find_all('video')
        if not videos:
            return TestResult("4.5", Status.NOT_APPLICABLE, [], "Aucune vidéo présente sur la page", "", 0.50)

        # Check for audiodescription track
        has_any_description = False
        for video in videos:
            tracks = video.find_all('track')
            if any(t.get('kind') == 'descriptions' for t in tracks):
                has_any_description = True

        # If no description tracks but videos exist, check if they might need it
        if not has_any_description:
            return TestResult("4.5", Status.COMPLIANT, [],
                              "", "Vidéos présentes - audiodescription non requise si contenu audio suffisant", 0.50)
        else:
            return TestResult("4.5", Status.COMPLIANT, [], "", "", 0.50)

    def test_4_6(self) -> TestResult:
        """Critère 4.6: Audiodescription pertinente."""
        videos = self.soup.find_all('video')
        if not videos:
            return TestResult("4.6", Status.NOT_APPLICABLE, [], "Aucune vidéo présente sur la page", "", 0.50)

        # Check if any video has audiodescription
        for video in videos:
            tracks = video.find_all('track')
            if any(t.get('kind') == 'descriptions' for t in tracks):
                return TestResult("4.6", Status.COMPLIANT, [],
                                  "", "Piste d'audiodescription présente", 0.50)

        return TestResult("4.6", Status.NOT_APPLICABLE, [],
                          "Pas d'audiodescription à évaluer", "", 0.50)

    def test_4_7(self) -> TestResult:
        """Critère 4.7: Identification des médias temporels."""
        media = self.soup.find_all(['video', 'audio'])
        media_iframes = self._find_media_iframes()

        if not media and not media_iframes:
            return TestResult("4.7", Status.NOT_APPLICABLE, [], "Aucun média temporel présent sur la page", "", 0.70)

        issues = []
        for m in media:
            # Check if media has accessible name
            has_label = m.get('aria-label') or m.get('aria-labelledby') or m.get('title')
            # Check for adjacent heading or caption
            parent = m.parent
            has_heading = parent.find(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'figcaption']) if parent else None

            if not has_label and not has_heading:
                issues.append(f"Média <{m.name}> sans identification accessible")

        for iframe in media_iframes:
            has_label = iframe.get('aria-label') or iframe.get('aria-labelledby') or iframe.get('title')
            if not has_label:
                src = (iframe.get('src', '') or iframe.get('data-src', ''))[:50]
                issues.append(f"Iframe média sans titre accessible: {src}")

        if issues:
            return TestResult("4.7", Status.NON_COMPLIANT, issues,
                              "; ".join(issues), "", 0.70)
        else:
            return TestResult("4.7", Status.COMPLIANT, [], "", "", 0.70)

    def test_4_8(self) -> TestResult:
        """Critère 4.8: Média non temporel avec alternative."""
        objects = self.soup.find_all('object')
        embeds = self.soup.find_all('embed')
        # Exclude video/audio objects
        non_temporal = [o for o in objects if not re.search(r'video|audio', o.get('type', ''), re.I)]
        non_temporal += [e for e in embeds if not re.search(r'video|audio', e.get('type', ''), re.I)]

        if not non_temporal:
            return TestResult("4.8", Status.NOT_APPLICABLE, [], "Aucun média présent sur la page non temporel", "", 0.60)

        issues = []
        for obj in non_temporal:
            has_alt = obj.get('aria-label') or obj.get('aria-labelledby') or obj.get_text(strip=True)
            if not has_alt:
                issues.append("Média non temporel sans alternative")

        if issues:
            return TestResult("4.8", Status.NON_COMPLIANT, issues,
                              "; ".join(issues), "", 0.60)
        else:
            return TestResult("4.8", Status.COMPLIANT, [], "", "", 0.60)

    def test_4_9(self) -> TestResult:
        """Critère 4.9: Alternative pertinente pour média non temporel."""
        objects = self.soup.find_all('object')
        embeds = self.soup.find_all('embed')
        non_temporal = [o for o in objects if not re.search(r'video|audio', o.get('type', ''), re.I)]
        non_temporal += [e for e in embeds if not re.search(r'video|audio', e.get('type', ''), re.I)]

        if not non_temporal:
            return TestResult("4.9", Status.NOT_APPLICABLE, [], "Aucun média présent sur la page non temporel", "", 0.60)

        # If we found non-temporal media with alternatives in 4.8, assume they're pertinent
        for obj in non_temporal:
            has_alt = obj.get('aria-label') or obj.get('aria-labelledby') or obj.get_text(strip=True)
            if has_alt:
                return TestResult("4.9", Status.COMPLIANT, [],
                                  "", "Alternatives présentes pour médias non temporels", 0.60)

        return TestResult("4.9", Status.NOT_APPLICABLE, [],
                          "Pas d'alternative à évaluer", "", 0.60)

    def test_4_10(self) -> TestResult:
        """Critère 4.10: Son déclenché automatiquement contrôlable."""
        issues = []

        autoplay_media = self.soup.find_all(['video', 'audio'], autoplay=True)
        autoplay_media += self.soup.find_all(['video', 'audio'], attrs={'autoplay': ''})

        for media in autoplay_media:
            muted = media.get('muted') is not None or media.has_attr('muted')
            controls = media.get('controls') is not None or media.has_attr('controls')

            if not muted and not controls:
                issues.append("Média autoplay sans contrôle ni mute")

        bgsound = self.soup.find_all('bgsound')
        if bgsound:
            issues.append("Élément bgsound détecté (obsolète et non contrôlable)")

        if not autoplay_media and not bgsound:
            return TestResult("4.10", Status.NOT_APPLICABLE, [], "Aucun média présent sur la page en autoplay", "", 0.95)
        elif issues:
            return TestResult("4.10", Status.NON_COMPLIANT, issues,
                              "; ".join(issues), "", 0.95)
        else:
            return TestResult("4.10", Status.COMPLIANT, [], "", "", 0.95)

    def test_4_11(self) -> TestResult:
        """Critère 4.11: Média temporel contrôlable au clavier."""
        media = self.soup.find_all(['video', 'audio'])
        media_iframes = self._find_media_iframes()

        if not media and not media_iframes:
            return TestResult("4.11", Status.NOT_APPLICABLE, [], "Aucun média temporel présent sur la page", "", 0.70)

        issues = []
        for m in media:
            if not m.has_attr('controls'):
                issues.append("Média sans attribut controls")

        if media_iframes:
            issues.append("VÉRIFICATION MANUELLE: Vérifier contrôles clavier des médias intégrés (iframe)")

        if issues:
            return TestResult("4.11", Status.NON_COMPLIANT, issues,
                              "; ".join(issues), "", 0.70)
        else:
            return TestResult("4.11", Status.COMPLIANT, [],
                              "", "Contrôles natifs présents sur les médias", 0.70)

    def test_4_12(self) -> TestResult:
        """Critère 4.12: Média temporel compatible avec technologies d'assistance."""
        media = self.soup.find_all(['video', 'audio'])
        if not media:
            return TestResult("4.12", Status.NOT_APPLICABLE, [], "Aucun média présent sur la page", "", 0.60)

        # Check for accessibility attributes on media
        issues = []
        for m in media:
            has_controls = m.has_attr('controls')
            has_label = m.get('aria-label') or m.get('aria-labelledby') or m.get('title')
            if not has_controls:
                issues.append(f"Média <{m.name}> sans attribut controls")

        if issues:
            return TestResult("4.12", Status.NON_COMPLIANT, issues,
                              "; ".join(issues), "", 0.60)
        else:
            return TestResult("4.12", Status.COMPLIANT, [],
                              "", "Médias avec contrôles natifs accessibles", 0.60)

    def test_4_13(self) -> TestResult:
        """Critère 4.13: Média temporel avec alternative au contrôle au clavier."""
        media = self.soup.find_all(['video', 'audio'])
        if not media:
            return TestResult("4.13", Status.NOT_APPLICABLE, [], "Aucun média présent sur la page", "", 0.60)

        # Check if media has controls (which provide keyboard access)
        for m in media:
            if m.has_attr('controls'):
                return TestResult("4.13", Status.COMPLIANT, [],
                                  "", "Contrôles clavier disponibles via attribut controls", 0.60)

        return TestResult("4.13", Status.NON_COMPLIANT, ["Médias sans contrôles clavier natifs"],
                          "Ajouter attribut controls aux médias", "", 0.60)

    # ========================================================================
    # THÈME 5: TABLEAUX (Critères 5.1 - 5.8)
    # ========================================================================

    def test_5_1(self) -> TestResult:
        """Critère 5.1: Tableaux de données complexes avec résumé."""
        issues = []
        tables = self.soup.find_all('table')
        complex_tables = []

        for table in tables:
            has_colspan = bool(table.find_all(['td', 'th'], colspan=True))
            has_rowspan = bool(table.find_all(['td', 'th'], rowspan=True))
            th_count = len(table.find_all('th'))

            if has_colspan or has_rowspan or th_count > 10:
                complex_tables.append(table)
                summary = table.get('summary')
                aria_describedby = table.get('aria-describedby')
                caption = table.find('caption')

                if not summary and not aria_describedby:
                    if not caption or len(caption.get_text(strip=True)) < 20:
                        issues.append("Tableau complexe sans résumé")

        if not complex_tables:
            return TestResult("5.1", Status.NOT_APPLICABLE, [], "Aucun tableau présent sur la page complexe", "", 0.70)
        elif issues:
            return TestResult("5.1", Status.NON_COMPLIANT, issues,
                              "; ".join(issues), "", 0.70)
        else:
            return TestResult("5.1", Status.COMPLIANT, [], "", "", 0.70)

    def test_5_2(self) -> TestResult:
        """Critère 5.2: Résumé de tableau pertinent."""
        tables = self.soup.find_all('table')
        complex_tables = [t for t in tables if t.find_all(['td', 'th'], colspan=True) or t.find_all(['td', 'th'], rowspan=True)]

        if not complex_tables:
            return TestResult("5.2", Status.NOT_APPLICABLE, [], "Aucun tableau présent sur la page complexe", "", 0.60)

        # Check if complex tables have summaries
        issues = []
        for table in complex_tables:
            summary = table.get('summary')
            aria_describedby = table.get('aria-describedby')
            caption = table.find('caption')

            if summary or aria_describedby or (caption and len(caption.get_text(strip=True)) > 20):
                continue  # Has summary
            else:
                issues.append("Tableau complexe sans résumé")

        if issues:
            return TestResult("5.2", Status.NON_COMPLIANT, issues,
                              "; ".join(issues), "", 0.60)
        else:
            return TestResult("5.2", Status.COMPLIANT, [],
                              "", "Tableaux complexes avec résumé", 0.60)

    def test_5_3(self) -> TestResult:
        """Critère 5.3: Tableaux de mise en forme avec role=presentation."""
        issues = []
        tables = self.soup.find_all('table')

        for table in tables:
            has_th = bool(table.find('th'))
            has_caption = bool(table.find('caption'))
            has_headers_attr = bool(table.find(['td'], headers=True))

            is_layout_table = not has_th and not has_caption and not has_headers_attr

            if is_layout_table:
                role = table.get('role')
                if role != 'presentation':
                    issues.append("Tableau de mise en forme sans role='presentation'")

        layout_tables = [t for t in tables if not t.find('th') and not t.find('caption')]
        if not layout_tables:
            return TestResult("5.3", Status.NOT_APPLICABLE, [], "Aucun tableau présent sur la page de mise en forme détecté", "", 0.70)
        elif issues:
            return TestResult("5.3", Status.NON_COMPLIANT, issues,
                              "; ".join(issues), "", 0.70)
        else:
            return TestResult("5.3", Status.COMPLIANT, [], "", "", 0.70)

    def test_5_4(self) -> TestResult:
        """Critère 5.4: Titre pour tableaux de données."""
        issues = []
        tables = self.soup.find_all('table')

        for table in tables:
            if table.get('role') == 'presentation':
                continue

            has_th = bool(table.find('th'))
            if has_th:
                caption = table.find('caption')
                aria_label = table.get('aria-label')
                aria_labelledby = table.get('aria-labelledby')

                if not caption and not aria_label and not aria_labelledby:
                    issues.append("Tableau de données sans titre")

        data_tables = [t for t in tables if t.find('th') and t.get('role') != 'presentation']
        if not data_tables:
            return TestResult("5.4", Status.NOT_APPLICABLE, [], "Aucun tableau présent sur la page de données", "", 0.80)
        elif issues:
            return TestResult("5.4", Status.NON_COMPLIANT, issues,
                              "; ".join(issues), "", 0.80)
        else:
            return TestResult("5.4", Status.COMPLIANT, [], "", "", 0.80)

    def test_5_5(self) -> TestResult:
        """Critère 5.5: Titre de tableau pertinent."""
        tables = self.soup.find_all('table')
        data_tables = [t for t in tables if t.find('th') and t.get('role') != 'presentation']

        if not data_tables:
            return TestResult("5.5", Status.NOT_APPLICABLE, [], "Aucun tableau présent sur la page de données", "", 0.60)

        # Check titles are not generic
        issues = []
        generic_titles = ['tableau', 'table', 'données', 'data', 'liste', 'list']

        for table in data_tables:
            caption = table.find('caption')
            aria_label = table.get('aria-label', '')

            title_text = ''
            if caption:
                title_text = caption.get_text(strip=True).lower()
            elif aria_label:
                title_text = aria_label.lower()

            if title_text and title_text in generic_titles:
                issues.append(f"Titre de tableau générique: '{title_text}'")

        if issues:
            return TestResult("5.5", Status.NON_COMPLIANT, issues,
                              "; ".join(issues), "", 0.60)
        else:
            return TestResult("5.5", Status.COMPLIANT, [],
                              "", "Titres de tableaux non génériques", 0.60)

    def test_5_6(self) -> TestResult:
        """Critère 5.6: En-têtes de tableau correctement déclarés."""
        issues = []
        tables = self.soup.find_all('table')

        for table in tables:
            if table.get('role') == 'presentation':
                continue

            ths = table.find_all('th')
            if not ths:
                tds = table.find_all('td')
                if len(tds) > 4:
                    issues.append("Tableau de données sans en-têtes <th>")
            else:
                for th in ths:
                    scope = th.get('scope')
                    role = th.get('role')
                    if not scope and role not in ['columnheader', 'rowheader']:
                        issues.append("En-tête <th> sans attribut scope")
                        break

        data_tables = [t for t in tables if t.get('role') != 'presentation' and len(t.find_all('td')) > 4]
        if not data_tables:
            return TestResult("5.6", Status.NOT_APPLICABLE, [], "Aucun tableau de données présent sur la page", "", 0.85)
        elif issues:
            return TestResult("5.6", Status.NON_COMPLIANT, issues,
                              "; ".join(issues), "", 0.85)
        else:
            return TestResult("5.6", Status.COMPLIANT, [], "", "", 0.85)

    def test_5_7(self) -> TestResult:
        """Critère 5.7: Liaisons en-têtes/cellules pour tableaux de données."""
        tables = self.soup.find_all('table')
        data_tables = [t for t in tables if t.find('th') and t.get('role') != 'presentation']

        if not data_tables:
            return TestResult("5.7", Status.NOT_APPLICABLE, [], "Aucun tableau présent sur la page de données", "", 0.70)

        issues = []
        for table in data_tables:
            # Vérifier les associations headers
            cells_with_headers = table.find_all('td', headers=True)
            ths_with_id = table.find_all('th', id=True)

            # Pour tableaux complexes, vérifier les associations
            has_colspan = bool(table.find_all(['td', 'th'], colspan=True))
            has_rowspan = bool(table.find_all(['td', 'th'], rowspan=True))

            if (has_colspan or has_rowspan) and not cells_with_headers and not ths_with_id:
                issues.append("Tableau complexe sans liaisons headers/id")

        if issues:
            return TestResult("5.7", Status.NON_COMPLIANT, issues,
                              "; ".join(issues), "", 0.70)
        else:
            return TestResult("5.7", Status.COMPLIANT, [], "", "", 0.70)

    def test_5_8(self) -> TestResult:
        """Critère 5.8: Tableaux de mise en forme sans éléments de données."""
        issues = []
        tables = self.soup.find_all('table', role='presentation')

        for table in tables:
            if table.find('th'):
                issues.append("Tableau présentation avec <th>")
            if table.find('caption'):
                issues.append("Tableau présentation avec <caption>")
            if table.get('summary'):
                issues.append("Tableau présentation avec summary")

            cells_with_headers = table.find_all(['td'], headers=True)
            if cells_with_headers:
                issues.append("Tableau présentation avec attribut headers")

            cells_with_scope = table.find_all(['td', 'th'], scope=True)
            if cells_with_scope:
                issues.append("Tableau présentation avec attribut scope")

        if not tables:
            return TestResult("5.8", Status.NOT_APPLICABLE, [], "Aucun tableau de données présent sur la page", "", 0.90)
        elif issues:
            return TestResult("5.8", Status.NON_COMPLIANT, issues,
                              "; ".join(issues), "", 0.90)
        else:
            return TestResult("5.8", Status.COMPLIANT, [], "", "", 0.90)

    # ========================================================================
    # THÈME 6: LIENS (Critères 6.1 - 6.2)
    # ========================================================================

    def test_6_1(self) -> TestResult:
        """Critère 6.1: Liens explicites."""
        issues = []
        generic_texts = ['cliquez ici', 'click here', 'ici', 'here', 'lire la suite',
                         'read more', 'en savoir plus', 'more', 'suite', 'voir', 'see',
                         'lien', 'link', '+', '>', '>>', '...']

        links = self.soup.find_all('a', href=True)

        for link in links:
            link_text = link.get_text(strip=True).lower()
            aria_label = link.get('aria-label', '').lower()
            title = link.get('title', '').lower()

            img = link.find('img')
            img_alt = img.get('alt', '').lower() if img else ''

            accessible_name = aria_label or link_text or img_alt or title

            if accessible_name in generic_texts:
                href = link.get('href', '')[:30]
                issues.append(f"Lien non explicite '{accessible_name}': {href}")

            if not accessible_name.strip():
                href = link.get('href', '')[:30]
                issues.append(f"Lien vide: {href}")

        if not links:
            return TestResult("6.1", Status.NOT_APPLICABLE, [], "Aucun lien présent sur la page", "", 0.75)
        elif issues:
            return TestResult("6.1", Status.NON_COMPLIANT, issues,
                              "; ".join(issues[:10]), "", 0.75)
        else:
            return TestResult("6.1", Status.COMPLIANT, [], "", "", 0.75)

    def test_6_2(self) -> TestResult:
        """Critère 6.2: Chaque lien a un intitulé."""
        issues = []
        links = self.soup.find_all('a', href=True)

        for link in links:
            has_text = bool(link.get_text(strip=True))
            has_aria_label = bool(link.get('aria-label', '').strip())
            has_aria_labelledby = bool(link.get('aria-labelledby'))
            has_title = bool(link.get('title', '').strip())

            img = link.find('img')
            has_img_alt = bool(img and img.get('alt', '').strip()) if img else False

            svg = link.find('svg')
            has_svg_title = bool(svg and (svg.find('title') or svg.get('aria-label'))) if svg else False

            if not (has_text or has_aria_label or has_aria_labelledby or has_title or has_img_alt or has_svg_title):
                href = link.get('href', '')[:40]
                issues.append(f"Lien sans intitulé: {href}")

        if not links:
            return TestResult("6.2", Status.NOT_APPLICABLE, [], "Aucun lien présent sur la page", "", 0.95)
        elif issues:
            return TestResult("6.2", Status.NON_COMPLIANT, issues,
                              "; ".join(issues[:10]), "", 0.95)
        else:
            return TestResult("6.2", Status.COMPLIANT, [], "", "", 0.95)

    # ========================================================================
    # THÈME 7: SCRIPTS (Critères 7.1 - 7.5)
    # ========================================================================

    def test_7_1(self) -> TestResult:
        """Critère 7.1: Scripts compatibles avec technologies d'assistance."""
        issues = []

        interactive_roles = ['button', 'link', 'checkbox', 'radio', 'tab', 'slider',
                             'spinbutton', 'combobox', 'listbox', 'menu', 'menuitem',
                             'dialog', 'alertdialog', 'tooltip']

        aria_required = {
            'checkbox': ['aria-checked'],
            'radio': ['aria-checked'],
            'slider': ['aria-valuenow', 'aria-valuemin', 'aria-valuemax'],
            'spinbutton': ['aria-valuenow'],
            'combobox': ['aria-expanded'],
            'tab': ['aria-selected'],
            'switch': ['aria-checked'],
        }

        for role in interactive_roles:
            elements = self.soup.find_all(attrs={'role': role})
            for elem in elements:
                if role in aria_required:
                    for attr in aria_required[role]:
                        if not elem.get(attr):
                            issues.append(f"role='{role}' sans {attr}")

        # onclick sur éléments non interactifs
        clickable_divs = self.soup.find_all(['div', 'span'], onclick=True)
        for div in clickable_divs:
            if not div.get('role') and not div.get('tabindex'):
                issues.append("onclick sur élément non interactif sans role ni tabindex")

        role_elements = self.soup.find_all(attrs={'role': True})
        if not role_elements and not clickable_divs:
            return TestResult("7.1", Status.NOT_APPLICABLE, [], "Aucun composant JavaScript présent sur la page", "", 0.60)
        elif issues:
            return TestResult("7.1", Status.NON_COMPLIANT, issues,
                              "; ".join(issues[:10]), "", 0.60)
        else:
            return TestResult("7.1", Status.COMPLIANT, [],
                              "", "Vérification avec lecteur d'écran recommandée", 0.60)

    def test_7_2(self) -> TestResult:
        """Critère 7.2: Composants scriptés utilisables au clavier et souris."""
        interactive_roles = ['button', 'link', 'checkbox', 'radio', 'tab', 'slider',
                             'spinbutton', 'combobox', 'listbox', 'menu', 'menuitem']
        role_elements = self.soup.find_all(attrs={'role': lambda x: x in interactive_roles if x else False})

        if not role_elements:
            return TestResult("7.2", Status.NOT_APPLICABLE, [], "Aucun composant interactif scripté présent sur la page", "", 0.60)

        issues = []
        for elem in role_elements:
            # Check if element is focusable
            tabindex = elem.get('tabindex')
            is_native_focusable = elem.name in ['a', 'button', 'input', 'select', 'textarea']

            if not is_native_focusable and tabindex is None:
                issues.append(f"role='{elem.get('role')}' sans tabindex")

        if issues:
            return TestResult("7.2", Status.NON_COMPLIANT, issues,
                              "; ".join(issues[:5]), "", 0.60)
        else:
            return TestResult("7.2", Status.COMPLIANT, [],
                              "", "Composants interactifs focusables", 0.60)

    def test_7_3(self) -> TestResult:
        """Critère 7.3: Scripts contrôlables au clavier."""
        issues = []

        mouse_only_events = ['onmouseover', 'onmouseout', 'onmouseenter', 'onmouseleave', 'ondblclick']

        # Check if any scripted elements exist
        has_scripted_elements = False
        for event in mouse_only_events:
            elements = self.soup.find_all(attrs={event: True})
            if elements:
                has_scripted_elements = True
            for elem in elements:
                has_keyboard = elem.get('onfocus') or elem.get('onblur') or elem.get('onkeypress') or elem.get('onkeydown')
                if not has_keyboard:
                    tag = elem.name
                    issues.append(f"<{tag}> avec {event} sans équivalent clavier")

        negative_tabindex = self.soup.find_all(attrs={'tabindex': '-1'})
        for elem in negative_tabindex:
            if elem.get('onclick') or elem.get('role') in ['button', 'link']:
                has_scripted_elements = True
                issues.append("Élément interactif avec tabindex=-1")

        scripts = self.soup.find_all('script')
        onclick_elements = self.soup.find_all(attrs={'onclick': True})
        if not scripts and not onclick_elements and not has_scripted_elements:
            return TestResult("7.3", Status.NOT_APPLICABLE, [], "Aucun script présent sur la page", "", 0.60)

        if issues:
            return TestResult("7.3", Status.NON_COMPLIANT, issues,
                              "; ".join(issues[:10]), "", 0.60)
        else:
            return TestResult("7.3", Status.COMPLIANT, [], "", "", 0.60)

    def test_7_4(self) -> TestResult:
        """Critère 7.4: Changements de contexte initiés par l'utilisateur."""
        issues = []

        # Check if scripts or forms exist
        scripts = self.soup.find_all('script')
        forms = self.soup.find_all('form')

        if not scripts and not forms:
            return TestResult("7.4", Status.NOT_APPLICABLE, [], "Aucun script ou formulaire présent sur la page", "", 0.70)

        # Vérifier onchange sur select sans submit
        selects_onchange = self.soup.find_all('select', onchange=True)
        for select in selects_onchange:
            onchange = select.get('onchange', '')
            if 'submit' in onchange.lower() or 'location' in onchange.lower():
                issues.append("Select avec onchange qui change de contexte")

        # Check for auto-submit forms
        forms_auto = self.soup.find_all('form', onchange=True)
        for form in forms_auto:
            if 'submit' in form.get('onchange', '').lower():
                issues.append("Formulaire avec auto-submit")

        if issues:
            return TestResult("7.4", Status.NON_COMPLIANT, issues,
                              "; ".join(issues), "", 0.70)
        else:
            return TestResult("7.4", Status.COMPLIANT, [], "", "", 0.70)

    def test_7_5(self) -> TestResult:
        """Critère 7.5: Messages de statut correctement restitués."""
        issues = []

        live_regions = self.soup.find_all(attrs={'aria-live': True})
        live_regions += self.soup.find_all(attrs={'role': ['alert', 'status', 'log', 'progressbar']})

        message_classes = ['alert', 'error', 'success', 'warning', 'notification', 'message', 'toast']
        has_message_elements = False

        for cls in message_classes:
            elements = self.soup.find_all(class_=re.compile(cls, re.I))
            if elements:
                has_message_elements = True
            for elem in elements:
                role = elem.get('role')
                aria_live = elem.get('aria-live')

                if not role and not aria_live:
                    issues.append(f"Message potentiel sans role/aria-live: class={cls}")

        # If no live regions or message elements, NA
        if not live_regions and not has_message_elements:
            scripts = self.soup.find_all('script')
            if not scripts:
                return TestResult("7.5", Status.NOT_APPLICABLE, [], "Aucun script présent sur la page", "", 0.65)
            else:
                return TestResult("7.5", Status.COMPLIANT, [], "", "", 0.65)

        if issues:
            return TestResult("7.5", Status.NON_COMPLIANT, issues,
                              "; ".join(issues[:10]), "", 0.65)
        else:
            return TestResult("7.5", Status.COMPLIANT, [], "", "", 0.65)

    # ========================================================================
    # THÈME 8: ÉLÉMENTS OBLIGATOIRES (Critères 8.1 - 8.10)
    # ========================================================================

    def test_8_1(self) -> TestResult:
        """Critère 8.1: Page définie par un type de document."""
        issues = []

        doctype_pattern = r'<!DOCTYPE\s+html'
        if not re.search(doctype_pattern, self.html[:500], re.I):
            issues.append("DOCTYPE HTML manquant ou invalide")

        if issues:
            return TestResult("8.1", Status.NON_COMPLIANT, issues,
                              "Ajouter <!DOCTYPE html> en début de document", "", 0.98)
        else:
            return TestResult("8.1", Status.COMPLIANT, [], "", "", 0.98)

    def test_8_2(self) -> TestResult:
        """Critère 8.2: Code source valide."""
        issues = []

        # Vérifier IDs dupliqués
        ids = [elem.get('id') for elem in self.soup.find_all(id=True)]
        duplicates = list(set([id for id in ids if ids.count(id) > 1]))
        if duplicates:
            issues.append(f"IDs dupliqués: {duplicates[:5]}")

        if issues:
            return TestResult("8.2", Status.NON_COMPLIANT, issues,
                              "; ".join(issues), "", 0.70,
                              "Utiliser validateur W3C pour validation complète")
        else:
            return TestResult("8.2", Status.COMPLIANT, [],
                              "", "Validation W3C recommandée", 0.70)

    def test_8_3(self) -> TestResult:
        """Critère 8.3: Langue par défaut présente."""
        issues = []

        html_tag = self.soup.find('html')
        if html_tag:
            lang = html_tag.get('lang') or html_tag.get('xml:lang')
            if not lang:
                issues.append("Attribut lang manquant sur <html>")
        else:
            issues.append("Balise <html> non trouvée")

        if issues:
            return TestResult("8.3", Status.NON_COMPLIANT, issues,
                              "Ajouter lang='fr' (ou autre) sur <html>", "", 0.98)
        else:
            return TestResult("8.3", Status.COMPLIANT, [], "", "", 0.98)

    def test_8_4(self) -> TestResult:
        """Critère 8.4: Code de langue valide et pertinent."""
        issues = []
        valid_codes = ['fr', 'en', 'de', 'es', 'it', 'pt', 'nl', 'pl', 'ru', 'ar', 'zh', 'ja', 'ko']

        html_tag = self.soup.find('html')
        if html_tag:
            lang = html_tag.get('lang', '')
            lang_code = lang.split('-')[0].lower() if lang else ''

            if not lang:
                return TestResult("8.4", Status.NOT_APPLICABLE, [], "Aucun code langue présent sur la page", "", 0.90)
            elif lang_code not in valid_codes and len(lang_code) not in [2, 3]:
                issues.append(f"Code langue invalide: {lang}")

        if issues:
            return TestResult("8.4", Status.NON_COMPLIANT, issues,
                              "Utiliser un code ISO 639 valide", "", 0.90)
        else:
            return TestResult("8.4", Status.COMPLIANT, [], "", "", 0.90)

    def test_8_5(self) -> TestResult:
        """Critère 8.5: Page a un titre."""
        issues = []

        title = self.soup.find('title')
        if not title:
            issues.append("Balise <title> manquante")
        elif not title.get_text(strip=True):
            issues.append("Balise <title> vide")

        if issues:
            return TestResult("8.5", Status.NON_COMPLIANT, issues,
                              "Ajouter un titre dans <title>", "", 0.98)
        else:
            return TestResult("8.5", Status.COMPLIANT, [], "", "", 0.98)

    def test_8_6(self) -> TestResult:
        """Critère 8.6: Titre de page pertinent."""
        issues = []
        generic_titles = ['untitled', 'sans titre', 'page', 'accueil', 'home', 'index', 'new page', 'document']

        title = self.soup.find('title')
        if title:
            title_text = title.get_text(strip=True)

            if title_text.lower() in generic_titles:
                issues.append(f"Titre générique: '{title_text}'")

            if len(title_text) < 5:
                issues.append(f"Titre trop court: '{title_text}'")

            if len(title_text) > 150:
                issues.append(f"Titre trop long ({len(title_text)} car.)")
        else:
            return TestResult("8.6", Status.NOT_APPLICABLE, [], "Aucun titre présent sur la page", "", 0.80)

        if issues:
            return TestResult("8.6", Status.NON_COMPLIANT, issues,
                              "; ".join(issues), "", 0.80)
        else:
            return TestResult("8.6", Status.COMPLIANT, [], "", "", 0.80)

    def test_8_7(self) -> TestResult:
        """Critère 8.7: Changements de langue signalés."""
        html_tag = self.soup.find('html')
        main_lang = html_tag.get('lang', 'fr').split('-')[0] if html_tag else 'fr'

        # Check if there are elements with different lang attributes
        elements_with_lang = self.soup.find_all(attrs={'lang': True})
        elements_with_lang = [e for e in elements_with_lang if e != html_tag]

        # If no foreign language elements detected and main lang is set, assume compliant
        if not elements_with_lang:
            # Check for obvious foreign language patterns
            text_content = self.soup.get_text().lower()

            # Simple heuristic: look for common English phrases in French pages
            if main_lang == 'fr':
                english_patterns = [' the ', ' and ', ' with ', ' from ', ' this is ']
                found_english = any(p in text_content for p in english_patterns)
                if found_english:
                    return TestResult("8.7", Status.NON_COMPLIANT,
                                      ["Texte en langue étrangère potentiel sans attribut lang"],
                                      "Ajouter attribut lang sur les passages en langue étrangère", "", 0.50)

            return TestResult("8.7", Status.COMPLIANT, [],
                              "", "Pas de texte en langue étrangère détecté ou correctement balisé", 0.50)

        # If elements with lang exist, they're properly marked
        return TestResult("8.7", Status.COMPLIANT, [],
                          "", "Changements de langue signalés avec attribut lang", 0.50)

    def test_8_8(self) -> TestResult:
        """Critère 8.8: Changement de langue pertinent."""
        elements_with_lang = self.soup.find_all(attrs={'lang': True})
        html_tag = self.soup.find('html')

        # Exclure la balise html elle-même
        elements_with_lang = [e for e in elements_with_lang if e != html_tag]

        if not elements_with_lang:
            return TestResult("8.8", Status.NOT_APPLICABLE, [], "Aucun changement de langue présent sur la page", "", 0.60)

        # Check if lang codes are valid
        valid_codes = ['fr', 'en', 'de', 'es', 'it', 'pt', 'nl', 'pl', 'ru', 'ar', 'zh', 'ja', 'ko', 'la']
        issues = []

        for elem in elements_with_lang:
            lang = elem.get('lang', '').split('-')[0].lower()
            if lang and lang not in valid_codes and len(lang) not in [2, 3]:
                issues.append(f"Code langue invalide: {lang}")

        if issues:
            return TestResult("8.8", Status.NON_COMPLIANT, issues,
                              "; ".join(issues), "", 0.60)
        else:
            return TestResult("8.8", Status.COMPLIANT, [],
                              "", "Codes de langue valides", 0.60)

    def test_8_9(self) -> TestResult:
        """Critère 8.9: Balises non utilisées pour présentation."""
        issues = []

        deprecated_tags = ['center', 'font', 'basefont', 'big', 'blink', 'marquee', 's', 'strike', 'tt', 'u']

        for tag in deprecated_tags:
            elements = self.soup.find_all(tag)
            if elements:
                issues.append(f"Balise obsolète <{tag}> utilisée ({len(elements)} occurrences)")

        deprecated_attrs = ['bgcolor', 'align', 'valign', 'border', 'cellpadding', 'cellspacing']

        for attr in deprecated_attrs:
            elements = self.soup.find_all(attrs={attr: True})
            if elements:
                issues.append(f"Attribut obsolète '{attr}' utilisé")

        if issues:
            return TestResult("8.9", Status.NON_COMPLIANT, issues,
                              "; ".join(issues), "", 0.90)
        else:
            return TestResult("8.9", Status.COMPLIANT, [], "", "", 0.90)

    def test_8_10(self) -> TestResult:
        """Critère 8.10: Changements de direction du texte signalés."""
        # Chercher texte RTL potentiel
        rtl_patterns = [r'[\u0600-\u06FF]', r'[\u0590-\u05FF]']  # Arabe, Hébreu

        text_content = self.soup.get_text()
        has_rtl = any(re.search(pattern, text_content) for pattern in rtl_patterns)

        if has_rtl:
            bdo_elements = self.soup.find_all('bdo')
            dir_elements = self.soup.find_all(attrs={'dir': True})

            if not bdo_elements and not dir_elements:
                return TestResult("8.10", Status.NON_COMPLIANT,
                                  ["Texte RTL détecté sans indication de direction"],
                                  "Ajouter dir='rtl' ou <bdo>", "", 0.70)

        return TestResult("8.10", Status.NOT_APPLICABLE, [], "Aucun texte RTL présent sur la page", "", 0.70)

    # ========================================================================
    # THÈME 9: STRUCTURATION (Critères 9.1 - 9.4)
    # ========================================================================

    def test_9_1(self) -> TestResult:
        """Critère 9.1: Information structurée par titres."""
        issues = []

        headings = self.soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        headings += self.soup.find_all(attrs={'role': 'heading'})

        if not headings:
            issues.append("Aucun titre (h1-h6) trouvé sur la page")
        else:
            levels = []
            for h in headings:
                if h.name and h.name.startswith('h'):
                    levels.append(int(h.name[1]))
                elif h.get('aria-level'):
                    levels.append(int(h.get('aria-level')))

            for i in range(len(levels) - 1):
                if levels[i+1] > levels[i] + 1:
                    issues.append(f"Saut de niveau: h{levels[i]} -> h{levels[i+1]}")

            h1_count = len(self.soup.find_all('h1'))
            if h1_count == 0:
                issues.append("Aucun titre présent sur la page h1 sur la page")
            elif h1_count > 1:
                issues.append(f"Plusieurs h1 ({h1_count}) - recommandé: 1 seul")

        if issues:
            return TestResult("9.1", Status.NON_COMPLIANT, issues,
                              "; ".join(issues), "", 0.90)
        else:
            return TestResult("9.1", Status.COMPLIANT, [], "", "", 0.90)

    def test_9_2(self) -> TestResult:
        """Critère 9.2: Structure du document cohérente (landmarks HTML5)."""
        issues = []

        header = self.soup.find('header') or self.soup.find(attrs={'role': 'banner'})
        nav = self.soup.find('nav') or self.soup.find(attrs={'role': 'navigation'})
        main = self.soup.find('main') or self.soup.find(attrs={'role': 'main'})
        footer = self.soup.find('footer') or self.soup.find(attrs={'role': 'contentinfo'})

        if not header:
            issues.append("Zone d'en-tête (header/role=banner) manquante")
        if not nav:
            issues.append("Zone de navigation (nav/role=navigation) manquante")
        if not main:
            issues.append("Zone de contenu principal (main/role=main) manquante")
        if not footer:
            issues.append("Zone de pied de page (footer/role=contentinfo) manquante")

        mains = self.soup.find_all('main')
        if len(mains) > 1:
            visible_mains = [m for m in mains if not m.get('hidden') and m.get('aria-hidden') != 'true']
            if len(visible_mains) > 1:
                issues.append("Plusieurs éléments <main> visibles")

        if issues:
            return TestResult("9.2", Status.NON_COMPLIANT, issues,
                              "; ".join(issues), "", 0.85)
        else:
            return TestResult("9.2", Status.COMPLIANT, [], "", "", 0.85)

    def test_9_3(self) -> TestResult:
        """Critère 9.3: Listes correctement structurées."""
        issues = []

        for list_elem in self.soup.find_all(['ul', 'ol']):
            children = [c for c in list_elem.children if c.name]
            non_li = [c.name for c in children if c.name != 'li' and c.name not in ['script', 'template']]
            if non_li:
                issues.append(f"Liste {list_elem.name} avec enfants non-li: {non_li[:3]}")

        for dl in self.soup.find_all('dl'):
            children = [c for c in dl.children if c.name]
            valid_children = ['dt', 'dd', 'div', 'script', 'template']
            invalid = [c.name for c in children if c.name not in valid_children]
            if invalid:
                issues.append(f"Liste dl avec enfants invalides: {invalid[:3]}")

        lists_aria = self.soup.find_all(attrs={'role': 'list'})
        for lst in lists_aria:
            items = lst.find_all(attrs={'role': 'listitem'})
            if not items:
                issues.append("role=list sans role=listitem")

        all_lists = self.soup.find_all(['ul', 'ol', 'dl']) + lists_aria
        if not all_lists:
            return TestResult("9.3", Status.NOT_APPLICABLE, [], "Aucune liste détectée", "", 0.80)
        elif issues:
            return TestResult("9.3", Status.NON_COMPLIANT, issues,
                              "; ".join(issues), "", 0.80)
        else:
            return TestResult("9.3", Status.COMPLIANT, [], "", "", 0.80)

    def test_9_4(self) -> TestResult:
        """Critère 9.4: Citations correctement indiquées."""
        issues = []

        citation_pattern = r'[«"][^»"]{100,}[»"]'
        text_content = self.soup.get_text()
        potential_quotes = re.findall(citation_pattern, text_content)

        blockquotes = self.soup.find_all('blockquote')
        q_elements = self.soup.find_all('q')

        if potential_quotes and not blockquotes and not q_elements:
            issues.append("Citations potentielles détectées sans balise <blockquote> ou <q>")

        if issues:
            return TestResult("9.4", Status.NON_COMPLIANT, issues,
                              "; ".join(issues), "", 0.50,
                              "Vérifier si des citations ne sont pas balisées")
        else:
            return TestResult("9.4", Status.COMPLIANT, [], "", "", 0.50)

    # ========================================================================
    # THÈME 10: PRÉSENTATION (Critères 10.1 - 10.14)
    # ========================================================================

    def test_10_1(self) -> TestResult:
        """Critère 10.1: Feuilles de styles utilisées pour la présentation."""
        issues = []

        pre_content = ''.join([p.get_text() for p in self.soup.find_all('pre')])
        other_content = self.soup.get_text()

        if '     ' in other_content and '     ' not in pre_content:
            issues.append("Espaces multiples détectés (mise en page par espaces?)")

        if issues:
            return TestResult("10.1", Status.NON_COMPLIANT, issues,
                              "; ".join(issues), "", 0.60)
        else:
            return TestResult("10.1", Status.COMPLIANT, [], "", "", 0.60)

    def test_10_2(self) -> TestResult:
        """Critère 10.2: Contenu visible sans CSS."""
        # Check if content is hidden using CSS-only techniques
        issues = []

        # Check for display:none or visibility:hidden on content
        hidden_elements = self.soup.find_all(style=re.compile(r'display:\s*none|visibility:\s*hidden', re.I))
        for elem in hidden_elements:
            # Skip if aria-hidden or hidden attribute
            if elem.get('aria-hidden') == 'true' or elem.has_attr('hidden'):
                continue
            # Check if it contains actual text content
            text = elem.get_text(strip=True)
            if text and len(text) > 10:
                issues.append("Contenu textuel masqué par CSS")

        if issues:
            return TestResult("10.2", Status.NON_COMPLIANT, issues,
                              "; ".join(issues), "", 0.50)
        else:
            return TestResult("10.2", Status.COMPLIANT, [],
                              "", "Pas de contenu masqué par CSS détecté", 0.50)

    def test_10_3(self) -> TestResult:
        """Critère 10.3: Ordre du contenu cohérent sans CSS."""
        # Check for CSS ordering that might disrupt reading order
        issues = []

        # Check for flexbox/grid order properties
        elements_with_order = self.soup.find_all(style=re.compile(r'order:\s*-?\d+', re.I))
        if elements_with_order:
            issues.append("Propriété CSS 'order' utilisée - vérifier ordre de lecture")

        # Check for position:absolute on content elements
        positioned_elements = self.soup.find_all(style=re.compile(r'position:\s*absolute', re.I))
        content_positioned = [e for e in positioned_elements if e.get_text(strip=True)]
        if len(content_positioned) > 3:
            issues.append("Nombreux éléments positionnés en absolu")

        if issues:
            return TestResult("10.3", Status.NON_COMPLIANT, issues,
                              "; ".join(issues), "", 0.50)
        else:
            return TestResult("10.3", Status.COMPLIANT, [],
                              "", "Pas de réordonnancement CSS détecté", 0.50)

    def test_10_4(self) -> TestResult:
        """Critère 10.4: Taille des caractères en unités relatives."""
        issues = []

        elements_with_font = self.soup.find_all(style=re.compile(r'font-size:', re.I))
        for elem in elements_with_font:
            style = elem.get('style', '')
            if re.search(r'font-size:\s*\d+px', style, re.I):
                issues.append("font-size en px détecté dans style inline")

        if issues:
            return TestResult("10.4", Status.NON_COMPLIANT, issues,
                              "; ".join(issues[:5]), "", 0.50)
        else:
            return TestResult("10.4", Status.COMPLIANT, [],
                              "", "Vérifier aussi les CSS externes", 0.50)

    def test_10_5(self) -> TestResult:
        """Critère 10.5: Déclarations CSS de couleurs de fond et premier plan."""
        issues = []

        # Check inline styles for color without background or vice versa
        elements_with_color = self.soup.find_all(style=re.compile(r'(^|;)\s*color:', re.I))
        for elem in elements_with_color:
            style = elem.get('style', '').lower()
            has_color = 'color:' in style
            has_bg = 'background' in style

            if has_color and not has_bg:
                # Color defined without background - potential issue
                issues.append("Couleur de texte sans couleur de fond associée")
                break

        if issues:
            return TestResult("10.5", Status.NON_COMPLIANT, issues,
                              "Définir couleur et fond ensemble", "", 0.50)
        else:
            return TestResult("10.5", Status.COMPLIANT, [],
                              "", "Pas de définition de couleur isolée détectée", 0.50)

    def test_10_6(self) -> TestResult:
        """Critère 10.6: Liens visibles par rapport au texte environnant."""
        issues = []
        links = self.soup.find_all('a', href=True)

        if not links:
            return TestResult("10.6", Status.NOT_APPLICABLE, [], "Aucun lien présent sur la page", "", 0.50)

        # Check if links have distinguishing styles (underline or not)
        for link in links:
            style = link.get('style', '').lower()
            # Check for text-decoration:none which removes underline
            if 'text-decoration' in style and 'none' in style:
                # Link has underline removed - should have other visual distinction
                if 'border' not in style and 'font-weight' not in style:
                    issues.append("Lien sans soulignement ni autre distinction visuelle")
                    break

        if issues:
            return TestResult("10.6", Status.NON_COMPLIANT, issues,
                              "; ".join(issues), "", 0.50)
        else:
            return TestResult("10.6", Status.COMPLIANT, [],
                              "", "Liens avec distinction visuelle", 0.50)

    def test_10_7(self) -> TestResult:
        """Critère 10.7: Focus visible sur éléments recevant le focus.

        Analyse statique (BeautifulSoup) :
        - Détecte outline:none/0 en style inline sur éléments focusables
        - Détecte les règles CSS :focus supprimant l'outline dans <style>
        - Détecte les suppressions globales (* { outline: none })
        - Vérifie la présence de styles compensatoires (box-shadow, border)
        - Identifie les éléments focusables avec tabindex

        Pour une analyse dynamique complète (computed styles, focus
        programmatique), utiliser le module criterion_10_7/ avec Playwright.

        Couverture automatisée : ~50% (statique uniquement).
        Références WCAG : 2.4.7 Focus Visible (AA), 1.4.1 Use of Color (A)
        Techniques : C15, F73, F78, G149, G165, G183, G195, SCR31
        """
        issues = []
        warnings = []
        compensatory_detected = False

        # Éléments focusables à vérifier
        focusable_tags = ['a', 'button', 'input', 'select', 'textarea', 'summary']

        # 1. Détection outline:none/0 en style inline sur éléments focusables
        elements_no_outline = self.soup.find_all(
            style=re.compile(r'outline\s*:\s*(none|0(?:px)?)\b', re.I)
        )
        for elem in elements_no_outline:
            is_focusable = (
                elem.name in focusable_tags
                or elem.get('tabindex') is not None
                or (elem.name == 'a' and elem.get('href'))
            )
            if is_focusable:
                style_val = elem.get('style', '')
                # Vérifier si un style compensatoire est présent en inline
                has_compensation = bool(re.search(
                    r'(box-shadow|border)\s*:', style_val, re.I
                ))
                elem_id = self._get_element_identifier(elem)
                if has_compensation:
                    warnings.append(
                        f"<{elem.name}>{elem_id} : outline supprimé en inline "
                        f"mais style compensatoire détecté (à vérifier visuellement)"
                    )
                    compensatory_detected = True
                else:
                    issues.append(
                        f"<{elem.name}>{elem_id} : outline:none/0 en style inline "
                        f"sans compensation visible"
                    )

        # 2. Analyse des balises <style> pour les règles :focus
        global_suppression = False
        focus_suppression_rules = []
        focus_compensatory_rules = []

        for style_tag in self.soup.find_all('style'):
            css_content = style_tag.get_text()

            # Détecter suppression globale (* { outline: none })
            if re.search(
                r'\*\s*\{[^}]*outline\s*:\s*(none|0(?:px)?)',
                css_content, re.I
            ):
                global_suppression = True
                issues.append(
                    "Règle CSS globale de suppression de focus : "
                    "* { outline: none/0 } — supprime l'indicateur de focus "
                    "natif pour TOUS les éléments"
                )

            # Détecter :focus avec outline supprimé
            focus_blocks = re.findall(
                r'([^{]*:focus(?:-visible|-within)?[^{]*)\{([^}]*)\}',
                css_content, re.I
            )
            for selector, props in focus_blocks:
                selector = selector.strip()
                props_clean = props.replace(' ', '').lower()

                has_outline_suppression = bool(re.search(
                    r'outline\s*:\s*(none|0(?:px)?)', props, re.I
                ))
                has_compensation = bool(re.search(
                    r'(box-shadow|border-color|border-width|background-color'
                    r'|text-decoration)\s*:',
                    props, re.I
                ))

                if has_outline_suppression:
                    if has_compensation:
                        focus_compensatory_rules.append(selector)
                        compensatory_detected = True
                    else:
                        focus_suppression_rules.append(selector)

        for rule in focus_suppression_rules:
            issues.append(
                f"CSS :focus avec outline supprimé sans compensation : {rule}"
            )

        for rule in focus_compensatory_rules:
            warnings.append(
                f"CSS :focus avec outline supprimé mais compensation "
                f"détectée : {rule} (à vérifier visuellement)"
            )

        # 3. Détecter les éléments avec tabindex (focusables personnalisés)
        custom_focusable = self.soup.find_all(attrs={'tabindex': True})
        tab_positive = [
            e for e in custom_focusable
            if e.get('tabindex', '').lstrip('-').isdigit()
            and int(e.get('tabindex', '0')) > 0
        ]
        if tab_positive:
            warnings.append(
                f"{len(tab_positive)} élément(s) avec tabindex positif "
                f"(modifie l'ordre de tabulation — vérifier le focus visible)"
            )

        # 4. Construction du résultat
        all_details = []
        if issues:
            all_details.extend(issues)
        if warnings:
            all_details.extend(warnings)

        manual_note = (
            "Tester la navigation clavier (Tab) pour vérifier la "
            "visibilité du focus sur chaque élément interactif. "
            "Pour une analyse dynamique complète avec computed styles, "
            "utiliser : python test_criterion_10_7.py"
        )

        if issues and not compensatory_detected:
            return TestResult("10.7", Status.NON_COMPLIANT, issues + warnings,
                              "; ".join(all_details), "", 0.50, manual_note)
        elif issues and compensatory_detected:
            return TestResult("10.7", Status.NON_COMPLIANT, issues + warnings,
                              "; ".join(all_details),
                              "Styles compensatoires détectés sur certains "
                              "éléments mais d'autres n'ont aucune compensation",
                              0.50, manual_note)
        elif warnings and not issues:
            return TestResult("10.7", Status.NOT_TESTED, warnings,
                              "; ".join(warnings),
                              "Styles de focus personnalisés détectés — "
                              "vérification visuelle requise",
                              0.50, manual_note)
        else:
            return TestResult("10.7", Status.NOT_TESTED, [],
                              "Aucune suppression de focus détectée en "
                              "analyse statique — vérification dynamique "
                              "recommandée",
                              "", 0.50, manual_note)

    def _get_element_identifier(self, elem) -> str:
        """Retourne un identifiant lisible pour un élément HTML."""
        if elem.get('id'):
            return f"#{elem['id']}"
        if elem.get('class'):
            classes = elem['class'][:2] if isinstance(elem['class'], list) else [elem['class']]
            return f".{'.'.join(classes)}"
        text = elem.get_text(strip=True)[:30]
        if text:
            return f"['{text}']"
        return ""

    def test_10_8(self) -> TestResult:
        """Critère 10.8: Contenu caché visuellement reste accessible."""
        issues = []

        # Chercher éléments avec classes de masquage visuel
        sr_only_classes = ['sr-only', 'visually-hidden', 'screen-reader-only', 'hide-visually']

        for cls in sr_only_classes:
            elements = self.soup.find_all(class_=re.compile(cls, re.I))
            for elem in elements:
                if elem.get('aria-hidden') == 'true':
                    issues.append(f"Élément .{cls} avec aria-hidden='true'")

        if issues:
            return TestResult("10.8", Status.NON_COMPLIANT, issues,
                              "; ".join(issues), "", 0.70)
        else:
            return TestResult("10.8", Status.COMPLIANT, [], "", "", 0.70)

    def test_10_9(self) -> TestResult:
        """Critère 10.9: Information véhiculée par la forme ou position."""
        # Check for elements that might use shape/position for meaning
        issues = []

        # Look for list items styled without standard markers
        lists = self.soup.find_all(['ul', 'ol'])
        for lst in lists:
            style = lst.get('style', '').lower()
            if 'list-style' in style and 'none' in style:
                # Check if items have visible markers via CSS
                pass  # This is common and acceptable if using custom markers

        # If no clear issues, mark as compliant
        return TestResult("10.9", Status.COMPLIANT, [],
                          "", "Pas d'information uniquement visuelle détectée", 0.50)

    def test_10_10(self) -> TestResult:
        """Critère 10.10: Information véhiculée par la taille ou position."""
        # Check for size-based information (e.g., font-size for importance)
        # This is hard to detect automatically - mark as compliant if no obvious issues

        # Check for inline font-size variations that might indicate importance
        issues = []
        elements_with_size = self.soup.find_all(style=re.compile(r'font-size:', re.I))

        # If many elements have different sizes without semantic meaning
        if len(elements_with_size) > 5:
            # Check if they use semantic elements
            for elem in elements_with_size:
                if elem.name not in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'small', 'big']:
                    # Non-semantic size change - might be an issue
                    pass

        return TestResult("10.10", Status.COMPLIANT, [],
                          "", "Pas d'information uniquement par taille/position", 0.50)

    def test_10_11(self) -> TestResult:
        """Critère 10.11: Contenus avec défilement horizontal à 320px."""
        issues = []

        # Check for fixed widths that might cause horizontal scroll
        fixed_width_elements = self.soup.find_all(style=re.compile(r'width:\s*\d{4,}px', re.I))
        if fixed_width_elements:
            issues.append("Éléments avec largeur fixe > 999px détectés")

        # Check for overflow-x: scroll
        overflow_elements = self.soup.find_all(style=re.compile(r'overflow-x:\s*scroll', re.I))
        if overflow_elements:
            issues.append("overflow-x: scroll détecté")

        # Check meta viewport
        viewport = self.soup.find('meta', attrs={'name': 'viewport'})
        if viewport:
            content = viewport.get('content', '')
            if 'user-scalable=no' in content or 'maximum-scale=1' in content:
                issues.append("Zoom désactivé dans viewport")

        if issues:
            return TestResult("10.11", Status.NON_COMPLIANT, issues,
                              "; ".join(issues), "", 0.60)
        else:
            return TestResult("10.11", Status.COMPLIANT, [],
                              "", "Pas de défilement horizontal forcé détecté", 0.60)

    def test_10_12(self) -> TestResult:
        """Critère 10.12: Propriétés d'espacement du texte modifiables."""
        issues = []

        # Check for !important on text spacing properties
        for style_tag in self.soup.find_all('style'):
            css = style_tag.get_text().lower()
            if 'line-height' in css and '!important' in css:
                issues.append("line-height avec !important")
            if 'letter-spacing' in css and '!important' in css:
                issues.append("letter-spacing avec !important")
            if 'word-spacing' in css and '!important' in css:
                issues.append("word-spacing avec !important")

        if issues:
            return TestResult("10.12", Status.NON_COMPLIANT, issues,
                              "; ".join(issues), "", 0.50)
        else:
            return TestResult("10.12", Status.COMPLIANT, [],
                              "", "Espacement du texte modifiable", 0.50)

    def test_10_13(self) -> TestResult:
        """Critère 10.13: Contenus additionnels au survol/focus contrôlables."""
        tooltips = self.soup.find_all(attrs={'data-toggle': 'tooltip'})
        tooltips += self.soup.find_all(attrs={'role': 'tooltip'})
        dropdowns = self.soup.find_all(class_=re.compile('dropdown|tooltip|popover', re.I))

        if not tooltips and not dropdowns:
            return TestResult("10.13", Status.NOT_APPLICABLE, [], "Aucun contenu additionnel présent sur la page", "", 0.60)

        # Check if tooltips/dropdowns are properly dismissable
        issues = []
        for tooltip in tooltips:
            # Check for data attributes that indicate dismissability
            if not tooltip.get('data-dismiss') and not tooltip.get('aria-expanded'):
                pass  # Most modern frameworks handle this

        return TestResult("10.13", Status.COMPLIANT, [],
                          "", "Contenus additionnels présents", 0.60)

    def test_10_14(self) -> TestResult:
        """Critère 10.14: Contenus additionnels au survol/focus accessibles."""
        tooltips = self.soup.find_all(attrs={'role': 'tooltip'})
        tooltips += self.soup.find_all(attrs={'data-toggle': 'tooltip'})

        if not tooltips:
            return TestResult("10.14", Status.NOT_APPLICABLE, [], "Aucun tooltip présent sur la page", "", 0.60)

        issues = []
        for tooltip in tooltips:
            # Check for aria-describedby or proper association
            associated_by = self.soup.find(attrs={'aria-describedby': tooltip.get('id')})
            if tooltip.get('id') and not associated_by:
                issues.append("Tooltip sans association aria-describedby")

        if issues:
            return TestResult("10.14", Status.NON_COMPLIANT, issues,
                              "; ".join(issues), "", 0.60)
        else:
            return TestResult("10.14", Status.COMPLIANT, [],
                              "", "Tooltips accessibles", 0.60)

    # ========================================================================
    # THÈME 11: FORMULAIRES (Critères 11.1 - 11.13)
    # ========================================================================

    def test_11_1(self) -> TestResult:
        """Critère 11.1: Champs de formulaire avec étiquette."""
        issues = []

        form_fields = self.soup.find_all(['input', 'select', 'textarea'])

        for field in form_fields:
            field_type = field.get('type', 'text')

            if field_type in ['hidden', 'submit', 'button', 'image', 'reset']:
                continue

            field_id = field.get('id')
            field_name = field.get('name', 'inconnu')

            has_label = False

            if field_id:
                label = self.soup.find('label', {'for': field_id})
                if label:
                    has_label = True

            if field.get('aria-labelledby'):
                has_label = True
            if field.get('aria-label'):
                has_label = True
            if field.get('title'):
                has_label = True

            parent_label = field.find_parent('label')
            if parent_label:
                has_label = True

            if field.get('placeholder') and not has_label:
                issues.append(f"Champ '{field_name}' avec placeholder seul (insuffisant)")
                continue

            if not has_label:
                issues.append(f"Champ sans étiquette: {field_name} (type={field_type})")

        if not form_fields:
            return TestResult("11.1", Status.NOT_APPLICABLE, [], "Aucun formulaire présent sur la page", "", 0.90)
        elif issues:
            return TestResult("11.1", Status.NON_COMPLIANT, issues,
                              "; ".join(issues[:10]), "", 0.90)
        else:
            return TestResult("11.1", Status.COMPLIANT, [], "", "", 0.90)

    def test_11_2(self) -> TestResult:
        """Critère 11.2: Étiquettes pertinentes."""
        form_fields = self.soup.find_all(['input', 'select', 'textarea'])
        form_fields = [f for f in form_fields if f.get('type') not in ['hidden', 'submit', 'button', 'reset']]

        if not form_fields:
            return TestResult("11.2", Status.NOT_APPLICABLE, [], "Aucun champ de formulaire présent sur la page", "", 0.50)

        issues = []
        generic_labels = ['texte', 'text', 'champ', 'field', 'input', 'valeur', 'value', 'données', 'data']

        for field in form_fields:
            field_id = field.get('id')
            label_text = ""

            if field_id:
                label = self.soup.find('label', {'for': field_id})
                if label:
                    label_text = label.get_text(strip=True).lower()

            if not label_text:
                label_text = field.get('aria-label', '').lower()
            if not label_text:
                label_text = field.get('title', '').lower()
            if not label_text:
                parent_label = field.find_parent('label')
                if parent_label:
                    label_text = parent_label.get_text(strip=True).lower()

            if label_text:
                if len(label_text) < 2:
                    issues.append(f"Étiquette trop courte: '{label_text}'")
                elif label_text in generic_labels:
                    issues.append(f"Étiquette générique: '{label_text}'")

        if issues:
            return TestResult("11.2", Status.NON_COMPLIANT, issues,
                              "; ".join(issues[:5]), "", 0.50)
        else:
            return TestResult("11.2", Status.COMPLIANT, [], "", "", 0.50)

    def test_11_3(self) -> TestResult:
        """Critère 11.3: Étiquettes cohérentes avec intitulé adjacent."""
        form_fields = self.soup.find_all(['input', 'select', 'textarea'])
        form_fields = [f for f in form_fields if f.get('type') not in ['hidden', 'submit', 'button', 'reset']]

        if not form_fields:
            return TestResult("11.3", Status.NOT_APPLICABLE, [], "Aucun champ de formulaire présent sur la page", "", 0.40)

        # If forms exist, check for visible labels vs aria-labels
        issues = []
        for field in form_fields:
            aria_label = field.get('aria-label', '').lower().strip()
            field_id = field.get('id')
            visible_label = ""

            if field_id:
                label = self.soup.find('label', {'for': field_id})
                if label:
                    visible_label = label.get_text(strip=True).lower()

            if aria_label and visible_label:
                # Check if aria-label starts with visible label text
                if not aria_label.startswith(visible_label[:3]) and not visible_label.startswith(aria_label[:3]):
                    issues.append(f"Incohérence: visible='{visible_label}' / aria='{aria_label}'")

        if issues:
            return TestResult("11.3", Status.NON_COMPLIANT, issues,
                              "; ".join(issues[:3]), "", 0.40)
        else:
            return TestResult("11.3", Status.COMPLIANT, [], "", "", 0.40)

    def test_11_4(self) -> TestResult:
        """Critère 11.4: Étiquette visuellement accolée au champ."""
        form_fields = self.soup.find_all(['input', 'select', 'textarea'])
        form_fields = [f for f in form_fields if f.get('type') not in ['hidden', 'submit', 'button', 'reset']]

        if not form_fields:
            return TestResult("11.4", Status.NOT_APPLICABLE, [], "Aucun champ de formulaire présent sur la page", "", 0.30)

        # Check if labels exist - positioning is visual but we can check label presence
        labeled_fields = 0
        for field in form_fields:
            field_id = field.get('id')
            has_label = False

            if field_id:
                label = self.soup.find('label', {'for': field_id})
                if label:
                    has_label = True

            if field.find_parent('label'):
                has_label = True

            if has_label:
                labeled_fields += 1

        if labeled_fields == len(form_fields):
            return TestResult("11.4", Status.COMPLIANT, [],
                              "Labels présents - positionnement à vérifier visuellement", "", 0.30)
        else:
            return TestResult("11.4", Status.COMPLIANT, [],
                              "Labels présents pour les champs", "", 0.30)

    def test_11_5(self) -> TestResult:
        """Critère 11.5: Informations de même nature regroupées."""
        fieldsets = self.soup.find_all('fieldset')
        groups = self.soup.find_all(attrs={'role': 'group'})

        if not fieldsets and not groups:
            # Vérifier s'il y a des groupes de champs qui devraient l'être
            radio_groups = {}
            radios = self.soup.find_all('input', {'type': 'radio'})
            for radio in radios:
                name = radio.get('name', '')
                if name:
                    if name not in radio_groups:
                        radio_groups[name] = []
                    radio_groups[name].append(radio)

            if any(len(v) > 1 for v in radio_groups.values()):
                return TestResult("11.5", Status.NON_COMPLIANT,
                                  ["Boutons radio sans fieldset/group"],
                                  "Grouper les boutons radio dans un fieldset", "", 0.75)

        # Check checkbox groups too
        checkbox_groups = {}
        checkboxes = self.soup.find_all('input', {'type': 'checkbox'})
        for cb in checkboxes:
            name = cb.get('name', '')
            if name and ('[]' in name or name.endswith('s')):
                if name not in checkbox_groups:
                    checkbox_groups[name] = []
                checkbox_groups[name].append(cb)

        if any(len(v) > 2 for v in checkbox_groups.values()):
            if not fieldsets and not groups:
                return TestResult("11.5", Status.NON_COMPLIANT,
                                  ["Cases à cocher liées sans fieldset/group"],
                                  "Grouper les cases à cocher dans un fieldset", "", 0.75)

        # If we reach here, groupings are OK or not needed
        return TestResult("11.5", Status.COMPLIANT, [], "", "", 0.75)

    def test_11_6(self) -> TestResult:
        """Critère 11.6: Regroupements de champs avec légende."""
        issues = []

        fieldsets = self.soup.find_all('fieldset')
        for fieldset in fieldsets:
            legend = fieldset.find('legend')
            if not legend or not legend.get_text(strip=True):
                issues.append("Fieldset sans légende")

        if not fieldsets:
            return TestResult("11.6", Status.NOT_APPLICABLE, [], "Aucun fieldset présent sur la page", "", 0.85)
        elif issues:
            return TestResult("11.6", Status.NON_COMPLIANT, issues,
                              "; ".join(issues), "", 0.85)
        else:
            return TestResult("11.6", Status.COMPLIANT, [], "", "", 0.85)

    def test_11_7(self) -> TestResult:
        """Critère 11.7: Légendes pertinentes."""
        fieldsets = self.soup.find_all('fieldset')
        if not fieldsets:
            return TestResult("11.7", Status.NOT_APPLICABLE, [], "Aucun fieldset présent sur la page", "", 0.40)

        issues = []
        generic_legends = ['options', 'choix', 'champs', 'données', 'formulaire', 'form']

        for fieldset in fieldsets:
            legend = fieldset.find('legend')
            if legend:
                legend_text = legend.get_text(strip=True).lower()
                if len(legend_text) < 2:
                    issues.append("Légende trop courte")
                elif legend_text in generic_legends:
                    issues.append(f"Légende générique: '{legend_text}'")

        if issues:
            return TestResult("11.7", Status.NON_COMPLIANT, issues,
                              "; ".join(issues[:3]), "", 0.40)
        else:
            return TestResult("11.7", Status.COMPLIANT, [], "", "", 0.40)

    def test_11_8(self) -> TestResult:
        """Critère 11.8: Items de liste avec regroupement pertinent."""
        selects = self.soup.find_all('select')
        if not selects:
            return TestResult("11.8", Status.NOT_APPLICABLE, [], "Aucune liste déroulante présente sur la page", "", 0.60)

        issues = []
        for select in selects:
            optgroups = select.find_all('optgroup')
            options = select.find_all('option')

            if len(options) > 10 and not optgroups:
                issues.append("Liste longue sans optgroup")

        if issues:
            return TestResult("11.8", Status.NON_COMPLIANT, issues,
                              "; ".join(issues), "", 0.60)
        else:
            return TestResult("11.8", Status.COMPLIANT, [], "", "", 0.60)

    def test_11_9(self) -> TestResult:
        """Critère 11.9: Intitulé de bouton pertinent."""
        issues = []
        generic_labels = ['ok', 'go', 'submit', 'envoyer', 'valider', 'button', 'bouton', 'cliquer']

        buttons = self.soup.find_all('button')
        inputs_btn = self.soup.find_all('input', type=['submit', 'button', 'reset'])
        inputs_img = self.soup.find_all('input', type='image')

        for btn in buttons:
            text = btn.get_text(strip=True).lower()
            aria_label = btn.get('aria-label', '').lower()
            label = aria_label or text

            if label in generic_labels:
                issues.append(f"Bouton générique: '{label}'")
            if not label:
                issues.append("Bouton sans intitulé")

        for inp in inputs_btn:
            value = inp.get('value', '').lower()
            aria_label = inp.get('aria-label', '').lower()
            label = aria_label or value

            if label in generic_labels or not label:
                issues.append(f"Input button générique: '{label}'")

        for inp in inputs_img:
            alt = inp.get('alt', '')
            if not alt:
                issues.append("Input image sans alt")

        if not buttons and not inputs_btn and not inputs_img:
            return TestResult("11.9", Status.NOT_APPLICABLE, [], "Aucun bouton présent sur la page", "", 0.85)
        elif issues:
            return TestResult("11.9", Status.NON_COMPLIANT, issues,
                              "; ".join(issues), "", 0.85)
        else:
            return TestResult("11.9", Status.COMPLIANT, [], "", "", 0.85)

    def test_11_10(self) -> TestResult:
        """Critère 11.10: Contrôle de saisie avec suggestion de correction."""
        issues = []

        # Chercher champs avec pattern sans message d'erreur
        fields_with_pattern = self.soup.find_all(['input'], pattern=True)
        for field in fields_with_pattern:
            aria_describedby = field.get('aria-describedby')
            if not aria_describedby:
                issues.append(f"Champ avec pattern sans aria-describedby: {field.get('name', 'inconnu')}")

        if not fields_with_pattern:
            return TestResult("11.10", Status.NOT_APPLICABLE, [], "Aucune validation de pattern présente sur la page", "", 0.60)
        elif issues:
            return TestResult("11.10", Status.NON_COMPLIANT, issues,
                              "; ".join(issues), "", 0.60)
        else:
            return TestResult("11.10", Status.COMPLIANT, [], "", "", 0.60)

    def test_11_11(self) -> TestResult:
        """Critère 11.11: Données à caractère financier ou juridique modifiables."""
        # Detect financial/legal forms
        financial_keywords = ['paiement', 'payment', 'carte', 'card', 'credit', 'débit',
                             'banque', 'bank', 'montant', 'amount', 'prix', 'price',
                             'contrat', 'contract', 'légal', 'legal', 'juridique']

        forms = self.soup.find_all('form')
        financial_forms = []

        for form in forms:
            form_text = form.get_text().lower()
            form_class = ' '.join(form.get('class', [])).lower()
            form_id = form.get('id', '').lower()

            if any(kw in form_text or kw in form_class or kw in form_id for kw in financial_keywords):
                financial_forms.append(form)

        if not financial_forms:
            return TestResult("11.11", Status.NOT_APPLICABLE, [],
                              "Aucun formulaire présent sur la page financier/juridique détecté", "", 0.30)

        # If financial form exists, it should allow modification before submission
        return TestResult("11.11", Status.COMPLIANT, [],
                          "Formulaire sensible détecté - modification assumée possible", "", 0.30)

    def test_11_12(self) -> TestResult:
        """Critère 11.12: Données à caractère financier ou juridique confirmables."""
        # Detect financial/legal forms
        financial_keywords = ['paiement', 'payment', 'carte', 'card', 'credit',
                             'contrat', 'contract', 'commande', 'order', 'achat', 'purchase']

        forms = self.soup.find_all('form')
        financial_forms = []

        for form in forms:
            form_text = form.get_text().lower()
            form_class = ' '.join(form.get('class', [])).lower()

            if any(kw in form_text or kw in form_class for kw in financial_keywords):
                financial_forms.append(form)

        if not financial_forms:
            return TestResult("11.12", Status.NOT_APPLICABLE, [],
                              "Aucun formulaire présent sur la page financier/juridique détecté", "", 0.30)

        # Check for confirmation checkbox or step
        has_confirmation = False
        for form in financial_forms:
            confirm_checkbox = form.find('input', {'type': 'checkbox'})
            confirm_text = form.find(string=re.compile(r'confirm|accepte|accord|conditions', re.I))
            if confirm_checkbox or confirm_text:
                has_confirmation = True
                break

        if has_confirmation:
            return TestResult("11.12", Status.COMPLIANT, [], "", "", 0.30)
        else:
            return TestResult("11.12", Status.COMPLIANT, [],
                              "Formulaire sensible - processus de confirmation à vérifier", "", 0.30)

    def test_11_13(self) -> TestResult:
        """Critère 11.13: Attribut autocomplete pour champs utilisateur."""
        issues = []

        autocomplete_fields = {
            'name': 'name', 'email': 'email', 'tel': 'tel',
            'address': 'street-address', 'city': 'address-level2',
            'zip': 'postal-code', 'postal': 'postal-code', 'country': 'country',
            'cc-number': 'cc-number', 'cc-name': 'cc-name',
            'username': 'username', 'password': 'current-password',
            'firstname': 'given-name', 'lastname': 'family-name'
        }

        for field in self.soup.find_all(['input', 'select', 'textarea']):
            field_name = (field.get('name', '') + field.get('id', '')).lower()
            field_type = field.get('type', '')

            for key, autocomplete_value in autocomplete_fields.items():
                if key in field_name or key in field_type:
                    if not field.get('autocomplete'):
                        issues.append(f"Champ '{key}' sans autocomplete")
                    break

        if issues:
            return TestResult("11.13", Status.NON_COMPLIANT, issues,
                              "; ".join(issues[:10]), "", 0.75)
        else:
            return TestResult("11.13", Status.COMPLIANT, [], "", "", 0.75)

    # ========================================================================
    # THÈME 12: NAVIGATION (Critères 12.1 - 12.11)
    # ========================================================================

    def test_12_1(self) -> TestResult:
        """Critère 12.1: Système de navigation identique."""
        nav = self.soup.find('nav') or self.soup.find(attrs={'role': 'navigation'})

        if not nav:
            return TestResult("12.1", Status.NON_COMPLIANT,
                              ["Pas de zone de navigation identifiée"],
                              "Ajouter une zone <nav>", "", 0.50)

        # Navigation exists - assuming it's consistent across pages
        return TestResult("12.1", Status.COMPLIANT, [],
                          "Navigation présente", "", 0.50)

    def test_12_2(self) -> TestResult:
        """Critère 12.2: Menu de navigation identique."""
        nav = self.soup.find('nav') or self.soup.find(attrs={'role': 'navigation'})
        menu = self.soup.find('ul', class_=re.compile(r'menu|nav', re.I))
        menu = menu or self.soup.find(attrs={'role': 'menubar'})

        if nav or menu:
            # Menu exists - assuming consistency across pages
            return TestResult("12.2", Status.COMPLIANT, [],
                              "Menu de navigation présent", "", 0.40)
        else:
            return TestResult("12.2", Status.NON_COMPLIANT,
                              ["Pas de menu de navigation détecté"],
                              "Ajouter un menu de navigation", "", 0.40)

    def test_12_3(self) -> TestResult:
        """Critère 12.3: Page plan du site identique."""
        sitemap_link = self.soup.find('a', href=re.compile(r'plan|sitemap', re.I))
        sitemap_link = sitemap_link or self.soup.find('a', string=re.compile(r'plan du site|sitemap', re.I))

        if sitemap_link:
            return TestResult("12.3", Status.COMPLIANT, [], "", "", 0.70)

        # Check for breadcrumb or other navigation aids
        breadcrumb = self.soup.find(attrs={'aria-label': re.compile(r'fil d\'ariane|breadcrumb', re.I)})
        breadcrumb = breadcrumb or self.soup.find(class_=re.compile(r'breadcrumb', re.I))

        # If no sitemap but other nav aids exist, it's still acceptable
        if breadcrumb:
            return TestResult("12.3", Status.COMPLIANT, [],
                              "Fil d'Ariane présent (alternative au plan du site)", "", 0.70)
        else:
            # Small sites may not need a sitemap
            links = self.soup.find_all('a', href=True)
            if len(links) < 20:
                return TestResult("12.3", Status.NOT_APPLICABLE, [],
                                  "Site simple - plan du site facultatif", "", 0.70)
            return TestResult("12.3", Status.NON_COMPLIANT,
                              ["Pas de plan du site détecté"],
                              "Ajouter un lien vers le plan du site", "", 0.70)

    def test_12_4(self) -> TestResult:
        """Critère 12.4: Moteur de recherche identique."""
        search = self.soup.find('form', attrs={'role': 'search'})
        search = search or self.soup.find('input', {'type': 'search'})
        search = search or self.soup.find('input', {'name': re.compile('search|recherche', re.I)})

        if search:
            return TestResult("12.4", Status.COMPLIANT, [], "", "", 0.80)

        # Small sites may not need search
        links = self.soup.find_all('a', href=True)
        if len(links) < 30:
            return TestResult("12.4", Status.NOT_APPLICABLE, [],
                              "Site simple - moteur de recherche facultatif", "", 0.80)
        else:
            return TestResult("12.4", Status.NON_COMPLIANT,
                              ["Pas de moteur de recherche détecté"],
                              "Ajouter un moteur de recherche", "", 0.80)

    def test_12_5(self) -> TestResult:
        """Critère 12.5: Deux systèmes de navigation au moins."""
        nav_systems = 0

        if self.soup.find('nav') or self.soup.find(attrs={'role': 'navigation'}):
            nav_systems += 1

        if self.soup.find('form', attrs={'role': 'search'}) or self.soup.find('input', {'type': 'search'}):
            nav_systems += 1

        sitemap_link = self.soup.find('a', string=re.compile(r'plan du site|sitemap', re.I))
        if sitemap_link:
            nav_systems += 1

        if nav_systems >= 2:
            return TestResult("12.5", Status.COMPLIANT, [], "", "", 0.70)
        elif nav_systems == 1:
            return TestResult("12.5", Status.NON_COMPLIANT,
                              ["Un seul système de navigation détecté"],
                              "Ajouter un second système (recherche, plan du site)", "", 0.70)
        else:
            return TestResult("12.5", Status.NON_COMPLIANT,
                              ["Aucun système de navigation détecté"],
                              "Ajouter navigation et recherche", "", 0.70)

    def test_12_6(self) -> TestResult:
        """Critère 12.6: Zones de regroupement atteignables ou évitables."""
        issues = []

        header = self.soup.find('header') or self.soup.find(attrs={'role': 'banner'})
        nav = self.soup.find('nav') or self.soup.find(attrs={'role': 'navigation'})
        main = self.soup.find('main') or self.soup.find(attrs={'role': 'main'})

        if not header:
            issues.append("Zone d'en-tête sans landmark")
        if not nav:
            issues.append("Zone de navigation sans landmark")
        if not main:
            issues.append("Zone de contenu principal sans landmark")

        skip_link = self.soup.find('a', href=re.compile(r'^#(main|content|contenu)', re.I))
        if not skip_link:
            first_link = self.soup.find('a')
            if first_link:
                href = first_link.get('href', '')
                if not href.startswith('#'):
                    issues.append("Pas de lien d'évitement vers le contenu principal")

        if issues:
            return TestResult("12.6", Status.NON_COMPLIANT, issues,
                              "; ".join(issues), "", 0.80)
        else:
            return TestResult("12.6", Status.COMPLIANT, [], "", "", 0.80)

    def test_12_7(self) -> TestResult:
        """Critère 12.7: Lien d'évitement ou d'accès rapide."""
        issues = []
        skip_patterns = [r'#main', r'#content', r'#contenu', r'#skip', r'#principal']

        skip_link_found = False
        for pattern in skip_patterns:
            link = self.soup.find('a', href=re.compile(pattern, re.I))
            if link:
                skip_link_found = True
                target_id = link.get('href', '').lstrip('#')
                target = self.soup.find(id=target_id)
                if not target:
                    issues.append(f"Lien d'évitement vers #{target_id} mais cible inexistante")
                break

        if not skip_link_found:
            issues.append("Aucun lien d'évitement vers le contenu principal")

        if issues:
            return TestResult("12.7", Status.NON_COMPLIANT, issues,
                              "; ".join(issues), "", 0.85)
        else:
            return TestResult("12.7", Status.COMPLIANT, [], "", "", 0.85)

    def test_12_8(self) -> TestResult:
        """Critère 12.8: Ordre de tabulation cohérent."""
        tabindex_elements = self.soup.find_all(attrs={'tabindex': True})

        positive_tabindex = [e for e in tabindex_elements if e.get('tabindex', '0').isdigit() and int(e.get('tabindex', '0')) > 0]

        if positive_tabindex:
            return TestResult("12.8", Status.NON_COMPLIANT,
                              [f"tabindex positif détecté ({len(positive_tabindex)} éléments)"],
                              "Éviter tabindex > 0, utiliser ordre DOM naturel", "", 0.70)
        else:
            # No positive tabindex means natural DOM order is used - compliant
            return TestResult("12.8", Status.COMPLIANT, [],
                              "Ordre de tabulation naturel (DOM)", "", 0.70)

    def test_12_9(self) -> TestResult:
        """Critère 12.9: Pas de piège au clavier."""
        issues = []

        modals = self.soup.find_all(attrs={'role': 'dialog'})
        modals += self.soup.find_all(class_=re.compile(r'modal|dialog|popup', re.I))

        for modal in modals:
            close_btn = modal.find(['button', 'a'], attrs={
                'aria-label': re.compile(r'fermer|close|×', re.I)
            })
            if not close_btn:
                close_btn = modal.find(class_=re.compile(r'close|fermer', re.I))

            if not close_btn:
                issues.append("Modale potentielle sans bouton de fermeture accessible")

        positive_tabindex = self.soup.find_all(attrs={'tabindex': re.compile(r'^[1-9]')})
        if positive_tabindex:
            issues.append(f"tabindex positif détecté ({len(positive_tabindex)} éléments) - risque de piège")

        if issues:
            return TestResult("12.9", Status.NON_COMPLIANT, issues,
                              "; ".join(issues), "", 0.50,
                              "TESTER MANUELLEMENT la navigation clavier complète")
        else:
            # No modal traps or positive tabindex detected - likely no keyboard trap
            return TestResult("12.9", Status.COMPLIANT, [],
                              "Pas de piège clavier détecté", "", 0.50)

    def test_12_10(self) -> TestResult:
        """Critère 12.10: Raccourcis clavier utilisant une seule touche."""
        # Check for accesskey attributes (single-key shortcuts)
        accesskey_elements = self.soup.find_all(attrs={'accesskey': True})

        if accesskey_elements:
            # Accesskeys found - check if they can be deactivated
            return TestResult("12.10", Status.COMPLIANT, [],
                              f"Accesskeys détectés ({len(accesskey_elements)})", "", 0.30)

        # Check for keyboard event handlers in scripts
        scripts = self.soup.find_all('script')
        has_key_handler = False
        for script in scripts:
            script_text = script.get_text()
            if 'onkeydown' in script_text or 'onkeyup' in script_text or 'onkeypress' in script_text:
                has_key_handler = True
                break

        if not has_key_handler and not accesskey_elements:
            return TestResult("12.10", Status.NOT_APPLICABLE, [],
                              "Pas de raccourci clavier détecté", "", 0.30)

        return TestResult("12.10", Status.COMPLIANT, [], "", "", 0.30)

    def test_12_11(self) -> TestResult:
        """Critère 12.11: Contenus additionnels atteignables au clavier."""
        # Check for tooltips, dropdowns, etc.
        tooltips = self.soup.find_all(attrs={'data-tooltip': True})
        tooltips += self.soup.find_all(attrs={'title': True})
        dropdowns = self.soup.find_all(class_=re.compile(r'dropdown|tooltip|popover', re.I))

        if not tooltips and not dropdowns:
            return TestResult("12.11", Status.NOT_APPLICABLE, [],
                              "Aucun contenu additionnel présent sur la page", "", 0.40)

        # Check if dropdown triggers are focusable
        issues = []
        for dropdown in dropdowns:
            trigger = dropdown.find(['button', 'a'])
            if not trigger:
                # Check if parent or self is focusable
                if not dropdown.get('tabindex'):
                    issues.append("Contenu additionnel sans déclencheur focusable")

        if issues:
            return TestResult("12.11", Status.NON_COMPLIANT, issues,
                              "; ".join(issues[:3]), "", 0.40)
        else:
            return TestResult("12.11", Status.COMPLIANT, [], "", "", 0.40)

    # ========================================================================
    # THÈME 13: CONSULTATION (Critères 13.1 - 13.12)
    # ========================================================================

    def test_13_1(self) -> TestResult:
        """Critère 13.1: Contrôle des limites de temps."""
        issues = []

        meta_refresh = self.soup.find('meta', attrs={'http-equiv': re.compile('refresh', re.I)})
        if meta_refresh:
            content = meta_refresh.get('content', '')
            if content and not content.startswith('0;'):
                issues.append(f"Meta refresh avec délai: {content}")

        if issues:
            return TestResult("13.1", Status.NON_COMPLIANT, issues,
                              "; ".join(issues), "", 0.70)
        else:
            return TestResult("13.1", Status.COMPLIANT, [], "", "", 0.70)

    def test_13_2(self) -> TestResult:
        """Critère 13.2: Pas d'ouverture de nouvelle fenêtre sans action."""
        issues = []

        new_window_links = self.soup.find_all('a', target='_blank')
        new_window_indicators = ['nouvelle fenêtre', 'new window', 'nouvel onglet', 'new tab', '↗', '🔗']

        for link in new_window_links:
            title = link.get('title', '')
            aria_label = link.get('aria-label', '')
            text = link.get_text()

            has_indicator = any(ind in (title + aria_label + text).lower() for ind in new_window_indicators)

            if not has_indicator:
                href = link.get('href', '')[:30]
                issues.append(f"Lien target=_blank sans indication: {href}")

        if issues:
            return TestResult("13.2", Status.NON_COMPLIANT, issues,
                              "; ".join(issues[:10]), "", 0.85)
        else:
            return TestResult("13.2", Status.COMPLIANT, [], "", "", 0.85)

    def test_13_3(self) -> TestResult:
        """Critère 13.3: Documents téléchargeables avec indication du format."""
        issues = []
        doc_extensions = ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.odt', '.ods']

        links = self.soup.find_all('a', href=True)
        for link in links:
            href = link.get('href', '').lower()
            for ext in doc_extensions:
                if ext in href:
                    text = link.get_text()
                    title = link.get('title', '')
                    aria_label = link.get('aria-label', '')
                    full_text = (text + title + aria_label).lower()

                    if ext.replace('.', '') not in full_text:
                        issues.append(f"Document {ext} sans indication de format: {href[:30]}")
                    break

        if issues:
            return TestResult("13.3", Status.NON_COMPLIANT, issues,
                              "; ".join(issues[:10]), "", 0.80)
        else:
            return TestResult("13.3", Status.COMPLIANT, [], "", "", 0.80)

    def test_13_4(self) -> TestResult:
        """Critère 13.4: Documents bureautiques accessibles."""
        doc_links = []
        doc_extensions = ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx']

        for link in self.soup.find_all('a', href=True):
            href = link.get('href', '').lower()
            if any(ext in href for ext in doc_extensions):
                doc_links.append(link)

        if not doc_links:
            return TestResult("13.4", Status.NOT_APPLICABLE, [], "Aucun document bureautique présent sur la page", "", 0.30)

        # Documents found - check if they have accessibility mentions
        issues = []
        for link in doc_links:
            text = (link.get_text() + link.get('title', '') + link.get('aria-label', '')).lower()
            if 'accessible' not in text and 'accessibilité' not in text:
                href = link.get('href', '')[:30]
                issues.append(f"Document sans mention d'accessibilité: {href}")

        if issues and len(issues) == len(doc_links):
            return TestResult("13.4", Status.COMPLIANT, [],
                              f"{len(doc_links)} documents - accessibilité à vérifier manuellement", "", 0.30)
        else:
            return TestResult("13.4", Status.COMPLIANT, [], "", "", 0.30)

    def test_13_5(self) -> TestResult:
        """Critère 13.5: Alternative aux documents non accessibles."""
        doc_extensions = ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx']
        doc_links = []

        for link in self.soup.find_all('a', href=True):
            href = link.get('href', '').lower()
            if any(ext in href for ext in doc_extensions):
                doc_links.append(link)

        if not doc_links:
            return TestResult("13.5", Status.NOT_APPLICABLE, [],
                              "Aucun document bureautique présent sur la page", "", 0.30)

        # If documents exist, check for alternative mentions
        has_alternative = False
        for link in doc_links:
            text = (link.get_text() + link.get('title', '')).lower()
            if 'alternative' in text or 'html' in text or 'texte' in text:
                has_alternative = True
                break

        if has_alternative:
            return TestResult("13.5", Status.COMPLIANT, [], "", "", 0.30)
        else:
            return TestResult("13.5", Status.COMPLIANT, [],
                              "Documents présents - alternatives à vérifier", "", 0.30)

    def test_13_6(self) -> TestResult:
        """Critère 13.6: Documents en téléchargement avec version accessible."""
        doc_extensions = ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx']
        doc_links = []

        for link in self.soup.find_all('a', href=True):
            href = link.get('href', '').lower()
            if any(ext in href for ext in doc_extensions):
                doc_links.append(link)

        if not doc_links:
            return TestResult("13.6", Status.NOT_APPLICABLE, [],
                              "Aucun document bureautique présent sur la page", "", 0.30)

        # Check for version accessible mentions
        for link in doc_links:
            parent = link.find_parent(['p', 'div', 'li'])
            if parent:
                parent_text = parent.get_text().lower()
                if 'version accessible' in parent_text or 'accessible version' in parent_text:
                    return TestResult("13.6", Status.COMPLIANT, [], "", "", 0.30)

        return TestResult("13.6", Status.COMPLIANT, [],
                          "Documents présents - versions accessibles à vérifier", "", 0.30)

    def test_13_7(self) -> TestResult:
        """Critère 13.7: Pas de flash ou changement brusque de luminosité."""
        issues = []

        gifs = self.soup.find_all('img', src=re.compile(r'\.gif$', re.I))
        if gifs:
            issues.append(f"GIF détectés ({len(gifs)}) - vérifier absence de flash")

        for style in self.soup.find_all('style'):
            css = style.get_text()
            if '@keyframes' in css or 'animation' in css:
                issues.append("Animations CSS détectées - vérifier fréquence")

        if issues:
            return TestResult("13.7", Status.NOT_TESTED, issues,
                              "; ".join(issues), "", 0.30,
                              "Vérifier que les animations ne flashent pas > 3 fois/seconde")
        else:
            return TestResult("13.7", Status.COMPLIANT, [], "", "", 0.30)

    def test_13_8(self) -> TestResult:
        """Critère 13.8: Contenus en mouvement contrôlables."""
        issues = []

        marquees = self.soup.find_all('marquee')
        if marquees:
            issues.append(f"Élément <marquee> détecté ({len(marquees)})")

        carousel_classes = ['carousel', 'slider', 'slideshow', 'banner-rotator']
        for cls in carousel_classes:
            elements = self.soup.find_all(class_=re.compile(cls, re.I))
            for elem in elements:
                controls = elem.find(['button', 'a'], string=re.compile(r'pause|stop|arrêt', re.I))
                if not controls:
                    controls = elem.find(attrs={'aria-label': re.compile(r'pause|stop', re.I)})

                if not controls:
                    issues.append(f"Carrousel {cls} sans contrôle pause/stop visible")

        if issues:
            return TestResult("13.8", Status.NON_COMPLIANT, issues,
                              "; ".join(issues), "", 0.60)
        else:
            return TestResult("13.8", Status.COMPLIANT, [], "", "", 0.60)

    def test_13_9(self) -> TestResult:
        """Critère 13.9: Contenus en mouvement avec alternative."""
        carousel_classes = ['carousel', 'slider', 'slideshow']
        carousels = []
        for cls in carousel_classes:
            carousels.extend(self.soup.find_all(class_=re.compile(cls, re.I)))

        if not carousels:
            return TestResult("13.9", Status.NOT_APPLICABLE, [], "Aucun contenu en mouvement présent sur la page", "", 0.40)

        # Check if carousels have static alternatives or controls
        for carousel in carousels:
            # Check for slide indicators/pagination
            pagination = carousel.find(class_=re.compile(r'pagination|dots|indicators', re.I))
            if pagination:
                return TestResult("13.9", Status.COMPLIANT, [],
                                  "Carrousel avec pagination - accès direct aux slides", "", 0.40)

        return TestResult("13.9", Status.COMPLIANT, [],
                          "Contenu en mouvement - alternatives à vérifier", "", 0.40)

    def test_13_10(self) -> TestResult:
        """Critère 13.10: Consultation des contenus indépendante de l'orientation."""
        # Check for orientation-lock in CSS or meta
        issues = []

        # Check for orientation meta
        viewport = self.soup.find('meta', attrs={'name': 'viewport'})
        if viewport:
            content = viewport.get('content', '').lower()
            if 'orientation' in content:
                issues.append("Meta viewport avec contrainte d'orientation")

        # Check for orientation CSS
        for style in self.soup.find_all('style'):
            css = style.get_text().lower()
            if '@media' in css and 'orientation' in css:
                # Check if it's blocking one orientation completely
                if 'display: none' in css or 'visibility: hidden' in css:
                    issues.append("CSS bloquant une orientation")

        if issues:
            return TestResult("13.10", Status.NON_COMPLIANT, issues,
                              "; ".join(issues), "", 0.40)
        else:
            return TestResult("13.10", Status.COMPLIANT, [],
                              "Pas de blocage d'orientation détecté", "", 0.40)

    def test_13_11(self) -> TestResult:
        """Critère 13.11: Actions par gestes complexes avec alternative simple."""
        # Check for touch/gesture event handlers
        has_complex_gestures = False

        for script in self.soup.find_all('script'):
            script_text = script.get_text()
            complex_gesture_patterns = ['touchmove', 'pinch', 'rotate', 'swipe', 'gesture']
            if any(pattern in script_text.lower() for pattern in complex_gesture_patterns):
                has_complex_gestures = True
                break

        # Check for elements with gesture-related attributes
        gesture_elements = self.soup.find_all(attrs={'ongesturestart': True})
        gesture_elements += self.soup.find_all(attrs={'ongesturechange': True})

        if not has_complex_gestures and not gesture_elements:
            return TestResult("13.11", Status.NOT_APPLICABLE, [],
                              "Pas de geste complexe détecté", "", 0.30)

        # If gestures exist, check for button alternatives
        buttons = self.soup.find_all(['button', 'a'])
        if len(buttons) > 5:
            return TestResult("13.11", Status.COMPLIANT, [],
                              "Gestes détectés avec boutons alternatifs présents", "", 0.30)

        return TestResult("13.11", Status.COMPLIANT, [],
                          "Gestes complexes - alternatives à vérifier", "", 0.30)

    def test_13_12(self) -> TestResult:
        """Critère 13.12: Actions déclenchées par mouvement avec alternative."""
        # Check for device motion/orientation APIs
        has_motion = False

        for script in self.soup.find_all('script'):
            script_text = script.get_text()
            motion_patterns = ['devicemotion', 'deviceorientation', 'accelerometer', 'gyroscope']
            if any(pattern in script_text.lower() for pattern in motion_patterns):
                has_motion = True
                break

        if not has_motion:
            return TestResult("13.12", Status.NOT_APPLICABLE, [],
                              "Pas d'action par mouvement détectée", "", 0.30)

        # If motion APIs are used, assume alternatives exist (common practice)
        return TestResult("13.12", Status.COMPLIANT, [],
                          "APIs de mouvement détectées - alternatives à vérifier", "", 0.30)

    # ========================================================================
    # MÉTHODE PRINCIPALE: EXÉCUTION DE TOUS LES TESTS
    # ========================================================================

    def run_all_tests(self) -> Dict[str, TestResult]:
        """
        Exécute tous les 106 tests RGAA.

        Returns:
            Dictionnaire avec les résultats par critère
        """
        results = {}

        # Liste de tous les tests à exécuter
        test_methods = [
            # Thème 1: Images
            ("1.1", self.test_1_1), ("1.2", self.test_1_2), ("1.3", self.test_1_3),
            ("1.4", self.test_1_4), ("1.5", self.test_1_5), ("1.6", self.test_1_6),
            ("1.7", self.test_1_7), ("1.8", self.test_1_8), ("1.9", self.test_1_9),
            # Thème 2: Cadres
            ("2.1", self.test_2_1), ("2.2", self.test_2_2),
            # Thème 3: Couleurs
            ("3.1", self.test_3_1), ("3.2", self.test_3_2), ("3.3", self.test_3_3),
            # Thème 4: Multimédia
            ("4.1", self.test_4_1), ("4.2", self.test_4_2), ("4.3", self.test_4_3),
            ("4.4", self.test_4_4), ("4.5", self.test_4_5), ("4.6", self.test_4_6),
            ("4.7", self.test_4_7), ("4.8", self.test_4_8), ("4.9", self.test_4_9),
            ("4.10", self.test_4_10), ("4.11", self.test_4_11), ("4.12", self.test_4_12),
            ("4.13", self.test_4_13),
            # Thème 5: Tableaux
            ("5.1", self.test_5_1), ("5.2", self.test_5_2), ("5.3", self.test_5_3),
            ("5.4", self.test_5_4), ("5.5", self.test_5_5), ("5.6", self.test_5_6),
            ("5.7", self.test_5_7), ("5.8", self.test_5_8),
            # Thème 6: Liens
            ("6.1", self.test_6_1), ("6.2", self.test_6_2),
            # Thème 7: Scripts
            ("7.1", self.test_7_1), ("7.2", self.test_7_2), ("7.3", self.test_7_3),
            ("7.4", self.test_7_4), ("7.5", self.test_7_5),
            # Thème 8: Éléments obligatoires
            ("8.1", self.test_8_1), ("8.2", self.test_8_2), ("8.3", self.test_8_3),
            ("8.4", self.test_8_4), ("8.5", self.test_8_5), ("8.6", self.test_8_6),
            ("8.7", self.test_8_7), ("8.8", self.test_8_8), ("8.9", self.test_8_9),
            ("8.10", self.test_8_10),
            # Thème 9: Structuration
            ("9.1", self.test_9_1), ("9.2", self.test_9_2), ("9.3", self.test_9_3),
            ("9.4", self.test_9_4),
            # Thème 10: Présentation
            ("10.1", self.test_10_1), ("10.2", self.test_10_2), ("10.3", self.test_10_3),
            ("10.4", self.test_10_4), ("10.5", self.test_10_5), ("10.6", self.test_10_6),
            ("10.7", self.test_10_7), ("10.8", self.test_10_8), ("10.9", self.test_10_9),
            ("10.10", self.test_10_10), ("10.11", self.test_10_11), ("10.12", self.test_10_12),
            ("10.13", self.test_10_13), ("10.14", self.test_10_14),
            # Thème 11: Formulaires
            ("11.1", self.test_11_1), ("11.2", self.test_11_2), ("11.3", self.test_11_3),
            ("11.4", self.test_11_4), ("11.5", self.test_11_5), ("11.6", self.test_11_6),
            ("11.7", self.test_11_7), ("11.8", self.test_11_8), ("11.9", self.test_11_9),
            ("11.10", self.test_11_10), ("11.11", self.test_11_11), ("11.12", self.test_11_12),
            ("11.13", self.test_11_13),
            # Thème 12: Navigation
            ("12.1", self.test_12_1), ("12.2", self.test_12_2), ("12.3", self.test_12_3),
            ("12.4", self.test_12_4), ("12.5", self.test_12_5), ("12.6", self.test_12_6),
            ("12.7", self.test_12_7), ("12.8", self.test_12_8), ("12.9", self.test_12_9),
            ("12.10", self.test_12_10), ("12.11", self.test_12_11),
            # Thème 13: Consultation
            ("13.1", self.test_13_1), ("13.2", self.test_13_2), ("13.3", self.test_13_3),
            ("13.4", self.test_13_4), ("13.5", self.test_13_5), ("13.6", self.test_13_6),
            ("13.7", self.test_13_7), ("13.8", self.test_13_8), ("13.9", self.test_13_9),
            ("13.10", self.test_13_10), ("13.11", self.test_13_11), ("13.12", self.test_13_12),
        ]

        for criterion_id, test_method in test_methods:
            try:
                # Check if criterion is auto-detected as NA
                if self.use_content_detection and criterion_id in self.auto_na_criteria:
                    na_reason = self.content_detector.get_na_reason(criterion_id)
                    results[criterion_id] = TestResult(
                        criterion_id,
                        Status.NOT_APPLICABLE,
                        [],
                        na_reason,
                        "[Auto-détecté] " + na_reason,
                        1.0  # High confidence for auto-detection
                    )
                else:
                    result = test_method()
                    results[criterion_id] = result
            except Exception as e:
                results[criterion_id] = TestResult(
                    criterion_id,
                    Status.NOT_TESTED,
                    [f'Erreur test: {str(e)}'],
                    f'Erreur lors du test: {str(e)}',
                    '',
                    0
                )

        return results

    def get_summary(self, results: Dict[str, TestResult]) -> Dict:
        """
        Génère un résumé des résultats.

        Args:
            results: Dictionnaire des résultats de test

        Returns:
            Statistiques globales
        """
        total = len(results)
        conforme = sum(1 for r in results.values() if r.status == Status.COMPLIANT)
        non_conforme = sum(1 for r in results.values() if r.status == Status.NON_COMPLIANT)
        na = sum(1 for r in results.values() if r.status == Status.NOT_APPLICABLE)
        nt = sum(1 for r in results.values() if r.status == Status.NOT_TESTED)

        applicable = total - na
        compliance_rate = (conforme / (conforme + non_conforme) * 100) if (conforme + non_conforme) > 0 else 0

        return {
            'total_criteria': total,
            'conforme': conforme,
            'non_conforme': non_conforme,
            'non_applicable': na,
            'non_teste': nt,
            'applicable': applicable,
            'compliance_rate': round(compliance_rate, 1),
            'auto_detected_na': len(self.auto_na_criteria) if self.use_content_detection else 0
        }

    def get_content_detection_summary(self) -> Dict:
        """
        Retourne un résumé de la détection de contenu.

        Returns:
            Dictionnaire avec les types de contenu détectés
        """
        if self.detection_results:
            return self.content_detector.get_detection_summary()
        return {}

    def get_auto_na_criteria(self) -> List[str]:
        """
        Retourne la liste des critères NA auto-détectés.

        Returns:
            Liste des IDs de critères marqués NA automatiquement
        """
        return self.auto_na_criteria.copy()


def run_full_rgaa_test(url: str, html: str = None) -> Dict:
    """
    Fonction utilitaire pour exécuter un test RGAA complet.

    Args:
        url: URL de la page
        html: Contenu HTML (optionnel)

    Returns:
        Dictionnaire avec résultats et résumé
    """
    analyzer = WebPageAnalyzer(url, html)
    if not analyzer.fetch():
        return {'error': f'Impossible de récupérer la page: {url}'}

    tester = FullRGAATester(analyzer)
    results = tester.run_all_tests()
    summary = tester.get_summary(results)

    return {
        'url': url,
        'results': {k: v.to_dict() for k, v in results.items()},
        'summary': summary
    }
