# CLAUDE CODE — Instructions d'implémentation : Critère RGAA 10.7 — Visibilité du focus

## 1. Contexte et objectif

### 1.1 Critère RGAA concerné

**Critère 10.7** — *"Dans chaque page web, pour chaque élément recevant le focus, la prise de focus est-elle visible ?"*

**Test 10.7.1** — Pour chaque élément recevant le focus, la prise de focus vérifie-t-elle une de ces conditions :
- Le style du focus natif du navigateur n'est pas supprimé ou dégradé ;
- Un style du focus défini par l'auteur est visible.

**Références WCAG** : 2.4.7 Focus Visible (AA), 1.4.1 Use of Color (A)

**Techniques WCAG pertinentes** : C15, F73, F78, G149, G165, G183, G195, SCR31

### 1.2 Objectif de l'outil

Créer un module Python intégré à l'outil existant `rgaa-section2-tester` qui automatise partiellement le test du critère 10.7. Ce module doit :

1. Détecter tous les éléments focusables d'une page web
2. Analyser les styles CSS appliqués au focus (`:focus`, `:focus-visible`, `:focus-within`)
3. Identifier les suppressions de focus (`outline: none`, `outline: 0`, etc.)
4. Vérifier la présence de styles de focus compensatoires (box-shadow, border, background, etc.)
5. Évaluer automatiquement les cas clairs (suppression sans compensation = NC, focus natif préservé = C)
6. Signaler les cas ambigus nécessitant une vérification humaine
7. Générer un rapport Markdown détaillé par page

### 1.3 Couverture automatisée estimée

| Cas | Détection auto | Confiance | Statut auto |
|-----|---------------|-----------|-------------|
| `outline: none/0` sans compensation | Oui | ~95% | **NC** |
| Focus natif préservé (aucune règle CSS supprimant outline) | Oui | ~90% | **C** |
| Style custom focus visible (box-shadow, border ajoutés sur :focus) | Oui | ~70% | **C (à confirmer)** |
| Style custom subtil (couleur légère, ombre faible) | Détection partielle | ~40% | **À vérifier** |
| Focus dynamique via JavaScript | Non fiable | ~20% | **À vérifier** |

**Couverture globale estimée : 50-60% des cas résolus automatiquement avec haute confiance.**

---

## 2. Architecture technique

### 2.1 Structure des fichiers

Ajouter les fichiers suivants dans le répertoire existant `rgaa-section2-tester/` :

```
rgaa-section2-tester/
├── criterion_10_7/
│   ├── __init__.py
│   ├── focus_detector.py        # Détection des éléments focusables
│   ├── css_analyzer.py          # Analyse des styles CSS focus
│   ├── focus_tester.py          # Orchestrateur de test complet
│   ├── report_generator.py      # Génération du rapport Markdown
│   └── constants.py             # Constantes et sélecteurs
├── test_criterion_10_7.py       # Point d'entrée avec GUI tkinter
└── ... (fichiers existants)
```

### 2.2 Dépendances Python

```python
# Dépendances requises (à ajouter au requirements.txt existant)
playwright>=1.40.0    # Headless browser pour inspection des styles computés
cssutils>=2.9.0       # Parsing CSS (optionnel, pour analyse statique des feuilles)
```

**Note** : Playwright est préféré à Selenium pour sa capacité native à évaluer les computed styles et à simuler le focus programmatiquement via `element.focus()`.

### 2.3 Flux d'exécution principal

```
URL de la page
    │
    ▼
[1. Chargement Playwright]
    │
    ▼
[2. Inventaire éléments focusables]  ──► Liste des éléments + sélecteurs
    │
    ▼
[3. Analyse CSS statique]  ──► Détection rules outline:none, :focus, :focus-visible
    │
    ▼
[4. Analyse dynamique par élément]
    │   Pour chaque élément focusable :
    │   a. Capturer computed styles SANS focus
    │   b. Appliquer focus() programmatique
    │   c. Capturer computed styles AVEC focus
    │   d. Comparer les différences visuelles
    │
    ▼
[5. Classification]
    │   - CONFORME : focus natif préservé OU style custom détecté
    │   - NON CONFORME : outline supprimé sans compensation
    │   - À VÉRIFIER : cas ambigus
    │
    ▼
[6. Rapport Markdown + suggestion statut grille ODS]
```

---

## 3. Spécifications détaillées des modules

### 3.1 `constants.py` — Constantes et sélecteurs

```python
"""
Constantes pour le test du critère RGAA 10.7 — Visibilité du focus
"""

# Sélecteurs CSS des éléments nativement focusables (HTML)
NATIVE_FOCUSABLE_SELECTORS = [
    'a[href]',
    'button:not([disabled])',
    'input:not([disabled]):not([type="hidden"])',
    'select:not([disabled])',
    'textarea:not([disabled])',
    'area[href]',
    '[tabindex]',              # Tout élément avec tabindex (y compris -1)
    'summary',
    'details',
    'audio[controls]',
    'video[controls]',
]

# Sélecteur combiné pour requête unique
FOCUSABLE_SELECTOR = ', '.join(NATIVE_FOCUSABLE_SELECTORS)

# Éléments avec tabindex négatif (focusables par script mais pas par Tab)
# On les inclut car le critère 10.7 couvre TOUT élément recevant le focus
TABINDEX_NEGATIVE_NOTE = "tabindex='-1' : focusable par script/clic, pas par Tab"

# Propriétés CSS à comparer entre état normal et état focus
FOCUS_VISUAL_PROPERTIES = [
    'outline-style',
    'outline-width',
    'outline-color',
    'outline-offset',
    'outline',
    'box-shadow',
    'border-top-color',
    'border-right-color',
    'border-bottom-color',
    'border-left-color',
    'border-top-width',
    'border-right-width',
    'border-bottom-width',
    'border-left-width',
    'border-top-style',
    'border-right-style',
    'border-bottom-style',
    'border-left-style',
    'background-color',
    'color',
    'text-decoration-line',
    'text-decoration-color',
    'text-decoration-style',
    'transform',
    'opacity',
    'filter',
]

# Patterns CSS indiquant une suppression de focus
OUTLINE_SUPPRESSION_PATTERNS = [
    {'property': 'outline-style', 'value': 'none'},
    {'property': 'outline-width', 'value': '0px'},
    {'property': 'outline', 'value': 'none'},
    {'property': 'outline', 'value': '0'},
    {'property': 'outline', 'value': '0px'},
]

# Propriétés compensatoires : si l'une change au focus, c'est un style custom
COMPENSATORY_PROPERTIES = [
    'box-shadow',
    'border-top-color',
    'border-right-color',
    'border-bottom-color',
    'border-left-color',
    'border-top-width',
    'border-right-width',
    'border-bottom-width',
    'border-left-width',
    'background-color',
    'color',
    'text-decoration-line',
    'transform',
    'opacity',
    'filter',
]

# Seuil de différence de couleur pour considérer un changement visible
# (en luminance relative, selon WCAG)
MIN_CONTRAST_RATIO_FOCUS = 3.0  # Ratio minimum recommandé pour visibilité du focus

# Classification des résultats
class FocusStatus:
    CONFORME = "C"                 # Focus visible, pas de problème détecté
    NON_CONFORME = "NC"            # Suppression de focus sans compensation
    A_VERIFIER = "À_VÉRIFIER"      # Cas ambigu nécessitant vérification humaine
    NON_APPLICABLE = "NA"          # Pas d'éléments focusables sur la page
```

