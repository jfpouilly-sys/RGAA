# INSTRUCTIONS OBLIGATOIRES POUR CLAUDE CODE
## Vérification RGAA 4.1.2 - Audit Automatisé des Pages Web

---

## ⚠️ EXIGENCE CRITIQUE

**L'application DOIT VÉRIFIER RÉELLEMENT chaque critère RGAA sur les pages web.**

Claude Code ne doit PAS simplement manipuler le fichier ODS. Il DOIT :
1. **Récupérer le contenu HTML** de chaque URL listée dans l'onglet "Échantillon"
2. **Analyser le DOM** pour chaque critère RGAA
3. **Déterminer le statut** (C/NC/NA) basé sur l'analyse réelle
4. **Documenter les problèmes** trouvés dans la colonne "Modifications à apporter"

---

## ARCHITECTURE REQUISE

### Module de Récupération Web
```python
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re

class WebPageAnalyzer:
    def __init__(self, url: str):
        self.url = url
        self.html = None
        self.soup = None
        self.css_content = []
        
    def fetch(self) -> bool:
        """Récupère la page web et parse le HTML"""
        try:
            headers = {'User-Agent': 'RGAA-Auditor/1.0'}
            response = requests.get(self.url, headers=headers, timeout=30)
            response.raise_for_status()
            self.html = response.text
            self.soup = BeautifulSoup(self.html, 'lxml')
            return True
        except Exception as e:
            print(f"Erreur récupération {self.url}: {e}")
            return False
```

---

## VÉRIFICATION CRITÈRE PAR CRITÈRE

### THÈME 1 : IMAGES (Critères 1.1 à 1.9)

#### Critère 1.1 - Alternative textuelle des images porteuses d'information
```python
def test_1_1(self) -> dict:
    """Chaque image porteuse d'information a-t-elle une alternative textuelle ?"""
    issues = []
    
    # Test 1.1.1 - Balises <img> et role="img"
    images = self.soup.find_all('img')
    images += self.soup.find_all(attrs={'role': 'img'})
    
    for img in images:
        # Ignorer les images de décoration (alt="" sans autres attributs)
        if img.get('alt') == '' and not img.get('aria-label') and not img.get('aria-labelledby'):
            continue  # Image de décoration, OK
            
        # Vérifier présence alternative
        has_alt = img.get('alt') is not None and img.get('alt').strip() != ''
        has_aria_label = img.get('aria-label') is not None
        has_aria_labelledby = img.get('aria-labelledby') is not None
        has_title = img.get('title') is not None
        
        if not (has_alt or has_aria_label or has_aria_labelledby or has_title):
            src = img.get('src', 'source inconnue')
            issues.append(f"Image sans alternative: {src[:50]}")
    
    # Test 1.1.2 - Zones cliquables <area>
    areas = self.soup.find_all('area', href=True)
    for area in areas:
        if not area.get('alt'):
            issues.append(f"Zone cliquable sans alt: {area.get('href', '')[:30]}")
    
    # Test 1.1.3 - Boutons image <input type="image">
    input_images = self.soup.find_all('input', type='image')
    for inp in input_images:
        if not inp.get('alt'):
            issues.append(f"Bouton image sans alt: {inp.get('name', 'inconnu')}")
    
    # Test 1.1.5 - SVG avec role="img"
    svgs = self.soup.find_all('svg')
    for svg in svgs:
        if svg.get('role') == 'img':
            has_label = svg.get('aria-label') or svg.get('aria-labelledby')
            title_tag = svg.find('title')
            if not has_label and not title_tag:
                issues.append("SVG role=img sans alternative textuelle")
    
    # Test 1.1.6 - Objects image
    objects = self.soup.find_all('object', type=re.compile(r'image/'))
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
    
    return {
        'status': 'C' if not issues else 'NC',
        'issues': issues,
        'modifications': '; '.join(issues) if issues else '',
        'automated_coverage': 0.95
    }
```

#### Critère 1.2 - Images de décoration ignorées
```python
def test_1_2(self) -> dict:
    """Chaque image de décoration est-elle correctement ignorée ?"""
    issues = []
    
    # Chercher les images potentiellement décoratives mal configurées
    images = self.soup.find_all('img')
    
    for img in images:
        alt = img.get('alt')
        aria_hidden = img.get('aria-hidden')
        role = img.get('role')
        
        # Image avec alt="" mais avec d'autres attributs de labellisation
        if alt == '':
            if img.get('aria-label') or img.get('aria-labelledby') or img.get('title'):
                src = img.get('src', '')[:30]
                issues.append(f"Image déco avec attributs contradictoires: {src}")
        
        # Image avec role="presentation" doit avoir alt="" ou aria-hidden
        if role == 'presentation' and alt != '' and alt is not None:
            issues.append(f"role=presentation mais alt non vide")
    
    # SVG décoratifs
    svgs = self.soup.find_all('svg')
    for svg in svgs:
        if svg.get('aria-hidden') != 'true':
            # Vérifier si c'est décoratif (pas de texte, petit, etc.)
            if not svg.find('title') and not svg.get('aria-label'):
                # Potentiellement décoratif sans aria-hidden
                pass  # Nécessite vérification manuelle
    
    return {
        'status': 'C' if not issues else 'NC',
        'issues': issues,
        'modifications': '; '.join(issues),
        'automated_coverage': 0.70,
        'manual_check': "Vérifier visuellement si les images sans alt sont bien décoratives"
    }
```

#### Critère 1.3 - Pertinence des alternatives
```python
def test_1_3(self) -> dict:
    """L'alternative textuelle est-elle pertinente ?"""
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
        r'^\.{3,}$',  # Points de suspension seuls
    ]
    
    images = self.soup.find_all('img', alt=True)
    
    for img in images:
        alt = img.get('alt', '').strip()
        if not alt:
            continue  # Image déco, pas concernée
            
        # Vérifier patterns suspects
        for pattern in suspicious_patterns:
            if re.match(pattern, alt, re.IGNORECASE):
                issues.append(f"Alt suspect (nom fichier?): '{alt[:30]}'")
                break
        
        # Alt trop long (>250 caractères)
        if len(alt) > 250:
            issues.append(f"Alt trop long ({len(alt)} car.): '{alt[:30]}...'")
        
        # Alt identique au src (copier-coller du nom fichier)
        src = img.get('src', '')
        if alt.lower() in src.lower():
            issues.append(f"Alt = nom fichier: '{alt[:30]}'")
    
    return {
        'status': 'C' if not issues else 'NC',
        'issues': issues,
        'modifications': '; '.join(issues),
        'automated_coverage': 0.40,
        'manual_check': "Vérifier la pertinence sémantique des alternatives"
    }
```

