# Claude Code Instructions: RGAA Criteria Verification Implementation

## 🚨 CRITICAL REQUIREMENT

**The application MUST actually verify each RGAA criterion against the web pages listed in the Échantillon sheet.** 

The tool is NOT just a file editor - it is an **automated accessibility auditing tool** that must:
1. Fetch each web page from the URLs in the Échantillon sheet
2. Parse the HTML content
3. Run specific tests for each of the 106 RGAA criteria
4. Update the Status column (D) based on actual test results
5. Populate the "Modifications à apporter" column (F) with specific issues found

---

## 🔧 STEP 1: Verify and Update Your Code Architecture

Before implementing tests, ensure your code has these components:

```python
# Required architecture - verify these modules exist and work correctly

# 1. Web Page Fetcher
class WebPageFetcher:
    """Fetches and caches web pages for analysis"""
    def fetch(self, url: str) -> str:
        """Returns HTML content of the page"""
        pass

# 2. HTML Parser  
class HTMLAnalyzer:
    """Parses HTML and provides query methods"""
    def __init__(self, html: str, url: str):
        self.soup = BeautifulSoup(html, 'lxml')
        self.url = url
    
    def find_all(self, tag, attrs=None) -> List:
        pass
    
    def get_frames(self) -> List[dict]:
        pass
    
    def get_images(self) -> List[dict]:
        pass
    # ... etc

# 3. Criterion Tester Base Class
class CriterionTester:
    """Base class for all criterion tests"""
    def __init__(self, analyzer: HTMLAnalyzer):
        self.analyzer = analyzer
    
    def test(self) -> TestResult:
        """Returns test result with status and details"""
        raise NotImplementedError

# 4. Test Result Structure
@dataclass
class TestResult:
    criterion_id: str
    status: str  # C, NC, NA, NT
    issues: List[str]  # List of specific issues found
    modifications: str  # Required fixes
    automated_coverage: float  # 0.0 to 1.0
```

---

## 🔍 STEP 2: Implement Verification for Each Criterion

### Theme 1: IMAGES (Critères 1.1 - 1.9)

```python
class ImageTests:
    """Tests for RGAA Image criteria"""
    
    def __init__(self, analyzer: HTMLAnalyzer):
        self.analyzer = analyzer
    
    def test_1_1(self) -> TestResult:
        """
        Critère 1.1: Chaque image porteuse d'information a-t-elle une alternative textuelle ?
        
        VERIFICATION METHOD:
        1. Find all <img> elements
        2. Find all elements with role="img"
        3. Find all <area> elements with href
        4. Find all <input type="image">
        5. Find all <svg> elements (check for role="img")
        6. Find all <canvas> elements
        7. Find all <object type="image/*">
        8. Find all <embed type="image/*">
        
        For each: Check if alt attribute exists (or aria-label, aria-labelledby, title)
        """
        issues = []
        
        # Test 1.1.1: <img> tags
        images = self.analyzer.soup.find_all('img')
        for img in images:
            if not self._has_text_alternative(img):
                src = img.get('src', 'unknown')[:50]
                issues.append(f"<img> sans alternative textuelle: {src}")
        
        # Test 1.1.2: <area> tags
        areas = self.analyzer.soup.find_all('area', href=True)
        for area in areas:
            if not area.get('alt'):
                issues.append(f"<area> sans attribut alt")
        
        # Test 1.1.3: <input type="image">
        input_images = self.analyzer.soup.find_all('input', {'type': 'image'})
        for inp in input_images:
            if not inp.get('alt'):
                issues.append(f"<input type='image'> sans alt: {inp.get('name', 'unknown')}")
        
        # Test 1.1.5: <svg> with role="img"
        svgs = self.analyzer.soup.find_all('svg')
        for svg in svgs:
            if svg.get('role') == 'img' and not self._has_text_alternative(svg):
                issues.append("<svg role='img'> sans alternative textuelle")
        
        # Determine status
        if not images and not areas and not input_images and not svgs:
            return TestResult("1.1", "NA", [], "", 0.95)
        elif issues:
            return TestResult("1.1", "NC", issues, 
                            "Ajouter des alternatives textuelles aux images", 0.95)
        else:
            return TestResult("1.1", "C", [], "", 0.95)
    
    def _has_text_alternative(self, element) -> bool:
        """Check if element has any form of text alternative"""
        # Check alt attribute
        if element.get('alt'):
            return True
        # Check aria-label
        if element.get('aria-label'):
            return True
        # Check aria-labelledby
        if element.get('aria-labelledby'):
            labelledby_id = element.get('aria-labelledby')
            referenced = self.analyzer.soup.find(id=labelledby_id)
            if referenced and referenced.get_text(strip=True):
                return True
        # Check title
        if element.get('title'):
            return True
        # For SVG, check <title> child
        if element.name == 'svg':
            title = element.find('title')
            if title and title.get_text(strip=True):
                return True
        return False
    
    def test_1_2(self) -> TestResult:
        """
        Critère 1.2: Chaque image de décoration est-elle correctement ignorée ?
        
        VERIFICATION METHOD:
        1. Find images with empty alt="" 
        2. Verify they don't have other text alternatives
        3. Check for aria-hidden="true" or role="presentation"
        
        NOTE: This requires human judgment to determine if image IS decorative.
        Automated test can only verify IMPLEMENTATION is correct IF decorative.
        """
        issues = []
        decorative_images = []
        
        # Find images that appear to be decorative (empty alt)
        images = self.analyzer.soup.find_all('img', alt='')
        for img in images:
            decorative_images.append(img)
            # Verify no other text alternative attributes
            if img.get('title'):
                issues.append(f"Image décorative avec title non vide: {img.get('src', '')[:30]}")
            if img.get('aria-label'):
                issues.append(f"Image décorative avec aria-label: {img.get('src', '')[:30]}")
            if img.get('aria-labelledby'):
                issues.append(f"Image décorative avec aria-labelledby: {img.get('src', '')[:30]}")
        
        # Check SVGs with aria-hidden
        svgs = self.analyzer.soup.find_all('svg', {'aria-hidden': 'true'})
        for svg in svgs:
            if svg.get('aria-label') or svg.get('aria-labelledby'):
                issues.append("SVG avec aria-hidden='true' mais alternative textuelle présente")
        
        if not decorative_images and not svgs:
            return TestResult("1.2", "NA", [], "", 0.70)
        elif issues:
            return TestResult("1.2", "NC", issues,
                            "Corriger les attributs des images de décoration", 0.70)
        else:
            return TestResult("1.2", "C", [], 
                            "Note: Vérification manuelle requise pour confirmer que les images sont bien décoratives", 0.70)
    
    def test_1_3(self) -> TestResult:
        """
        Critère 1.3: Alternative textuelle pertinente ?
        
        VERIFICATION METHOD:
        - Check alt text is not just filename
        - Check alt text is not too generic ("image", "photo", etc.)
        - Check alt text length (not too short, not too long)
        
        NOTE: Pertinence requires human judgment. Automated test flags suspicious cases.
        """
        issues = []
        suspicious_patterns = [
            r'^img\d*\.', r'^image\d*\.', r'^photo\d*\.',  # Filenames
            r'^image$', r'^photo$', r'^picture$', r'^img$',  # Generic
            r'^\s*$',  # Empty/whitespace
            r'^\.+$',  # Just dots
        ]
        
        images = self.analyzer.soup.find_all('img', alt=True)
        for img in images:
            alt = img.get('alt', '')
            if alt:  # Non-empty alt
                # Check for suspicious patterns
                for pattern in suspicious_patterns:
                    if re.match(pattern, alt.lower()):
                        issues.append(f"Alternative suspecte '{alt}' pour: {img.get('src', '')[:30]}")
                        break
                # Check length
                if len(alt) > 250:
                    issues.append(f"Alternative trop longue ({len(alt)} car.): {alt[:30]}...")
        
        if not images:
            return TestResult("1.3", "NA", [], "", 0.40)
        elif issues:
            return TestResult("1.3", "NC", issues,
                            "Revoir les alternatives textuelles signalées", 0.40)
        else:
            return TestResult("1.3", "C", [], 
                            "Vérification manuelle recommandée pour confirmer la pertinence", 0.40)
```