### 3.2 `focus_detector.py` — Détection des éléments focusables

```python
"""
Module de détection des éléments focusables d'une page web.
Utilise Playwright pour identifier tous les éléments pouvant recevoir le focus.
"""

from playwright.sync_api import Page, Locator
from .constants import FOCUSABLE_SELECTOR, NATIVE_FOCUSABLE_SELECTORS


class FocusableElement:
    """Représente un élément focusable détecté sur la page."""
    
    def __init__(self, tag_name: str, selector_path: str, 
                 attributes: dict, text_content: str,
                 is_visible: bool, tabindex: int | None,
                 locator: Locator):
        self.tag_name = tag_name
        self.selector_path = selector_path  # Sélecteur CSS unique
        self.attributes = attributes        # id, class, role, aria-*, etc.
        self.text_content = text_content[:80]  # Tronqué pour le rapport
        self.is_visible = is_visible
        self.tabindex = tabindex
        self.locator = locator
        
        # Résultats d'analyse (remplis par css_analyzer)
        self.styles_normal = {}
        self.styles_focused = {}
        self.outline_suppressed = False
        self.has_custom_focus_style = False
        self.visual_changes = []        # Liste des propriétés qui changent
        self.status = None              # FocusStatus
        self.details = ""               # Explication textuelle
    
    @property
    def identifier(self) -> str:
        """Identifiant lisible pour le rapport."""
        if self.attributes.get('id'):
            return f"{self.tag_name}#{self.attributes['id']}"
        if self.attributes.get('class'):
            classes = self.attributes['class'].split()[:2]
            return f"{self.tag_name}.{'.'.join(classes)}"
        if self.text_content:
            return f"{self.tag_name}['{self.text_content[:30]}']"
        return f"{self.tag_name}({self.selector_path})"


class FocusDetector:
    """Détecte tous les éléments focusables d'une page."""
    
    def __init__(self, page: Page):
        self.page = page
    
    def detect_all(self) -> list[FocusableElement]:
        """
        Détecte tous les éléments focusables de la page.
        
        Retourne une liste de FocusableElement.
        Exclut les éléments :
        - avec display:none ou visibility:hidden (non visibles)
        - à l'intérieur d'éléments aria-hidden="true"
        - de type input[type="hidden"]
        """
        elements = []
        
        # Exécuter le script de détection côté navigateur
        raw_elements = self.page.evaluate('''() => {
            const selector = ''' + f'`{FOCUSABLE_SELECTOR}`' + ''';
            const nodes = document.querySelectorAll(selector);
            const results = [];
            
            for (const node of nodes) {
                // Vérifier la visibilité
                const style = window.getComputedStyle(node);
                const isVisible = style.display !== 'none' 
                    && style.visibility !== 'hidden'
                    && style.opacity !== '0'
                    && node.offsetWidth > 0 
                    && node.offsetHeight > 0;
                
                // Vérifier aria-hidden sur les parents
                let ariaHidden = false;
                let parent = node.parentElement;
                while (parent) {
                    if (parent.getAttribute('aria-hidden') === 'true') {
                        ariaHidden = true;
                        break;
                    }
                    parent = parent.parentElement;
                }
                
                if (ariaHidden) continue;
                
                // Construire un sélecteur unique
                let selectorPath = '';
                if (node.id) {
                    selectorPath = '#' + CSS.escape(node.id);
                } else {
                    // Construire un sélecteur basé sur le chemin
                    const parts = [];
                    let el = node;
                    while (el && el !== document.body) {
                        let part = el.tagName.toLowerCase();
                        if (el.id) {
                            part = '#' + CSS.escape(el.id);
                            parts.unshift(part);
                            break;
                        }
                        const idx = Array.from(el.parentElement?.children || [])
                            .filter(c => c.tagName === el.tagName)
                            .indexOf(el);
                        if (idx > 0) part += ':nth-of-type(' + (idx + 1) + ')';
                        parts.unshift(part);
                        el = el.parentElement;
                    }
                    selectorPath = parts.join(' > ');
                }
                
                // Collecter les attributs pertinents
                const attrs = {};
                for (const attr of ['id', 'class', 'role', 'type', 'href',
                                     'aria-label', 'aria-labelledby', 
                                     'aria-describedby', 'name', 'title']) {
                    if (node.hasAttribute(attr)) {
                        attrs[attr] = node.getAttribute(attr);
                    }
                }
                
                results.push({
                    tagName: node.tagName.toLowerCase(),
                    selectorPath: selectorPath,
                    attributes: attrs,
                    textContent: (node.textContent || '').trim().substring(0, 80),
                    isVisible: isVisible,
                    tabindex: node.hasAttribute('tabindex') 
                        ? parseInt(node.getAttribute('tabindex')) 
                        : null,
                });
            }
            return results;
        }''')
        
        for raw in raw_elements:
            try:
                locator = self.page.locator(raw['selectorPath']).first
                element = FocusableElement(
                    tag_name=raw['tagName'],
                    selector_path=raw['selectorPath'],
                    attributes=raw['attributes'],
                    text_content=raw['textContent'],
                    is_visible=raw['isVisible'],
                    tabindex=raw['tabindex'],
                    locator=locator
                )
                elements.append(element)
            except Exception:
                # Sélecteur invalide, ignorer cet élément
                continue
        
        return elements
    
    def count_by_type(self, elements: list[FocusableElement]) -> dict:
        """Retourne un comptage par type d'élément pour le rapport."""
        counts = {}
        for el in elements:
            key = el.tag_name
            if el.attributes.get('type'):
                key += f'[type={el.attributes["type"]}]'
            counts[key] = counts.get(key, 0) + 1
        return counts
```

### 3.3 `css_analyzer.py` — Analyse des styles CSS au focus