#### Critères 1.4-1.5 - CAPTCHA
```python
def test_1_4(self) -> dict:
    """CAPTCHA avec alternative identifiant sa nature"""
    captcha_indicators = ['captcha', 'recaptcha', 'hcaptcha', 'securimage', 'verification']
    issues = []
    
    # Chercher éléments CAPTCHA
    for indicator in captcha_indicators:
        elements = self.soup.find_all(class_=re.compile(indicator, re.I))
        elements += self.soup.find_all(id=re.compile(indicator, re.I))
        
        for elem in elements:
            imgs = elem.find_all('img')
            for img in imgs:
                alt = img.get('alt', '')
                if not alt or 'captcha' not in alt.lower():
                    issues.append("Image CAPTCHA sans alternative descriptive")
    
    if not issues and not self.soup.find_all(class_=re.compile('captcha', re.I)):
        return {'status': 'NA', 'issues': [], 'modifications': 'Pas de CAPTCHA détecté'}
    
    return {
        'status': 'C' if not issues else 'NC',
        'issues': issues,
        'modifications': '; '.join(issues),
        'automated_coverage': 0.60
    }

def test_1_5(self) -> dict:
    """Alternative non graphique au CAPTCHA"""
    # Chercher alternative audio ou autre
    captcha_zones = self.soup.find_all(class_=re.compile('captcha', re.I))
    
    if not captcha_zones:
        return {'status': 'NA', 'issues': [], 'modifications': 'Pas de CAPTCHA'}
    
    issues = []
    for zone in captcha_zones:
        has_audio = zone.find('audio') or zone.find(class_=re.compile('audio', re.I))
        has_alt_link = zone.find('a', string=re.compile('audio|sonore|alternative', re.I))
        
        if not has_audio and not has_alt_link:
            issues.append("CAPTCHA sans alternative non graphique")
    
    return {
        'status': 'C' if not issues else 'NC',
        'issues': issues,
        'modifications': '; '.join(issues),
        'automated_coverage': 0.70
    }
```

#### Critères 1.6-1.7 - Description détaillée
```python
def test_1_6(self) -> dict:
    """Images complexes avec description détaillée"""
    issues = []
    
    # Chercher images complexes (graphiques, infographies, schémas)
    complex_indicators = ['chart', 'graph', 'diagram', 'schema', 'infograph', 'map']
    
    for img in self.soup.find_all('img'):
        src = img.get('src', '').lower()
        alt = img.get('alt', '').lower()
        classes = ' '.join(img.get('class', [])).lower()
        
        is_complex = any(ind in src or ind in alt or ind in classes for ind in complex_indicators)
        
        if is_complex:
            # Vérifier présence longdesc ou aria-describedby ou lien adjacent
            has_longdesc = img.get('longdesc')
            has_describedby = img.get('aria-describedby')
            
            # Chercher lien adjacent
            parent = img.parent
            adjacent_link = parent.find('a', string=re.compile('description|détail|voir', re.I)) if parent else None
            
            if not has_longdesc and not has_describedby and not adjacent_link:
                issues.append(f"Image complexe sans description détaillée: {src[:40]}")
    
    if not issues:
        # Vérifier s'il y a des images complexes
        return {'status': 'NA' if not any(ind in str(self.soup).lower() for ind in complex_indicators) else 'C',
                'issues': [], 'modifications': ''}
    
    return {
        'status': 'NC',
        'issues': issues,
        'modifications': '; '.join(issues),
        'automated_coverage': 0.50,
        'manual_check': "Identifier manuellement les images nécessitant une description détaillée"
    }
```

#### Critère 1.8 - Images texte
```python
def test_1_8(self) -> dict:
    """Images texte remplaçables par du texte stylé"""
    issues = []
    
    # Détecter images potentiellement textuelles
    text_image_patterns = ['button', 'btn', 'title', 'heading', 'logo', 'banner']
    
    for img in self.soup.find_all('img'):
        src = img.get('src', '').lower()
        alt = img.get('alt', '')
        
        # Si l'alt contient du texte lisible qui pourrait être du CSS
        if alt and len(alt) > 3:
            # Heuristique: alt sans extension fichier, phrases simples
            if not re.search(r'\.(png|jpg|gif|svg)$', alt, re.I):
                # Pourrait être une image-texte
                if any(p in src for p in text_image_patterns):
                    issues.append(f"Image-texte potentielle: '{alt[:30]}' - envisager texte CSS")
    
    return {
        'status': 'C' if not issues else 'NC',
        'issues': issues,
        'modifications': '; '.join(issues),
        'automated_coverage': 0.30,
        'manual_check': "Vérifier visuellement si des images contenant du texte peuvent être remplacées"
    }
```

#### Critère 1.9 - Légendes d'images
```python
def test_1_9(self) -> dict:
    """Légendes correctement reliées aux images"""
    issues = []
    
    figures = self.soup.find_all('figure')
    
    for figure in figures:
        img = figure.find('img') or figure.find('svg') or figure.find('canvas')
        figcaption = figure.find('figcaption')
        
        if img and figcaption:
            # Vérifier role et aria-label sur figure
            role = figure.get('role')
            if role not in ['figure', 'group']:
                issues.append("Figure sans role='figure' ou 'group'")
            
            aria_label = figure.get('aria-label', '')
            caption_text = figcaption.get_text(strip=True)
            
            if aria_label and aria_label != caption_text:
                issues.append(f"aria-label différent de figcaption")
    
    if not figures:
        return {'status': 'NA', 'issues': [], 'modifications': 'Pas de figure avec légende'}
    
    return {
        'status': 'C' if not issues else 'NC',
        'issues': issues,
        'modifications': '; '.join(issues),
        'automated_coverage': 0.85
    }
```

---

### THÈME 2 : CADRES (Critères 2.1 à 2.2)

```python
def test_2_1(self) -> dict:
    """Chaque cadre a-t-il un titre ?"""
    issues = []
    
    iframes = self.soup.find_all('iframe')
    frames = self.soup.find_all('frame')
    
    for frame in iframes + frames:
        title = frame.get('title', '').strip()
        if not title:
            src = frame.get('src', 'source inconnue')[:40]
            issues.append(f"Cadre sans titre: {src}")
    
    if not iframes and not frames:
        return {'status': 'NA', 'issues': [], 'modifications': 'Pas de cadre iframe/frame'}
    
    return {
        'status': 'C' if not issues else 'NC',
        'issues': issues,
        'modifications': '; '.join(issues),
        'automated_coverage': 0.98
    }

def test_2_2(self) -> dict:
    """Titre de cadre pertinent"""
    issues = []
    generic_titles = ['iframe', 'frame', 'cadre', 'contenu', 'content', 'widget']
    
    for frame in self.soup.find_all(['iframe', 'frame']):
        title = frame.get('title', '').strip().lower()
        src = frame.get('src', '')
        
        if title:
            # Vérifier si titre générique
            if title in generic_titles:
                issues.append(f"Titre générique: '{title}'")
            
            # Vérifier si titre = URL
            if title == src or src in title:
                issues.append(f"Titre = URL: '{title[:30]}'")
            
            # Titre trop court
            if len(title) < 3:
                issues.append(f"Titre trop court: '{title}'")
    
    if not self.soup.find_all(['iframe', 'frame']):
        return {'status': 'NA', 'issues': [], 'modifications': ''}
    
    return {
        'status': 'C' if not issues else 'NC',
        'issues': issues,
        'modifications': '; '.join(issues),
        'automated_coverage': 0.35,
        'manual_check': "Vérifier que le titre décrit bien le contenu du cadre"
    }
```

