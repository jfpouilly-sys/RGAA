# Instructions Claude Code : Détection Automatique NA (Non Applicable)

## Objectif

Ce document définit la logique de détection automatique des critères "Non Applicable" (NA) basée sur l'absence d'éléments testables sur la page. Avant tout audit, Claude Code doit scanner la page pour identifier les types de contenu présents et marquer automatiquement comme NA tous les critères dont l'objet de test est absent.

---

## Principe Fondamental

**Un critère est NA si et seulement si l'objet qu'il teste n'existe pas sur la page.**

Exemples :
- Pas de `<script>` ni de composants JavaScript → Tous les critères Scripts (7.x) = NA
- Pas de `<video>` ni `<audio>` → Tous les critères Multimédia (4.x) = NA
- Pas de `<form>` ni champs de saisie → Tous les critères Formulaires (11.x) = NA

---

## Détection de Contenu par Thème

### Thème 1 : Images

#### Sélecteurs de détection
```python
IMAGE_SELECTORS = {
    'img': 'img',
    'svg': 'svg',
    'canvas': 'canvas',
    'object_image': 'object[type^="image/"]',
    'embed_image': 'embed[type^="image/"]',
    'area': 'area',
    'role_img': '[role="img"]',
    'input_image': 'input[type="image"]'
}
```

#### Logique de détection
```python
def detect_images(soup):
    """Détecte la présence d'images sur la page."""
    elements = {
        'img': soup.select('img'),
        'svg': soup.select('svg'),
        'canvas': soup.select('canvas'),
        'object_image': soup.select('object[type^="image/"]'),
        'embed_image': soup.select('embed[type^="image/"]'),
        'area': soup.select('area'),
        'role_img': soup.select('[role="img"]'),
        'input_image': soup.select('input[type="image"]')
    }
    
    has_images = any(len(v) > 0 for v in elements.values())
    
    return {
        'present': has_images,
        'elements': elements,
        'count': sum(len(v) for v in elements.values())
    }
```

#### Critères concernés si absence d'images
| Critère | Statut si aucune image |
|---------|------------------------|
| 1.1 | NA |
| 1.2 | NA |
| 1.3 | NA |
| 1.4 | NA |
| 1.5 | NA |
| 1.6 | NA |
| 1.7 | NA |
| 1.8 | NA |
| 1.9 | NA |

---

### Thème 2 : Cadres (Frames)

#### Sélecteurs de détection
```python
FRAME_SELECTORS = {
    'iframe': 'iframe',
    'frame': 'frame'
}
```

#### Logique de détection
```python
def detect_frames(soup):
    """Détecte la présence de cadres sur la page."""
    elements = {
        'iframe': soup.select('iframe'),
        'frame': soup.select('frame')
    }
    
    has_frames = any(len(v) > 0 for v in elements.values())
    
    return {
        'present': has_frames,
        'elements': elements,
        'count': sum(len(v) for v in elements.values())
    }
```

#### Critères concernés si absence de cadres
| Critère | Statut si aucun cadre |
|---------|----------------------|
| 2.1 | NA |
| 2.2 | NA |

---

### Thème 3 : Couleurs

#### Sélecteurs de détection
```python
# Les couleurs sont TOUJOURS applicables car il y a toujours du texte
# Cependant, certains sous-critères peuvent être NA

COLOR_SPECIFIC_SELECTORS = {
    'graphical_elements': '[role="img"], svg, canvas, img',
    'ui_components': 'button, input, select, a, [role="button"], [role="link"]'
}
```

#### Logique de détection
```python
def detect_color_context(soup):
    """Détecte les contextes de couleur spécifiques."""
    return {
        'text_present': True,  # Toujours vrai si page HTML
        'graphical_elements': len(soup.select('[role="img"], svg, canvas')) > 0,
        'ui_components': len(soup.select('button, input, select, a')) > 0
    }
```

#### Critères concernés
| Critère | Condition NA |
|---------|-------------|
| 3.1 | Jamais NA (texte toujours présent) |
| 3.2 | Jamais NA (texte toujours présent) |
| 3.3 | NA si aucun composant d'interface ni élément graphique |

---

### Thème 4 : Multimédia