### Theme 2: CADRES (Critères 2.1 - 2.2)

```python
class FrameTests:
    """Tests for RGAA Frame criteria"""
    
    def __init__(self, analyzer: HTMLAnalyzer):
        self.analyzer = analyzer
    
    def test_2_1(self) -> TestResult:
        """
        Critère 2.1: Chaque cadre a-t-il un titre de cadre ?
        
        VERIFICATION METHOD:
        1. Find all <iframe> elements
        2. Find all <frame> elements (legacy)
        3. Check each has a title attribute
        4. Check title is not empty
        """
        issues = []
        
        # Find all frames
        iframes = self.analyzer.soup.find_all('iframe')
        frames = self.analyzer.soup.find_all('frame')
        all_frames = iframes + frames
        
        for frame in all_frames:
            tag_name = frame.name
            src = frame.get('src', 'no src')[:50]
            
            title = frame.get('title')
            if not title:
                issues.append(f"<{tag_name}> sans attribut title: src={src}")
            elif not title.strip():
                issues.append(f"<{tag_name}> avec title vide: src={src}")
        
        if not all_frames:
            return TestResult("2.1", "NA", [], "Aucun cadre présent sur la page", 0.98)
        elif issues:
            return TestResult("2.1", "NC", issues,
                            "Ajouter un attribut title à chaque iframe/frame", 0.98)
        else:
            return TestResult("2.1", "C", [], "", 0.98)
    
    def test_2_2(self) -> TestResult:
        """
        Critère 2.2: Pour chaque cadre ayant un titre, ce titre est-il pertinent ?
        
        VERIFICATION METHOD:
        1. Check title is not generic ("frame", "iframe", etc.)
        2. Check title is not just the URL
        3. Check title describes the content purpose
        
        NOTE: Full pertinence check requires human judgment.
        """
        issues = []
        suspicious_titles = [
            'iframe', 'frame', 'cadre', 'contenu', 'content',
            'untitled', 'sans titre', 'no title', '.'
        ]
        
        iframes = self.analyzer.soup.find_all('iframe', title=True)
        frames = self.analyzer.soup.find_all('frame', title=True)
        all_frames = iframes + frames
        
        for frame in all_frames:
            title = frame.get('title', '').strip().lower()
            src = frame.get('src', '')
            
            # Check for generic titles
            if title in suspicious_titles:
                issues.append(f"Titre générique '{title}' pour: {src[:30]}")
            
            # Check if title is just the URL
            if title == src.lower() or title == src.split('/')[-1].lower():
                issues.append(f"Titre = URL pour: {src[:30]}")
            
            # Check minimum length
            if len(title) < 3:
                issues.append(f"Titre trop court '{title}' pour: {src[:30]}")
        
        if not all_frames:
            return TestResult("2.2", "NA", [], "Aucun cadre avec titre", 0.35)
        elif issues:
            return TestResult("2.2", "NC", issues,
                            "Améliorer les titres des cadres pour décrire leur contenu", 0.35)
        else:
            return TestResult("2.2", "C", [], 
                            "Vérification manuelle recommandée pour confirmer la pertinence", 0.35)
```

