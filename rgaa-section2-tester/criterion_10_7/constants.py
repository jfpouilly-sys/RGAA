"""
Constantes pour le test du critere RGAA 10.7 — Visibilite du focus.

References :
    - RGAA 4.1.2, Critere 10.7, Test 10.7.1
    - WCAG 2.1 SC 2.4.7 Focus Visible (AA)
    - WCAG 2.1 SC 1.4.1 Use of Color (A)
    - Techniques : C15, F73, F78, G149, G165, G183, G195, SCR31
"""

# Selecteurs CSS des elements nativement focusables (HTML)
NATIVE_FOCUSABLE_SELECTORS = [
    'a[href]',
    'button:not([disabled])',
    'input:not([disabled]):not([type="hidden"])',
    'select:not([disabled])',
    'textarea:not([disabled])',
    'area[href]',
    '[tabindex]',
    'summary',
    'details',
    'audio[controls]',
    'video[controls]',
]

# Selecteur combine pour requete unique
FOCUSABLE_SELECTOR = ', '.join(NATIVE_FOCUSABLE_SELECTORS)

# Note sur tabindex negatif
TABINDEX_NEGATIVE_NOTE = "tabindex='-1' : focusable par script/clic, pas par Tab"

# Proprietes CSS a comparer entre etat normal et etat focus
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

# Proprietes compensatoires : si l'une change au focus, c'est un style custom
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

# Seuil de ratio de contraste minimum pour visibilite du focus (WCAG)
MIN_CONTRAST_RATIO_FOCUS = 3.0


class FocusStatus:
    """Classification des resultats de l'analyse du focus."""
    CONFORME = "C"
    NON_CONFORME = "NC"
    A_VERIFIER = "A_VERIFIER"
    NON_APPLICABLE = "NA"