```python
"""
Module d'analyse des styles CSS appliqués au focus.
Compare les computed styles d'un élément avant et après focus()
pour déterminer si un indicateur visuel de focus est présent.
"""

import re
from playwright.sync_api import Page
from .constants import (
    FOCUS_VISUAL_PROPERTIES, 
    OUTLINE_SUPPRESSION_PATTERNS,
    COMPENSATORY_PROPERTIES,
    FocusStatus,
)
from .focus_detector import FocusableElement


class CSSFocusAnalyzer:
    """Analyse les styles CSS de focus pour chaque élément focusable."""
    
    def __init__(self, page: Page):
        self.page = page
    
    def analyze_element(self, element: FocusableElement) -> FocusableElement:
        """
        Analyse un élément focusable :
        1. Capture les computed styles sans focus
        2. Applique le focus
        3. Capture les computed styles avec focus
        4. Compare et classifie
        
        Modifie l'objet element en place et le retourne.
        """
        if not element.is_visible:
            element.status = FocusStatus.A_VERIFIER
            element.details = "Élément non visible — vérification manuelle requise"
            return element
        
        try:
            # Étape 1 : capturer les styles SANS focus
            # D'abord, retirer le focus de tout élément
            self.page.evaluate('() => { if (document.activeElement) document.activeElement.blur(); }')
            
            styles_normal = self._get_computed_styles(element.selector_path)
            element.styles_normal = styles_normal
            
            # Étape 2 : appliquer le focus
            self.page.evaluate(f'''(selector) => {{
                const el = document.querySelector(selector);
                if (el) el.focus();
            }}''', element.selector_path)
            
            # Petit délai pour les transitions CSS
            self.page.wait_for_timeout(100)
            
            # Étape 3 : capturer les styles AVEC focus
            styles_focused = self._get_computed_styles(element.selector_path)
            element.styles_focused = styles_focused
            
            # Étape 4 : analyser les différences
            self._classify_element(element)
            
            # Retirer le focus pour l'élément suivant
            self.page.evaluate('() => { if (document.activeElement) document.activeElement.blur(); }')
            
        except Exception as e:
            element.status = FocusStatus.A_VERIFIER
            element.details = f"Erreur lors de l'analyse : {str(e)}"
        
        return element
    
    def _get_computed_styles(self, selector: str) -> dict:
        """Récupère les computed styles pertinents d'un élément."""
        return self.page.evaluate(f'''(selector) => {{
            const el = document.querySelector(selector);
            if (!el) return {{}};
            const cs = window.getComputedStyle(el);
            const result = {{}};
            const props = {FOCUS_VISUAL_PROPERTIES};
            for (const prop of props) {{
                result[prop] = cs.getPropertyValue(prop);
            }}
            return result;
        }}''', selector)
    
    def _classify_element(self, element: FocusableElement):
        """
        Classifie un élément selon l'analyse de ses styles focus.
        
        Logique de décision :
        
        1. L'outline est-il supprimé au focus ?
           → Vérifier : outline-style == 'none' ou outline-width == '0px'
        
        2. Si supprimé, y a-t-il un style compensatoire ?
           → Vérifier : box-shadow, border, background, etc. changent
        
        3. Si non supprimé, le focus natif est préservé → C
        
        4. Si supprimé sans compensation → NC
        
        5. Si compensation détectée mais subtile → À VÉRIFIER
        """
        normal = element.styles_normal
        focused = element.styles_focused
        
        # Détecter les changements visuels
        visual_changes = []
        for prop in FOCUS_VISUAL_PROPERTIES:
            val_normal = normal.get(prop, '')
            val_focused = focused.get(prop, '')
            if val_normal != val_focused:
                visual_changes.append({
                    'property': prop,
                    'before': val_normal,
                    'after': val_focused,
                })
        element.visual_changes = visual_changes
        
        # Vérifier si outline est supprimé au focus
        outline_style_focused = focused.get('outline-style', '')
        outline_width_focused = focused.get('outline-width', '')
        
        outline_suppressed = (
            outline_style_focused == 'none' 
            or outline_width_focused == '0px'
            or outline_width_focused == '0'
        )
        element.outline_suppressed = outline_suppressed
        
        # Vérifier s'il y a un changement visuel compensatoire
        compensatory_changes = [
            vc for vc in visual_changes 
            if vc['property'] in COMPENSATORY_PROPERTIES
            and vc['before'] != vc['after']
        ]
        element.has_custom_focus_style = len(compensatory_changes) > 0
        
        # --- Classification ---
        
        if not outline_suppressed:
            # Outline natif préservé
            # Vérifier qu'il y a bien un outline visible
            if outline_style_focused not in ('none', '') and outline_width_focused not in ('0px', '0', ''):
                element.status = FocusStatus.CONFORME
                element.details = (
                    f"Focus natif préservé : outline-style={outline_style_focused}, "
                    f"outline-width={outline_width_focused}"
                )
            else:
                # Outline non explicitement supprimé mais pas clairement visible
                if compensatory_changes:
                    element.status = FocusStatus.A_VERIFIER
                    props_changed = ', '.join(c['property'] for c in compensatory_changes)
                    element.details = (
                        f"Style custom détecté ({props_changed}) — "
                        f"vérifier la visibilité suffisante du focus"
                    )
                else:
                    element.status = FocusStatus.A_VERIFIER
                    element.details = "Aucun changement visuel détecté au focus — vérifier manuellement"
        
        elif outline_suppressed and compensatory_changes:
            # Outline supprimé MAIS style compensatoire présent
            # Vérifier si le changement est significatif
            has_significant_change = self._is_change_significant(compensatory_changes)
            
            if has_significant_change:
                element.status = FocusStatus.CONFORME
                props_changed = ', '.join(c['property'] for c in compensatory_changes)
                element.details = (
                    f"Outline supprimé mais style custom visible : {props_changed}. "
                    f"Changements : {self._format_changes(compensatory_changes)}"
                )
            else:
                element.status = FocusStatus.A_VERIFIER
                props_changed = ', '.join(c['property'] for c in compensatory_changes)
                element.details = (
                    f"Outline supprimé, style custom subtil détecté ({props_changed}) — "
                    f"vérifier si suffisamment visible. "
                    f"Changements : {self._format_changes(compensatory_changes)}"
                )
            element.has_custom_focus_style = True
        
        elif outline_suppressed and not compensatory_changes:
            # Outline supprimé et AUCUNE compensation → NON CONFORME
            element.status = FocusStatus.NON_CONFORME
            element.details = (
                f"Outline supprimé (outline-style: {outline_style_focused}, "
                f"outline-width: {outline_width_focused}) "
                f"sans aucun style de focus compensatoire détecté"
            )
        
        else:
            element.status = FocusStatus.A_VERIFIER
            element.details = "Cas non classifié — vérification manuelle requise"
    
    def _is_change_significant(self, changes: list[dict]) -> bool:
        """
        Évalue si les changements visuels sont suffisamment significatifs
        pour constituer un indicateur de focus visible.
        
        Heuristiques :
        - box-shadow ajouté (de 'none' à une valeur) → significatif
        - border-width augmenté → significatif  
        - background-color changé significativement → significatif
        - Changement de couleur seul → peut être insuffisant (à vérifier)
        """
        for change in changes:
            prop = change['property']
            before = change['before']
            after = change['after']
            
            # box-shadow ajouté
            if prop == 'box-shadow' and before == 'none' and after != 'none':
                return True
            
            # border-width augmenté
            if 'border' in prop and 'width' in prop:
                try:
                    before_px = float(re.sub(r'[^0-9.]', '', before or '0'))
                    after_px = float(re.sub(r'[^0-9.]', '', after or '0'))
                    if after_px > before_px:
                        return True
                except ValueError:
                    pass
            
            # background-color changé
            if prop == 'background-color' and before != after:
                return True
            
            # text-decoration ajouté
            if prop == 'text-decoration-line' and before == 'none' and after != 'none':
                return True
            
            # transform ajouté
            if prop == 'transform' and before == 'none' and after != 'none':
                return True
        
        return False
    
    def _format_changes(self, changes: list[dict]) -> str:
        """Formate les changements pour le rapport."""
        parts = []
        for c in changes[:5]:  # Limiter à 5 pour lisibilité
            parts.append(f"{c['property']}: {c['before']} → {c['after']}")
        return '; '.join(parts)
    
    def analyze_stylesheet_rules(self) -> dict:
        """
        Analyse statique des feuilles de style pour détecter les règles
        globales de suppression de focus.
        
        Retourne un dict avec :
        - global_outline_none: bool (présence de * { outline: none } ou similaire)
        - focus_rules: list des règles CSS contenant :focus
        - suppression_rules: list des règles supprimant l'outline
        """
        return self.page.evaluate('''() => {
            const result = {
                global_outline_none: false,
                focus_rules: [],
                suppression_rules: [],
                custom_focus_rules: [],
            };
            
            try {
                for (const sheet of document.styleSheets) {
                    try {
                        const rules = sheet.cssRules || sheet.rules;
                        for (const rule of rules) {
                            if (rule.type !== 1) continue;  // CSSStyleRule only
                            
                            const selector = rule.selectorText || '';
                            const cssText = rule.cssText || '';
                            
                            // Détecter les règles :focus
                            if (selector.includes(':focus')) {
                                result.focus_rules.push({
                                    selector: selector,
                                    cssText: cssText.substring(0, 500),
                                });
                                
                                // Vérifier suppression outline dans :focus
                                if (rule.style.outlineStyle === 'none' 
                                    || rule.style.outlineWidth === '0px'
                                    || rule.style.outlineWidth === '0'
                                    || rule.style.outline === 'none'
                                    || rule.style.outline === '0') {
                                    result.suppression_rules.push({
                                        selector: selector,
                                        cssText: cssText.substring(0, 500),
                                    });
                                }
                                
                                // Vérifier présence de styles compensatoires
                                if (rule.style.boxShadow 
                                    || rule.style.borderColor 
                                    || rule.style.backgroundColor
                                    || rule.style.textDecoration) {
                                    result.custom_focus_rules.push({
                                        selector: selector,
                                        cssText: cssText.substring(0, 500),
                                    });
                                }
                            }
                            
                            // Détecter suppression globale
                            if ((selector === '*' || selector === '*:focus' 
                                 || selector === ':focus')
                                && (rule.style.outlineStyle === 'none'
                                    || rule.style.outline === 'none'
                                    || rule.style.outline === '0')) {
                                result.global_outline_none = true;
                            }
                        }
                    } catch (e) {
                        // CORS : feuille externe inaccessible
                        continue;
                    }
                }
            } catch (e) {
                // Erreur globale
            }
            
            return result;
        }''')
```

