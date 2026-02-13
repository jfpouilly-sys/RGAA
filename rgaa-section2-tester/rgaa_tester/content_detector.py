# -*- coding: utf-8 -*-
"""
Content Detector for automatic NA (Not Applicable) detection.

Scans a web page to identify which types of content are present,
allowing automatic marking of RGAA criteria as NA when their test
objects are absent from the page.
"""

import re
from typing import Dict, List, Any, Optional
from bs4 import BeautifulSoup, Tag


class ContentDetector:
    """Detects all types of content on a page to determine NA criteria."""

    def __init__(self, soup: BeautifulSoup):
        """
        Initialize the content detector.

        Args:
            soup: BeautifulSoup object of the parsed HTML
        """
        self.soup = soup
        self.results = {}

    def detect_all(self) -> Dict[str, Any]:
        """Execute all content detections."""
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

    def detect_images(self) -> Dict[str, Any]:
        """Detect presence of images on the page."""
        elements = {
            'img': self.soup.select('img'),
            'svg': self.soup.select('svg'),
            'canvas': self.soup.select('canvas'),
            'object_image': self.soup.select('object[type^="image/"]'),
            'embed_image': self.soup.select('embed[type^="image/"]'),
            'area': self.soup.select('area'),
            'role_img': self.soup.select('[role="img"]'),
            'input_image': self.soup.select('input[type="image"]')
        }

        has_images = any(len(v) > 0 for v in elements.values())

        return {
            'present': has_images,
            'elements': elements,
            'count': sum(len(v) for v in elements.values())
        }

    def detect_frames(self) -> Dict[str, Any]:
        """Detect presence of frames on the page."""
        elements = {
            'iframe': self.soup.select('iframe'),
            'frame': self.soup.select('frame')
        }

        has_frames = any(len(v) > 0 for v in elements.values())

        return {
            'present': has_frames,
            'elements': elements,
            'count': sum(len(v) for v in elements.values())
        }

    def detect_color_context(self) -> Dict[str, Any]:
        """Detect color-specific contexts."""
        graphical_elements = self.soup.select('[role="img"], svg, canvas')
        ui_components = self.soup.select('button, input, select, a')

        return {
            'text_present': True,  # Always true for HTML pages
            'graphical_elements': len(graphical_elements) > 0,
            'ui_components': len(ui_components) > 0,
            'graphical_count': len(graphical_elements),
            'ui_count': len(ui_components)
        }

    def detect_media(self) -> Dict[str, Any]:
        """Detect presence of temporal and non-temporal media."""
        # Detect media iframes (YouTube, Vimeo, Dailymotion, etc.)
        all_iframes = self.soup.select('iframe')
        media_iframes = []
        media_iframe_pattern = re.compile(
            r'youtube|youtu\.be|vimeo|dailymotion|twitch|soundcloud|spotify|deezer|bandcamp|'
            r'vidyard|wistia|brightcove|jwplatform|player\.',
            re.I
        )
        for iframe in all_iframes:
            src = iframe.get('src', '') or iframe.get('data-src', '') or ''
            if media_iframe_pattern.search(src):
                media_iframes.append(iframe)

        elements = {
            'video': self.soup.select('video'),
            'audio': self.soup.select('audio'),
            'object_media': self.soup.select(
                'object[type^="video/"], object[type^="audio/"], '
                'object[type="application/x-shockwave-flash"]'
            ),
            'embed_media': self.soup.select('embed[type^="video/"], embed[type^="audio/"]'),
            'bgsound': self.soup.select('bgsound'),
            'media_iframes': media_iframes
        }

        has_temporal_media = any(len(v) > 0 for v in elements.values())

        # Non-temporal media (interactive Flash, applets, etc.)
        non_temporal = self.soup.select(
            'object[type="application/x-shockwave-flash"]:not([data*="video"]), '
            'embed[type="application/x-shockwave-flash"]:not([src*="video"])'
        )

        # Autoplay media
        autoplay_media = self.soup.select('video[autoplay], audio[autoplay]')

        return {
            'temporal_present': has_temporal_media,
            'non_temporal_present': len(non_temporal) > 0,
            'autoplay_present': len(autoplay_media) > 0,
            'elements': elements,
            'count': sum(len(v) for v in elements.values())
        }

    def detect_tables(self) -> Dict[str, Any]:
        """Detect presence of tables on the page."""
        tables = self.soup.select('table, [role="table"], [role="grid"], [role="treegrid"]')

        # Distinguish data tables vs layout tables
        data_tables = []
        layout_tables = []
        complex_tables = []

        for table in tables:
            if table.get('role') == 'presentation':
                layout_tables.append(table)
            elif table.select('th, [role="columnheader"], [role="rowheader"]'):
                data_tables.append(table)
                # Check for complex tables (colspan, rowspan, headers attribute)
                if table.select('[colspan], [rowspan], [headers]'):
                    complex_tables.append(table)
            else:
                # Heuristic: tables without <th> but with multiple data rows
                # are likely data tables (missing proper headers = accessibility issue)
                rows = table.select('tr')
                cells = table.select('td')
                has_caption = bool(table.select('caption'))
                has_summary = bool(table.get('summary'))
                has_scope = bool(table.select('[scope]'))
                has_headers_attr = bool(table.select('[headers]'))

                # Consider as data table if it has structured content:
                # - has caption or summary (author intended it as data table)
                # - has scope or headers attributes
                # - has multiple rows with multiple cells (looks like tabular data)
                if (has_caption or has_summary or has_scope or has_headers_attr or
                        (len(rows) >= 2 and len(cells) >= 4)):
                    data_tables.append(table)
                    if table.select('[colspan], [rowspan], [headers]'):
                        complex_tables.append(table)
                else:
                    layout_tables.append(table)

        return {
            'present': len(tables) > 0,
            'data_tables': data_tables,
            'layout_tables': layout_tables,
            'complex_tables': complex_tables,
            'has_data_tables': len(data_tables) > 0,
            'has_layout_tables': len(layout_tables) > 0,
            'has_complex_tables': len(complex_tables) > 0,
            'count': len(tables)
        }

    def detect_links(self) -> Dict[str, Any]:
        """Detect presence of links on the page."""
        elements = {
            'a_href': self.soup.select('a[href]'),
            'area_href': self.soup.select('area[href]'),
            'role_link': self.soup.select('[role="link"]')
        }

        # Categorize links
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

    def detect_scripts(self) -> Dict[str, Any]:
        """Detect presence of scripts and JavaScript components."""
        # Scripts
        scripts = self.soup.select('script')
        has_js_files = any(s.get('src') for s in scripts)
        has_inline_js = any(s.string for s in scripts if s.string)

        # Event handlers
        event_handlers = self.soup.select(
            '[onclick], [onchange], [onsubmit], [onfocus], [onblur], '
            '[onkeydown], [onkeyup], [onkeypress], [onmouseover], [onmouseout]'
        )

        # ARIA widgets (indicate interactive JS components)
        aria_widgets = self.soup.select(
            '[role="button"], [role="checkbox"], [role="combobox"], [role="dialog"], '
            '[role="listbox"], [role="menu"], [role="slider"], [role="switch"], '
            '[role="tab"], [role="tabpanel"], [role="tooltip"], [role="tree"]'
        )

        # ARIA live regions (status messages)
        aria_live = self.soup.select('[aria-live], [role="alert"], [role="log"], [role="status"]')

        has_scripts = has_js_files or has_inline_js or len(event_handlers) > 0 or len(aria_widgets) > 0

        return {
            'present': has_scripts,
            'has_js_files': has_js_files,
            'has_inline_js': has_inline_js,
            'event_handlers': event_handlers,
            'aria_widgets': aria_widgets,
            'aria_live': aria_live,
            'has_status_messages': len(aria_live) > 0,
            'has_event_handlers': len(event_handlers) > 0,
            'has_aria_widgets': len(aria_widgets) > 0
        }

    def detect_mandatory_elements(self) -> Dict[str, Any]:
        """Detect mandatory elements - always applicable."""
        html_tag = self.soup.find('html')

        # Language changes in content
        lang_changes = self.soup.select('[lang], [xml\\:lang]')
        # Exclude the html tag itself
        content_lang_changes = [el for el in lang_changes if el.name != 'html']

        # RTL content
        rtl_content = self.soup.select('[dir="rtl"], [dir="ltr"]')
        arabic_hebrew = self.soup.find_all(string=re.compile(r'[\u0600-\u06FF\u0590-\u05FF]'))

        return {
            'present': True,  # Always applicable
            'html': html_tag is not None,
            'lang': html_tag.get('lang') if html_tag else None,
            'title': self.soup.find('title') is not None,
            'has_lang_changes': len(content_lang_changes) > 0,
            'has_rtl_content': len(rtl_content) > 0 or len(arabic_hebrew) > 0,
            'lang_changes_count': len(content_lang_changes)
        }

    def detect_structure(self) -> Dict[str, Any]:
        """Detect structure elements."""
        headings = self.soup.select('h1, h2, h3, h4, h5, h6, [role="heading"]')
        lists = self.soup.select('ul, ol, dl, [role="list"]')
        quotes = self.soup.select('blockquote, q')

        # HTML5 structure
        header = self.soup.select('header')
        nav = self.soup.select('nav')
        main = self.soup.select('main')
        footer = self.soup.select('footer')
        aside = self.soup.select('aside')
        article = self.soup.select('article')
        section = self.soup.select('section')

        return {
            'headings_present': len(headings) > 0,
            'lists_present': len(lists) > 0,
            'quotes_present': len(quotes) > 0,
            'has_html5_structure': any([header, nav, main, footer, aside, article, section]),
            'elements': {
                'headings': headings,
                'lists': lists,
                'quotes': quotes
            },
            'headings_count': len(headings),
            'lists_count': len(lists),
            'quotes_count': len(quotes)
        }

    def detect_presentation(self) -> Dict[str, Any]:
        """Detect presentation elements - always applicable."""
        # Hidden content
        hidden_content = self.soup.select(
            '[hidden], [aria-hidden="true"], '
            '[style*="display:none"], [style*="display: none"], '
            '[style*="visibility:hidden"], [style*="visibility: hidden"]'
        )

        # Additional content (hover/focus)
        hover_focus_content = self.soup.select(
            '[aria-expanded], [aria-haspopup], .tooltip, .dropdown, .modal, '
            '[data-toggle], [data-tooltip]'
        )

        # Tooltips
        tooltips = self.soup.select('[title], [data-tooltip], .tooltip')

        return {
            'present': True,  # Always applicable
            'has_hidden_content': len(hidden_content) > 0,
            'has_hover_focus_content': len(hover_focus_content) > 0,
            'has_tooltips': len(tooltips) > 0,
            'hidden_count': len(hidden_content),
            'hover_focus_count': len(hover_focus_content)
        }

    def detect_forms(self) -> Dict[str, Any]:
        """Detect presence of forms on the page."""
        forms = self.soup.select('form, [role="form"]')
        inputs = self.soup.select('input:not([type="hidden"]), textarea, select')
        aria_fields = self.soup.select(
            '[role="textbox"], [role="searchbox"], [role="combobox"], [role="listbox"], '
            '[role="checkbox"], [role="radio"], [role="switch"], [role="slider"], [role="spinbutton"]'
        )
        buttons = self.soup.select(
            'button, input[type="submit"], input[type="reset"], '
            'input[type="button"], input[type="image"]'
        )
        fieldsets = self.soup.select('fieldset, [role="group"], [role="radiogroup"]')

        # Autocomplete candidates
        autocomplete_fields = self.soup.select(
            'input[type="text"], input[type="email"], input[type="tel"], '
            'input[type="url"], input[type="password"], input[name]'
        )

        # Radio/checkbox groups
        radios = self.soup.select('input[type="radio"]')
        checkboxes = self.soup.select('input[type="checkbox"]')

        # Select with optgroups
        selects_with_optgroups = self.soup.select('select:has(optgroup)')

        has_forms = len(forms) > 0 or len(inputs) > 0 or len(aria_fields) > 0

        return {
            'present': has_forms,
            'forms': forms,
            'inputs': inputs,
            'aria_fields': aria_fields,
            'buttons': buttons,
            'fieldsets': fieldsets,
            'has_fieldsets': len(fieldsets) > 0,
            'has_buttons': len(buttons) > 0,
            'has_autocomplete_candidates': len(autocomplete_fields) > 0,
            'has_radio_groups': len(radios) > 1,
            'has_checkbox_groups': len(checkboxes) > 1,
            'has_selects_with_optgroups': len(selects_with_optgroups) > 0,
            'count': len(inputs) + len(aria_fields)
        }

    def detect_navigation(self) -> Dict[str, Any]:
        """Detect navigation elements."""
        nav = self.soup.select('nav, [role="navigation"]')
        skip_links = self.soup.select('a[href^="#"]')
        landmarks = self.soup.select(
            '[role="banner"], [role="main"], [role="contentinfo"], [role="search"]'
        )
        search = self.soup.select('[role="search"], form[action*="search"], input[type="search"]')

        # Keyboard shortcuts
        accesskeys = self.soup.select('[accesskey]')

        # Sitemap/plan links
        sitemap_links = self.soup.select('a[href*="plan"], a[href*="sitemap"]')

        return {
            'has_navigation': len(nav) > 0,
            'has_skip_links': len(skip_links) > 0,
            'has_landmarks': len(landmarks) > 0,
            'has_search': len(search) > 0,
            'has_accesskeys': len(accesskeys) > 0,
            'has_sitemap': len(sitemap_links) > 0,
            'elements': {
                'nav': nav,
                'skip_links': skip_links,
                'landmarks': landmarks,
                'search': search,
                'accesskeys': accesskeys
            }
        }

    def detect_consultation(self) -> Dict[str, Any]:
        """Detect consultation elements."""
        refresh = self.soup.select('meta[http-equiv="refresh"]')
        auto_play = self.soup.select('video[autoplay], audio[autoplay]')
        downloads = self.soup.select(
            'a[href$=".pdf"], a[href$=".doc"], a[href$=".docx"], '
            'a[href$=".xls"], a[href$=".xlsx"], a[href$=".odt"], '
            'a[href$=".ods"], a[href$=".ppt"], a[href$=".pptx"]'
        )
        animations = self.soup.select('[style*="animation"], .animate, .animated, marquee, blink')

        # Time limits
        time_limits = self.soup.select('[data-timeout], [data-timer]')

        # Orientation lock
        orientation_meta = self.soup.select('meta[name="viewport"][content*="orientation"]')

        return {
            'has_refresh': len(refresh) > 0,
            'has_auto_play': len(auto_play) > 0,
            'has_downloads': len(downloads) > 0,
            'has_animations': len(animations) > 0,
            'has_time_limits': len(time_limits) > 0,
            'has_orientation_lock': len(orientation_meta) > 0,
            'elements': {
                'refresh': refresh,
                'auto_play': auto_play,
                'downloads': downloads,
                'animations': animations
            },
            'downloads_count': len(downloads)
        }

    def get_na_criteria(self) -> List[str]:
        """Return list of NA criteria based on detection."""
        if not self.results:
            self.detect_all()

        na_criteria = []

        # Theme 1: Images
        if not self.results['images']['present']:
            na_criteria.extend(['1.1', '1.2', '1.3', '1.4', '1.5', '1.6', '1.7', '1.8', '1.9'])

        # Theme 2: Frames
        if not self.results['frames']['present']:
            na_criteria.extend(['2.1', '2.2'])

        # Theme 3: Colors - 3.3 only if no UI components
        if not self.results['colors']['graphical_elements'] and not self.results['colors']['ui_components']:
            na_criteria.append('3.3')

        # Theme 4: Multimedia
        if not self.results['media']['temporal_present']:
            na_criteria.extend(['4.1', '4.2', '4.3', '4.4', '4.5', '4.6', '4.7', '4.11', '4.13'])
        if not self.results['media']['non_temporal_present']:
            na_criteria.extend(['4.8', '4.9', '4.12'])
        if not self.results['media']['autoplay_present']:
            na_criteria.append('4.10')

        # Theme 5: Tables
        if not self.results['tables']['present']:
            na_criteria.extend(['5.1', '5.2', '5.3', '5.4', '5.5', '5.6', '5.7', '5.8'])
        else:
            if not self.results['tables']['has_complex_tables']:
                na_criteria.extend(['5.1', '5.2'])
            if not self.results['tables']['has_layout_tables']:
                na_criteria.extend(['5.3', '5.8'])
            if not self.results['tables']['has_data_tables']:
                na_criteria.extend(['5.4', '5.5', '5.6', '5.7'])

        # Theme 6: Links
        if not self.results['links']['present']:
            na_criteria.extend(['6.1', '6.2'])

        # Theme 7: Scripts
        if not self.results['scripts']['present']:
            na_criteria.extend(['7.1', '7.2', '7.3', '7.4'])
        if not self.results['scripts']['has_status_messages']:
            na_criteria.append('7.5')

        # Theme 8: Mandatory elements - some conditions
        if not self.results['mandatory']['has_lang_changes']:
            na_criteria.extend(['8.7', '8.8'])
        if not self.results['mandatory']['has_rtl_content']:
            na_criteria.append('8.10')

        # Theme 9: Structure
        if not self.results['structure']['lists_present']:
            na_criteria.append('9.3')
        if not self.results['structure']['quotes_present']:
            na_criteria.append('9.4')

        # Theme 10: Presentation
        if not self.results['presentation']['has_hidden_content']:
            na_criteria.append('10.8')
        if not self.results['presentation']['has_hover_focus_content']:
            na_criteria.extend(['10.13', '10.14'])

        # Theme 11: Forms
        if not self.results['forms']['present']:
            na_criteria.extend([
                '11.1', '11.2', '11.3', '11.4', '11.5', '11.6', '11.7',
                '11.8', '11.9', '11.10', '11.11', '11.12', '11.13'
            ])
        else:
            if not self.results['forms']['has_fieldsets']:
                na_criteria.extend(['11.6', '11.7'])
            if not self.results['forms']['has_buttons']:
                na_criteria.append('11.9')
            if not self.results['forms']['has_selects_with_optgroups']:
                na_criteria.append('11.8')

        # Theme 12: Navigation
        if not self.results['navigation']['has_accesskeys']:
            na_criteria.append('12.10')
        if not self.results['presentation']['has_hover_focus_content']:
            na_criteria.append('12.11')

        # Theme 13: Consultation
        if not self.results['consultation']['has_downloads']:
            na_criteria.extend(['13.3', '13.4'])
        if not self.results['consultation']['has_animations']:
            na_criteria.extend(['13.7', '13.8'])

        # Remove duplicates and sort
        na_criteria = list(set(na_criteria))
        na_criteria.sort(key=lambda x: (int(x.split('.')[0]), int(x.split('.')[1])))

        return na_criteria

    def get_na_reason(self, criterion: str) -> str:
        """Return the NA reason for a given criterion."""
        theme = criterion.split('.')[0]

        reasons = {
            '1': "Aucune image présente sur la page",
            '2': "Aucun cadre (iframe/frame) présent sur la page",
            '3.3': "Aucun composant d'interface ni élément graphique présent sur la page",
            '4': "Aucun média temporel ou non temporel présent sur la page",
            '4.8': "Aucun média non temporel présent sur la page",
            '4.9': "Aucun média non temporel présent sur la page",
            '4.10': "Aucun média avec lecture automatique présent sur la page",
            '4.12': "Aucun média non temporel présent sur la page",
            '5': "Aucun tableau présent sur la page",
            '5.1': "Aucun tableau de données complexe présent sur la page",
            '5.2': "Aucun tableau de données complexe présent sur la page",
            '5.3': "Aucun tableau de mise en forme présent sur la page",
            '5.4': "Aucun tableau de données présent sur la page",
            '5.5': "Aucun tableau de données présent sur la page",
            '5.6': "Aucun tableau de données présent sur la page",
            '5.7': "Aucun tableau de données présent sur la page",
            '5.8': "Aucun tableau de mise en forme présent sur la page",
            '6': "Aucun lien présent sur la page",
            '7': "Aucun script ou composant JavaScript présent sur la page",
            '7.5': "Aucun message de statut (aria-live, role=status) présent sur la page",
            '8.7': "Aucun changement de langue dans le contenu",
            '8.8': "Aucun changement de langue dans le contenu",
            '8.10': "Aucun contenu avec direction de lecture différente (RTL/LTR)",
            '9.3': "Aucune liste présente sur la page",
            '9.4': "Aucune citation présente sur la page",
            '10.8': "Aucun contenu caché présent sur la page",
            '10.13': "Aucun contenu additionnel au survol/focus présent sur la page",
            '10.14': "Aucun contenu additionnel CSS au survol/focus présent sur la page",
            '11': "Aucun formulaire ni champ de saisie présent sur la page",
            '11.6': "Aucun regroupement de champs (fieldset) présent sur la page",
            '11.7': "Aucun regroupement de champs (fieldset) présent sur la page",
            '11.8': "Aucune liste déroulante avec regroupement d'options présente sur la page",
            '11.9': "Aucun bouton présent sur la page",
            '12.10': "Aucun raccourci clavier (accesskey) présent sur la page",
            '12.11': "Aucun contenu additionnel au survol/focus/activation présent sur la page",
            '13.3': "Aucun document bureautique en téléchargement présent sur la page",
            '13.4': "Aucun document bureautique en téléchargement présent sur la page",
            '13.7': "Aucun effet de flash ou changement de luminosité présent sur la page",
            '13.8': "Aucun contenu en mouvement ou clignotant présent sur la page"
        }

        # Look for specific reason or generic by theme
        if criterion in reasons:
            return reasons[criterion]
        elif theme in reasons:
            return reasons[theme]
        else:
            return "Objet de test absent de la page"

    def generate_na_report(self) -> List[Dict[str, Any]]:
        """Generate a report of NA criteria with justifications."""
        na_criteria = self.get_na_criteria()
        report = []

        for criterion in na_criteria:
            theme = criterion.split('.')[0]
            reason = self.get_na_reason(criterion)
            report.append({
                'criterion': criterion,
                'theme': theme,
                'status': 'NA',
                'reason': reason,
                'auto_detected': True
            })

        return report

    def get_detection_summary(self) -> Dict[str, Any]:
        """Generate a summary of detected content."""
        if not self.results:
            self.detect_all()

        return {
            'images': {
                'present': self.results['images']['present'],
                'count': self.results['images']['count']
            },
            'frames': {
                'present': self.results['frames']['present'],
                'count': self.results['frames']['count']
            },
            'media': {
                'temporal': self.results['media']['temporal_present'],
                'non_temporal': self.results['media']['non_temporal_present'],
                'count': self.results['media']['count']
            },
            'tables': {
                'present': self.results['tables']['present'],
                'data': len(self.results['tables']['data_tables']),
                'layout': len(self.results['tables']['layout_tables']),
                'complex': len(self.results['tables']['complex_tables'])
            },
            'links': {
                'present': self.results['links']['present'],
                'count': self.results['links']['count']
            },
            'scripts': {
                'present': self.results['scripts']['present'],
                'has_widgets': self.results['scripts']['has_aria_widgets'],
                'has_events': self.results['scripts']['has_event_handlers']
            },
            'forms': {
                'present': self.results['forms']['present'],
                'count': self.results['forms']['count']
            },
            'na_criteria_count': len(self.get_na_criteria())
        }