### Theme 3: COULEURS (Critères 3.1 - 3.3)

```python
class ColorTests:
    """Tests for RGAA Color criteria"""
    
    def __init__(self, analyzer: HTMLAnalyzer):
        self.analyzer = analyzer
    
    def test_3_1(self) -> TestResult:
        """
        Critère 3.1: L'information n'est pas donnée uniquement par la couleur
        
        VERIFICATION METHOD:
        1. Find elements with color-related CSS only (no other indicator)
        2. Check form error messages have icons/text, not just red color
        3. Check links are underlined or have other visual indicator
        4. Check required fields have * or text, not just color
        
        NOTE: This requires visual/contextual analysis - limited automation.
        """
        issues = []
        warnings = []
        
        # Check links - should be underlined or have other indicator
        links = self.analyzer.soup.find_all('a', href=True)
        # This needs CSS analysis which is complex
        
        # Check for required field indicators
        required_inputs = self.analyzer.soup.find_all(['input', 'select', 'textarea'], required=True)
        for inp in required_inputs:
            # Check if there's a visible indicator near the field
            label = self.analyzer.soup.find('label', {'for': inp.get('id')})
            if label:
                label_text = label.get_text()
                if '*' not in label_text and 'obligatoire' not in label_text.lower() and 'required' not in label_text.lower():
                    warnings.append(f"Champ requis sans indicateur visible: {inp.get('name', inp.get('id', 'unknown'))}")
        
        # Check error messages
        error_elements = self.analyzer.soup.find_all(class_=re.compile(r'error|erreur|invalid', re.I))
        for err in error_elements:
            # Check if error has icon or text indicator
            if not err.find(['svg', 'img', 'i']) and len(err.get_text(strip=True)) < 3:
                warnings.append(f"Message d'erreur potentiellement indiqué uniquement par couleur")
        
        # This criterion is hard to fully automate
        return TestResult("3.1", "NT", warnings,
                        "Vérification manuelle requise: s'assurer que l'information n'est pas véhiculée uniquement par la couleur", 0.25)
    
    def test_3_2(self) -> TestResult:
        """
        Critère 3.2: Contraste texte/fond suffisant (4.5:1 minimum, 3:1 pour grands textes)
        
        VERIFICATION METHOD:
        1. Extract all text elements
        2. Get computed background color
        3. Get text color
        4. Calculate contrast ratio
        5. Compare to WCAG thresholds
        
        NOTE: Requires rendering engine or CSS computation. Limited in static analysis.
        """
        issues = []
        
        # This requires CSS computation which is complex
        # We can flag inline styles that might have issues
        
        elements_with_color = self.analyzer.soup.find_all(style=re.compile(r'color:', re.I))
        for el in elements_with_color:
            style = el.get('style', '')
            # Extract colors from inline style
            # This is a simplified check
            if 'color:' in style.lower():
                issues.append(f"Style inline avec couleur - vérifier le contraste: {el.name}")
        
        return TestResult("3.2", "NT", issues,
                        "Utiliser un outil de vérification de contraste (Colour Contrast Analyser, axe, etc.)", 0.20)
    
    def test_3_3(self) -> TestResult:
        """
        Critère 3.3: Contraste des composants d'interface (3:1 minimum)
        
        Similar to 3.2 but for UI components like buttons, form fields, etc.
        """
        return TestResult("3.3", "NT", [],
                        "Vérification manuelle requise avec outil de contraste", 0.15)
```

### Theme 4: MULTIMÉDIA (Critères 4.1 - 4.13)