#### Sélecteurs de détection
```python
MEDIA_SELECTORS = {
    'video': 'video',
    'audio': 'audio',
    'object_video': 'object[type^="video/"], object[type="application/x-shockwave-flash"]',
    'object_audio': 'object[type^="audio/"]',
    'embed_video': 'embed[type^="video/"], embed[type="application/x-shockwave-flash"]',
    'embed_audio': 'embed[type^="audio/"]',
    'bgsound': 'bgsound',
    'track': 'track'
}
```

#### Logique de détection
```python
def detect_media(soup):
    """Détecte la présence de médias temporels et non temporels."""
    elements = {
        'video': soup.select('video'),
        'audio': soup.select('audio'),
        'object_media': soup.select('object[type^="video/"], object[type^="audio/"], object[type="application/x-shockwave-flash"]'),
        'embed_media': soup.select('embed[type^="video/"], embed[type^="audio/"]'),
        'bgsound': soup.select('bgsound')
    }
    
    has_temporal_media = any(len(v) > 0 for v in elements.values())
    
    # Médias non temporels (Flash interactif, applets, etc.)
    non_temporal = soup.select('object[type="application/x-shockwave-flash"]:not([data*="video"]), embed[type="application/x-shockwave-flash"]:not([src*="video"])')
    
    return {
        'temporal_present': has_temporal_media,
        'non_temporal_present': len(non_temporal) > 0,
        'elements': elements,
        'count': sum(len(v) for v in elements.values())
    }
```

#### Critères concernés si absence de médias
| Critère | Condition NA |
|---------|-------------|
| 4.1 | NA si aucun média temporel pré-enregistré |
| 4.2 | NA si aucun média temporel pré-enregistré |
| 4.3 | NA si aucun média temporel synchronisé |
| 4.4 | NA si aucun média temporel synchronisé avec sous-titres |
| 4.5 | NA si aucun média temporel pré-enregistré |
| 4.6 | NA si aucun média temporel avec audiodescription |
| 4.7 | NA si aucun média temporel |
| 4.8 | NA si aucun média non temporel |
| 4.9 | NA si aucun média non temporel avec alternative |
| 4.10 | NA si aucun son déclenché automatiquement |
| 4.11 | NA si aucun média temporel |
| 4.12 | NA si aucun média non temporel |
| 4.13 | NA si aucun média temporel ou non temporel |

---

### Thème 5 : Tableaux

#### Sélecteurs de détection
```python
TABLE_SELECTORS = {
    'table': 'table',
    'role_table': '[role="table"]',
    'role_grid': '[role="grid"]',
    'role_treegrid': '[role="treegrid"]'
}
```

#### Logique de détection
```python
def detect_tables(soup):
    """Détecte la présence de tableaux sur la page."""
    tables = soup.select('table, [role="table"], [role="grid"], [role="treegrid"]')
    
    # Distinguer tableaux de données vs mise en forme
    data_tables = []
    layout_tables = []
    
    for table in tables:
        if table.get('role') == 'presentation' or table.select('th, [role="columnheader"], [role="rowheader"]'):
            if table.get('role') == 'presentation':
                layout_tables.append(table)
            else:
                data_tables.append(table)
        else:
            # Heuristique : si pas de th, probablement mise en forme
            if table.select('th'):
                data_tables.append(table)
            else:
                layout_tables.append(table)
    
    return {
        'present': len(tables) > 0,
        'data_tables': data_tables,
        'layout_tables': layout_tables,
        'count': len(tables)
    }
```

#### Critères concernés si absence de tableaux
| Critère | Condition NA |
|---------|-------------|
| 5.1 | NA si aucun tableau de données complexe |
| 5.2 | NA si aucun tableau de données complexe avec résumé |
| 5.3 | NA si aucun tableau de mise en forme |
| 5.4 | NA si aucun tableau de données avec titre |
| 5.5 | NA si aucun tableau de données avec titre |
| 5.6 | NA si aucun tableau de données |
| 5.7 | NA si aucun tableau de données |
| 5.8 | NA si aucun tableau de mise en forme |

---

### Thème 6 : Liens

#### Sélecteurs de détection
```python
LINK_SELECTORS = {
    'a_href': 'a[href]',
    'area_href': 'area[href]',
    'role_link': '[role="link"]'
}
```

