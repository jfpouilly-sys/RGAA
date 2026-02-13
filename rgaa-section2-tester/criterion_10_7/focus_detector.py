"""
Module de detection des elements focusables d'une page web.
Utilise Playwright pour identifier tous les elements pouvant recevoir le focus.

Exclut automatiquement :
    - Elements avec display:none ou visibility:hidden
    - Elements a l'interieur de aria-hidden="true"
    - Elements input[type="hidden"]
"""

import json
from playwright.sync_api import Page, Locator
from .constants import FOCUSABLE_SELECTOR


class FocusableElement:
    """Represente un element focusable detecte sur la page."""

    def __init__(self, tag_name: str, selector_path: str,
                 attributes: dict, text_content: str,
                 is_visible: bool, tabindex: int | None,
                 locator: Locator):
        self.tag_name = tag_name
        self.selector_path = selector_path
        self.attributes = attributes
        self.text_content = text_content[:80]
        self.is_visible = is_visible
        self.tabindex = tabindex
        self.locator = locator

        # Resultats d'analyse (remplis par css_analyzer)
        self.styles_normal = {}
        self.styles_focused = {}
        self.outline_suppressed = False
        self.has_custom_focus_style = False
        self.visual_changes = []
        self.status = None
        self.details = ""

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
    """Detecte tous les elements focusables d'une page."""

    def __init__(self, page: Page):
        self.page = page

    def detect_all(self) -> list[FocusableElement]:
        """
        Detecte tous les elements focusables de la page.

        Retourne une liste de FocusableElement.
        Exclut les elements :
        - avec display:none ou visibility:hidden (non visibles)
        - a l'interieur d'elements aria-hidden="true"
        - de type input[type="hidden"]
        """
        elements = []

        selector_json = json.dumps(FOCUSABLE_SELECTOR)

        raw_elements = self.page.evaluate('''(selectorStr) => {
            const nodes = document.querySelectorAll(selectorStr);
            const results = [];

            for (const node of nodes) {
                // Verifier la visibilite
                const style = window.getComputedStyle(node);
                const isVisible = style.display !== 'none'
                    && style.visibility !== 'hidden'
                    && style.opacity !== '0'
                    && node.offsetWidth > 0
                    && node.offsetHeight > 0;

                // Verifier aria-hidden sur les parents
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

                // Construire un selecteur unique
                let selectorPath = '';
                if (node.id) {
                    selectorPath = '#' + CSS.escape(node.id);
                } else {
                    const parts = [];
                    let el = node;
                    while (el && el !== document.body) {
                        let part = el.tagName.toLowerCase();
                        if (el.id) {
                            part = '#' + CSS.escape(el.id);
                            parts.unshift(part);
                            break;
                        }
                        const siblings = el.parentElement
                            ? Array.from(el.parentElement.children)
                                .filter(c => c.tagName === el.tagName)
                            : [];
                        const idx = siblings.indexOf(el);
                        if (siblings.length > 1) {
                            part += ':nth-of-type(' + (idx + 1) + ')';
                        }
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
        }''', FOCUSABLE_SELECTOR)

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
                continue

        return elements

    def count_by_type(self, elements: list[FocusableElement]) -> dict:
        """Retourne un comptage par type d'element pour le rapport."""
        counts = {}
        for el in elements:
            key = el.tag_name
            if el.attributes.get('type'):
                key += f'[type={el.attributes["type"]}]'
            counts[key] = counts.get(key, 0) + 1
        return counts