```python
class MultimediaTests:
    """Tests for RGAA Multimedia criteria"""
    
    def __init__(self, analyzer: HTMLAnalyzer):
        self.analyzer = analyzer
    
    def test_4_1(self) -> TestResult:
        """
        Critère 4.1: Média temporel a transcription ou audiodescription
        
        VERIFICATION METHOD:
        1. Find <audio> and <video> elements
        2. Check for adjacent transcript link/content
        3. Check for <track> elements with kind="descriptions"
        """
        issues = []
        
        videos = self.analyzer.soup.find_all('video')
        audios = self.analyzer.soup.find_all('audio')
        media_objects = self.analyzer.soup.find_all('object', type=re.compile(r'video|audio', re.I))
        
        all_media = videos + audios + media_objects
        
        for media in all_media:
            src = media.get('src', media.find('source').get('src') if media.find('source') else 'unknown')
            
            # Check for <track> with captions or descriptions
            tracks = media.find_all('track')
            has_transcript = any(t.get('kind') in ['captions', 'descriptions', 'subtitles'] for t in tracks)
            
            # Check for adjacent transcript link
            parent = media.parent
            transcript_link = parent.find('a', string=re.compile(r'transcript|transcription', re.I)) if parent else None
            
            if not has_transcript and not transcript_link:
                issues.append(f"Média sans transcription/audiodescription: {src[:50]}")
        
        if not all_media:
            return TestResult("4.1", "NA", [], "Aucun média temporel détecté", 0.80)
        elif issues:
            return TestResult("4.1", "NC", issues,
                            "Ajouter transcription textuelle ou audiodescription", 0.80)
        else:
            return TestResult("4.1", "C", [], "", 0.80)
    
    def test_4_3(self) -> TestResult:
        """
        Critère 4.3: Sous-titres synchronisés pour vidéos
        
        VERIFICATION METHOD:
        1. Find <video> elements
        2. Check for <track kind="captions"> or <track kind="subtitles">
        """
        issues = []
        
        videos = self.analyzer.soup.find_all('video')
        
        for video in videos:
            src = video.get('src', '')
            if not src:
                source = video.find('source')
                src = source.get('src', 'unknown') if source else 'unknown'
            
            # Check for caption track
            tracks = video.find_all('track')
            has_captions = any(t.get('kind') == 'captions' for t in tracks)
            
            if not has_captions:
                issues.append(f"Vidéo sans sous-titres: {src[:50]}")
        
        if not videos:
            return TestResult("4.3", "NA", [], "Aucune vidéo détectée", 0.90)
        elif issues:
            return TestResult("4.3", "NC", issues,
                            "Ajouter <track kind='captions'> aux vidéos", 0.90)
        else:
            return TestResult("4.3", "C", [], "", 0.90)
    
    def test_4_10(self) -> TestResult:
        """
        Critère 4.10: Son déclenché automatiquement contrôlable
        
        VERIFICATION METHOD:
        1. Find <audio> and <video> with autoplay
        2. Check they have controls or muted attribute
        """
        issues = []
        
        autoplay_media = self.analyzer.soup.find_all(['audio', 'video'], autoplay=True)
        
        for media in autoplay_media:
            has_controls = media.has_attr('controls')
            is_muted = media.has_attr('muted')
            
            if not has_controls and not is_muted:
                src = media.get('src', 'unknown')[:50]
                issues.append(f"Média autoplay sans contrôles ni muted: {src}")
        
        if not autoplay_media:
            return TestResult("4.10", "NA", [], "Aucun média en autoplay", 0.95)
        elif issues:
            return TestResult("4.10", "NC", issues,
                            "Ajouter controls ou muted aux médias autoplay", 0.95)
        else:
            return TestResult("4.10", "C", [], "", 0.95)
```

### Theme 5: TABLEAUX (Critères 5.1 - 5.8)

```python
class TableTests:
    """Tests for RGAA Table criteria"""
    
    def __init__(self, analyzer: HTMLAnalyzer):
        self.analyzer = analyzer
    
    def test_5_3(self) -> TestResult:
        """
        Critère 5.3: Tableau de mise en forme - contenu linéarisé compréhensible
        
        VERIFICATION METHOD:
        1. Find tables with role="presentation" or without <th>
        2. These are layout tables
        3. Check they have role="presentation"
        """
        issues = []
        
        tables = self.analyzer.soup.find_all('table')
        
        for table in tables:
            has_headers = table.find('th') is not None
            has_caption = table.find('caption') is not None
            role = table.get('role', '')
            
            # Heuristic: table without headers might be layout table
            if not has_headers and not has_caption:
                if role != 'presentation':
                    issues.append("Tableau potentiel de mise en forme sans role='presentation'")
        
        if not tables:
            return TestResult("5.3", "NA", [], "Aucun tableau", 0.70)
        elif issues:
            return TestResult("5.3", "NC", issues,
                            "Ajouter role='presentation' aux tableaux de mise en forme", 0.70)
        else:
            return TestResult("5.3", "C", [], "", 0.70)
    
    def test_5_6(self) -> TestResult:
        """
        Critère 5.6: En-têtes de tableau correctement déclarés
        
        VERIFICATION METHOD:
        1. Find data tables (with <th> or <caption>)
        2. Check <th> elements have scope attribute
        3. Or check headers/id associations
        """
        issues = []
        
        tables = self.analyzer.soup.find_all('table')
        
        for i, table in enumerate(tables):
            if table.get('role') == 'presentation':
                continue  # Skip layout tables
            
            headers = table.find_all('th')
            if headers:
                for th in headers:
                    scope = th.get('scope')
                    th_id = th.get('id')
                    
                    if not scope and not th_id:
                        issues.append(f"Tableau {i+1}: <th> sans scope ni id: '{th.get_text()[:20]}'")
        
        data_tables = [t for t in tables if t.get('role') != 'presentation' and t.find('th')]
        
        if not data_tables:
            return TestResult("5.6", "NA", [], "Aucun tableau de données", 0.85)
        elif issues:
            return TestResult("5.6", "NC", issues,
                            "Ajouter scope='col' ou scope='row' aux cellules d'en-tête", 0.85)
        else:
            return TestResult("5.6", "C", [], "", 0.85)
```

### Theme 6: LIENS (Critères 6.1 - 6.2)