#### Logique de détection
```python
def detect_links(soup):
    """Détecte la présence de liens sur la page."""
    elements = {
        'a_href': soup.select('a[href]'),
        'area_href': soup.select('area[href]'),
        'role_link': soup.select('[role="link"]')
    }
    
    # Catégoriser les liens
    text_links = []
    image_links = []
    composite_links = []
    svg_links = []
    
    for link in elements['a_href']:
        imgs = link.select('img, svg, canvas, object, embed, [role="img"]')
        text = link.get_text(strip=True)
        
        if link.name == 'svg' or link.find_parent('svg'):
            svg_links.append(link)
        elif imgs and not text:
            image_links.append(link)
        elif imgs and text:
            composite_links.append(link)
        else:
            text_links.append(link)
    
    has_links = any(len(v) > 0 for v in elements.values())
    
    return {
        'present': has_links,
        'text_links': text_links,
        'image_links': image_links,
        'composite_links': composite_links,
        'svg_links': svg_links,
        'elements': elements,
        'count': sum(len(v) for v in elements.values())
    }
```

#### Critères concernés si absence de liens
| Critère | Condition NA |
|---------|-------------|
| 6.1 | NA si aucun lien |
| 6.2 | NA si aucun lien |

---

### Thème 7 : Scripts

#### Sélecteurs de détection
```python
SCRIPT_INDICATORS = {
    'script_tags': 'script',
    'event_handlers': '[onclick], [onchange], [onsubmit], [onfocus], [onblur], [onkeydown], [onkeyup], [onkeypress], [onmouseover], [onmouseout], [onload]',
    'aria_widgets': '[role="button"], [role="checkbox"], [role="combobox"], [role="dialog"], [role="grid"], [role="listbox"], [role="menu"], [role="menubar"], [role="menuitem"], [role="progressbar"], [role="radio"], [role="scrollbar"], [role="slider"], [role="spinbutton"], [role="switch"], [role="tab"], [role="tablist"], [role="tabpanel"], [role="tooltip"], [role="tree"], [role="treeitem"]',
    'aria_live': '[aria-live], [role="alert"], [role="log"], [role="marquee"], [role="status"], [role="timer"]'
}
```

#### Logique de détection
```python
def detect_scripts(soup):
    """Détecte la présence de scripts et composants JavaScript."""
    
    # Scripts
    scripts = soup.select('script')
    has_js_files = any(s.get('src') for s in scripts)
    has_inline_js = any(s.string for s in scripts if s.string)
    
    # Gestionnaires d'événements
    event_handlers = soup.select('[onclick], [onchange], [onsubmit], [onfocus], [onblur], [onkeydown], [onkeyup], [onkeypress], [onmouseover], [onmouseout]')
    
    # Widgets ARIA (indiquent composants interactifs JS)
    aria_widgets = soup.select('[role="button"], [role="checkbox"], [role="combobox"], [role="dialog"], [role="listbox"], [role="menu"], [role="slider"], [role="switch"], [role="tab"], [role="tabpanel"], [role="tooltip"], [role="tree"]')
    
    # Zones live ARIA (messages de statut)
    aria_live = soup.select('[aria-live], [role="alert"], [role="log"], [role="status"]')
    
    has_scripts = has_js_files or has_inline_js or len(event_handlers) > 0 or len(aria_widgets) > 0
    
    return {
        'present': has_scripts,
        'has_js_files': has_js_files,
        'has_inline_js': has_inline_js,
        'event_handlers': event_handlers,
        'aria_widgets': aria_widgets,
        'aria_live': aria_live,
        'has_status_messages': len(aria_live) > 0
    }
```

#### Critères concernés si absence de scripts
| Critère | Condition NA |
|---------|-------------|
| 7.1 | NA si aucun script générant/contrôlant composant d'interface |
| 7.2 | NA si aucun script avec alternative |
| 7.3 | NA si aucun élément avec gestionnaire d'événement |
| 7.4 | NA si aucun script initiant changement de contexte |
| 7.5 | NA si aucun message de statut (aria-live, role="status", etc.) |

---

### Thème 8 : Éléments Obligatoires