### 3.4 `focus_tester.py` — Orchestrateur principal

```python
"""
Orchestrateur du test RGAA 10.7 — Visibilité du focus.
Coordonne la détection, l'analyse et la classification.
"""

from dataclasses import dataclass, field
from playwright.sync_api import sync_playwright, Page, Browser
from .focus_detector import FocusDetector, FocusableElement
from .css_analyzer import CSSFocusAnalyzer
from .constants import FocusStatus
from .report_generator import FocusReportGenerator


@dataclass
class PageFocusResult:
    """Résultat complet de l'analyse d'une page."""
    url: str
    page_id: str               # ex: "P01"
    total_focusable: int = 0
    total_visible: int = 0
    total_conforme: int = 0
    total_non_conforme: int = 0
    total_a_verifier: int = 0
    elements: list = field(default_factory=list)
    stylesheet_analysis: dict = field(default_factory=dict)
    suggested_status: str = ""  # Statut suggéré pour la grille ODS
    confidence: str = ""        # "haute", "moyenne", "faible"
    details: str = ""
    
    def compute_suggested_status(self):
        """
        Détermine le statut suggéré pour la grille ODS.
        
        Logique :
        - Si au moins 1 NC et 0 À_VÉRIFIER → NC (haute confiance)
        - Si 0 NC et 0 À_VÉRIFIER et >0 C → C (haute confiance)
        - Si des À_VÉRIFIER existent → NT ou C/NC selon proportions (faible confiance)
        - Si 0 éléments focusables → NA
        """
        if self.total_focusable == 0 or self.total_visible == 0:
            self.suggested_status = FocusStatus.NON_APPLICABLE
            self.confidence = "haute"
            self.details = "Aucun élément focusable visible détecté"
            return
        
        if self.total_non_conforme > 0 and self.total_a_verifier == 0:
            self.suggested_status = FocusStatus.NON_CONFORME
            self.confidence = "haute"
            self.details = (
                f"{self.total_non_conforme} élément(s) avec outline supprimé "
                f"sans compensation détectée"
            )
        elif self.total_non_conforme == 0 and self.total_a_verifier == 0:
            self.suggested_status = FocusStatus.CONFORME
            self.confidence = "haute"
            self.details = (
                f"Tous les {self.total_conforme} éléments analysés ont un "
                f"indicateur de focus visible"
            )
        elif self.total_non_conforme > 0 and self.total_a_verifier > 0:
            self.suggested_status = FocusStatus.NON_CONFORME
            self.confidence = "moyenne"
            self.details = (
                f"{self.total_non_conforme} NC confirmé(s), "
                f"{self.total_a_verifier} à vérifier manuellement"
            )
        else:
            # Que des À_VÉRIFIER, pas de NC
            self.suggested_status = FocusStatus.A_VERIFIER
            self.confidence = "faible"
            self.details = (
                f"{self.total_a_verifier} élément(s) nécessitent une "
                f"vérification manuelle"
            )


class FocusTester:
    """
    Testeur principal pour le critère RGAA 10.7.
    
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
        Teste une page complète pour le critère 10.7.
        
        Args:
            url: URL de la page à tester
            page_id: Identifiant de la page (ex: "P01")
            progress_callback: Fonction optionnelle (message: str, percent: float)
        
        Returns:
            PageFocusResult avec tous les détails
        """
        result = PageFocusResult(url=url, page_id=page_id)
        
        page = self._browser.new_page()
        try:
            # Charger la page
            if progress_callback:
                progress_callback(f"Chargement de {url}...", 0.0)
            
            page.goto(url, wait_until='networkidle', timeout=30000)
            page.wait_for_timeout(1000)  # Attendre les scripts dynamiques
            
            # Étape 1 : Analyse des feuilles de style
            if progress_callback:
                progress_callback("Analyse des feuilles de style...", 0.1)
            
            analyzer = CSSFocusAnalyzer(page)
            result.stylesheet_analysis = analyzer.analyze_stylesheet_rules()
            
            # Étape 2 : Détecter les éléments focusables
            if progress_callback:
                progress_callback("Détection des éléments focusables...", 0.2)
            
            detector = FocusDetector(page)
            elements = detector.detect_all()
            result.total_focusable = len(elements)
            
            visible_elements = [e for e in elements if e.is_visible]
            result.total_visible = len(visible_elements)
            
            if not visible_elements:
                result.suggested_status = FocusStatus.NON_APPLICABLE
                result.confidence = "haute"
                result.details = "Aucun élément focusable visible"
                return result
            
            # Étape 3 : Analyser chaque élément
            for i, element in enumerate(visible_elements):
                if progress_callback:
                    pct = 0.2 + (0.7 * (i / len(visible_elements)))
                    progress_callback(
                        f"Analyse élément {i+1}/{len(visible_elements)} : "
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
            
            # Étape 4 : Calculer le statut suggéré
            result.compute_suggested_status()
            
            if progress_callback:
                progress_callback("Analyse terminée", 1.0)
            
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
```

