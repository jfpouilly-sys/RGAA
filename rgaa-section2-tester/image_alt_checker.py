# -*- coding: utf-8 -*-
"""
Module de verification des alternatives textuelles pour les images selon RGAA 4.1.2 Critere 1.1
Implemente l'algorithme de calcul du "nom accessible"

Tests couverts :
- Test 1.1.1 : Images <img> ou role="img"
- Test 1.1.2 : Zones d'images reactives <area>
- Test 1.1.3 : Boutons image <input type="image">
- Test 1.1.5 : Images vectorielles <svg>
- Test 1.1.6 : Images objet <object type="image/...">
- Test 1.1.7 : Images embarquees <embed type="image/...">
- Test 1.1.8 : Images bitmap <canvas>
"""

from playwright.async_api import Page
from typing import Dict, List, Any, Optional
import logging
import re

logger = logging.getLogger(__name__)


class ImageAltChecker:
    """
    Verificateur d'alternatives textuelles pour images selon RGAA 4.1.2
    """

    @staticmethod
    async def check_all_images(page: Page) -> Dict[str, Any]:
        """
        Verifie toutes les images de la page selon le critere 1.1 RGAA

        Returns:
            {
                'test_1_1_1': {...},  # Images <img> et role="img"
                'test_1_1_2': {...},  # Zones <area>
                'test_1_1_3': {...},  # Boutons <input type="image">
                'test_1_1_5': {...},  # Images <svg>
                'test_1_1_6': {...},  # Images <object>
                'test_1_1_7': {...},  # Images <embed>
                'test_1_1_8': {...},  # Images <canvas>
                'summary': {...}
            }
        """

        results = await page.evaluate("""
            () => {
                // Fonction pour calculer le nom accessible selon l'algorithme RGAA
                function getAccessibleName(element, elementType) {
                    let name = null;
                    let source = null;

                    // 1. Verifier aria-labelledby
                    const labelledby = element.getAttribute('aria-labelledby');
                    if (labelledby) {
                        const ids = labelledby.trim().split(/\\s+/);
                        const texts = ids.map(id => {
                            const el = document.getElementById(id);
                            return el ? el.textContent.trim() : '';
                        }).filter(t => t);

                        if (texts.length > 0) {
                            name = texts.join(' ');
                            source = 'aria-labelledby';
                            return { name, source, ids: labelledby };
                        }
                    }

                    // 2. Verifier aria-label
                    const ariaLabel = element.getAttribute('aria-label');
                    if (ariaLabel && ariaLabel.trim()) {
                        return {
                            name: ariaLabel.trim(),
                            source: 'aria-label'
                        };
                    }

                    // 3. Verifier alt (pour img, area, input)
                    if (['img', 'area', 'input'].includes(elementType)) {
                        const alt = element.getAttribute('alt');
                        if (alt !== null) {  // alt="" est valide !
                            return {
                                name: alt.trim(),
                                source: 'alt'
                            };
                        }
                    }

                    // 4. Pour SVG : verifier <title>
                    if (elementType === 'svg') {
                        const titleElement = element.querySelector('title');
                        if (titleElement && titleElement.textContent.trim()) {
                            return {
                                name: titleElement.textContent.trim(),
                                source: 'svg-title'
                            };
                        }
                    }

                    // 5. Pour canvas : verifier contenu interne
                    if (elementType === 'canvas') {
                        const content = element.textContent || '';
                        if (content.trim()) {
                            return {
                                name: content.trim(),
                                source: 'canvas-content'
                            };
                        }
                    }

                    // 6. Verifier title (pour img, input, object, embed)
                    if (['img', 'input', 'object', 'embed'].includes(elementType)) {
                        const title = element.getAttribute('title');
                        if (title && title.trim()) {
                            return {
                                name: title.trim(),
                                source: 'title'
                            };
                        }
                    }

                    // Aucune alternative trouvee
                    return { name: null, source: null };
                }

                // Fonction pour verifier si une image est decorative
                function isProbablyDecorative(element, accessibleName) {
                    // Image avec alt=""
                    if (element.hasAttribute('alt') && element.getAttribute('alt') === '') {
                        return true;
                    }

                    // Image avec aria-hidden="true"
                    if (element.getAttribute('aria-hidden') === 'true') {
                        return true;
                    }

                    // Image avec role="presentation" ou role="none"
                    const role = element.getAttribute('role');
                    if (role === 'presentation' || role === 'none') {
                        return true;
                    }

                    return false;
                }

                // Fonction pour detecter les problemes courants
                function detectIssues(element, accessibleName, elementType) {
                    const issues = [];
                    const isDecorative = isProbablyDecorative(element, accessibleName);

                    // Pas d'alternative (sauf images decoratives)
                    if (!accessibleName.name && !isDecorative) {
                        issues.push({
                            type: 'NO_ALT',
                            severity: 'error',
                            message: 'Aucune alternative textuelle detectee'
                        });
                    }

                    // Alternative vide (mais pas alt="" qui est valide pour decoration)
                    if (accessibleName.name === '' && accessibleName.source !== 'alt' && !isDecorative) {
                        issues.push({
                            type: 'EMPTY_ALT',
                            severity: 'error',
                            message: 'Alternative textuelle vide'
                        });
                    }

                    // Alternative trop longue (>80 caracteres recommande)
                    if (accessibleName.name && accessibleName.name.length > 80) {
                        issues.push({
                            type: 'ALT_TOO_LONG',
                            severity: 'warning',
                            message: 'Alternative de ' + accessibleName.name.length + ' caracteres (recommandation: <=80)'
                        });
                    }

                    // Detection d'alternatives generiques non pertinentes
                    const genericAlts = [
                        'image', 'photo', 'picture', 'img', 'icon', 'graphic',
                        'logo', 'banner', 'spacer', 'decoration', 'bullet'
                    ];
                    if (accessibleName.name) {
                        const lowerAlt = accessibleName.name.toLowerCase();
                        if (genericAlts.some(generic => lowerAlt === generic)) {
                            issues.push({
                                type: 'GENERIC_ALT',
                                severity: 'warning',
                                message: 'Alternative generique peu informative: "' + accessibleName.name + '"'
                            });
                        }
                    }

                    // Detection de nom de fichier comme alt
                    if (accessibleName.name && /\\.(jpg|jpeg|png|gif|svg|webp|bmp)$/i.test(accessibleName.name)) {
                        issues.push({
                            type: 'FILENAME_AS_ALT',
                            severity: 'error',
                            message: 'Nom de fichier utilise comme alternative'
                        });
                    }

                    // Pour SVG : verifier role="img"
                    if (elementType === 'svg' && element.getAttribute('role') !== 'img') {
                        issues.push({
                            type: 'SVG_MISSING_ROLE',
                            severity: 'error',
                            message: 'SVG sans role="img" (requis par test 1.1.5)'
                        });
                    }

                    // Pour object/embed : verifier role="img"
                    if (['object', 'embed'].includes(elementType)) {
                        if (element.getAttribute('role') !== 'img' && accessibleName.name) {
                            issues.push({
                                type: 'MISSING_ROLE_IMG',
                                severity: 'warning',
                                message: 'Absence de role="img" recommande'
                            });
                        }
                    }

                    return issues;
                }

                const results = {
                    test_1_1_1: { images: [], total: 0, with_alt: 0, without_alt: 0 },
                    test_1_1_2: { areas: [], total: 0, with_alt: 0, without_alt: 0 },
                    test_1_1_3: { buttons: [], total: 0, with_alt: 0, without_alt: 0 },
                    test_1_1_5: { svgs: [], total: 0, with_alt: 0, without_alt: 0 },
                    test_1_1_6: { objects: [], total: 0, with_alt: 0, without_alt: 0 },
                    test_1_1_7: { embeds: [], total: 0, with_alt: 0, without_alt: 0 },
                    test_1_1_8: { canvas: [], total: 0, with_alt: 0, without_alt: 0 }
                };

                // Test 1.1.1 : Images <img> et elements avec role="img"
                const imgElements = Array.from(document.querySelectorAll('img, [role="img"]'));
                imgElements.forEach((img, index) => {
                    const accessibleName = getAccessibleName(img, 'img');
                    const isDecorative = isProbablyDecorative(img, accessibleName);
                    const issues = detectIssues(img, accessibleName, 'img');

                    results.test_1_1_1.images.push({
                        index,
                        tag: img.tagName.toLowerCase(),
                        src: img.getAttribute('src') || '',
                        accessible_name: accessibleName.name,
                        alt_source: accessibleName.source,
                        is_decorative: isDecorative,
                        issues: issues,
                        attributes: {
                            alt: img.getAttribute('alt'),
                            'aria-label': img.getAttribute('aria-label'),
                            'aria-labelledby': img.getAttribute('aria-labelledby'),
                            title: img.getAttribute('title'),
                            role: img.getAttribute('role')
                        }
                    });

                    results.test_1_1_1.total++;
                    if (accessibleName.name !== null || isDecorative) {
                        results.test_1_1_1.with_alt++;
                    } else {
                        results.test_1_1_1.without_alt++;
                    }
                });

                // Test 1.1.2 : Zones <area>
                const areaElements = Array.from(document.querySelectorAll('area[href]'));
                areaElements.forEach((area, index) => {
                    const accessibleName = getAccessibleName(area, 'area');
                    const issues = detectIssues(area, accessibleName, 'area');

                    results.test_1_1_2.areas.push({
                        index,
                        href: area.getAttribute('href'),
                        accessible_name: accessibleName.name,
                        alt_source: accessibleName.source,
                        issues: issues,
                        attributes: {
                            alt: area.getAttribute('alt'),
                            'aria-label': area.getAttribute('aria-label'),
                            'aria-labelledby': area.getAttribute('aria-labelledby'),
                            title: area.getAttribute('title')
                        }
                    });

                    results.test_1_1_2.total++;
                    if (accessibleName.name !== null) {
                        results.test_1_1_2.with_alt++;
                    } else {
                        results.test_1_1_2.without_alt++;
                    }
                });

                // Test 1.1.3 : Boutons image <input type="image">
                const inputImages = Array.from(document.querySelectorAll('input[type="image"]'));
                inputImages.forEach((input, index) => {
                    const accessibleName = getAccessibleName(input, 'input');
                    const issues = detectIssues(input, accessibleName, 'input');

                    results.test_1_1_3.buttons.push({
                        index,
                        src: input.getAttribute('src'),
                        accessible_name: accessibleName.name,
                        alt_source: accessibleName.source,
                        issues: issues,
                        attributes: {
                            alt: input.getAttribute('alt'),
                            'aria-label': input.getAttribute('aria-label'),
                            'aria-labelledby': input.getAttribute('aria-labelledby'),
                            title: input.getAttribute('title')
                        }
                    });

                    results.test_1_1_3.total++;
                    if (accessibleName.name !== null) {
                        results.test_1_1_3.with_alt++;
                    } else {
                        results.test_1_1_3.without_alt++;
                    }
                });

                // Test 1.1.5 : Images SVG
                const svgElements = Array.from(document.querySelectorAll('svg'));
                svgElements.forEach((svg, index) => {
                    const accessibleName = getAccessibleName(svg, 'svg');
                    const isDecorative = isProbablyDecorative(svg, accessibleName);
                    const issues = detectIssues(svg, accessibleName, 'svg');

                    results.test_1_1_5.svgs.push({
                        index,
                        accessible_name: accessibleName.name,
                        alt_source: accessibleName.source,
                        is_decorative: isDecorative,
                        has_title: svg.querySelector('title') !== null,
                        has_desc: svg.querySelector('desc') !== null,
                        issues: issues,
                        attributes: {
                            role: svg.getAttribute('role'),
                            'aria-label': svg.getAttribute('aria-label'),
                            'aria-labelledby': svg.getAttribute('aria-labelledby'),
                            'aria-hidden': svg.getAttribute('aria-hidden')
                        }
                    });

                    results.test_1_1_5.total++;
                    if ((accessibleName.name !== null && svg.getAttribute('role') === 'img') || isDecorative) {
                        results.test_1_1_5.with_alt++;
                    } else {
                        results.test_1_1_5.without_alt++;
                    }
                });

                // Test 1.1.6 : Images <object>
                const objectElements = Array.from(document.querySelectorAll('object[type^="image/"]'));
                objectElements.forEach((obj, index) => {
                    const accessibleName = getAccessibleName(obj, 'object');
                    const isDecorative = isProbablyDecorative(obj, accessibleName);
                    const issues = detectIssues(obj, accessibleName, 'object');

                    const fallbackContent = obj.textContent || '';

                    results.test_1_1_6.objects.push({
                        index,
                        type: obj.getAttribute('type'),
                        data: obj.getAttribute('data'),
                        accessible_name: accessibleName.name,
                        alt_source: accessibleName.source,
                        is_decorative: isDecorative,
                        has_fallback: fallbackContent.trim().length > 0,
                        issues: issues,
                        attributes: {
                            role: obj.getAttribute('role'),
                            'aria-label': obj.getAttribute('aria-label'),
                            'aria-labelledby': obj.getAttribute('aria-labelledby'),
                            title: obj.getAttribute('title')
                        }
                    });

                    results.test_1_1_6.total++;
                    if (accessibleName.name !== null || isDecorative) {
                        results.test_1_1_6.with_alt++;
                    } else {
                        results.test_1_1_6.without_alt++;
                    }
                });

                // Test 1.1.7 : Images <embed>
                const embedElements = Array.from(document.querySelectorAll('embed[type^="image/"]'));
                embedElements.forEach((emb, index) => {
                    const accessibleName = getAccessibleName(emb, 'embed');
                    const isDecorative = isProbablyDecorative(emb, accessibleName);
                    const issues = detectIssues(emb, accessibleName, 'embed');

                    results.test_1_1_7.embeds.push({
                        index,
                        type: emb.getAttribute('type'),
                        src: emb.getAttribute('src'),
                        accessible_name: accessibleName.name,
                        alt_source: accessibleName.source,
                        is_decorative: isDecorative,
                        issues: issues,
                        attributes: {
                            role: emb.getAttribute('role'),
                            'aria-label': emb.getAttribute('aria-label'),
                            'aria-labelledby': emb.getAttribute('aria-labelledby'),
                            title: emb.getAttribute('title')
                        }
                    });

                    results.test_1_1_7.total++;
                    if (accessibleName.name !== null || isDecorative) {
                        results.test_1_1_7.with_alt++;
                    } else {
                        results.test_1_1_7.without_alt++;
                    }
                });

                // Test 1.1.8 : Images <canvas>
                const canvasElements = Array.from(document.querySelectorAll('canvas'));
                canvasElements.forEach((cnv, index) => {
                    const accessibleName = getAccessibleName(cnv, 'canvas');
                    const isDecorative = isProbablyDecorative(cnv, accessibleName);
                    const issues = detectIssues(cnv, accessibleName, 'canvas');

                    results.test_1_1_8.canvas.push({
                        index,
                        width: cnv.getAttribute('width') || cnv.width,
                        height: cnv.getAttribute('height') || cnv.height,
                        accessible_name: accessibleName.name,
                        alt_source: accessibleName.source,
                        is_decorative: isDecorative,
                        issues: issues,
                        attributes: {
                            role: cnv.getAttribute('role'),
                            'aria-label': cnv.getAttribute('aria-label'),
                            'aria-labelledby': cnv.getAttribute('aria-labelledby'),
                            title: cnv.getAttribute('title')
                        }
                    });

                    results.test_1_1_8.total++;
                    if (accessibleName.name !== null || isDecorative) {
                        results.test_1_1_8.with_alt++;
                    } else {
                        results.test_1_1_8.without_alt++;
                    }
                });

                return results;
            }
        """)

        # Generer le resume
        summary = ImageAltChecker._generate_summary(results)
        results['summary'] = summary

        logger.info(f"Verification critere 1.1 terminee: {summary['total_images']} images analysees")

        return results

    @staticmethod
    def _generate_summary(results: Dict[str, Any]) -> Dict[str, Any]:
        """Genere un resume global des resultats"""

        total_images = sum([
            results['test_1_1_1']['total'],
            results['test_1_1_2']['total'],
            results['test_1_1_3']['total'],
            results['test_1_1_5']['total'],
            results['test_1_1_6']['total'],
            results['test_1_1_7']['total'],
            results['test_1_1_8']['total']
        ])

        total_with_alt = sum([
            results['test_1_1_1']['with_alt'],
            results['test_1_1_2']['with_alt'],
            results['test_1_1_3']['with_alt'],
            results['test_1_1_5']['with_alt'],
            results['test_1_1_6']['with_alt'],
            results['test_1_1_7']['with_alt'],
            results['test_1_1_8']['with_alt']
        ])

        total_without_alt = sum([
            results['test_1_1_1']['without_alt'],
            results['test_1_1_2']['without_alt'],
            results['test_1_1_3']['without_alt'],
            results['test_1_1_5']['without_alt'],
            results['test_1_1_6']['without_alt'],
            results['test_1_1_7']['without_alt'],
            results['test_1_1_8']['without_alt']
        ])

        # Compter tous les problemes
        all_issues = []
        for test_key in ['test_1_1_1', 'test_1_1_2', 'test_1_1_3', 'test_1_1_5', 'test_1_1_6', 'test_1_1_7', 'test_1_1_8']:
            test_data = results[test_key]
            for items_key in test_data.keys():
                if items_key in ['total', 'with_alt', 'without_alt']:
                    continue
                items = test_data[items_key]
                for item in items:
                    all_issues.extend(item.get('issues', []))

        errors = [i for i in all_issues if i['severity'] == 'error']
        warnings = [i for i in all_issues if i['severity'] == 'warning']

        compliance_rate = (total_with_alt / total_images * 100) if total_images > 0 else 0

        return {
            'total_images': total_images,
            'with_alternative': total_with_alt,
            'without_alternative': total_without_alt,
            'total_errors': len(errors),
            'total_warnings': len(warnings),
            'compliance_rate': round(compliance_rate, 1),
            'status': 'C' if total_without_alt == 0 and len(errors) == 0 else 'NC'
        }

    @staticmethod
    def format_report(results: Dict[str, Any]) -> str:
        """Formate un rapport textuel des resultats"""

        lines = []
        lines.append("=" * 80)
        lines.append("RAPPORT CRITERE 1.1 - ALTERNATIVES TEXTUELLES DES IMAGES")
        lines.append("=" * 80)

        summary = results['summary']
        lines.append(f"\nRESUME GLOBAL")
        lines.append(f"  Total d'images analysees : {summary['total_images']}")
        lines.append(f"  Avec alternative         : {summary['with_alternative']}")
        lines.append(f"  Sans alternative         : {summary['without_alternative']}")
        lines.append(f"  Taux de conformite       : {summary['compliance_rate']}%")
        lines.append(f"  Statut                   : {summary['status']}")
        lines.append(f"  Erreurs                  : {summary['total_errors']}")
        lines.append(f"  Avertissements           : {summary['total_warnings']}")

        # Detail par test
        test_labels = {
            'test_1_1_1': 'Test 1.1.1 - Images <img> et role="img"',
            'test_1_1_2': 'Test 1.1.2 - Zones <area>',
            'test_1_1_3': 'Test 1.1.3 - Boutons <input type="image">',
            'test_1_1_5': 'Test 1.1.5 - Images <svg>',
            'test_1_1_6': 'Test 1.1.6 - Images <object>',
            'test_1_1_7': 'Test 1.1.7 - Images <embed>',
            'test_1_1_8': 'Test 1.1.8 - Images <canvas>'
        }

        for test_key, test_label in test_labels.items():
            test_data = results[test_key]
            if test_data['total'] == 0:
                continue

            lines.append(f"\n{test_label}")
            lines.append(f"  Total : {test_data['total']}")
            lines.append(f"  Avec alternative : {test_data['with_alt']}")
            lines.append(f"  Sans alternative : {test_data['without_alt']}")

            # Lister les images sans alternative
            items_key = [k for k in test_data.keys() if k not in ('total', 'with_alt', 'without_alt')][0]
            items = test_data[items_key]

            images_without_alt = [
                item for item in items
                if not item.get('is_decorative') and item.get('accessible_name') is None
            ]

            if images_without_alt:
                lines.append(f"\n  Images sans alternative :")
                for item in images_without_alt[:5]:  # Limiter a 5
                    src = item.get('src') or item.get('data') or '(pas de source)'
                    lines.append(f"    - {src}")
                    for issue in item.get('issues', []):
                        lines.append(f"      [{issue['severity'].upper()}] {issue['message']}")

        # Couverture automatique
        lines.append("\n" + "-" * 80)
        lines.append("COUVERTURE AUTOMATIQUE : 60%")
        lines.append("")
        lines.append("Teste automatiquement :")
        lines.append("  - Presence d'une alternative textuelle")
        lines.append("  - Conformite de l'algorithme de calcul du nom accessible")
        lines.append("  - Detection des erreurs techniques (absence d'alt, role manquant)")
        lines.append("")
        lines.append("VERIFICATION MANUELLE OBLIGATOIRE :")
        lines.append("  - Pertinence des alternatives textuelles (critere 1.3)")
        lines.append("  - Distinction informative/decorative selon le contexte")
        lines.append("  - Qualite des descriptions")

        lines.append("\n" + "=" * 80)

        return "\n".join(lines)