#### Logique de détection
```python
def detect_mandatory_elements(soup):
    """Les éléments obligatoires sont TOUJOURS applicables."""
    return {
        'present': True,  # Toujours applicable
        'doctype': True,  # Toute page a un doctype (ou devrait)
        'html': soup.find('html') is not None,
        'lang': soup.find('html', attrs={'lang': True}) is not None,
        'title': soup.find('title') is not None
    }
```

#### Critères concernés
| Critère | Condition NA |
|---------|-------------|
| 8.1 | Jamais NA |
| 8.2 | Jamais NA |
| 8.3 | Jamais NA |
| 8.4 | Jamais NA |
| 8.5 | Jamais NA |
| 8.6 | Jamais NA |
| 8.7 | NA si aucun changement de langue dans le contenu |
| 8.8 | NA si aucun changement de langue |
| 8.9 | Jamais NA |
| 8.10 | NA si aucun contenu avec sens de lecture différent (RTL/LTR) |

---

### Thème 9 : Structuration de l'Information

#### Sélecteurs de détection
```python
STRUCTURE_SELECTORS = {
    'headings': 'h1, h2, h3, h4, h5, h6, [role="heading"]',
    'lists': 'ul, ol, dl, [role="list"]',
    'quotes': 'blockquote, q'
}
```

#### Logique de détection
```python
def detect_structure(soup):
    """Détecte les éléments de structure."""
    headings = soup.select('h1, h2, h3, h4, h5, h6, [role="heading"]')
    lists = soup.select('ul, ol, dl, [role="list"]')
    quotes = soup.select('blockquote, q')
    
    # Structure HTML5
    header = soup.select('header')
    nav = soup.select('nav')
    main = soup.select('main')
    footer = soup.select('footer')
    
    return {
        'headings_present': len(headings) > 0,
        'lists_present': len(lists) > 0,
        'quotes_present': len(quotes) > 0,
        'has_html5_structure': any([header, nav, main, footer]),
        'elements': {
            'headings': headings,
            'lists': lists,
            'quotes': quotes
        }
    }
```

#### Critères concernés
| Critère | Condition NA |
|---------|-------------|
| 9.1 | Jamais NA (toute page devrait avoir des titres) |
| 9.2 | NA si DOCTYPE n'est pas HTML5 |
| 9.3 | NA si aucune liste visuelle |
| 9.4 | NA si aucune citation |

---

### Thème 10 : Présentation de l'Information

#### Logique de détection
```python
def detect_presentation(soup):
    """La présentation est TOUJOURS applicable."""
    
    # Contenus cachés
    hidden_content = soup.select('[hidden], [aria-hidden], [style*="display:none"], [style*="visibility:hidden"]')
    
    # Contenus additionnels (survol/focus)
    hover_focus_content = soup.select('[aria-expanded], [aria-haspopup], .tooltip, .dropdown, .modal')
    
    return {
        'present': True,  # Toujours applicable
        'has_hidden_content': len(hidden_content) > 0,
        'has_hover_focus_content': len(hover_focus_content) > 0
    }
```

#### Critères concernés
| Critère | Condition NA |
|---------|-------------|
| 10.1 | Jamais NA |
| 10.2 | Jamais NA |
| 10.3 | Jamais NA |
| 10.4 | Jamais NA |
| 10.5 | Jamais NA |
| 10.6 | NA si aucun lien dont la nature n'est pas évidente |
| 10.7 | Jamais NA (focus toujours applicable) |
| 10.8 | NA si aucun contenu caché |
| 10.9 | Jamais NA |
| 10.10 | Jamais NA |
| 10.11 | Jamais NA |
| 10.12 | Jamais NA |
| 10.13 | NA si aucun contenu additionnel au survol/focus |
| 10.14 | NA si aucun contenu additionnel CSS au survol/focus |

---

### Thème 11 : Formulaires

#### Sélecteurs de détection
```python
FORM_SELECTORS = {
    'form': 'form, [role="form"]',
    'inputs': 'input:not([type="hidden"]), textarea, select',
    'buttons': 'button, input[type="submit"], input[type="reset"], input[type="button"], input[type="image"], [role="button"]',
    'fieldsets': 'fieldset, [role="group"], [role="radiogroup"]',
    'labels': 'label',
    'aria_fields': '[role="textbox"], [role="searchbox"], [role="combobox"], [role="listbox"], [role="checkbox"], [role="radio"], [role="switch"], [role="slider"], [role="spinbutton"]'
}
```

