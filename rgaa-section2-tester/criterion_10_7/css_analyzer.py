"""
Module d'analyse des styles CSS appliques au focus.
Compare les computed styles d'un element avant et apres focus()
pour determiner si un indicateur visuel de focus est present.

Logique de classification :
    1. L'outline est-il supprime au focus ?
    2. Si supprime, y a-t-il un style compensatoire ?
    3. Si non supprime, le focus natif est preserve -> C
    4. Si supprime sans compensation -> NC
    5. Si compensation detectee mais subtile -> A verifier
"""

import re
import json
from playwright.sync_api import Page
from .constants import (
    FOCUS_VISUAL_PROPERTIES,
    COMPENSATORY_PROPERTIES,
    FocusStatus,
)
from .focus_detector import FocusableElement


class CSSFocusAnalyzer:
    """Analyse les styles CSS de focus pour chaque element focusable."""

    def __init__(self, page: Page):
        self.page = page

    def analyze_element(self, element: FocusableElement) -> FocusableElement:
        """
        Analyse un element focusable :
        1. Capture les computed styles sans focus
        2. Applique le focus
        3. Capture les computed styles avec focus
        4. Compare et classifie

        Modifie l'objet element en place et le retourne.
        """
        if not element.is_visible:
            element.status = FocusStatus.A_VERIFIER
            element.details = "Element non visible — verification manuelle requise"
            return element

        try:
            # Etape 1 : capturer les styles SANS focus
            self.page.evaluate(
                '() => { if (document.activeElement) document.activeElement.blur(); }'
            )

            styles_normal = self._get_computed_styles(element.selector_path)
            element.styles_normal = styles_normal

            # Etape 2 : appliquer le focus
            self.page.evaluate('''(selector) => {
                const el = document.querySelector(selector);
                if (el) el.focus();
            }''', element.selector_path)

            # Petit delai pour les transitions CSS
            self.page.wait_for_timeout(100)

            # Etape 3 : capturer les styles AVEC focus
            styles_focused = self._get_computed_styles(element.selector_path)
            element.styles_focused = styles_focused

            # Etape 4 : analyser les differences
            self._classify_element(element)

            # Retirer le focus pour l'element suivant
            self.page.evaluate(
                '() => { if (document.activeElement) document.activeElement.blur(); }'
            )

        except Exception as e:
            element.status = FocusStatus.A_VERIFIER
            element.details = f"Erreur lors de l'analyse : {str(e)}"

        return element

    def _get_computed_styles(self, selector: str) -> dict:
        """Recupere les computed styles pertinents d'un element."""
        props_json = json.dumps(FOCUS_VISUAL_PROPERTIES)
        return self.page.evaluate('''(args) => {
            const [selector, props] = args;
            const el = document.querySelector(selector);
            if (!el) return {};
            const cs = window.getComputedStyle(el);
            const result = {};
            for (const prop of props) {
                result[prop] = cs.getPropertyValue(prop);
            }
            return result;
        }''', [selector, FOCUS_VISUAL_PROPERTIES])

    def _classify_element(self, element: FocusableElement):
        """
        Classifie un element selon l'analyse de ses styles focus.
        """
        normal = element.styles_normal
        focused = element.styles_focused

        # Detecter les changements visuels
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

        # Verifier si outline est supprime au focus
        outline_style_focused = focused.get('outline-style', '')
        outline_width_focused = focused.get('outline-width', '')

        outline_suppressed = (
            outline_style_focused == 'none'
            or outline_width_focused == '0px'
            or outline_width_focused == '0'
        )
        element.outline_suppressed = outline_suppressed

        # Verifier s'il y a un changement visuel compensatoire
        compensatory_changes = [
            vc for vc in visual_changes
            if vc['property'] in COMPENSATORY_PROPERTIES
            and vc['before'] != vc['after']
        ]
        element.has_custom_focus_style = len(compensatory_changes) > 0

        # --- Classification ---

        if not outline_suppressed:
            # Outline natif preserve
            if (outline_style_focused not in ('none', '')
                    and outline_width_focused not in ('0px', '0', '')):
                element.status = FocusStatus.CONFORME
                element.details = (
                    f"Focus natif preserve : outline-style={outline_style_focused}, "
                    f"outline-width={outline_width_focused}"
                )
            else:
                if compensatory_changes:
                    element.status = FocusStatus.A_VERIFIER
                    props_changed = ', '.join(
                        c['property'] for c in compensatory_changes
                    )
                    element.details = (
                        f"Style custom detecte ({props_changed}) — "
                        f"verifier la visibilite suffisante du focus"
                    )
                else:
                    element.status = FocusStatus.A_VERIFIER
                    element.details = (
                        "Aucun changement visuel detecte au focus — "
                        "verifier manuellement"
                    )

        elif outline_suppressed and compensatory_changes:
            # Outline supprime MAIS style compensatoire present
            has_significant_change = self._is_change_significant(
                compensatory_changes
            )

            if has_significant_change:
                element.status = FocusStatus.CONFORME
                props_changed = ', '.join(
                    c['property'] for c in compensatory_changes
                )
                element.details = (
                    f"Outline supprime mais style custom visible : "
                    f"{props_changed}. "
                    f"Changements : {self._format_changes(compensatory_changes)}"
                )
            else:
                element.status = FocusStatus.A_VERIFIER
                props_changed = ', '.join(
                    c['property'] for c in compensatory_changes
                )
                element.details = (
                    f"Outline supprime, style custom subtil detecte "
                    f"({props_changed}) — verifier si suffisamment visible. "
                    f"Changements : {self._format_changes(compensatory_changes)}"
                )
            element.has_custom_focus_style = True

        elif outline_suppressed and not compensatory_changes:
            # Outline supprime et AUCUNE compensation -> NON CONFORME
            element.status = FocusStatus.NON_CONFORME
            element.details = (
                f"Outline supprime (outline-style: {outline_style_focused}, "
                f"outline-width: {outline_width_focused}) "
                f"sans aucun style de focus compensatoire detecte"
            )

        else:
            element.status = FocusStatus.A_VERIFIER
            element.details = "Cas non classifie — verification manuelle requise"

    def _is_change_significant(self, changes: list[dict]) -> bool:
        """
        Evalue si les changements visuels sont suffisamment significatifs
        pour constituer un indicateur de focus visible.

        Heuristiques :
        - box-shadow ajoute (de 'none' a une valeur) -> significatif
        - border-width augmente -> significatif
        - background-color change significativement -> significatif
        - text-decoration ajoute -> significatif
        - transform ajoute -> significatif
        """
        for change in changes:
            prop = change['property']
            before = change['before']
            after = change['after']

            # box-shadow ajoute
            if prop == 'box-shadow' and before == 'none' and after != 'none':
                return True

            # border-width augmente
            if 'border' in prop and 'width' in prop:
                try:
                    before_px = float(re.sub(r'[^0-9.]', '', before or '0'))
                    after_px = float(re.sub(r'[^0-9.]', '', after or '0'))
                    if after_px > before_px:
                        return True
                except ValueError:
                    pass

            # background-color change
            if prop == 'background-color' and before != after:
                return True

            # text-decoration ajoute
            if (prop == 'text-decoration-line'
                    and before == 'none' and after != 'none'):
                return True

            # transform ajoute
            if prop == 'transform' and before == 'none' and after != 'none':
                return True

        return False

    def _format_changes(self, changes: list[dict]) -> str:
        """Formate les changements pour le rapport."""
        parts = []
        for c in changes[:5]:
            parts.append(f"{c['property']}: {c['before']} -> {c['after']}")
        return '; '.join(parts)

    def analyze_stylesheet_rules(self) -> dict:
        """
        Analyse statique des feuilles de style pour detecter les regles
        globales de suppression de focus.

        Retourne un dict avec :
        - global_outline_none: bool
        - focus_rules: list des regles CSS contenant :focus
        - suppression_rules: list des regles supprimant l'outline
        - custom_focus_rules: list des regles avec styles compensatoires
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
                            if (rule.type !== 1) continue;

                            const selector = rule.selectorText || '';
                            const cssText = rule.cssText || '';

                            if (selector.includes(':focus')) {
                                result.focus_rules.push({
                                    selector: selector,
                                    cssText: cssText.substring(0, 500),
                                });

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