---

### THÈME 3 : COULEURS (Critères 3.1 à 3.3)

```python
def test_3_1(self) -> dict:
    """Information non donnée uniquement par la couleur"""
    issues = []
    
    # Chercher champs obligatoires (souvent signalés par couleur rouge)
    required_fields = self.soup.find_all(['input', 'select', 'textarea'], required=True)
    required_fields += self.soup.find_all(attrs={'aria-required': 'true'})
    
    for field in required_fields:
        # Chercher indication visible autre que couleur
        label = None
        if field.get('id'):
            label = self.soup.find('label', {'for': field.get('id')})
        
        if label:
            label_text = label.get_text()
            # Vérifier présence d'astérisque ou "(obligatoire)"
            if '*' not in label_text and 'obligatoire' not in label_text.lower() and 'required' not in label_text.lower():
                issues.append(f"Champ obligatoire sans indication visuelle autre que couleur: {field.get('name', 'inconnu')}")
    
    # Chercher messages d'erreur
    error_elements = self.soup.find_all(class_=re.compile('error|erreur|invalid', re.I))
    for elem in error_elements:
        # Vérifier présence d'icône ou texte explicite
        has_icon = elem.find(['svg', 'i', 'img', 'span'])
        text = elem.get_text(strip=True)
        if not has_icon and not text:
            issues.append("Message d'erreur potentiellement signalé uniquement par couleur")
    
    return {
        'status': 'C' if not issues else 'NC',
        'issues': issues,
        'modifications': '; '.join(issues),
        'automated_coverage': 0.25,
        'manual_check': "VÉRIFICATION MANUELLE REQUISE: Analyser visuellement si des informations sont données uniquement par la couleur"
    }

def test_3_2(self) -> dict:
    """Contraste texte/arrière-plan suffisant"""
    # NOTE: Nécessite analyse CSS complète
    issues = []
    
    # Heuristique: chercher styles inline avec couleurs faibles
    elements_with_color = self.soup.find_all(style=re.compile(r'color:', re.I))
    
    for elem in elements_with_color:
        style = elem.get('style', '')
        # Détecter couleurs potentiellement problématiques (gris clair, etc.)
        light_colors = ['#ccc', '#ddd', '#eee', '#fff', '#aaa', '#bbb', 'lightgray', 'lightgrey', '#999']
        for color in light_colors:
            if color in style.lower():
                issues.append(f"Couleur potentiellement peu contrastée détectée: {color}")
    
    return {
        'status': 'NT',  # Nécessite vérification manuelle avec outil de contraste
        'issues': issues,
        'modifications': "VÉRIFICATION MANUELLE REQUISE avec outil de mesure de contraste (ex: Colour Contrast Analyser)",
        'automated_coverage': 0.20,
        'manual_check': "Utiliser un outil de mesure de contraste pour vérifier ratio 4.5:1 (texte normal) ou 3:1 (grands textes)"
    }

def test_3_3(self) -> dict:
    """Contraste des composants d'interface"""
    return {
        'status': 'NT',
        'issues': [],
        'modifications': "VÉRIFICATION MANUELLE REQUISE: Contraste 3:1 minimum pour composants UI",
        'automated_coverage': 0.15,
        'manual_check': "Vérifier le contraste des bordures de champs, boutons, icônes avec l'arrière-plan"
    }
```

---

### THÈME 4 : MULTIMÉDIA (Critères 4.1 à 4.13)

```python
def test_4_1(self) -> dict:
    """Média temporel avec transcription ou audiodescription"""
    issues = []
    
    videos = self.soup.find_all('video')
    audios = self.soup.find_all('audio')
    objects_media = self.soup.find_all('object', type=re.compile(r'video/|audio/', re.I))
    embeds = self.soup.find_all('embed', type=re.compile(r'video/|audio/', re.I))
    
    media_elements = videos + audios + objects_media + embeds
    
    if not media_elements:
        # Chercher aussi les iframes YouTube, Vimeo, etc.
        youtube = self.soup.find_all('iframe', src=re.compile(r'youtube|vimeo|dailymotion', re.I))
        media_elements += youtube
    
    for media in media_elements:
        # Chercher track pour transcription
        tracks = media.find_all('track') if hasattr(media, 'find_all') else []
        
        # Chercher lien transcription adjacent
        parent = media.parent
        transcript_link = None
        if parent:
            transcript_link = parent.find('a', string=re.compile(r'transcript|transcription|texte', re.I))
        
        if not tracks and not transcript_link:
            src = media.get('src', media.get('data', ''))[:40]
            issues.append(f"Média sans transcription: {src}")
    
    if not media_elements:
        return {'status': 'NA', 'issues': [], 'modifications': 'Pas de média temporel détecté'}
    
    return {
        'status': 'C' if not issues else 'NC',
        'issues': issues,
        'modifications': '; '.join(issues),
        'automated_coverage': 0.80
    }

def test_4_3(self) -> dict:
    """Sous-titres synchronisés pour vidéos"""
    issues = []
    
    videos = self.soup.find_all('video')
    
    for video in videos:
        tracks = video.find_all('track')
        has_captions = any(t.get('kind') == 'captions' or t.get('kind') == 'subtitles' for t in tracks)
        
        if not has_captions:
            src = video.get('src', '')[:40]
            issues.append(f"Vidéo sans sous-titres: {src}")
    
    # Vérifier iframes vidéo
    video_iframes = self.soup.find_all('iframe', src=re.compile(r'youtube|vimeo', re.I))
    if video_iframes:
        issues.append("VÉRIFICATION MANUELLE: Vérifier sous-titres des vidéos intégrées (YouTube/Vimeo)")
    
    if not videos and not video_iframes:
        return {'status': 'NA', 'issues': [], 'modifications': 'Pas de vidéo'}
    
    return {
        'status': 'C' if not issues else 'NC',
        'issues': issues,
        'modifications': '; '.join(issues),
        'automated_coverage': 0.75
    }

def test_4_10(self) -> dict:
    """Son déclenché automatiquement contrôlable"""
    issues = []
    
    # Chercher autoplay
    autoplay_media = self.soup.find_all(['video', 'audio'], autoplay=True)
    autoplay_media += self.soup.find_all(['video', 'audio'], attrs={'autoplay': ''})
    
    for media in autoplay_media:
        muted = media.get('muted') is not None
        controls = media.get('controls') is not None
        
        if not muted and not controls:
            issues.append("Média autoplay sans contrôle ni mute")
    
    # Chercher bgsound (obsolète mais vérifié)
    bgsound = self.soup.find_all('bgsound')
    if bgsound:
        issues.append("Élément bgsound détecté (obsolète et non contrôlable)")
    
    if not autoplay_media and not bgsound:
        return {'status': 'NA', 'issues': [], 'modifications': ''}
    
    return {
        'status': 'C' if not issues else 'NC',
        'issues': issues,
        'modifications': '; '.join(issues),
        'automated_coverage': 0.95
    }
```

---

### THÈME 5 : TABLEAUX (Critères 5.1 à 5.8)