#### Logique de détection
```python
def detect_forms(soup):
    """Détecte la présence de formulaires sur la page."""
    
    forms = soup.select('form, [role="form"]')
    inputs = soup.select('input:not([type="hidden"]), textarea, select')
    aria_fields = soup.select('[role="textbox"], [role="searchbox"], [role="combobox"], [role="listbox"], [role="checkbox"], [role="radio"], [role="switch"], [role="slider"], [role="spinbutton"]')
    buttons = soup.select('button, input[type="submit"], input[type="reset"], input[type="button"], input[type="image"]')
    fieldsets = soup.select('fieldset, [role="group"], [role="radiogroup"]')
    
    # Champs avec autocomplete potentiel
    autocomplete_fields = soup.select('input[type="text"], input[type="email"], input[type="tel"], input[type="url"], input[type="password"], input[name]')
    
    has_forms = len(forms) > 0 or len(inputs) > 0 or len(aria_fields) > 0
    
    return {
        'present': has_forms,
        'forms': forms,
        'inputs': inputs,
        'aria_fields': aria_fields,
        'buttons': buttons,
        'fieldsets': fieldsets,
        'has_fieldsets': len(fieldsets) > 0,
        'has_autocomplete_candidates': len(autocomplete_fields) > 0,
        'count': len(inputs) + len(aria_fields)
    }
```

#### Critères concernés si absence de formulaires
| Critère | Condition NA |
|---------|-------------|
| 11.1 | NA si aucun champ de formulaire |
| 11.2 | NA si aucun champ avec étiquette |
| 11.3 | NA si aucun champ répété |
| 11.4 | NA si aucun champ avec étiquette |
| 11.5 | NA si aucun champ de même nature à regrouper |
| 11.6 | NA si aucun regroupement de champs |
| 11.7 | NA si aucun regroupement avec légende |
| 11.8 | NA si aucun select avec items à regrouper |
| 11.9 | NA si aucun bouton |
| 11.10 | NA si aucun formulaire avec contrôle de saisie |
| 11.11 | NA si aucun formulaire avec erreurs possibles |
| 11.12 | NA si aucun formulaire à conséquences (financières, juridiques, données) |
| 11.13 | NA si aucun champ concernant l'utilisateur |

---

### Thème 12 : Navigation

#### Sélecteurs de détection
```python
NAVIGATION_SELECTORS = {
    'nav': 'nav, [role="navigation"]',
    'skip_links': 'a[href^="#"]',
    'landmarks': '[role="banner"], [role="main"], [role="contentinfo"], [role="search"], [role="navigation"]',
    'sitemap_link': 'a[href*="plan"], a[href*="sitemap"]',
    'search': '[role="search"], form[action*="search"], input[type="search"]'
}
```

#### Logique de détection
```python
def detect_navigation(soup):
    """Détecte les éléments de navigation."""
    
    nav = soup.select('nav, [role="navigation"]')
    skip_links = soup.select('a[href^="#"]')
    landmarks = soup.select('[role="banner"], [role="main"], [role="contentinfo"], [role="search"]')
    search = soup.select('[role="search"], form[action*="search"], input[type="search"]')
    
    # Raccourcis clavier
    accesskeys = soup.select('[accesskey]')
    
    return {
        'has_navigation': len(nav) > 0,
        'has_skip_links': len(skip_links) > 0,
        'has_landmarks': len(landmarks) > 0,
        'has_search': len(search) > 0,
        'has_accesskeys': len(accesskeys) > 0,
        'elements': {
            'nav': nav,
            'skip_links': skip_links,
            'landmarks': landmarks,
            'search': search
        }
    }
```

#### Critères concernés
| Critère | Condition NA |
|---------|-------------|
| 12.1 | NA si site d'une seule page |
| 12.2 | NA si page d'accueil seule ou site une page |
| 12.3 | NA si pas de plan du site |
| 12.4 | NA si pas de plan du site |
| 12.5 | NA si pas de moteur de recherche |
| 12.6 | NA si aucune zone de regroupement |
| 12.7 | NA si site d'une seule page |
| 12.8 | Jamais NA |
| 12.9 | Jamais NA |
| 12.10 | NA si aucun raccourci clavier à une touche |
| 12.11 | NA si aucun contenu additionnel au survol/focus/activation |