### 3.5 `report_generator.py` — Génération du rapport Markdown

```python
"""
Génération du rapport Markdown pour le critère 10.7.
Suit le format ISIT de rapport d'audit RGAA.
"""

from datetime import datetime
from .focus_tester import PageFocusResult
from .constants import FocusStatus


class FocusReportGenerator:
    """Génère le rapport d'analyse du critère 10.7."""
    
    def generate(self, results: list[PageFocusResult], 
                 output_path: str,
                 site_name: str = "Site audité"):
        """
        Génère un rapport Markdown complet.
        """
        lines = []
        
        # En-tête
        lines.append(f"# Rapport d'analyse automatisée — Critère RGAA 10.7")
        lines.append(f"# Visibilité du focus")
        lines.append("")
        lines.append(f"**Site** : {site_name}")
        lines.append(f"**Date d'analyse** : {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        lines.append(f"**Outil** : RGAA Focus Tester (analyse automatisée)")
        lines.append(f"**Pages analysées** : {len(results)}")
        lines.append("")
        
        # Avertissement légal
        lines.append("---")
        lines.append("")
        lines.append("## ⚠️ Avertissement — Limites de l'analyse automatisée")
        lines.append("")
        lines.append(
            "Ce rapport est généré par un outil d'analyse automatisée. "
            "**Il ne constitue pas un audit complet** du critère RGAA 10.7. "
            "Les limitations suivantes s'appliquent :"
        )
        lines.append("")
        lines.append(
            "- **Détection fiable** : suppression de l'outline CSS "
            "(`outline: none`, `outline: 0`) sans style compensatoire. "
            "Ces cas sont identifiés comme Non Conformes avec haute confiance."
        )
        lines.append(
            "- **Détection partielle** : styles de focus personnalisés "
            "(box-shadow, border, background). L'outil détecte leur présence "
            "mais ne peut pas évaluer si le contraste et la taille de "
            "l'indicateur sont suffisants pour être perçus par tous les utilisateurs."
        )
        lines.append(
            "- **Non détecté** : indicateurs de focus gérés dynamiquement "
            "par JavaScript, transitions CSS complexes, focus visible uniquement "
            "via `:focus-visible` (géré par le navigateur selon l'heuristique "
            "de saisie), ou styles dépendant de media queries."
        )
        lines.append("")
        lines.append(
            "**L'auditeur doit impérativement vérifier visuellement "
            "tous les éléments marqués « À vérifier » en naviguant au clavier "
            "(touche Tab) sur chaque page.**"
        )
        lines.append("")
        
        # Synthèse globale
        lines.append("---")
        lines.append("")
        lines.append("## Synthèse globale")
        lines.append("")
        
        total_c = sum(r.total_conforme for r in results)
        total_nc = sum(r.total_non_conforme for r in results)
        total_av = sum(r.total_a_verifier for r in results)
        total_el = sum(r.total_visible for r in results)
        
        lines.append(f"| Indicateur | Valeur |")
        lines.append(f"|-----------|--------|")
        lines.append(f"| Pages analysées | {len(results)} |")
        lines.append(f"| Éléments focusables visibles (total) | {total_el} |")
        lines.append(f"| Éléments conformes (focus visible) | {total_c} |")
        lines.append(f"| Éléments non conformes (focus supprimé) | {total_nc} |")
        lines.append(f"| Éléments à vérifier manuellement | {total_av} |")
        lines.append("")
        
        # Tableau de synthèse par page
        lines.append("### Statut suggéré par page")
        lines.append("")
        lines.append("| Page | URL | Éléments | C | NC | À vérifier | Statut suggéré | Confiance |")
        lines.append("|------|-----|----------|---|----|-----------|--------------:|-----------|")
        
        for r in results:
            url_short = r.url[:60] + "..." if len(r.url) > 60 else r.url
            status_emoji = {
                FocusStatus.CONFORME: "✅ C",
                FocusStatus.NON_CONFORME: "❌ NC",
                FocusStatus.A_VERIFIER: "🔍 NT",
                FocusStatus.NON_APPLICABLE: "⬜ NA",
            }.get(r.suggested_status, "❓")
            
            lines.append(
                f"| {r.page_id} | {url_short} | {r.total_visible} | "
                f"{r.total_conforme} | {r.total_non_conforme} | "
                f"{r.total_a_verifier} | {status_emoji} | {r.confidence} |"
            )
        
        lines.append("")
        
        # Analyse des feuilles de style (si pertinente)
        any_global = any(
            r.stylesheet_analysis.get('global_outline_none') for r in results
        )
        any_suppression = any(
            r.stylesheet_analysis.get('suppression_rules') for r in results
        )
        
        if any_global or any_suppression:
            lines.append("---")
            lines.append("")
            lines.append("## ⚠️ Analyse des feuilles de style")
            lines.append("")
            
            if any_global:
                lines.append(
                    "**ALERTE** : Une règle CSS globale de suppression de "
                    "l'outline a été détectée (`* { outline: none }` ou similaire). "
                    "Cette pratique supprime l'indicateur de focus natif du "
                    "navigateur pour TOUS les éléments et constitue une "
                    "non-conformité sauf si un style de focus personnalisé "
                    "est défini pour chaque élément focusable."
                )
                lines.append("")
            
            for r in results:
                supp_rules = r.stylesheet_analysis.get('suppression_rules', [])
                if supp_rules:
                    lines.append(f"### {r.page_id} — Règles de suppression détectées")
                    lines.append("")
                    for rule in supp_rules[:10]:
                        lines.append(f"```css")
                        lines.append(f"{rule.get('cssText', '')}")
                        lines.append(f"```")
                        lines.append("")
        
        # Détail par page
        lines.append("---")
        lines.append("")
        lines.append("## Détail par page")
        lines.append("")
        
        for r in results:
            lines.append(f"### {r.page_id} — {r.url}")
            lines.append("")
            lines.append(f"**Statut suggéré** : {r.suggested_status} "
                        f"(confiance : {r.confidence})")
            lines.append(f"**Détail** : {r.details}")
            lines.append("")
            
            # Éléments non conformes (en premier)
            nc_elements = [e for e in r.elements 
                          if e.status == FocusStatus.NON_CONFORME]
            if nc_elements:
                lines.append(f"#### ❌ Éléments non conformes ({len(nc_elements)})")
                lines.append("")
                for el in nc_elements:
                    lines.append(f"- **`{el.identifier}`**")
                    lines.append(f"  - {el.details}")
                    if el.visual_changes:
                        for vc in el.visual_changes[:3]:
                            lines.append(
                                f"  - `{vc['property']}`: "
                                f"`{vc['before']}` → `{vc['after']}`"
                            )
                lines.append("")
            
            # Éléments à vérifier
            av_elements = [e for e in r.elements 
                          if e.status == FocusStatus.A_VERIFIER]
            if av_elements:
                lines.append(f"#### 🔍 Éléments à vérifier ({len(av_elements)})")
                lines.append("")
                for el in av_elements:
                    lines.append(f"- **`{el.identifier}`**")
                    lines.append(f"  - {el.details}")
                lines.append("")
            
            # Éléments conformes (résumé compact)
            c_elements = [e for e in r.elements 
                         if e.status == FocusStatus.CONFORME]
            if c_elements:
                lines.append(f"#### ✅ Éléments conformes ({len(c_elements)})")
                lines.append("")
                # Grouper par type pour éviter un rapport trop long
                by_type = {}
                for el in c_elements:
                    key = el.tag_name
                    if key not in by_type:
                        by_type[key] = []
                    by_type[key].append(el)
                for tag, els in by_type.items():
                    if len(els) <= 3:
                        for el in els:
                            lines.append(f"- `{el.identifier}` — {el.details}")
                    else:
                        lines.append(
                            f"- **{len(els)} `<{tag}>`** — focus natif préservé "
                            f"(ex: `{els[0].identifier}`)"
                        )
                lines.append("")
            
            lines.append("---")
            lines.append("")
        
        # Guide de vérification manuelle
        lines.append("## 📋 Guide de vérification manuelle pour les éléments « À vérifier »")
        lines.append("")
        lines.append(
            "Pour chaque élément marqué « À vérifier », l'auditeur doit :"
        )
        lines.append("")
        lines.append(
            "1. **Naviguer au clavier** (touche Tab) jusqu'à l'élément concerné"
        )
        lines.append(
            "2. **Observer** si un indicateur visuel de focus est clairement "
            "visible (contour, ombre, changement de fond, soulignement…)"
        )
        lines.append(
            "3. **Évaluer le contraste** : l'indicateur doit être suffisamment "
            "contrasté par rapport à l'arrière-plan pour être perçu par "
            "un utilisateur ayant une vision normale"
        )
        lines.append(
            "4. **Tester avec différents fonds** si l'élément apparaît sur "
            "des fonds de couleur variable"
        )
        lines.append(
            "5. **Statuer** : Conforme (C) si l'indicateur est clairement visible, "
            "Non Conforme (NC) s'il est absent ou insuffisant"
        )
        lines.append("")
        lines.append(
            "**Référence** : RGAA 4.1.2 — Critère 10.7, Test 10.7.1 — "
            "WCAG 2.1 SC 2.4.7 Focus Visible (AA)"
        )
        lines.append("")
        
        # Écriture du fichier
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        
        return output_path