```python
class LinkTests:
    """Tests for RGAA Link criteria"""
    
    def __init__(self, analyzer: HTMLAnalyzer):
        self.analyzer = analyzer
    
    def test_6_1(self) -> TestResult:
        """
        Critère 6.1: Chaque lien est-il explicite ?
        
        VERIFICATION METHOD:
        1. Find all <a> elements with href
        2. Check link text is not generic ("click here", "read more", etc.)
        3. Check link has meaningful text or aria-label
        4. Check image links have alt text
        """
        issues = []
        generic_texts = [
            'cliquez ici', 'click here', 'ici', 'here', 'lire la suite', 'read more',
            'en savoir plus', 'learn more', 'plus', 'more', 'lien', 'link',
            'cliquer', 'click', '>', '>>', '...', 'suite', 'voir', 'see'
        ]
        
        links = self.analyzer.soup.find_all('a', href=True)
        
        for link in links:
            # Get accessible name
            aria_label = link.get('aria-label', '')
            aria_labelledby = link.get('aria-labelledby', '')
            link_text = link.get_text(strip=True)
            
            # Check for image-only links
            img = link.find('img')
            if img and not link_text:
                img_alt = img.get('alt', '')
                if not img_alt and not aria_label:
                    issues.append(f"Lien image sans alternative: href={link.get('href', '')[:30]}")
                    continue
                link_text = img_alt
            
            # Get effective text
            effective_text = aria_label or link_text
            
            if not effective_text:
                issues.append(f"Lien sans intitulé: href={link.get('href', '')[:30]}")
            elif effective_text.lower().strip() in generic_texts:
                issues.append(f"Lien générique '{effective_text}': href={link.get('href', '')[:30]}")
        
        if not links:
            return TestResult("6.1", "NA", [], "Aucun lien", 0.75)
        elif issues:
            return TestResult("6.1", "NC", issues,
                            "Rendre les intitulés de liens explicites", 0.75)
        else:
            return TestResult("6.1", "C", [], "", 0.75)
    
    def test_6_2(self) -> TestResult:
        """
        Critère 6.2: Chaque lien a-t-il un intitulé ?
        
        VERIFICATION METHOD:
        1. Find all <a> elements
        2. Check they have text content, aria-label, or contain image with alt
        """
        issues = []
        
        links = self.analyzer.soup.find_all('a', href=True)
        
        for link in links:
            has_text = bool(link.get_text(strip=True))
            has_aria_label = bool(link.get('aria-label', '').strip())
            has_aria_labelledby = bool(link.get('aria-labelledby', '').strip())
            has_title = bool(link.get('title', '').strip())
            
            # Check for image with alt
            img = link.find('img')
            has_img_alt = img and bool(img.get('alt', '').strip()) if img else False
            
            if not any([has_text, has_aria_label, has_aria_labelledby, has_title, has_img_alt]):
                issues.append(f"Lien sans intitulé: href={link.get('href', '')[:40]}")
        
        if not links:
            return TestResult("6.2", "NA", [], "Aucun lien", 0.95)
        elif issues:
            return TestResult("6.2", "NC", issues,
                            "Ajouter un intitulé à chaque lien", 0.95)
        else:
            return TestResult("6.2", "C", [], "", 0.95)
```

### Theme 7: SCRIPTS (Critères 7.1 - 7.5)

```python
class ScriptTests:
    """Tests for RGAA Script/JavaScript criteria"""
    
    def __init__(self, analyzer: HTMLAnalyzer):
        self.analyzer = analyzer
    
    def test_7_1(self) -> TestResult:
        """
        Critère 7.1: Scripts compatibles avec technologies d'assistance
        
        VERIFICATION METHOD:
        1. Find interactive elements created by JS (role attributes)
        2. Check ARIA roles have required attributes
        3. Check custom widgets follow ARIA patterns
        """
        issues = []
        
        # Check elements with ARIA roles
        role_elements = self.analyzer.soup.find_all(attrs={'role': True})
        
        aria_required_attrs = {
            'slider': ['aria-valuenow', 'aria-valuemin', 'aria-valuemax'],
            'progressbar': ['aria-valuenow'],
            'checkbox': ['aria-checked'],
            'radio': ['aria-checked'],
            'switch': ['aria-checked'],
            'combobox': ['aria-expanded'],
            'tab': ['aria-selected'],
            'tabpanel': ['aria-labelledby'],
            'dialog': ['aria-labelledby'],
            'alertdialog': ['aria-labelledby'],
            'menu': [],
            'menuitem': [],
            'tree': [],
            'treeitem': ['aria-expanded'],
        }
        
        for el in role_elements:
            role = el.get('role', '')
            if role in aria_required_attrs:
                required = aria_required_attrs[role]
                for attr in required:
                    if not el.get(attr):
                        issues.append(f"Élément role='{role}' sans {attr}")
        
        # Check for onclick on non-interactive elements
        onclick_elements = self.analyzer.soup.find_all(attrs={'onclick': True})
        for el in onclick_elements:
            if el.name not in ['a', 'button', 'input', 'select', 'textarea']:
                if not el.get('tabindex') and not el.get('role'):
                    issues.append(f"<{el.name}> avec onclick mais sans tabindex ni role")
        
        if not role_elements and not onclick_elements:
            return TestResult("7.1", "NA", [], "Aucun composant JavaScript détecté", 0.60)
        elif issues:
            return TestResult("7.1", "NC", issues,
                            "Corriger les attributs ARIA des composants", 0.60)
        else:
            return TestResult("7.1", "C", [], 
                            "Vérification manuelle recommandée avec lecteur d'écran", 0.60)
    
    def test_7_3(self) -> TestResult:
        """
        Critère 7.3: Scripts contrôlables au clavier
        
        VERIFICATION METHOD:
        1. Find elements with mouse-only events (onmouseover, onclick on div/span)
        2. Check they have keyboard equivalents (onkeydown, onfocus)
        3. Check interactive elements are focusable
        """
        issues = []
        
        mouse_events = ['onclick', 'onmouseover', 'onmouseout', 'onmousedown', 'onmouseup', 'ondblclick']
        keyboard_events = ['onkeydown', 'onkeyup', 'onkeypress', 'onfocus', 'onblur']
        
        for event in mouse_events:
            elements = self.analyzer.soup.find_all(attrs={event: True})
            for el in elements:
                # Non-interactive elements
                if el.name not in ['a', 'button', 'input', 'select', 'textarea', 'summary']:
                    has_keyboard = any(el.get(ke) for ke in keyboard_events)
                    has_tabindex = el.get('tabindex') is not None
                    has_role = el.get('role') in ['button', 'link', 'checkbox', 'menuitem', 'tab']
                    
                    if not has_keyboard and not (has_tabindex and has_role):
                        issues.append(f"<{el.name}> avec {event} non accessible au clavier")
        
        if not issues:
            # Check for tabindex=-1 that might trap focus
            negative_tabindex = self.analyzer.soup.find_all(attrs={'tabindex': '-1'})
            for el in negative_tabindex:
                if el.name in ['a', 'button', 'input']:
                    issues.append(f"<{el.name}> interactif avec tabindex='-1' (potentiel piège clavier)")
        
        return TestResult("7.3", "NT" if not issues else "NC", issues,
                        "Vérification manuelle requise: tester la navigation clavier", 0.50)
```