---

### Thème 13 : Consultation

#### Sélecteurs de détection
```python
CONSULTATION_SELECTORS = {
    'refresh': 'meta[http-equiv="refresh"]',
    'auto_play': 'video[autoplay], audio[autoplay]',
    'downloads': 'a[href$=".pdf"], a[href$=".doc"], a[href$=".docx"], a[href$=".xls"], a[href$=".xlsx"], a[href$=".odt"], a[href$=".ods"]',
    'cryptic': '[title], abbr',
    'animations': 'marquee, blink, [style*="animation"]',
    'flashing': 'blink, [style*="animation"]'
}
```

#### Logique de détection
```python
def detect_consultation(soup):
    """Détecte les éléments de consultation."""
    
    refresh = soup.select('meta[http-equiv="refresh"]')
    auto_play = soup.select('video[autoplay], audio[autoplay]')
    downloads = soup.select('a[href$=".pdf"], a[href$=".doc"], a[href$=".docx"], a[href$=".xls"], a[href$=".xlsx"], a[href$=".odt"], a[href$=".ods"], a[href$=".ppt"], a[href$=".pptx"]')
    animations = soup.select('[style*="animation"], .animate, .animated')
    
    return {
        'has_refresh': len(refresh) > 0,
        'has_auto_play': len(auto_play) > 0,
        'has_downloads': len(downloads) > 0,
        'has_animations': len(animations) > 0,
        'elements': {
            'refresh': refresh,
            'auto_play': auto_play,
            'downloads': downloads,
            'animations': animations
        }
    }
```

#### Critères concernés
| Critère | Condition NA |
|---------|-------------|
| 13.1 | NA si aucune limite de temps |
| 13.2 | NA (toujours vérifier qu'aucune fenêtre ne s'ouvre automatiquement) |
| 13.3 | NA si aucun document bureautique en téléchargement |
| 13.4 | NA si aucun document bureautique avec version accessible |
| 13.5 | NA si aucun contenu cryptique |
| 13.6 | NA si aucun contenu cryptique avec alternative |
| 13.7 | NA si aucun effet de flash/luminosité |
| 13.8 | NA si aucun contenu en mouvement/clignotant |
| 13.9 | Jamais NA |
| 13.10 | NA si aucune fonctionnalité avec geste complexe |
| 13.11 | NA si aucune action par dispositif de pointage |
| 13.12 | NA si aucune fonctionnalité impliquant mouvement appareil |

---

## Implémentation : Classe de Détection Globale