```python
def test_5_1(self) -> dict:
    """Tableaux de données complexes avec résumé"""
    issues = []
    
    tables = self.soup.find_all('table')
    
    for table in tables:
        # Détecter si complexe (colspan/rowspan ou headers multiples)
        is_complex = bool(table.find_all(['td', 'th'], colspan=True)) or \
                     bool(table.find_all(['td', 'th'], rowspan=True)) or \
                     len(table.find_all('th')) > 10
        
        if is_complex:
            # Chercher résumé
            summary = table.get('summary')  # Obsolète mais encore utilisé
            aria_describedby = table.get('aria-describedby')
            caption = table.find('caption')
            
            # En HTML5, le résumé peut être dans le caption
            if not summary and not aria_describedby:
                if not caption or len(caption.get_text(strip=True)) < 20:
                    issues.append("Tableau complexe sans résumé")
    
    complex_tables = [t for t in tables if bool(t.find_all(['td', 'th'], colspan=True)) or bool(t.find_all(['td', 'th'], rowspan=True))]
    
    if not complex_tables:
        return {'status': 'NA', 'issues': [], 'modifications': 'Pas de tableau complexe'}
    
    return {
        'status': 'C' if not issues else 'NC',
        'issues': issues,
        'modifications': '; '.join(issues),
        'automated_coverage': 0.70
    }

def test_5_3(self) -> dict:
    """Tableaux de mise en forme avec role=presentation"""
    issues = []
    
    tables = self.soup.find_all('table')
    
    for table in tables:
        # Détecter tableau de mise en forme (pas de th, pas de caption, structure simple)
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
        return {'status': 'NA', 'issues': [], 'modifications': 'Pas de tableau de mise en forme détecté'}
    
    return {
        'status': 'C' if not issues else 'NC',
        'issues': issues,
        'modifications': '; '.join(issues),
        'automated_coverage': 0.70
    }

def test_5_6(self) -> dict:
    """En-têtes de tableau correctement déclarés"""
    issues = []
    
    tables = self.soup.find_all('table')
    
    for table in tables:
        # Ignorer tableaux de mise en forme
        if table.get('role') == 'presentation':
            continue
        
        # Vérifier présence de th
        ths = table.find_all('th')
        if not ths:
            # Vérifier si c'est un tableau de données (a des données structurées)
            tds = table.find_all('td')
            if len(tds) > 4:  # Plus de 4 cellules = probablement tableau de données
                issues.append("Tableau de données sans en-têtes <th>")
        else:
            # Vérifier scope sur les th
            for th in ths:
                scope = th.get('scope')
                role = th.get('role')
                if not scope and role not in ['columnheader', 'rowheader']:
                    issues.append("En-tête <th> sans attribut scope")
                    break
    
    data_tables = [t for t in tables if t.get('role') != 'presentation' and len(t.find_all('td')) > 4]
    
    if not data_tables:
        return {'status': 'NA', 'issues': [], 'modifications': ''}
    
    return {
        'status': 'C' if not issues else 'NC',
        'issues': issues,
        'modifications': '; '.join(issues),
        'automated_coverage': 0.85
    }

def test_5_8(self) -> dict:
    """Tableaux de mise en forme sans éléments de données"""
    issues = []
    
    tables = self.soup.find_all('table', role='presentation')
    
    for table in tables:
        # Ne doit pas contenir: th, caption, summary, headers, scope
        if table.find('th'):
            issues.append("Tableau présentation avec <th>")
        if table.find('caption'):
            issues.append("Tableau présentation avec <caption>")
        if table.get('summary'):
            issues.append("Tableau présentation avec summary")
        
        cells_with_headers = table.find_all(['td'], headers=True)
        if cells_with_headers:
            issues.append("Tableau présentation avec attribut headers")
        
        cells_with_scope = table.find_all(['td'], scope=True)
        if cells_with_scope:
            issues.append("Tableau présentation avec attribut scope")
    
    if not tables:
        return {'status': 'NA', 'issues': [], 'modifications': ''}
    
    return {
        'status': 'C' if not issues else 'NC',
        'issues': issues,
        'modifications': '; '.join(issues),
        'automated_coverage': 0.90
    }
```

---

### THÈME 6 : LIENS (Critères 6.1 à 6.2)

```python
def test_6_1(self) -> dict:
    """Liens explicites"""
    issues = []
    generic_texts = ['cliquez ici', 'click here', 'ici', 'here', 'lire la suite', 
                     'read more', 'en savoir plus', 'more', 'suite', 'voir', 'see',
                     'lien', 'link', '+', '>', '>>', '...']
    
    links = self.soup.find_all('a', href=True)
    
    for link in links:
        # Obtenir le texte accessible du lien
        link_text = link.get_text(strip=True).lower()
        aria_label = link.get('aria-label', '').lower()
        title = link.get('title', '').lower()
        
        # Vérifier images dans le lien
        img = link.find('img')
        img_alt = img.get('alt', '').lower() if img else ''
        
        accessible_name = aria_label or link_text or img_alt or title
        
        if accessible_name in generic_texts:
            href = link.get('href', '')[:30]
            issues.append(f"Lien non explicite '{accessible_name}': {href}")
        
        # Lien sans texte ni image avec alt
        if not accessible_name.strip():
            href = link.get('href', '')[:30]
            issues.append(f"Lien vide: {href}")
    
    return {
        'status': 'C' if not issues else 'NC',
        'issues': issues,
        'modifications': '; '.join(issues[:10]),  # Limiter le nombre
        'automated_coverage': 0.75
    }

def test_6_2(self) -> dict:
    """Chaque lien a un intitulé"""
    issues = []
    
    links = self.soup.find_all('a', href=True)
    
    for link in links:
        # Vérifier présence d'un nom accessible
        has_text = bool(link.get_text(strip=True))
        has_aria_label = bool(link.get('aria-label', '').strip())
        has_aria_labelledby = bool(link.get('aria-labelledby'))
        has_title = bool(link.get('title', '').strip())
        
        # Vérifier image avec alt
        img = link.find('img')
        has_img_alt = bool(img and img.get('alt', '').strip()) if img else False
        
        # SVG avec titre
        svg = link.find('svg')
        has_svg_title = bool(svg and (svg.find('title') or svg.get('aria-label'))) if svg else False
        
        if not (has_text or has_aria_label or has_aria_labelledby or has_title or has_img_alt or has_svg_title):
            href = link.get('href', '')[:40]
            issues.append(f"Lien sans intitulé: {href}")
    
    return {
        'status': 'C' if not issues else 'NC',
        'issues': issues,
        'modifications': '; '.join(issues[:10]),
        'automated_coverage': 0.95
    }
```

---

### THÈME 7 : SCRIPTS (Critères 7.1 à 7.5)