### Theme 8: ÉLÉMENTS OBLIGATOIRES (Critères 8.1 - 8.10)

```python
class MandatoryElementsTests:
    """Tests for RGAA Mandatory Elements criteria"""
    
    def __init__(self, analyzer: HTMLAnalyzer):
        self.analyzer = analyzer
    
    def test_8_1(self) -> TestResult:
        """
        Critère 8.1: Page définie par un type de document ?
        
        VERIFICATION METHOD:
        1. Check for DOCTYPE declaration at start of document
        """
        issues = []
        
        # Get raw HTML and check for DOCTYPE
        html_str = str(self.analyzer.soup)
        if not html_str.strip().lower().startswith('<!doctype'):
            # Check original HTML (BeautifulSoup may modify)
            issues.append("Déclaration DOCTYPE absente ou mal placée")
        
        if issues:
            return TestResult("8.1", "NC", issues,
                            "Ajouter <!DOCTYPE html> en début de document", 0.95)
        else:
            return TestResult("8.1", "C", [], "", 0.95)
    
    def test_8_3(self) -> TestResult:
        """
        Critère 8.3: Langue par défaut présente ?
        
        VERIFICATION METHOD:
        1. Check <html> has lang attribute
        """
        issues = []
        
        html_tag = self.analyzer.soup.find('html')
        if html_tag:
            lang = html_tag.get('lang') or html_tag.get('xml:lang')
            if not lang:
                issues.append("Attribut lang absent sur <html>")
        else:
            issues.append("Balise <html> non trouvée")
        
        if issues:
            return TestResult("8.3", "NC", issues,
                            "Ajouter lang='fr' (ou autre) sur <html>", 0.98)
        else:
            return TestResult("8.3", "C", [], "", 0.98)
    
    def test_8_4(self) -> TestResult:
        """
        Critère 8.4: Code de langue pertinent ?
        
        VERIFICATION METHOD:
        1. Check lang attribute value is valid ISO 639 code
        2. Check it matches page content language
        """
        issues = []
        valid_lang_codes = ['fr', 'en', 'de', 'es', 'it', 'pt', 'nl', 'pl', 'ru', 'zh', 'ja', 'ar', 'ko']
        
        html_tag = self.analyzer.soup.find('html')
        if html_tag:
            lang = html_tag.get('lang', '')
            lang_code = lang.split('-')[0].lower() if lang else ''
            
            if not lang_code:
                return TestResult("8.4", "NA", [], "Pas d'attribut lang", 0.90)
            
            if lang_code not in valid_lang_codes and len(lang_code) not in [2, 3]:
                issues.append(f"Code de langue invalide: '{lang}'")
        
        if issues:
            return TestResult("8.4", "NC", issues,
                            "Utiliser un code de langue ISO 639 valide", 0.90)
        else:
            return TestResult("8.4", "C", [], "", 0.90)
    
    def test_8_5(self) -> TestResult:
        """
        Critère 8.5: Page a un titre ?
        
        VERIFICATION METHOD:
        1. Check <title> element exists in <head>
        2. Check it has content
        """
        issues = []
        
        title = self.analyzer.soup.find('title')
        if not title:
            issues.append("Balise <title> absente")
        elif not title.get_text(strip=True):
            issues.append("Balise <title> vide")
        
        if issues:
            return TestResult("8.5", "NC", issues,
                            "Ajouter un titre de page dans <title>", 0.98)
        else:
            return TestResult("8.5", "C", [], "", 0.98)
    
    def test_8_6(self) -> TestResult:
        """
        Critère 8.6: Titre de page pertinent ?
        
        VERIFICATION METHOD:
        1. Check title is not generic
        2. Check title is not too long
        3. Check title contains meaningful content
        """
        issues = []
        generic_titles = ['home', 'accueil', 'untitled', 'sans titre', 'page', 'document', 'index']
        
        title = self.analyzer.soup.find('title')
        if title:
            title_text = title.get_text(strip=True)
            
            if title_text.lower() in generic_titles:
                issues.append(f"Titre générique: '{title_text}'")
            elif len(title_text) < 3:
                issues.append(f"Titre trop court: '{title_text}'")
            elif len(title_text) > 100:
                issues.append(f"Titre très long ({len(title_text)} car.)")
        else:
            return TestResult("8.6", "NA", [], "Pas de titre", 0.80)
        
        if issues:
            return TestResult("8.6", "NC", issues,
                            "Améliorer le titre de la page", 0.80)
        else:
            return TestResult("8.6", "C", [], "", 0.80)
    
    def test_8_9(self) -> TestResult:
        """
        Critère 8.9: Balises utilisées à des fins de présentation ?
        
        VERIFICATION METHOD:
        1. Check for deprecated presentational elements
        2. Check for misuse of semantic elements
        """
        issues = []
        
        # Deprecated/presentational elements
        bad_elements = ['center', 'font', 'marquee', 'blink', 'big', 'strike', 's', 'u', 'tt']
        
        for tag in bad_elements:
            found = self.analyzer.soup.find_all(tag)
            if found:
                issues.append(f"Élément de présentation interdit: <{tag}> ({len(found)} occurrence(s))")
        
        # Check for potential misuse of blockquote for indentation
        blockquotes = self.analyzer.soup.find_all('blockquote')
        for bq in blockquotes:
            if not bq.get('cite') and len(bq.get_text(strip=True)) < 20:
                issues.append("Utilisation suspecte de <blockquote> (peut-être pour indentation)")
        
        if issues:
            return TestResult("8.9", "NC", issues,
                            "Remplacer les éléments de présentation par du CSS", 0.90)
        else:
            return TestResult("8.9", "C", [], "", 0.90)
```

