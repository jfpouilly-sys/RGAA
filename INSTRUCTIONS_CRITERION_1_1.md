# Instructions Claude Code : Amélioration du test du critère 1.1 RGAA

## 📋 Contexte

Le critère 1.1 du RGAA 4.1.2 vérifie : **"Chaque image porteuse d'information a-t-elle une alternative textuelle ?"**

Ce critère comporte **8 tests** couvrant différents types d'images :
- Test 1.1.1 : Images `<img>` ou `role="img"`
- Test 1.1.2 : Zones d'images réactives `<area>`
- Test 1.1.3 : Boutons image `<input type="image">`
- Test 1.1.4 : Images réactives côté serveur
- Test 1.1.5 : Images vectorielles `<svg>`
- Test 1.1.6 : Images objet `<object type="image/...">`
- Test 1.1.7 : Images embarquées `<embed type="image/...">`
- Test 1.1.8 : Images bitmap `<canvas>`

## 🎯 Objectif

Créer un module Python qui détecte automatiquement :
1. ✅ La **présence** d'une alternative textuelle pour chaque type d'image
2. ✅ Le **calcul du "nom accessible"** selon l'algorithme RGAA
3. ⚠️ Les **cas problématiques** nécessitant une vérification humaine
4. ❌ Les images **sans alternative** (non-conformités automatiques)

## 🔍 Algorithme de calcul du "nom accessible"

Selon le RGAA 4.1.2, l'alternative textuelle (nom accessible) est obtenue dans cet ordre de priorité :

### Pour `<img>`, `<input type="image">`, `<svg>`, `<object>`, `<embed>`, `<canvas>`, `role="img"` :