```

### 3.6 `test_criterion_10_7.py` — Point d'entrée GUI tkinter

```python
"""
Point d'entrée GUI tkinter pour le test du critère RGAA 10.7.
Interface cohérente avec l'outil rgaa-section2-tester existant.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import os
from criterion_10_7.focus_tester import FocusTester
from criterion_10_7.report_generator import FocusReportGenerator


class FocusTestGUI:
    """Interface graphique pour le test du critère 10.7."""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("RGAA 10.7 — Test de visibilité du focus")
        self.root.geometry("900x700")
        self.root.minsize(800, 600)
        
        self._build_ui()
        self._running = False
    
    def _build_ui(self):
        """Construit l'interface utilisateur."""
        
        # === Frame supérieure : URLs ===
        url_frame = ttk.LabelFrame(self.root, text="Pages à tester", padding=10)
        url_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(url_frame, text=(
            "Entrez les URLs à tester (une par ligne, format : ID|URL)\n"
            "Exemple : P01|https://www.example.com/"
        )).pack(anchor=tk.W)
        
        self.url_text = scrolledtext.ScrolledText(
            url_frame, height=8, width=80, font=("Consolas", 10)
        )
        self.url_text.pack(fill=tk.X, pady=5)
        
        # Bouton import depuis fichier
        btn_frame = ttk.Frame(url_frame)
        btn_frame.pack(fill=tk.X)
        
        ttk.Button(
            btn_frame, text="📂 Importer depuis fichier", 
            command=self._import_urls
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            btn_frame, text="📋 Coller depuis presse-papiers",
            command=self._paste_urls
        ).pack(side=tk.LEFT, padx=5)
        
        # === Frame options ===
        options_frame = ttk.LabelFrame(self.root, text="Options", padding=10)
        options_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Nom du site
        site_frame = ttk.Frame(options_frame)
        site_frame.pack(fill=tk.X, pady=2)
        ttk.Label(site_frame, text="Nom du site :").pack(side=tk.LEFT)
        self.site_name_var = tk.StringVar(value="Site audité")
        ttk.Entry(site_frame, textvariable=self.site_name_var, 
                  width=50).pack(side=tk.LEFT, padx=10)
        
        # Headless
        self.headless_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            options_frame, text="Mode headless (sans fenêtre navigateur)",
            variable=self.headless_var
        ).pack(anchor=tk.W)
        
        # Chemin de sortie
        output_frame = ttk.Frame(options_frame)
        output_frame.pack(fill=tk.X, pady=2)
        ttk.Label(output_frame, text="Dossier de sortie :").pack(side=tk.LEFT)
        self.output_dir_var = tk.StringVar(value=os.path.expanduser("~/rgaa-reports"))
        ttk.Entry(output_frame, textvariable=self.output_dir_var, 
                  width=50).pack(side=tk.LEFT, padx=10)
        ttk.Button(output_frame, text="...", 
                   command=self._browse_output).pack(side=tk.LEFT)
        
        # === Bouton lancer ===
        self.run_btn = ttk.Button(
            self.root, text="▶️ Lancer l'analyse", 
            command=self._start_analysis,
            style="Accent.TButton"
        )
        self.run_btn.pack(pady=10)
        
        # === Barre de progression ===
        self.progress_var = tk.DoubleVar(value=0.0)
        self.progress_bar = ttk.Progressbar(
            self.root, variable=self.progress_var, 
            maximum=100, mode='determinate'
        )
        self.progress_bar.pack(fill=tk.X, padx=10)
        
        self.status_var = tk.StringVar(value="Prêt")
        ttk.Label(self.root, textvariable=self.status_var, 
                  font=("Arial", 9)).pack(pady=2)
        
        # === Zone de log ===
        log_frame = ttk.LabelFrame(self.root, text="Journal", padding=5)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame, height=12, width=80, 
            font=("Consolas", 9), state=tk.DISABLED
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)
    
    def _log(self, message: str):
        """Ajoute un message au journal."""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
    
    def _import_urls(self):
        """Importe les URLs depuis un fichier texte."""
        filepath = filedialog.askopenfilename(
            filetypes=[("Fichiers texte", "*.txt"), ("Tous", "*.*")]
        )
        if filepath:
            with open(filepath, 'r') as f:
                self.url_text.delete('1.0', tk.END)
                self.url_text.insert('1.0', f.read())
    
    def _paste_urls(self):
        """Colle le contenu du presse-papiers."""
        try:
            content = self.root.clipboard_get()
            self.url_text.insert(tk.END, content)
        except tk.TclError:
            pass
    
    def _browse_output(self):
        """Sélectionne le dossier de sortie."""
        path = filedialog.askdirectory()
        if path:
            self.output_dir_var.set(path)
    
    def _parse_urls(self) -> list[tuple[str, str]]:
        """Parse les URLs depuis la zone de texte."""
        urls = []
        content = self.url_text.get('1.0', tk.END).strip()
        for line in content.split('\n'):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '|' in line:
                page_id, url = line.split('|', 1)
                urls.append((url.strip(), page_id.strip()))
            else:
                # Auto-générer un ID
                urls.append((line, f"P{len(urls)+1:02d}"))
        return urls
    
    def _start_analysis(self):
        """Lance l'analyse dans un thread séparé."""
        if self._running:
            return
        
        urls = self._parse_urls()
        if not urls:
            messagebox.showwarning("Aucune URL", 
                                   "Veuillez entrer au moins une URL.")
            return
        
        self._running = True
        self.run_btn.config(state=tk.DISABLED)
        self.progress_var.set(0)
        
        thread = threading.Thread(target=self._run_analysis, args=(urls,))
        thread.daemon = True
        thread.start()
    
    def _run_analysis(self, urls: list[tuple[str, str]]):
        """Exécute l'analyse (dans un thread séparé)."""
        try:
            self.root.after(0, self._log, 
                           f"Démarrage de l'analyse de {len(urls)} pages...")
            
            with FocusTester(headless=self.headless_var.get()) as tester:
                results = []
                
                for i, (url, page_id) in enumerate(urls):
                    def progress_cb(msg, pct):
                        overall = (i + pct) / len(urls) * 100
                        self.root.after(0, self.progress_var.set, overall)
                        self.root.after(0, self.status_var.set, 
                                       f"{page_id}: {msg}")
                        self.root.after(0, self._log, f"  {msg}")
                    
                    self.root.after(0, self._log, 
                                   f"\n{'='*60}")
                    self.root.after(0, self._log, 
                                   f"Page {page_id} : {url}")
                    
                    result = tester.test_page(url, page_id, progress_cb)
                    results.append(result)
                    
                    self.root.after(0, self._log,
                        f"  → Statut suggéré : {result.suggested_status} "
                        f"(confiance: {result.confidence})")
                    self.root.after(0, self._log,
                        f"  → {result.total_conforme} C, "
                        f"{result.total_non_conforme} NC, "
                        f"{result.total_a_verifier} à vérifier")
                
                # Générer le rapport
                output_dir = self.output_dir_var.get()
                os.makedirs(output_dir, exist_ok=True)
                
                report_path = os.path.join(
                    output_dir, 
                    f"rapport_10_7_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
                )
                
                generator = FocusReportGenerator()
                generator.generate(
                    results, report_path, 
                    self.site_name_var.get()
                )
                
                self.root.after(0, self._log, f"\n{'='*60}")
                self.root.after(0, self._log, 
                               f"✅ Rapport généré : {report_path}")
                self.root.after(0, self.progress_var.set, 100)
                self.root.after(0, self.status_var.set, "Analyse terminée")
                
                self.root.after(0, lambda: messagebox.showinfo(
                    "Analyse terminée",
                    f"Rapport sauvegardé :\n{report_path}\n\n"
                    f"Pages analysées : {len(results)}\n"
                    f"Total NC : {sum(r.total_non_conforme for r in results)}\n"
                    f"Total à vérifier : {sum(r.total_a_verifier for r in results)}"
                ))
        
        except Exception as e:
            self.root.after(0, self._log, f"\n❌ Erreur : {str(e)}")
            self.root.after(0, lambda: messagebox.showerror(
                "Erreur", str(e)))
        
        finally:
            self._running = False
            self.root.after(0, lambda: self.run_btn.config(state=tk.NORMAL))