async def audit_criterion_1_1(page: Page) -> Dict[str, Any]:
    """
    Audit du critere 1.1 RGAA

    Returns:
        {
            'criterion': '1.1',
            'status': 'C' | 'NC' | 'NA',
            'automated_coverage': '60%',
            'results': {...},
            'manual_checks_needed': [...]
        }
    """

    checker = ImageAltChecker()
    results = await checker.check_all_images(page)

    # Determiner les verifications manuelles necessaires
    manual_checks = []

    # Pertinence des alternatives (necessite toujours verification humaine)
    if results['summary']['with_alternative'] > 0:
        manual_checks.append({
            'test': '1.3',
            'reason': "Verifier la pertinence des alternatives textuelles",
            'count': results['summary']['with_alternative'],
            'instruction': "Un auditeur doit verifier que chaque alternative decrit correctement le contenu informatif de l'image"
        })

    # Images potentiellement decoratives a verifier
    decorative_to_verify = []
    items_keys_map = {
        'test_1_1_1': 'images',
        'test_1_1_5': 'svgs',
        'test_1_1_6': 'objects',
        'test_1_1_7': 'embeds',
        'test_1_1_8': 'canvas'
    }
    for test_key, items_key in items_keys_map.items():
        for item in results[test_key].get(items_key, []):
            if item.get('is_decorative'):
                decorative_to_verify.append(item)

    if decorative_to_verify:
        manual_checks.append({
            'test': '1.2',
            'reason': "Verifier que les images marquees comme decoratives le sont vraiment",
            'count': len(decorative_to_verify),
            'instruction': "Confirmer que ces images n'apportent aucune information"
        })

    # Avertissements a verifier
    if results['summary']['total_warnings'] > 0:
        manual_checks.append({
            'test': '1.1 / 1.3',
            'reason': "Verifier les avertissements detectes",
            'count': results['summary']['total_warnings'],
            'instruction': "Examiner les alternatives generiques, trop longues, etc."
        })

    # Determine NA status if no images at all
    status = results['summary']['status']
    if results['summary']['total_images'] == 0:
        status = 'NA'

    return {
        'criterion': '1.1',
        'status': status,
        'automated_coverage': '60%',
        'total_images': results['summary']['total_images'],
        'errors': results['summary']['total_errors'],
        'warnings': results['summary']['total_warnings'],
        'results': results,
        'manual_checks_needed': manual_checks,
        'report': ImageAltChecker.format_report(results)
    }