```python
def test_7_1(self) -> dict:
    """Scripts compatibles avec technologies d'assistance"""
    issues = []
    
    # Vérifier éléments interactifs personnalisés
    interactive_roles = ['button', 'link', 'checkbox', 'radio', 'tab', 'slider', 
                         'spinbutton', 'combobox', 'listbox', 'menu', 'menuitem', 
                         'dialog', 'alertdialog', 'tooltip']
    
    for role in interactive_roles:
        elements = self.soup.find_all(attrs={'role': role})
        for elem in elements:
            # Vérifier attributs ARIA requis
            if role == 'checkbox' and not elem.get('aria-checked'):
                issues.append(f"role=checkbox sans aria-checked")
            if role == 'slider' and not elem.get('aria-valuenow'):
                issues.append(f"role=slider sans aria-valuenow")
            if role == 'tab' and not elem.get('aria-selected'):
                issues.append(f"role=tab sans aria-selected")
            if role == 'combobox' and not elem.get('aria-expanded'):
                issues.append(f"role=combobox sans aria-expanded")
    
    # Vérifier onclick sur éléments non interactifs
    clickable_divs = self.soup.find_all(['div', 'span'], onclick=True)
    for div in clickable_divs:
        if not div.get('role') and not div.get('tabindex'):
            issues.append("onclick sur élément non interactif sans role ni tabindex")
    
    return {
        'status': 'C' if not issues else 'NC',
        'issues': issues,
        'modifications': '; '.join(issues),
        'automated_coverage': 0.60
    }

def test_7_3(self) -> dict:
    """Scripts contrôlables au clavier"""
    issues = []
    
    # Chercher événements souris sans équivalent clavier
    mouse_only_events = ['onmouseover', 'onmouseout', 'onmouseenter', 'onmouseleave', 'ondblclick']
    
    for event in mouse_only_events:
        elements = self.soup.find_all(attrs={event: True})
        for elem in elements:
            # Vérifier présence événement clavier correspondant
            has_keyboard = elem.get('onfocus') or elem.get('onblur') or elem.get('onkeypress') or elem.get('onkeydown')
            if not has_keyboard:
                tag = elem.name
                issues.append(f"<{tag}> avec {event} sans équivalent clavier")
    
    # Vérifier éléments avec tabindex="-1" qui devraient être accessibles
    negative_tabindex = self.soup.find_all(attrs={'tabindex': '-1'})
    for elem in negative_tabindex:
        if elem.get('onclick') or elem.get('role') in ['button', 'link']:
            issues.append(f"Élément interactif avec tabindex=-1")
    
    return {
        'status': 'C' if not issues else 'NC',
        'issues': issues,
        'modifications': '; '.join(issues),
        'automated_coverage': 0.50,
        'manual_check': "Tester navigation clavier complète sur la page"
    }

def test_7_5(self) -> dict:
    """Messages de statut correctement restitués"""
    issues = []
    
    # Chercher zones live
    live_regions = self.soup.find_all(attrs={'aria-live': True})
    live_regions += self.soup.find_all(attrs={'role': ['alert', 'status', 'log', 'progressbar']})
    
    # Chercher messages d'erreur/succès potentiels
    message_classes = ['alert', 'error', 'success', 'warning', 'notification', 'message', 'toast']
    
    for cls in message_classes:
        elements = self.soup.find_all(class_=re.compile(cls, re.I))
        for elem in elements:
            role = elem.get('role')
            aria_live = elem.get('aria-live')
            
            if not role and not aria_live:
                issues.append(f"Message potentiel sans role/aria-live: class={cls}")
    
    return {
        'status': 'C' if not issues else 'NC',
        'issues': issues,
        'modifications': '; '.join(issues),
        'automated_coverage': 0.65,
        'manual_check': "Vérifier avec lecteur d'écran que les messages dynamiques sont annoncés"
    }
```

---

### THÈME 8 : ÉLÉMENTS OBLIGATOIRES (Critères 8.1 à 8.10)

```python
def test_8_1(self) -> dict:
    """Page définie par un type de document"""
    issues = []
    
    # Vérifier DOCTYPE
    doctype_pattern = r'<!DOCTYPE\s+html'
    if not re.search(doctype_pattern, self.html[:500], re.I):
        issues.append("DOCTYPE HTML manquant ou invalide")
    
    return {
        'status': 'C' if not issues else 'NC',
        'issues': issues,
        'modifications': '; '.join(issues),
        'automated_coverage': 0.98
    }

def test_8_2(self) -> dict:
    """Code source valide"""
    issues = []
    
    # Vérifications basiques de validité
    # ID dupliqués
    ids = [elem.get('id') for elem in self.soup.find_all(id=True)]
    duplicates = [id for id in ids if ids.count(id) > 1]
    if duplicates:
        issues.append(f"IDs dupliqués: {list(set(duplicates))[:5]}")
    
    # Attributs dupliqués (nécessite parsing brut)
    # ... analyse supplémentaire possible
    
    return {
        'status': 'C' if not issues else 'NC',
        'issues': issues,
        'modifications': '; '.join(issues),
        'automated_coverage': 0.70,
        'manual_check': "Utiliser validateur W3C pour validation complète"
    }

def test_8_3(self) -> dict:
    """Langue par défaut présente"""
    issues = []
    
    html_tag = self.soup.find('html')
    if html_tag:
        lang = html_tag.get('lang') or html_tag.get('xml:lang')
        if not lang:
            issues.append("Attribut lang manquant sur <html>")
    else:
        issues.append("Balise <html> non trouvée")
    
    return {
        'status': 'C' if not issues else 'NC',
        'issues': issues,
        'modifications': '; '.join(issues),
        'automated_coverage': 0.98
    }

def test_8_4(self) -> dict:
    """Code de langue valide et pertinent"""
    issues = []
    
    html_tag = self.soup.find('html')
    if html_tag:
        lang = html_tag.get('lang', '')
        
        # Codes ISO 639 valides (liste partielle)
        valid_codes = ['fr', 'en', 'de', 'es', 'it', 'pt', 'nl', 'pl', 'ru', 'ar', 'zh', 'ja', 'ko']
        
        lang_code = lang.split('-')[0].lower() if lang else ''
        
        if not lang:
            issues.append("Pas de code langue")
        elif lang_code not in valid_codes and len(lang_code) not in [2, 3]:
            issues.append(f"Code langue invalide: {lang}")
    
    return {
        'status': 'C' if not issues else 'NC',
        'issues': issues,
        'modifications': '; '.join(issues),
        'automated_coverage': 0.90
    }

def test_8_5(self) -> dict:
    """Page a un titre"""
    issues = []
    
    title = self.soup.find('title')
    if not title:
        issues.append("Balise <title> manquante")
    elif not title.get_text(strip=True):
        issues.append("Balise <title> vide")
    
    return {
        'status': 'C' if not issues else 'NC',
        'issues': issues,
        'modifications': '; '.join(issues),
        'automated_coverage': 0.98
    }

def test_8_6(self) -> dict:
    """Titre de page pertinent"""
    issues = []
    
    title = self.soup.find('title')
    if title:
        title_text = title.get_text(strip=True)
        
        generic_titles = ['untitled', 'sans titre', 'page', 'accueil', 'home', 'index', 'new page', 'document']
        
        if title_text.lower() in generic_titles:
            issues.append(f"Titre générique: '{title_text}'")
        
        if len(title_text) < 5:
            issues.append(f"Titre trop court: '{title_text}'")
        
        if len(title_text) > 150:
            issues.append(f"Titre trop long ({len(title_text)} car.)")
    
    return {
        'status': 'C' if not issues else 'NC',
        'issues': issues,
        'modifications': '; '.join(issues),
        'automated_coverage': 0.80
    }

def test_8_9(self) -> dict:
    """Balises non utilisées uniquement pour présentation"""
    issues = []
    
    # Balises de présentation obsolètes
    deprecated_tags = ['center', 'font', 'basefont', 'big', 'blink', 'marquee', 's', 'strike', 'tt', 'u']
    
    for tag in deprecated_tags:
        elements = self.soup.find_all(tag)
        if elements:
            issues.append(f"Balise obsolète <{tag}> utilisée ({len(elements)} occurrences)")
    
    # Attributs de présentation obsolètes
    deprecated_attrs = ['bgcolor', 'align', 'valign', 'border', 'cellpadding', 'cellspacing']
    
    for attr in deprecated_attrs:
        elements = self.soup.find_all(attrs={attr: True})
        if elements:
            # Exclure les cas acceptables (border="0" sur table)
            issues.append(f"Attribut obsolète '{attr}' utilisé")
    
    return {
        'status': 'C' if not issues else 'NC',
        'issues': issues,
        'modifications': '; '.join(issues),
        'automated_coverage': 0.90
    }
```