```python
class ContentDetector:
    """Détecte tous les types de contenu sur une page pour déterminer les critères NA."""
    
    def __init__(self, soup):
        self.soup = soup
        self.results = {}
        
    def detect_all(self):
        """Exécute toutes les détections."""
        self.results = {
            'images': self.detect_images(),
            'frames': self.detect_frames(),
            'colors': self.detect_color_context(),
            'media': self.detect_media(),
            'tables': self.detect_tables(),
            'links': self.detect_links(),
            'scripts': self.detect_scripts(),
            'mandatory': self.detect_mandatory_elements(),
            'structure': self.detect_structure(),
            'presentation': self.detect_presentation(),
            'forms': self.detect_forms(),
            'navigation': self.detect_navigation(),
            'consultation': self.detect_consultation()
        }
        return self.results
    
    def get_na_criteria(self):
        """Retourne la liste des critères NA basés sur la détection."""
        na_criteria = []
        
        # Images (Thème 1)
        if not self.results['images']['present']:
            na_criteria.extend(['1.1', '1.2', '1.3', '1.4', '1.5', '1.6', '1.7', '1.8', '1.9'])
        
        # Cadres (Thème 2)
        if not self.results['frames']['present']:
            na_criteria.extend(['2.1', '2.2'])
        
        # Multimédia (Thème 4)
        if not self.results['media']['temporal_present']:
            na_criteria.extend(['4.1', '4.2', '4.3', '4.4', '4.5', '4.6', '4.7', '4.11', '4.13'])
        if not self.results['media']['non_temporal_present']:
            na_criteria.extend(['4.8', '4.9', '4.12'])
            
        # Tableaux (Thème 5)
        if not self.results['tables']['present']:
            na_criteria.extend(['5.1', '5.2', '5.3', '5.4', '5.5', '5.6', '5.7', '5.8'])
        
        # Liens (Thème 6)
        if not self.results['links']['present']:
            na_criteria.extend(['6.1', '6.2'])
        
        # Scripts (Thème 7)
        if not self.results['scripts']['present']:
            na_criteria.extend(['7.1', '7.2', '7.3', '7.4'])
        if not self.results['scripts']['has_status_messages']:
            na_criteria.append('7.5')
        
        # Structure (Thème 9)
        if not self.results['structure']['quotes_present']:
            na_criteria.append('9.4')
        
        # Formulaires (Thème 11)
        if not self.results['forms']['present']:
            na_criteria.extend(['11.1', '11.2', '11.3', '11.4', '11.5', '11.6', '11.7', '11.8', '11.9', '11.10', '11.11', '11.12', '11.13'])
        
        # Consultation (Thème 13)
        if not self.results['consultation']['has_downloads']:
            na_criteria.extend(['13.3', '13.4'])
        if not self.results['consultation']['has_animations']:
            na_criteria.extend(['13.7', '13.8'])
        
        return sorted(set(na_criteria), key=lambda x: (int(x.split('.')[0]), int(x.split('.')[1])))
    
    def generate_na_report(self):
        """Génère un rapport des critères NA avec justifications."""
        na_criteria = self.get_na_criteria()
        report = []
        
        for criterion in na_criteria:
            theme = criterion.split('.')[0]
            reason = self._get_na_reason(criterion)
            report.append({
                'criterion': criterion,
                'theme': theme,
                'status': 'NA',
                'reason': reason,
                'auto_detected': True
            })
        
        return report
    
    def _get_na_reason(self, criterion):
        """Retourne la raison du NA pour un critère donné."""
        theme = criterion.split('.')[0]
        
        reasons = {
            '1': "Aucune image détectée sur la page",
            '2': "Aucun cadre (iframe/frame) détecté sur la page",
            '4': "Aucun média temporel ou non temporel détecté sur la page",
            '5': "Aucun tableau détecté sur la page",
            '6': "Aucun lien détecté sur la page",
            '7': "Aucun script ou composant JavaScript détecté sur la page",
            '9.4': "Aucune citation détectée sur la page",
            '11': "Aucun formulaire ni champ de saisie détecté sur la page",
            '13.3': "Aucun document bureautique en téléchargement détecté",
            '13.4': "Aucun document bureautique en téléchargement détecté",
            '13.7': "Aucun effet de flash ou changement brusque de luminosité détecté",
            '13.8': "Aucun contenu en mouvement ou clignotant détecté"
        }
        
        # Chercher la raison spécifique ou générique
        if criterion in reasons:
            return reasons[criterion]
        elif theme in reasons:
            return reasons[theme]
        else:
            return "Objet de test absent de la page"
```

---

## Intégration dans la Grille d'Audit ODS

### Mise à jour automatique de la grille

```python
def update_ods_with_na(ods_path, url, na_results):
    """Met à jour la grille ODS avec les statuts NA détectés automatiquement."""
    
    from odf.opendocument import load
    from odf.table import Table, TableRow, TableCell
    from odf.text import P
    
    doc = load(ods_path)
    
    # Trouver la feuille de la page
    sheet = find_or_create_page_sheet(doc, url)
    
    for na_item in na_results:
        criterion = na_item['criterion']
        reason = na_item['reason']
        
        # Trouver la ligne du critère
        row = find_criterion_row(sheet, criterion)
        if row:
            # Colonne C : Statut
            status_cell = row.getElementsByType(TableCell)[2]  # Index 2 = Colonne C
            clear_cell(status_cell)
            status_cell.addElement(P(text="NA"))
            
            # Colonne D : Commentaire/Raison
            comment_cell = row.getElementsByType(TableCell)[3]  # Index 3 = Colonne D
            clear_cell(comment_cell)
            comment_cell.addElement(P(text=f"[Auto-détecté] {reason}"))
    
    doc.save(ods_path)
```