def generate_ods_entries(audit_results: Dict[str, Any]) -> List[Dict]:
    """
    Genere les entrees pour la grille d'audit ODS
    """

    entries = []
    results = audit_results['results']

    # Critere 1.1 - Presence d'alternative
    entries.append({
        'critere': '1.1',
        'statut': audit_results['status'],
        'commentaire': (
            f"{results['summary']['total_images']} images analysees, "
            f"{results['summary']['without_alternative']} sans alternative. "
            f"Detection automatique de la presence d'alternative."
        ),
        'verification_manuelle': "Pertinence des alternatives (critere 1.3)"
    })

    return entries


# Fonction de test
async def main_test():
    """Test du module"""
    from playwright.async_api import async_playwright

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        # Creer une page de test
        await page.set_content("""
            <!DOCTYPE html>
            <html lang="fr">
            <head><title>Test Critere 1.1</title></head>
            <body>
                <h1>Page de test RGAA 1.1</h1>

                <!-- Image avec alt correct -->
                <img src="logo.png" alt="Logo de l'entreprise">

                <!-- Image sans alt (NC) -->
                <img src="photo.jpg">

                <!-- Image decorative (conforme) -->
                <img src="deco.gif" alt="">

                <!-- Image avec aria-label -->
                <img src="icon.svg" aria-label="Icone de validation">

                <!-- SVG sans role="img" (NC) -->
                <svg><title>Diagramme</title></svg>

                <!-- SVG correct -->
                <svg role="img" aria-label="Graphique des ventes"></svg>

                <!-- Canvas sans alternative (NC) -->
                <canvas id="myCanvas"></canvas>

                <!-- Input image avec alt -->
                <input type="image" src="submit.png" alt="Soumettre le formulaire">
            </body>
            </html>
        """)

        checker = ImageAltChecker()
        results = await checker.check_all_images(page)

        print(checker.format_report(results))

        await browser.close()


if __name__ == "__main__":
    import asyncio
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main_test())