---

### THÈME 9 : STRUCTURATION (Critères 9.1 à 9.4)

```python
def test_9_1(self) -> dict:
    """Information structurée par titres"""
    issues = []
    
    headings = self.soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
    headings += self.soup.find_all(attrs={'role': 'heading'})
    
    if not headings:
        issues.append("Aucun titre (h1-h6) trouvé sur la page")
    else:
        # Vérifier hiérarchie
        levels = []
        for h in headings:
            if h.name and h.name.startswith('h'):
                levels.append(int(h.name[1]))
            elif h.get('aria-level'):
                levels.append(int(h.get('aria-level')))
        
        # Vérifier saut de niveaux
        for i in range(len(levels) - 1):
            if levels[i+1] > levels[i] + 1:
                issues.append(f"Saut de niveau: h{levels[i]} -> h{levels[i+1]}")
        
        # Vérifier présence h1
        h1_count = len(self.soup.find_all('h1'))
        if h1_count == 0:
            issues.append("Pas de titre h1 sur la page")
        elif h1_count > 1:
            issues.append(f"Plusieurs h1 ({h1_count}) - recommandé: 1 seul")
    
    return {
        'status': 'C' if not issues else 'NC',
        'issues': issues,
        'modifications': '; '.join(issues),
        'automated_coverage': 0.90
    }

def test_9_2(self) -> dict:
    """Structure du document cohérente (landmarks HTML5)"""
    issues = []
    
    # Vérifier présence des zones principales
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
    
    # Vérifier unicité de main
    mains = self.soup.find_all('main')
    if len(mains) > 1:
        visible_mains = [m for m in mains if not m.get('hidden') and m.get('aria-hidden') != 'true']
        if len(visible_mains) > 1:
            issues.append("Plusieurs éléments <main> visibles")
    
    return {
        'status': 'C' if not issues else 'NC',
        'issues': issues,
        'modifications': '; '.join(issues),
        'automated_coverage': 0.85
    }

def test_9_3(self) -> dict:
    """Listes correctement structurées"""
    issues = []
    
    # Vérifier ul/ol contiennent uniquement li
    for list_elem in self.soup.find_all(['ul', 'ol']):
        children = [c for c in list_elem.children if c.name]
        non_li = [c.name for c in children if c.name != 'li' and c.name != 'script' and c.name != 'template']
        if non_li:
            issues.append(f"Liste {list_elem.name} avec enfants non-li: {non_li[:3]}")
    
    # Vérifier dl structure
    for dl in self.soup.find_all('dl'):
        children = [c for c in dl.children if c.name]
        valid_children = ['dt', 'dd', 'div', 'script', 'template']
        invalid = [c.name for c in children if c.name not in valid_children]
        if invalid:
            issues.append(f"Liste dl avec enfants invalides: {invalid[:3]}")
    
    # Vérifier role="list" a des role="listitem"
    lists_aria = self.soup.find_all(attrs={'role': 'list'})
    for lst in lists_aria:
        items = lst.find_all(attrs={'role': 'listitem'})
        if not items:
            issues.append("role=list sans role=listitem")
    
    return {
        'status': 'C' if not issues else 'NC',
        'issues': issues,
        'modifications': '; '.join(issues),
        'automated_coverage': 0.80
    }

def test_9_4(self) -> dict:
    """Citations correctement indiquées"""
    issues = []
    
    # Chercher texte qui ressemble à citation sans balise
    # Heuristique: guillemets longs sans <q> ou <blockquote>
    text_content = self.soup.get_text()
    
    # Citations longues avec guillemets
    citation_pattern = r'[«"][^»"]{100,}[»"]'
    potential_quotes = re.findall(citation_pattern, text_content)
    
    for quote in potential_quotes:
        # Vérifier si encapsulé dans blockquote
        if quote[:50] in str(self.soup.find_all('blockquote')):
            continue
        issues.append(f"Citation potentielle non balisée: '{quote[:50]}...'")
    
    blockquotes = self.soup.find_all('blockquote')
    q_elements = self.soup.find_all('q')
    
    if not blockquotes and not q_elements and potential_quotes:
        issues.append("Citations potentielles détectées sans balise <blockquote> ou <q>")
    
    return {
        'status': 'C' if not issues else 'NC',
        'issues': issues,
        'modifications': '; '.join(issues),
        'automated_coverage': 0.50,
        'manual_check': "Vérifier visuellement si des citations ne sont pas balisées"
    }
```

---

### THÈME 10 : PRÉSENTATION (Critères 10.1 à 10.14)

```python
def test_10_1(self) -> dict:
    """Feuilles de styles utilisées pour la présentation"""
    issues = []
    
    # Vérifier absence éléments/attributs de présentation
    # (déjà vérifié en 8.9, mais complémentaire)
    
    # Vérifier pas d'espaces multiples pour simuler colonnes
    pre_content = ''.join([p.get_text() for p in self.soup.find_all('pre')])
    other_content = self.soup.get_text()
    
    # Espaces multiples suspects hors <pre>
    if '     ' in other_content and '     ' not in pre_content:
        issues.append("Espaces multiples détectés (mise en page par espaces?)")
    
    return {
        'status': 'C' if not issues else 'NC',
        'issues': issues,
        'modifications': '; '.join(issues),
        'automated_coverage': 0.60
    }

def test_10_7(self) -> dict:
    """Focus visible sur éléments recevant le focus"""
    issues = []
    
    # Chercher outline:none ou outline:0 dans styles inline
    elements_no_outline = self.soup.find_all(style=re.compile(r'outline\s*:\s*(none|0)', re.I))
    
    for elem in elements_no_outline:
        if elem.name in ['a', 'button', 'input', 'select', 'textarea']:
            issues.append(f"<{elem.name}> avec outline:none/0 en style inline")
    
    # Vérifier les <style> embarqués
    for style_tag in self.soup.find_all('style'):
        css_content = style_tag.get_text()
        if ':focus' in css_content and 'outline' in css_content:
            if 'outline:none' in css_content.replace(' ', '') or 'outline:0' in css_content.replace(' ', ''):
                issues.append("CSS avec :focus { outline: none } détecté")
    
    return {
        'status': 'C' if not issues else 'NC',
        'issues': issues,
        'modifications': '; '.join(issues),
        'automated_coverage': 0.40,
        'manual_check': "Tester la navigation clavier pour vérifier visibilité du focus"
    }
```