def main():
    """Point d'entrée principal."""
    root = tk.Tk()
    app = FocusTestGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
```

---

## 4. Intégration avec la grille ODS existante

### 4.1 Mise à jour automatique de la grille

Le module peut optionnellement mettre à jour le fichier ODS d'audit pour le critère 10.7. Suivre la même logique que le module existant `rgaa-section2-tester` pour l'écriture ODS :

```python
"""
Module d'intégration ODS — mise à jour du critère 10.7 dans la grille d'audit.
À intégrer dans criterion_10_7/ods_updater.py
"""

from pyexcel_ods3 import get_data, save_data


class ODSFocusUpdater:
    """Met à jour la grille ODS pour le critère 10.7."""
    
    CRITERION_ID = "10.7"
    
    def update_grid(self, ods_path: str, results: list, output_path: str = None):
        """
        Met à jour les feuilles P01-P20 de la grille ODS pour le critère 10.7.
        
        IMPORTANT : Ne met à jour QUE les pages avec confiance "haute".
        Les pages avec confiance "moyenne" ou "faible" restent NT.
        
        Args:
            ods_path: Chemin de la grille ODS source
            results: Liste de PageFocusResult
            output_path: Chemin de sortie (si None, écrase le fichier source)
        """
        if output_path is None:
            output_path = ods_path
        
        data = get_data(ods_path)
        
        for result in results:
            sheet_name = result.page_id  # ex: "P01"
            if sheet_name not in data:
                continue
            
            sheet = data[sheet_name]
            
            # Trouver la ligne du critère 10.7
            for row_idx, row in enumerate(sheet):
                if len(row) >= 2 and str(row[1]).strip() == self.CRITERION_ID:
                    # Colonne D (index 3) = Statut
                    # Colonne F (index 5) = Modifications à apporter
                    
                    if result.confidence == "haute":
                        # Mise à jour automatique
                        while len(row) < 7:
                            row.append("")
                        
                        row[3] = result.suggested_status  # Statut
                        row[5] = (  # Commentaire
                            f"[AUTO] {result.details}. "
                            f"Éléments analysés : {result.total_visible}, "
                            f"C={result.total_conforme}, "
                            f"NC={result.total_non_conforme}. "
                            f"Analyse automatisée — confiance haute."
                        )
                    else:
                        # Laisser NT mais ajouter un commentaire d'aide
                        while len(row) < 7:
                            row.append("")
                        
                        row[5] = (
                            f"[AUTO-PARTIEL] {result.details}. "
                            f"Confiance {result.confidence} — "
                            f"vérification manuelle requise."
                        )
                    
                    break
        
        save_data(output_path, data)