---

## Format du Rapport de Détection

### Rapport Markdown

```markdown
# Rapport de Détection NA - [URL]

## Résumé de la Détection

| Type de Contenu | Présent | Nombre | Critères NA |
|-----------------|---------|--------|-------------|
| Images | ❌ Non | 0 | 1.1-1.9 |
| Cadres | ❌ Non | 0 | 2.1-2.2 |
| Médias | ❌ Non | 0 | 4.1-4.13 |
| Tableaux | ✅ Oui | 3 | - |
| Liens | ✅ Oui | 45 | - |
| Scripts | ❌ Non | 0 | 7.1-7.5 |
| Formulaires | ❌ Non | 0 | 11.1-11.13 |

## Critères Marqués NA

### Thème 1 : Images
- **1.1** : NA - Aucune image détectée sur la page
- **1.2** : NA - Aucune image détectée sur la page
[...]

### Thème 7 : Scripts  
- **7.1** : NA - Aucun script ou composant JavaScript détecté
[...]

## Éléments Détectés (pour tests applicables)

### Tableaux (3 éléments)
1. Tableau de données à la ligne 45
2. Tableau de mise en forme à la ligne 120
3. Tableau de données complexe à la ligne 200

### Liens (45 éléments)
- 40 liens texte
- 3 liens image
- 2 liens composites
```

---

## Règles de Précaution

### Ne jamais marquer NA automatiquement pour :

1. **Critères toujours applicables** :
   - 3.1, 3.2 (couleurs/contraste texte)
   - 8.1-8.6, 8.9 (éléments obligatoires)
   - 10.1-10.5, 10.7, 10.9-10.12 (présentation)
   - 12.8, 12.9 (navigation clavier)
   - 13.9 (orientation écran)

2. **Critères nécessitant analyse manuelle** :
   - Même si aucun élément n'est détecté, certains critères peuvent s'appliquer à du contenu généré dynamiquement

### Alerte pour vérification manuelle

```python
MANUAL_VERIFICATION_NEEDED = [
    "Scripts détectés mais widgets ARIA potentiellement manquants",
    "Formulaire sans contrôle de saisie visible",
    "Liens sans intitulé visible détectés",
    "Tableaux ambigus (données vs mise en forme)"
]
```

---

## Exemple d'Utilisation Complète

```python
from bs4 import BeautifulSoup
import requests

def audit_page_with_na_detection(url, ods_path):
    """Effectue un audit avec détection automatique des NA."""
    
    # 1. Récupérer la page
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # 2. Détecter le contenu
    detector = ContentDetector(soup)
    detector.detect_all()
    
    # 3. Obtenir les critères NA
    na_report = detector.generate_na_report()
    
    # 4. Mettre à jour la grille ODS
    update_ods_with_na(ods_path, url, na_report)
    
    # 5. Générer le rapport
    print(f"Détection terminée pour {url}")
    print(f"Critères NA automatiques : {len(na_report)}")
    
    for item in na_report:
        print(f"  - {item['criterion']}: {item['reason']}")
    
    # 6. Retourner les critères à tester manuellement
    all_criteria = get_all_rgaa_criteria()  # Liste des 106 critères
    na_ids = [item['criterion'] for item in na_report]
    to_test = [c for c in all_criteria if c not in na_ids]
    
    print(f"Critères à tester : {len(to_test)}")
    return to_test

# Exécution
remaining_criteria = audit_page_with_na_detection(
    "https://example.com/page",
    "/path/to/grilleAudit.ods"
)
```

---

## Notes Importantes

1. **La détection NA est une première passe** : Elle accélère l'audit mais ne remplace pas la vérification humaine finale.

2. **Contenu dynamique** : Si du JavaScript charge du contenu dynamiquement, la détection initiale peut être incomplète. Il faut attendre le chargement complet.

3. **Documenter les NA** : Toujours indiquer dans la colonne commentaire que le NA a été détecté automatiquement.

4. **Réévaluation possible** : Si l'auditeur découvre du contenu non détecté, il peut passer le critère de NA à C/NC.