---

### THÈME 11 : FORMULAIRES (Critères 11.1 à 11.13)

```python
def test_11_1(self) -> dict:
    """Champs de formulaire avec étiquette"""
    issues = []
    
    form_fields = self.soup.find_all(['input', 'select', 'textarea'])
    
    for field in form_fields:
        field_type = field.get('type', 'text')
        
        # Exclure hidden, submit, button, image, reset
        if field_type in ['hidden', 'submit', 'button', 'image', 'reset']:
            continue
        
        field_id = field.get('id')
        field_name = field.get('name', 'inconnu')
        
        # Vérifier association étiquette
        has_label = False
        
        # 1. Label avec for
        if field_id:
            label = self.soup.find('label', {'for': field_id})
            if label:
                has_label = True
        
        # 2. aria-labelledby
        if field.get('aria-labelledby'):
            has_label = True
        
        # 3. aria-label
        if field.get('aria-label'):
            has_label = True
        
        # 4. title
        if field.get('title'):
            has_label = True
        
        # 5. Label englobant
        parent_label = field.find_parent('label')
        if parent_label:
            has_label = True
        
        # 6. Placeholder seul (insuffisant mais détecté)
        if field.get('placeholder') and not has_label:
            issues.append(f"Champ '{field_name}' avec placeholder seul (insuffisant)")
            continue
        
        if not has_label:
            issues.append(f"Champ sans étiquette: {field_name} (type={field_type})")
    
    return {
        'status': 'C' if not issues else 'NC',
        'issues': issues,
        'modifications': '; '.join(issues[:10]),
        'automated_coverage': 0.90
    }

def test_11_9(self) -> dict:
    """Intitulé de bouton pertinent"""
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
    
    return {
        'status': 'C' if not issues else 'NC',
        'issues': issues,
        'modifications': '; '.join(issues),
        'automated_coverage': 0.85
    }

def test_11_13(self) -> dict:
    """Attribut autocomplete pour champs utilisateur"""
    issues = []
    
    autocomplete_fields = {
        'name': 'name',
        'email': 'email',
        'tel': 'tel',
        'address': 'street-address',
        'city': 'address-level2',
        'zip': 'postal-code',
        'postal': 'postal-code',
        'country': 'country',
        'cc-number': 'cc-number',
        'cc-name': 'cc-name',
        'username': 'username',
        'password': 'current-password',
        'new-password': 'new-password',
        'bday': 'bday',
        'firstname': 'given-name',
        'lastname': 'family-name'
    }
    
    for field in self.soup.find_all(['input', 'select', 'textarea']):
        field_name = (field.get('name', '') + field.get('id', '')).lower()
        field_type = field.get('type', '')
        
        # Détecter champs concernés
        for key, autocomplete_value in autocomplete_fields.items():
            if key in field_name or key in field_type:
                if not field.get('autocomplete'):
                    issues.append(f"Champ '{key}' sans autocomplete")
                break
    
    return {
        'status': 'C' if not issues else 'NC',
        'issues': issues,
        'modifications': '; '.join(issues),
        'automated_coverage': 0.75
    }
```

---

### THÈME 12 : NAVIGATION (Critères 12.1 à 12.11)

```python
def test_12_6(self) -> dict:
    """Zones de regroupement atteignables ou évitables"""
    issues = []
    
    # Vérifier landmarks
    header = self.soup.find('header') or self.soup.find(attrs={'role': 'banner'})
    nav = self.soup.find('nav') or self.soup.find(attrs={'role': 'navigation'})
    main = self.soup.find('main') or self.soup.find(attrs={'role': 'main'})
    footer = self.soup.find('footer') or self.soup.find(attrs={'role': 'contentinfo'})
    search = self.soup.find(attrs={'role': 'search'}) or self.soup.find('form', attrs={'role': 'search'})
    
    if not header and not self.soup.find(attrs={'role': 'banner'}):
        issues.append("Zone d'en-tête sans landmark")
    if not nav and not self.soup.find(attrs={'role': 'navigation'}):
        issues.append("Zone de navigation sans landmark")
    if not main and not self.soup.find(attrs={'role': 'main'}):
        issues.append("Zone de contenu principal sans landmark")
    
    # Vérifier liens d'évitement
    skip_link = self.soup.find('a', href=re.compile(r'^#(main|content|contenu)', re.I))
    if not skip_link:
        first_link = self.soup.find('a')
        if first_link:
            href = first_link.get('href', '')
            if not href.startswith('#'):
                issues.append("Pas de lien d'évitement vers le contenu principal")
    
    return {
        'status': 'C' if not issues else 'NC',
        'issues': issues,
        'modifications': '; '.join(issues),
        'automated_coverage': 0.80
    }

def test_12_7(self) -> dict:
    """Lien d'évitement ou d'accès rapide au contenu principal"""
    issues = []
    
    # Chercher lien vers #main, #content, #contenu, etc.
    skip_patterns = [r'#main', r'#content', r'#contenu', r'#skip', r'#principal']
    
    skip_link_found = False
    for pattern in skip_patterns:
        link = self.soup.find('a', href=re.compile(pattern, re.I))
        if link:
            skip_link_found = True
            
            # Vérifier que la cible existe
            target_id = link.get('href', '').lstrip('#')
            target = self.soup.find(id=target_id)
            if not target:
                issues.append(f"Lien d'évitement vers #{target_id} mais cible inexistante")
            break
    
    if not skip_link_found:
        issues.append("Aucun lien d'évitement vers le contenu principal")
    
    return {
        'status': 'C' if not issues else 'NC',
        'issues': issues,
        'modifications': '; '.join(issues),
        'automated_coverage': 0.85
    }

def test_12_9(self) -> dict:
    """Pas de piège au clavier"""
    issues = []
    
    # Détecter éléments potentiellement piégeants
    # Modales sans fermeture accessible
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
    
    # tabindex positifs (peuvent créer des pièges)
    positive_tabindex = self.soup.find_all(attrs={'tabindex': re.compile(r'^[1-9]')})
    if positive_tabindex:
        issues.append(f"tabindex positif détecté ({len(positive_tabindex)} éléments) - risque de piège")
    
    return {
        'status': 'C' if not issues else 'NC',
        'issues': issues,
        'modifications': '; '.join(issues),
        'automated_coverage': 0.50,
        'manual_check': "TESTER MANUELLEMENT la navigation clavier complète"
    }
```

---

### THÈME 13 : CONSULTATION (Critères 13.1 à 13.12)