### Theme 9: STRUCTURATION (Critères 9.1 - 9.4)

```python
class StructureTests:
    """Tests for RGAA Structure criteria"""
    
    def __init__(self, analyzer: HTMLAnalyzer):
        self.analyzer = analyzer
    
    def test_9_1(self) -> TestResult:
        """
        Critère 9.1: Information structurée par titres appropriés
        
        VERIFICATION METHOD:
        1. Check page has headings (h1-h6)
        2. Check heading hierarchy is logical
        3. Check no skipped levels
        """
        issues = []
        
        headings = []
        for level in range(1, 7):
            for h in self.analyzer.soup.find_all(f'h{level}'):
                headings.append((level, h.get_text(strip=True)[:50]))
        
        # Also check role="heading"
        role_headings = self.analyzer.soup.find_all(attrs={'role': 'heading'})
        for h in role_headings:
            level = int(h.get('aria-level', 2))
            headings.append((level, h.get_text(strip=True)[:50]))
        
        if not headings:
            issues.append("Aucun titre (h1-h6) sur la page")
        else:
            # Check for h1
            h1_count = sum(1 for h in headings if h[0] == 1)
            if h1_count == 0:
                issues.append("Aucun titre <h1> sur la page")
            elif h1_count > 1:
                issues.append(f"Plusieurs titres <h1> ({h1_count})")
            
            # Check hierarchy
            prev_level = 0
            for level, text in headings:
                if level > prev_level + 1 and prev_level > 0:
                    issues.append(f"Saut de niveau: h{prev_level} -> h{level} ('{text}')")
                prev_level = level
        
        if issues:
            return TestResult("9.1", "NC", issues,
                            "Corriger la hiérarchie des titres", 0.90)
        else:
            return TestResult("9.1", "C", [], "", 0.90)
    
    def test_9_2(self) -> TestResult:
        """
        Critère 9.2: Structure du document cohérente (landmarks HTML5)
        
        VERIFICATION METHOD:
        1. Check for <header>, <nav>, <main>, <footer>
        2. Check <main> is unique and visible
        3. Check structure makes sense
        """
        issues = []
        
        # Check for main landmarks
        header = self.analyzer.soup.find('header')
        nav = self.analyzer.soup.find('nav')
        main = self.analyzer.soup.find('main')
        footer = self.analyzer.soup.find('footer')
        
        if not main:
            # Check for role="main"
            main = self.analyzer.soup.find(attrs={'role': 'main'})
        
        if not main:
            issues.append("Aucun élément <main> ou role='main'")
        else:
            # Check uniqueness
            all_mains = self.analyzer.soup.find_all('main') + self.analyzer.soup.find_all(attrs={'role': 'main'})
            visible_mains = [m for m in all_mains if not m.get('hidden') and m.get('aria-hidden') != 'true']
            if len(visible_mains) > 1:
                issues.append(f"Plusieurs <main> visibles ({len(visible_mains)})")
        
        if not header and not self.analyzer.soup.find(attrs={'role': 'banner'}):
            issues.append("Aucun élément <header> ou role='banner'")
        
        if not nav and not self.analyzer.soup.find(attrs={'role': 'navigation'}):
            issues.append("Aucun élément <nav> ou role='navigation'")
        
        if not footer and not self.analyzer.soup.find(attrs={'role': 'contentinfo'}):
            issues.append("Aucun élément <footer> ou role='contentinfo'")
        
        if issues:
            return TestResult("9.2", "NC", issues,
                            "Ajouter les landmarks HTML5 manquants", 0.85)
        else:
            return TestResult("9.2", "C", [], "", 0.85)
    
    def test_9_3(self) -> TestResult:
        """
        Critère 9.3: Listes correctement structurées
        
        VERIFICATION METHOD:
        1. Find visual lists (items with bullets/numbers)
        2. Check they use <ul>, <ol>, or <dl>
        3. Check list structure is valid
        """
        issues = []
        
        # Check list structure
        uls = self.analyzer.soup.find_all('ul')
        ols = self.analyzer.soup.find_all('ol')
        dls = self.analyzer.soup.find_all('dl')
        
        for ul in uls:
            # Check children are li
            non_li = [child for child in ul.children if child.name and child.name != 'li' and child.name not in ['script', 'template']]
            if non_li:
                issues.append(f"<ul> contient des éléments non-<li>: {[c.name for c in non_li]}")
        
        for ol in ols:
            non_li = [child for child in ol.children if child.name and child.name != 'li' and child.name not in ['script', 'template']]
            if non_li:
                issues.append(f"<ol> contient des éléments non-<li>")
        
        for dl in dls:
            valid_children = ['dt', 'dd', 'div', 'script', 'template']
            non_valid = [child for child in dl.children if child.name and child.name not in valid_children]
            if non_valid:
                issues.append(f"<dl> contient des éléments invalides")
        
        # Check for role="list"
        role_lists = self.analyzer.soup.find_all(attrs={'role': 'list'})
        for lst in role_lists:
            listitems = lst.find_all(attrs={'role': 'listitem'})
            if not listitems:
                issues.append("Élément role='list' sans role='listitem'")
        
        if not uls and not ols and not dls and not role_lists:
            return TestResult("9.3", "NA", [], "Aucune liste détectée", 0.80)
        elif issues:
            return TestResult("9.3", "NC", issues,
                            "Corriger la structure des listes", 0.80)
        else:
            return TestResult("9.3", "C", [], "", 0.80)
```