```

### 4.2 Colonne F — Format du commentaire automatique

Le commentaire inséré en colonne F (Modifications à apporter) suit ce format :

```
[AUTO] Focus natif préservé sur tous les 23 éléments analysés. Analyse automatisée — confiance haute.
```

ou

```
[AUTO] 3 élément(s) avec outline supprimé sans compensation détectée. Éléments analysés : 45, C=40, NC=3. Analyse automatisée — confiance haute.
```

ou

```
[AUTO-PARTIEL] 5 élément(s) nécessitent une vérification manuelle. Confiance faible — vérification manuelle requise.
```

Le préfixe `[AUTO]` ou `[AUTO-PARTIEL]` permet de distinguer les résultats automatisés des saisies manuelles.

---

## 5. Installation et prérequis

### 5.1 Installation de Playwright

```bash
pip install playwright
playwright install chromium
```

### 5.2 Dépendances complètes

Ajouter au `requirements.txt` existant :

```
playwright>=1.40.0
pyexcel-ods3>=0.6.0
```

### 5.3 Vérification de l'installation

```bash
python -c "from playwright.sync_api import sync_playwright; print('Playwright OK')"
python -c "from criterion_10_7.focus_tester import FocusTester; print('Module OK')"
```

---

## 6. Utilisation

### 6.1 Via GUI

```bash
cd rgaa-section2-tester
python test_criterion_10_7.py
```

### 6.2 Via ligne de commande (optionnel)

```bash
python -m criterion_10_7.focus_tester \
    --urls "P01|https://www.example.com/" "P02|https://www.example.com/about" \
    --output ./rapport_10_7.md \
    --site "Mon Site" \
    --headless
```

### 6.3 Via script Python

```python
from criterion_10_7.focus_tester import FocusTester
from criterion_10_7.report_generator import FocusReportGenerator

urls = [
    ("https://www.isit.fr/fr/", "P01"),
    ("https://www.isit.fr/fr/about", "P02"),
]

with FocusTester(headless=True) as tester:
    results = tester.test_urls(urls)

generator = FocusReportGenerator()
generator.generate(results, "rapport_10_7.md", "ISIT")
```

---

## 7. Cas de test et validation

### 7.1 Cas de test à vérifier après implémentation

| # | Scénario | Résultat attendu |
|---|----------|-----------------|
| 1 | Page avec tous les liens/boutons utilisant le focus natif | Tous C |
| 2 | Page avec `* { outline: none }` sans compensation | Tous NC |
| 3 | Page avec `outline: none` + `box-shadow` sur `:focus` | C si box-shadow visible |
| 4 | Page avec `:focus-visible` uniquement | À vérifier (dépend du navigateur) |
| 5 | Page sans éléments focusables | NA |
| 6 | Page avec éléments `tabindex="-1"` uniquement | Inclus mais signalé |
| 7 | Page avec focus géré par JavaScript (`onfocus` handler) | À vérifier |
| 8 | Input disabled | Exclu de l'analyse |
| 9 | Élément dans `aria-hidden="true"` | Exclu de l'analyse |

### 7.2 Pages de test recommandées

Pour valider l'outil, tester avec :
- Une page minimaliste avec focus natif (devrait tout marquer C)
- Le site https://www.isit.fr/fr/ (cohérence avec l'audit existant)
- https://accessibilite.numerique.gouv.fr/ (site de référence RGAA)

---

## 8. Limitations connues et évolutions possibles

### 8.1 Limitations actuelles

1. **`:focus-visible`** : Le navigateur headless peut ne pas appliquer `:focus-visible` comme un navigateur réel (l'heuristique dépend de la méthode d'activation du focus)
2. **Cross-origin stylesheets** : Les feuilles CSS servies depuis un autre domaine ne peuvent pas être analysées (CORS)
3. **Shadow DOM** : Les éléments dans le Shadow DOM nécessitent un traitement spécifique non couvert
4. **Transitions CSS** : Les indicateurs de focus avec animation/transition peuvent ne pas être capturés si le délai d'attente (100ms) est insuffisant
5. **Contraste du focus** : L'outil ne mesure pas le ratio de contraste de l'indicateur de focus (pertinent pour WCAG 2.4.11 / RGAA v5 potentiel)

### 8.2 Évolutions possibles

- Capture d'écran comparative (avant/après focus) pour chaque élément ambigu
- Mesure du ratio de contraste de l'indicateur de focus
- Support du Shadow DOM
- Intégration directe avec l'outil `rgaa-section2-tester` via menu partagé
- Export CSV des résultats pour analyse statistique