1. **aria-labelledby** (passage de texte référencé par ID)
2. **aria-label** (contenu de l'attribut)
3. **alt** (pour `<img>`, `<area>`, `<input type="image">`)
4. **title** (pour `<img>`, `<input type="image">`, `<object>`, `<embed>`)

### Pour `<svg>` spécifiquement :

1. **aria-labelledby**
2. **aria-label**
3. **`<title>`** (élément enfant du `<svg>`)

### Pour `<canvas>` spécifiquement :

1. **aria-labelledby**
2. **aria-label**
3. **title**
4. **Contenu entre `<canvas>` et `</canvas>`**

## 📝 Tâche 1 : Créer le module `image_alt_checker.py`

```python
"""
Module de vérification des alternatives textuelles pour les images selon RGAA 4.1.2 Critère 1.1
Implémente l'algorithme de calcul du "nom accessible"
"""

from playwright.async_api import Page
from typing import Dict, List, Any, Optional
import logging
import re

logger = logging.getLogger(__name__)


class ImageAltChecker:
    """
    Vérificateur d'alternatives textuelles pour images selon RGAA 4.1.2
    """
    
    @staticmethod
    async def check_all_images(page: Page) -> Dict[str, Any]:
        """
        Vérifie toutes les images de la page selon le critère 1.1 RGAA
        
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
                    
                    // 1. Vérifier aria-labelledby
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
                    
                    // 2. Vérifier aria-label
                    const ariaLabel = element.getAttribute('aria-label');
                    if (ariaLabel && ariaLabel.trim()) {
                        return {
                            name: ariaLabel.trim(),
                            source: 'aria-label'
                        };
                    }
                    
                    // 3. Vérifier alt (pour img, area, input)
                    if (['img', 'area', 'input'].includes(elementType)) {
                        const alt = element.getAttribute('alt');
                        if (alt !== null) {  // alt="" est valide !
                            return {
                                name: alt.trim(),
                                source: 'alt'
                            };
                        }
                    }
                    
                    // 4. Pour SVG : vérifier <title>
                    if (elementType === 'svg') {
                        const titleElement = element.querySelector('title');
                        if (titleElement && titleElement.textContent.trim()) {
                            return {
                                name: titleElement.textContent.trim(),
                                source: 'svg-title'
                            };
                        }
                    }
                    
                    // 5. Pour canvas : vérifier contenu interne
                    if (elementType === 'canvas') {
                        const content = element.textContent || '';
                        if (content.trim()) {
                            return {
                                name: content.trim(),
                                source: 'canvas-content'
                            };
                        }
                    }
                    
                    // 6. Vérifier title (pour img, input, object, embed)
                    if (['img', 'input', 'object', 'embed'].includes(elementType)) {
                        const title = element.getAttribute('title');
                        if (title && title.trim()) {
                            return {
                                name: title.trim(),
                                source: 'title'
                            };
                        }
                    }
                    
                    // Aucune alternative trouvée
                    return { name: null, source: null };
                }
                
                // Fonction pour vérifier si une image est décorative
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
                
                // Fonction pour détecter les problèmes courants
                function detectIssues(element, accessibleName, elementType) {
                    const issues = [];
                    
                    // Pas d'alternative
                    if (!accessibleName.name) {
                        issues.push({
                            type: 'NO_ALT',
                            severity: 'error',
                            message: 'Aucune alternative textuelle détectée'
                        });
                    }
                    
                    // Alternative vide (mais pas alt="" qui est valide pour décoration)
                    if (accessibleName.name === '' && accessibleName.source !== 'alt') {
                        issues.push({
                            type: 'EMPTY_ALT',
                            severity: 'error',
                            message: 'Alternative textuelle vide'
                        });
                    }
                    
                    // Alternative trop longue (>80 caractères recommandé)
                    if (accessibleName.name && accessibleName.name.length > 80) {
                        issues.push({
                            type: 'ALT_TOO_LONG',
                            severity: 'warning',
                            message: `Alternative de ${accessibleName.name.length} caractères (recommandation: ≤80)`
                        });
                    }
                    
                    // Détection d'alternatives génériques non pertinentes
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
                                message: `Alternative générique peu informative: "${accessibleName.name}"`
                            });
                        }
                    }
                    
                    // Détection de nom de fichier comme alt
                    if (accessibleName.name && /\\.(jpg|jpeg|png|gif|svg|webp|bmp)$/i.test(accessibleName.name)) {
                        issues.push({
                            type: 'FILENAME_AS_ALT',
                            severity: 'error',
                            message: 'Nom de fichier utilisé comme alternative'
                        });
                    }
                    
                    // Pour SVG : vérifier role="img"
                    if (elementType === 'svg' && element.getAttribute('role') !== 'img') {
                        issues.push({
                            type: 'SVG_MISSING_ROLE',
                            severity: 'error',
                            message: 'SVG sans role="img" (requis par test 1.1.5)'
                        });
                    }
                    
                    // Pour object/embed : vérifier role="img"
                    if (['object', 'embed'].includes(elementType)) {
                        if (element.getAttribute('role') !== 'img' && accessibleName.name) {
                            issues.push({
                                type: 'MISSING_ROLE_IMG',
                                severity: 'warning',
                                message: 'Absence de role="img" recommandé'
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
                
                // Test 1.1.1 : Images <img> et éléments avec role="img"
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
        
        # Générer le résumé
        summary = ImageAltChecker._generate_summary(results)
        results['summary'] = summary
        
        logger.info(f"Vérification critère 1.1 terminée: {summary['total_images']} images analysées")
        
        return results
    
    @staticmethod
    def _generate_summary(results: Dict[str, Any]) -> Dict[str, Any]:
        """Génère un résumé global des résultats"""
        
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
        
        # Compter tous les problèmes
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
        """Formate un rapport textuel des résultats"""
        
        lines = []
        lines.append("="*80)
        lines.append("RAPPORT CRITÈRE 1.1 - ALTERNATIVES TEXTUELLES DES IMAGES")
        lines.append("="*80)
        
        summary = results['summary']
        lines.append(f"\n📊 RÉSUMÉ GLOBAL")
        lines.append(f"  Total d'images analysées : {summary['total_images']}")
        lines.append(f"  Avec alternative        : {summary['with_alternative']}")
        lines.append(f"  Sans alternative        : {summary['without_alternative']}")
        lines.append(f"  Taux de conformité      : {summary['compliance_rate']}%")
        lines.append(f"  Statut                  : {summary['status']}")
        lines.append(f"  Erreurs                 : {summary['total_errors']}")
        lines.append(f"  Avertissements          : {summary['total_warnings']}")
        
        # Détail par test
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
            items_key = list(test_data.keys())[0]  # premier clé qui n'est pas total/with_alt/without_alt
            items = test_data[items_key]
            
            images_without_alt = [
                item for item in items 
                if not item.get('is_decorative') and item.get('accessible_name') is None
            ]
            
            if images_without_alt:
                lines.append(f"\n  ⚠️ Images sans alternative :")
                for item in images_without_alt[:5]:  # Limiter à 5
                    src = item.get('src') or item.get('data') or '(pas de source)'
                    lines.append(f"    - {src}")
                    for issue in item.get('issues', []):
                        lines.append(f"      [{issue['severity'].upper()}] {issue['message']}")
        
        lines.append("\n" + "="*80)
        
        return "\n".join(lines)


# Fonction de test
async def main_test():
    """Test du module"""
    from playwright.async_api import async_playwright
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # URL de test
        test_url = input("URL à tester (ou Entrée pour test local) : ").strip()
        
        if not test_url:
            # Créer une page de test
            await page.set_content("""
                <!DOCTYPE html>
                <html lang="fr">
                <head><title>Test Critère 1.1</title></head>
                <body>
                    <h1>Page de test RGAA 1.1</h1>
                    
                    <!-- Image avec alt correct -->
                    <img src="logo.png" alt="Logo de l'entreprise">
                    
                    <!-- Image sans alt (NC) -->
                    <img src="photo.jpg">
                    
                    <!-- Image décorative (conforme) -->
                    <img src="deco.gif" alt="">
                    
                    <!-- Image avec aria-label -->
                    <img src="icon.svg" aria-label="Icône de validation">
                    
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
        else:
            await page.goto(test_url, wait_until='domcontentloaded')
        
        checker = ImageAltChecker()
        results = await checker.check_all_images(page)
        
        print(checker.format_report(results))
        
        await browser.close()


if __name__ == "__main__":
    import asyncio
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main_test())
```

## 📝 Tâche 2 : Intégration dans le système d'audit

```python
from image_alt_checker import ImageAltChecker

async def audit_criterion_1_1(page: Page) -> Dict[str, Any]:
    """
    Audit du critère 1.1 RGAA
    
    Returns:
        {
            'criterion': '1.1',
            'status': 'C' | 'NC' | 'NA',
            'automated_coverage': '60%',  # Pourcentage testable automatiquement
            'results': {...},
            'manual_checks_needed': [...]
        }
    """
    
    checker = ImageAltChecker()
    results = await checker.check_all_images(page)
    
    # Déterminer les vérifications manuelles nécessaires
    manual_checks = []
    
    # Pertinence des alternatives (nécessite toujours vérification humaine)
    if results['summary']['with_alternative'] > 0:
        manual_checks.append({
            'test': '1.3',
            'reason': 'Vérifier la pertinence des alternatives textuelles',
            'count': results['summary']['with_alternative'],
            'instruction': 'Un auditeur doit vérifier que chaque alternative décrit correctement le contenu informatif de l\'image'
        })
    
    # Images potentiellement décoratives à vérifier
    decorative_to_verify = []
    for test_key in ['test_1_1_1', 'test_1_1_5', 'test_1_1_6', 'test_1_1_7', 'test_1_1_8']:
        for item in results[test_key].get(list(results[test_key].keys())[0], []):
            if item.get('is_decorative'):
                decorative_to_verify.append(item)
    
    if decorative_to_verify:
        manual_checks.append({
            'test': '1.2',
            'reason': 'Vérifier que les images marquées comme décoratives le sont vraiment',
            'count': len(decorative_to_verify),
            'instruction': 'Confirmer que ces images n\'apportent aucune information'
        })
    
    # Avertissements à vérifier
    if results['summary']['total_warnings'] > 0:
        manual_checks.append({
            'test': '1.1 / 1.3',
            'reason': 'Vérifier les avertissements détectés',
            'count': results['summary']['total_warnings'],
            'instruction': 'Examiner les alternatives génériques, trop longues, etc.'
        })
    
    return {
        'criterion': '1.1',
        'status': results['summary']['status'],
        'automated_coverage': '60%',  # Présence = 100%, pertinence = 0%
        'total_images': results['summary']['total_images'],
        'errors': results['summary']['total_errors'],
        'warnings': results['summary']['total_warnings'],
        'results': results,
        'manual_checks_needed': manual_checks,
        'report': ImageAltChecker.format_report(results)
    }
```

## 📝 Tâche 3 : Rapport dans la grille d'audit

Le module doit générer des entrées pour le fichier ODS :

```python
def generate_ods_entries(audit_results: Dict[str, Any]) -> List[Dict]:
    """
    Génère les entrées pour la grille d'audit ODS
    """
    
    entries = []
    results = audit_results['results']
    
    # Critère 1.1 - Présence d'alternative
    entries.append({
        'critere': '1.1',
        'statut': audit_results['status'],
        'commentaire': f"{results['summary']['total_images']} images analysées, "
                      f"{results['summary']['without_alternative']} sans alternative. "
                      f"Détection automatique de la présence d'alternative.",
        'verification_manuelle': 'Pertinence des alternatives (critère 1.3)'
    })
    
    return entries
```

## ✅ Ce qui peut être testé automatiquement (≈60%)

1. ✅ **Présence** d'une alternative textuelle (100%)
2. ✅ **Calcul du nom accessible** selon l'algorithme RGAA (100%)
3. ✅ **Détection** des images sans alternative (100%)
4. ✅ **Vérification** de role="img" pour SVG (100%)
5. ✅ **Détection** d'alternatives vides (hors alt="")
6. ✅ **Détection** d'alternatives trop longues (>80 car)
7. ✅ **Détection** de noms de fichiers comme alt
8. ✅ **Détection** d'alternatives génériques

## ⚠️ Ce qui nécessite vérification humaine (≈40%)

1. ❌ **Pertinence** de l'alternative (critère 1.3) - 0% automatisable
2. ❌ Distinction entre images **informatives** et **décoratives** - impossible sans contexte
3. ❌ **Qualité** de la description (courte/concise/exacte)
4. ❌ Images **complexes** nécessitant description détaillée (critère 1.7)

## 📊 Transparence dans les rapports

Chaque rapport doit clairement indiquer :

```markdown
### COUVERTURE AUTOMATIQUE : 60%

**Testé automatiquement :**
- Présence d'une alternative textuelle
- Conformité de l'algorithme de calcul du nom accessible
- Détection des erreurs techniques (absence d'alt, rôle manquant)

**VÉRIFICATION MANUELLE OBLIGATOIRE :**
- Pertinence des alternatives textuelles (critère 1.3)
- Distinction informative/décorative selon le contexte
- Qualité des descriptions
```

## 🧪 Tests de validation

```python
# test_image_alt_checker.py
import pytest

@pytest.mark.asyncio
async def test_img_with_alt():
    """Image avec alt correct doit être détectée conforme"""
    # ...

@pytest.mark.asyncio
async def test_img_without_alt():
    """Image sans alt doit être détectée NC"""
    # ...

@pytest.mark.asyncio
async def test_svg_without_role():
    """SVG sans role='img' doit être détecté NC"""
    # ...

@pytest.mark.asyncio
async def test_accessible_name_priority():
    """Vérifier l'ordre de priorité aria-labelledby > aria-label > alt"""
    # ...
```

## 📋 Checklist finale

- [ ] Module `image_alt_checker.py` créé et testé
- [ ] Tests unitaires passent
- [ ] Intégration dans le système d'audit
- [ ] Rapport ODS généré correctement
- [ ] Documentation de la couverture automatique
- [ ] Instructions pour vérifications manuelles
- [ ] Transparence sur les limitations

---

**Fin des instructions - Bonne implémentation ! 🚀**