```python
def test_13_1(self) -> dict:
    """Contrôle des limites de temps"""
    issues = []
    
    # Chercher meta refresh
    meta_refresh = self.soup.find('meta', attrs={'http-equiv': re.compile('refresh', re.I)})
    if meta_refresh:
        content = meta_refresh.get('content', '')
        if content and not content.startswith('0;'):
            issues.append(f"Meta refresh avec délai: {content}")
    
    return {
        'status': 'C' if not issues else 'NC',
        'issues': issues,
        'modifications': '; '.join(issues),
        'automated_coverage': 0.70
    }

def test_13_2(self) -> dict:
    """Pas d'ouverture de nouvelle fenêtre sans action utilisateur"""
    issues = []
    
    # Chercher target="_blank" ou JavaScript window.open
    new_window_links = self.soup.find_all('a', target='_blank')
    
    # Vérifier si indication de nouvelle fenêtre
    for link in new_window_links:
        title = link.get('title', '')
        aria_label = link.get('aria-label', '')
        text = link.get_text()
        
        new_window_indicators = ['nouvelle fenêtre', 'new window', 'nouvel onglet', 'new tab', '↗', '🔗']
        
        has_indicator = any(ind in (title + aria_label + text).lower() for ind in new_window_indicators)
        
        if not has_indicator:
            href = link.get('href', '')[:30]
            issues.append(f"Lien target=_blank sans indication: {href}")
    
    return {
        'status': 'C' if not issues else 'NC',
        'issues': issues,
        'modifications': '; '.join(issues[:10]),
        'automated_coverage': 0.85
    }

def test_13_7(self) -> dict:
    """Pas de flash ou changement brusque de luminosité"""
    issues = []
    
    # Chercher GIFs animés potentiels
    gifs = self.soup.find_all('img', src=re.compile(r'\.gif$', re.I))
    if gifs:
        issues.append(f"GIF détectés ({len(gifs)}) - vérifier absence de flash")
    
    # Chercher animations CSS
    for style in self.soup.find_all('style'):
        css = style.get_text()
        if '@keyframes' in css or 'animation' in css:
            issues.append("Animations CSS détectées - vérifier fréquence")
    
    return {
        'status': 'C' if not issues else 'NT',
        'issues': issues,
        'modifications': '; '.join(issues),
        'automated_coverage': 0.30,
        'manual_check': "Vérifier que les animations ne flashent pas plus de 3 fois par seconde"
    }

def test_13_8(self) -> dict:
    """Contenus en mouvement contrôlables"""
    issues = []
    
    # Chercher marquee (obsolète)
    marquees = self.soup.find_all('marquee')
    if marquees:
        issues.append(f"Élément <marquee> détecté ({len(marquees)})")
    
    # Chercher carrousels/sliders
    carousel_classes = ['carousel', 'slider', 'slideshow', 'banner-rotator']
    for cls in carousel_classes:
        elements = self.soup.find_all(class_=re.compile(cls, re.I))
        for elem in elements:
            # Chercher contrôles pause/stop
            controls = elem.find(['button', 'a'], string=re.compile(r'pause|stop|arrêt', re.I))
            if not controls:
                controls = elem.find(attrs={'aria-label': re.compile(r'pause|stop', re.I)})
            
            if not controls:
                issues.append(f"Carrousel {cls} sans contrôle pause/stop visible")
    
    return {
        'status': 'C' if not issues else 'NC',
        'issues': issues,
        'modifications': '; '.join(issues),
        'automated_coverage': 0.60
    }
```

---

## CLASSE PRINCIPALE D'ORCHESTRATION

```python
class RGAATestRunner:
    """Exécute tous les tests RGAA sur une page web"""
    
    def __init__(self, url: str):
        self.analyzer = WebPageAnalyzer(url)
        self.results = {}
        
    def run_all_tests(self) -> dict:
        """Exécute tous les 106 critères"""
        if not self.analyzer.fetch():
            return {'error': 'Impossible de récupérer la page'}
        
        # Liste tous les tests à exécuter
        test_methods = [
            ('1.1', self.test_1_1),
            ('1.2', self.test_1_2),
            ('1.3', self.test_1_3),
            # ... tous les autres tests
            ('13.12', self.test_13_12),
        ]
        
        for criterion_id, test_method in test_methods:
            try:
                self.results[criterion_id] = test_method()
            except Exception as e:
                self.results[criterion_id] = {
                    'status': 'NT',
                    'issues': [f'Erreur test: {str(e)}'],
                    'modifications': f'Erreur lors du test: {str(e)}',
                    'automated_coverage': 0
                }
        
        return self.results
    
    def get_summary(self) -> dict:
        """Génère un résumé des résultats"""
        total = len(self.results)
        conforme = sum(1 for r in self.results.values() if r.get('status') == 'C')
        non_conforme = sum(1 for r in self.results.values() if r.get('status') == 'NC')
        na = sum(1 for r in self.results.values() if r.get('status') == 'NA')
        nt = sum(1 for r in self.results.values() if r.get('status') == 'NT')
        
        applicable = total - na
        compliance_rate = (conforme / applicable * 100) if applicable > 0 else 0
        
        return {
            'total_criteria': total,
            'conforme': conforme,
            'non_conforme': non_conforme,
            'non_applicable': na,
            'non_teste': nt,
            'compliance_rate': round(compliance_rate, 1)
        }
```

---

## WORKFLOW COMPLET D'AUDIT

```python
def audit_page(url: str, page_sheet_name: str, ods_handler) -> dict:
    """Audit complet d'une page et mise à jour ODS"""
    
    # 1. Exécuter tous les tests
    runner = RGAATestRunner(url)
    results = runner.run_all_tests()
    
    # 2. Pour chaque critère, mettre à jour l'ODS
    for criterion_id, result in results.items():
        ods_handler.update_criterion(
            sheet_name=page_sheet_name,
            criterion_id=criterion_id,
            status=result['status'],
            modifications=result.get('modifications', ''),
            comment=result.get('manual_check', '')
        )
    
    # 3. Retourner le résumé
    return runner.get_summary()
```

---

## CHECKLIST DE VÉRIFICATION DU CODE

Avant de déployer, Claude Code DOIT vérifier :

- [ ] Chaque méthode `test_X_Y()` analyse réellement le DOM HTML
- [ ] Les tests utilisent `self.soup` (BeautifulSoup) pour parser le HTML
- [ ] Chaque test retourne un dictionnaire avec: `status`, `issues`, `modifications`
- [ ] Les statuts sont uniquement: `'C'`, `'NC'`, `'NA'`, `'NT'`
- [ ] Les messages d'erreur sont en français et explicites
- [ ] Le code gère les exceptions et erreurs réseau
- [ ] La colonne "Modifications à apporter" est peuplée avec les problèmes trouvés
- [ ] Les critères nécessitant vérification manuelle sont marqués `NT` avec explication

---

## RAPPEL FINAL

**Cette application est un outil d'AUDIT qui doit TESTER réellement l'accessibilité.**

Elle ne doit PAS simplement:
- Lire/écrire le fichier ODS
- Afficher une interface
- Copier des données

Elle DOIT:
- Télécharger chaque page web
- Analyser le HTML pour chaque critère
- Détecter les non-conformités
- Documenter les corrections nécessaires
- Indiquer clairement ce qui nécessite vérification manuelle