---

## 📋 COMPLETE TEST RUNNER

```python
class RGAATestRunner:
    """Runs all RGAA criteria tests on a page"""
    
    def __init__(self, html_content: str, url: str):
        self.analyzer = HTMLAnalyzer(html_content, url)
        
        # Initialize all test classes
        self.image_tests = ImageTests(self.analyzer)
        self.frame_tests = FrameTests(self.analyzer)
        self.color_tests = ColorTests(self.analyzer)
        self.multimedia_tests = MultimediaTests(self.analyzer)
        self.table_tests = TableTests(self.analyzer)
        self.link_tests = LinkTests(self.analyzer)
        self.script_tests = ScriptTests(self.analyzer)
        self.mandatory_tests = MandatoryElementsTests(self.analyzer)
        self.structure_tests = StructureTests(self.analyzer)
        # Add remaining test classes...
    
    def run_all_tests(self) -> Dict[str, TestResult]:
        """Run all 106 criteria tests and return results"""
        results = {}
        
        # Theme 1: Images
        results["1.1"] = self.image_tests.test_1_1()
        results["1.2"] = self.image_tests.test_1_2()
        results["1.3"] = self.image_tests.test_1_3()
        # ... continue for 1.4-1.9
        
        # Theme 2: Cadres
        results["2.1"] = self.frame_tests.test_2_1()
        results["2.2"] = self.frame_tests.test_2_2()
        
        # Theme 3: Couleurs
        results["3.1"] = self.color_tests.test_3_1()
        results["3.2"] = self.color_tests.test_3_2()
        results["3.3"] = self.color_tests.test_3_3()
        
        # ... continue for all 106 criteria
        
        return results
    
    def get_automated_coverage_report(self) -> Dict:
        """Return report of what can be automated vs manual"""
        results = self.run_all_tests()
        
        fully_automated = []  # >80% coverage
        partially_automated = []  # 30-80% coverage
        manual_required = []  # <30% coverage
        
        for criterion_id, result in results.items():
            if result.automated_coverage >= 0.8:
                fully_automated.append(criterion_id)
            elif result.automated_coverage >= 0.3:
                partially_automated.append(criterion_id)
            else:
                manual_required.append(criterion_id)
        
        return {
            "fully_automated": fully_automated,
            "partially_automated": partially_automated,
            "manual_required": manual_required,
            "total_automated_coverage": sum(r.automated_coverage for r in results.values()) / len(results)
        }
```

---

## ⚠️ VERIFICATION CHECKLIST FOR CLAUDE CODE

Before considering the implementation complete, verify:

- [ ] **Each criterion has a test method** that actually analyzes HTML
- [ ] **Tests fetch real web pages** from URLs in Échantillon sheet
- [ ] **Tests examine actual DOM elements** (not just file structure)
- [ ] **Status values are based on test results**, not pre-filled
- [ ] **Modifications column is populated** with specific issues found
- [ ] **Coverage percentages are accurate** for each criterion
- [ ] **Manual verification notes are added** where automation is limited
- [ ] **All 106 criteria are implemented** (even if some are NT due to complexity)

---

## 🔄 EXPECTED WORKFLOW

```
1. Load grilleAudit.ods
2. Parse Échantillon to get list of pages (P01-P20) with URLs
3. FOR EACH PAGE where URL is valid (not "Absente"):
   a. Fetch HTML content from URL
   b. Parse HTML with BeautifulSoup
   c. Run all 106 criterion tests
   d. For each criterion:
      - Set Status (C/NC/NA/NT) based on test result
      - Populate "Modifications à apporter" with issues list
      - Add comments about automation coverage
   e. Update the P## sheet in the ODS file
4. Save updated ODS file
5. Generate summary report showing:
   - Overall compliance rate
   - Breakdown by theme
   - List of issues requiring manual review
```

---

## 📊 EXPECTED OUTPUT EXAMPLE

After running analysis on P01 (Accueil - https://www.isit.fr/fr/):

| Critère | Statut | Modifications à apporter |
|---------|--------|-------------------------|
| 1.1 | NC | 3 images sans alternative textuelle: logo.png, banner.jpg, icon-menu.svg |
| 2.1 | C | |
| 2.2 | C | |
| 8.3 | C | |
| 8.5 | C | |
| 9.1 | NC | Saut de niveau h1 -> h3, aucun h2 |
| ... | ... | ... |
