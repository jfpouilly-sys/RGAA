# Instructions Claude Code : Amélioration de la détection des objets multimédias RGAA

## 🎯 Contexte du problème

Le repository https://github.com/jfpouilly-sys/RGAA contient un outil d'audit RGAA automatisé. 

**Problème identifié :** Des critères RGAA de la Section 4 (Multimédia) sont marqués "NA" (Non Applicable) alors que des éléments multimédias (`<object>`, `<embed>`, `<video>`, `<audio>`, etc.) sont effectivement présents sur la page web auditée.

**Causes possibles :**
- Éléments chargés dynamiquement via JavaScript après le chargement initial
- Éléments présents dans des iframes non analysées
- Éléments masqués (CSS `display:none`) mais présents dans le DOM
- Variations dans les attributs `type=` non détectées
- Délai insuffisant avant l'analyse du DOM

## 🎯 Objectif de la mission

Créer un module Python robuste de détection des éléments multimédias qui :

1. ✅ Détecte **tous** les types d'objets selon le RGAA 4.1.2 (Section 4 - Multimédia)
2. ✅ Gère les cas de chargement dynamique (JavaScript)
3. ✅ Détecte les éléments même s'ils sont masqués par CSS
4. ✅ Capture les informations détaillées pour chaque élément (attributs d'accessibilité)
5. ✅ Fournit une catégorisation claire pour déterminer l'applicabilité des critères RGAA

## 📋 Éléments à détecter (selon RGAA 4.1.2)

### Médias temporels :
- `<video>` - vidéos HTML5
- `<audio>` - sons/podcasts HTML5
- `<object>` avec attributs type : `video/*`, `audio/*`, `application/*` (Flash, etc.)
- `<embed>` avec attributs type : `video/*`, `audio/*`, `application/*`
- `<bgsound>` (obsolète Internet Explorer, mais doit être détecté)

### Médias non temporels :
- `<object>` avec type=`image/*`
- `<embed>` avec type=`image/*`
- `<canvas>` - images bitmap dynamiques
- `<svg>` - images vectorielles

## 📝 Tâche 1 : Créer le module `media_detector.py`

Créez le fichier suivant dans le repository :

**Chemin :** `/rgaa-section2-tester/media_detector.py` (ou à la racine selon l'architecture)

```python
"""
Module de détection robuste des éléments multimédias pour RGAA 4.1.2
Détecte : <object>, <embed>, <video>, <audio>, <canvas>, <svg>, <bgsound>

Usage:
    detector = MediaDetector()
    media_data = await detector.detect_all_media(page)
    has_media = detector.has_media_elements(media_data)
"""

from playwright.async_api import Page
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)


class MediaDetector:
    """Détecteur d'éléments multimédias pour audits RGAA Section 4"""
    
    MEDIA_SELECTORS = {
        'object': 'object',
        'embed': 'embed', 
        'video': 'video',
        'audio': 'audio',
        'canvas': 'canvas',
        'svg': 'svg',
        'bgsound': 'bgsound'
    }
    
    @staticmethod
    async def detect_all_media(page: Page, timeout: int = 10000) -> Dict[str, Any]:
        """
        Détecte tous les éléments multimédias présents sur la page.
        
        Args:
            page: Page Playwright chargée
            timeout: Délai d'attente pour networkidle (ms)
            
        Returns:
            Dictionnaire contenant tous les médias détectés avec leurs propriétés
            
        Structure de retour:
            {
                'objects': [...],      # Liste des <object>
                'embeds': [...],       # Liste des <embed>
                'videos': [...],       # Liste des <video>
                'audios': [...],       # Liste des <audio>
                'canvas': [...],       # Liste des <canvas>
                'svg': [...],          # Liste des <svg>
                'bgsound': [...],      # Liste des <bgsound>
                'total_count': int     # Nombre total d'éléments
            }
        """
        # Attendre que la page soit complètement chargée (y compris JS dynamique)
        try:
            await page.wait_for_load_state('networkidle', timeout=timeout)
        except Exception as e:
            logger.warning(f"Timeout networkidle après {timeout}ms: {e}")
            # Continuer quand même pour détecter ce qui est déjà chargé
        
        # Pause supplémentaire pour laisser le JS s'exécuter
        await page.wait_for_timeout(1000)
        
        # Exécuter la détection dans le contexte du navigateur
        media_data = await page.evaluate("""
            () => {
                const result = {
                    objects: [],
                    embeds: [],
                    videos: [],
                    audios: [],
                    canvas: [],
                    svg: [],
                    bgsound: [],
                    total_count: 0
                };
                
                // Fonction utilitaire pour vérifier la visibilité
                function isVisible(element) {
                    const style = window.getComputedStyle(element);
                    const rect = element.getBoundingClientRect();
                    return {
                        display: style.display !== 'none',
                        visibility: style.visibility !== 'hidden',
                        opacity: parseFloat(style.opacity) > 0,
                        in_viewport: rect.height > 0 && rect.width > 0,
                        is_rendered: rect.height > 0 || rect.width > 0
                    };
                }
                
                // Détection des balises <object>
                document.querySelectorAll('object').forEach((obj, index) => {
                    const visibility = isVisible(obj);
                    const textContent = obj.textContent || '';
                    result.objects.push({
                        index: index,
                        type: obj.getAttribute('type') || 'non-défini',
                        data: obj.getAttribute('data') || '',
                        classid: obj.getAttribute('classid') || '',
                        visibility: visibility,
                        has_fallback: textContent.trim().length > 0,
                        fallback_length: textContent.trim().length,
                        attributes: {
                            id: obj.id || null,
                            class: obj.className || null,
                            'aria-hidden': obj.getAttribute('aria-hidden'),
                            'aria-label': obj.getAttribute('aria-label'),
                            'aria-labelledby': obj.getAttribute('aria-labelledby'),
                            role: obj.getAttribute('role'),
                            title: obj.getAttribute('title')
                        }
                    });
                });
                
                // Détection des balises <embed>
                document.querySelectorAll('embed').forEach((emb, index) => {
                    const visibility = isVisible(emb);
                    result.embeds.push({
                        index: index,
                        type: emb.getAttribute('type') || 'non-défini',
                        src: emb.getAttribute('src') || '',
                        visibility: visibility,
                        attributes: {
                            id: emb.id || null,
                            class: emb.className || null,
                            'aria-hidden': emb.getAttribute('aria-hidden'),
                            'aria-label': emb.getAttribute('aria-label'),
                            'aria-labelledby': emb.getAttribute('aria-labelledby'),
                            role: emb.getAttribute('role'),
                            title: emb.getAttribute('title'),
                            width: emb.getAttribute('width'),
                            height: emb.getAttribute('height')
                        }
                    });
                });
                
                // Détection des balises <video>
                document.querySelectorAll('video').forEach((vid, index) => {
                    const visibility = isVisible(vid);
                    const tracks = Array.from(vid.querySelectorAll('track')).map(t => ({
                        kind: t.getAttribute('kind'),
                        src: t.getAttribute('src'),
                        srclang: t.getAttribute('srclang'),
                        label: t.getAttribute('label')
                    }));
                    
                    result.videos.push({
                        index: index,
                        src: vid.getAttribute('src') || '',
                        sources: Array.from(vid.querySelectorAll('source')).map(s => ({
                            src: s.getAttribute('src'),
                            type: s.getAttribute('type')
                        })),
                        controls: vid.hasAttribute('controls'),
                        autoplay: vid.hasAttribute('autoplay'),
                        loop: vid.hasAttribute('loop'),
                        muted: vid.hasAttribute('muted'),
                        tracks: tracks,
                        has_captions: tracks.some(t => t.kind === 'captions'),
                        has_subtitles: tracks.some(t => t.kind === 'subtitles'),
                        visibility: visibility,
                        attributes: {
                            id: vid.id || null,
                            class: vid.className || null,
                            'aria-label': vid.getAttribute('aria-label'),
                            'aria-labelledby': vid.getAttribute('aria-labelledby'),
                            'aria-describedby': vid.getAttribute('aria-describedby'),
                            title: vid.getAttribute('title')
                        }
                    });
                });
                
                // Détection des balises <audio>
                document.querySelectorAll('audio').forEach((aud, index) => {
                    const visibility = isVisible(aud);
                    result.audios.push({
                        index: index,
                        src: aud.getAttribute('src') || '',
                        sources: Array.from(aud.querySelectorAll('source')).map(s => ({
                            src: s.getAttribute('src'),
                            type: s.getAttribute('type')
                        })),
                        controls: aud.hasAttribute('controls'),
                        autoplay: aud.hasAttribute('autoplay'),
                        loop: aud.hasAttribute('loop'),
                        muted: aud.hasAttribute('muted'),
                        visibility: visibility,
                        attributes: {
                            id: aud.id || null,
                            class: aud.className || null,
                            'aria-label': aud.getAttribute('aria-label'),
                            'aria-labelledby': aud.getAttribute('aria-labelledby'),
                            'aria-describedby': aud.getAttribute('aria-describedby'),
                            title: aud.getAttribute('title')
                        }
                    });
                });
                
                // Détection des balises <canvas>
                document.querySelectorAll('canvas').forEach((cnv, index) => {
                    const visibility = isVisible(cnv);
                    const textContent = cnv.textContent || '';
                    result.canvas.push({
                        index: index,
                        width: cnv.getAttribute('width') || cnv.width,
                        height: cnv.getAttribute('height') || cnv.height,
                        has_fallback: textContent.trim().length > 0,
                        fallback_content: textContent.trim(),
                        visibility: visibility,
                        attributes: {
                            id: cnv.id || null,
                            class: cnv.className || null,
                            'aria-label': cnv.getAttribute('aria-label'),
                            'aria-labelledby': cnv.getAttribute('aria-labelledby'),
                            'aria-describedby': cnv.getAttribute('aria-describedby'),
                            role: cnv.getAttribute('role'),
                            title: cnv.getAttribute('title')
                        }
                    });
                });
                
                // Détection des balises <svg>
                document.querySelectorAll('svg').forEach((svg, index) => {
                    const visibility = isVisible(svg);
                    const titleElement = svg.querySelector('title');
                    const descElement = svg.querySelector('desc');
                    
                    result.svg.push({
                        index: index,
                        role: svg.getAttribute('role'),
                        has_title: titleElement !== null,
                        title_content: titleElement ? titleElement.textContent.trim() : '',
                        has_desc: descElement !== null,
                        desc_content: descElement ? descElement.textContent.trim() : '',
                        visibility: visibility,
                        attributes: {
                            id: svg.id || null,
                            class: svg.className.baseVal || null,
                            'aria-label': svg.getAttribute('aria-label'),
                            'aria-labelledby': svg.getAttribute('aria-labelledby'),
                            'aria-describedby': svg.getAttribute('aria-describedby'),
                            'aria-hidden': svg.getAttribute('aria-hidden'),
                            title: svg.getAttribute('title')
                        }
                    });
                });
                
                // Détection des balises <bgsound> (obsolète IE)
                document.querySelectorAll('bgsound').forEach((bgs, index) => {
                    result.bgsound.push({
                        index: index,
                        src: bgs.getAttribute('src') || '',
                        loop: bgs.getAttribute('loop'),
                        balance: bgs.getAttribute('balance'),
                        volume: bgs.getAttribute('volume')
                    });
                });
                
                // Calcul du total
                result.total_count = result.objects.length + 
                                    result.embeds.length + 
                                    result.videos.length + 
                                    result.audios.length + 
                                    result.canvas.length + 
                                    result.svg.length +
                                    result.bgsound.length;
                
                return result;
            }
        """)
        
        logger.info(f"Détection médias terminée: {media_data['total_count']} éléments au total")
        logger.debug(f"Détail: objects={len(media_data['objects'])}, embeds={len(media_data['embeds'])}, "
                    f"videos={len(media_data['videos'])}, audios={len(media_data['audios'])}, "
                    f"canvas={len(media_data['canvas'])}, svg={len(media_data['svg'])}")
        
        return media_data
    
    @staticmethod
    def has_media_elements(media_data: Dict[str, Any]) -> bool:
        """
        Vérifie si des éléments multimédias sont présents.
        
        Args:
            media_data: Données retournées par detect_all_media()
            
        Returns:
            True si au moins un élément multimédia est présent
        """
        return media_data.get('total_count', 0) > 0
    
    @staticmethod
    def categorize_media_types(media_data: Dict[str, Any]) -> Dict[str, bool]:
        """
        Catégorise les types de médias présents pour déterminer 
        l'applicabilité des critères RGAA Section 4.
        
        Args:
            media_data: Données retournées par detect_all_media()
        
        Returns:
            Dictionnaire indiquant la présence de chaque catégorie de média:
            - has_temporal_media: médias temporels (video, audio)
            - has_non_temporal_media: médias non temporels (canvas, object image)
            - has_svg: images vectorielles SVG
            - has_object_tags: balises <object>
            - has_embed_tags: balises <embed>
            - has_bgsound: balises <bgsound>
            - has_autoplay_media: médias avec lecture automatique
        """
        # Détection des médias temporels
        has_video = len(media_data.get('videos', [])) > 0
        has_audio = len(media_data.get('audios', [])) > 0
        
        # Vérifier les objects avec type video/audio
        objects_temporal = any(
            obj.get('type', '').startswith(('video/', 'audio/', 'application/x-shockwave-flash'))
            for obj in media_data.get('objects', [])
        )
        
        # Vérifier les embeds avec type video/audio
        embeds_temporal = any(
            emb.get('type', '').startswith(('video/', 'audio/', 'application/x-shockwave-flash'))
            for emb in media_data.get('embeds', [])
        )
        
        # Détection des médias non temporels (images)
        has_canvas = len(media_data.get('canvas', [])) > 0
        
        objects_non_temporal = any(
            obj.get('type', '').startswith('image/')
            for obj in media_data.get('objects', [])
        )
        
        embeds_non_temporal = any(
            emb.get('type', '').startswith('image/')
            for emb in media_data.get('embeds', [])
        )
        
        # Détection de l'autoplay
        has_autoplay = (
            any(vid.get('autoplay', False) for vid in media_data.get('videos', [])) or
            any(aud.get('autoplay', False) for aud in media_data.get('audios', []))
        )
        
        return {
            'has_temporal_media': has_video or has_audio or objects_temporal or embeds_temporal,
            'has_non_temporal_media': has_canvas or objects_non_temporal or embeds_non_temporal,
            'has_svg': len(media_data.get('svg', [])) > 0,
            'has_object_tags': len(media_data.get('objects', [])) > 0,
            'has_embed_tags': len(media_data.get('embeds', [])) > 0,
            'has_bgsound': len(media_data.get('bgsound', [])) > 0,
            'has_autoplay_media': has_autoplay
        }
    
    @staticmethod
    def get_media_summary(media_data: Dict[str, Any]) -> str:
        """
        Génère un résumé textuel des médias détectés.
        
        Args:
            media_data: Données retournées par detect_all_media()
            
        Returns:
            Chaîne de caractères formatée avec le résumé
        """
        summary = []
        
        if media_data['total_count'] == 0:
            return "Aucun élément multimédia détecté sur la page."
        
        summary.append(f"Total: {media_data['total_count']} élément(s) multimédia détecté(s)")
        
        if media_data['objects']:
            summary.append(f"  - {len(media_data['objects'])} balise(s) <object>")
        if media_data['embeds']:
            summary.append(f"  - {len(media_data['embeds'])} balise(s) <embed>")
        if media_data['videos']:
            summary.append(f"  - {len(media_data['videos'])} balise(s) <video>")
        if media_data['audios']:
            summary.append(f"  - {len(media_data['audios'])} balise(s) <audio>")
        if media_data['canvas']:
            summary.append(f"  - {len(media_data['canvas'])} balise(s) <canvas>")
        if media_data['svg']:
            summary.append(f"  - {len(media_data['svg'])} balise(s) <svg>")
        if media_data['bgsound']:
            summary.append(f"  - {len(media_data['bgsound'])} balise(s) <bgsound>")
        
        return "\n".join(summary)


# Fonction de test autonome
async def main_test():
    """Fonction de test pour vérifier le détecteur"""
    from playwright.async_api import async_playwright
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # URL de test - Remplacer par une URL réelle
        test_url = input("Entrez l'URL à tester (ou Entrée pour exemple): ").strip()
        if not test_url:
            test_url = "https://www.youtube.com"
        
        print(f"\n🔍 Analyse de: {test_url}")
        await page.goto(test_url, wait_until='domcontentloaded')
        
        detector = MediaDetector()
        media_data = await detector.detect_all_media(page)
        
        print(f"\n{'='*60}")
        print(MediaDetector.get_media_summary(media_data))
        print(f"{'='*60}")
        
        categories = detector.categorize_media_types(media_data)
        print(f"\n📊 Catégorisation (applicabilité RGAA):")
        for cat, present in categories.items():
            status = "✅ OUI" if present else "❌ NON"
            print(f"  {cat}: {status}")
        
        # Afficher les détails des vidéos si présentes
        if media_data['videos']:
            print(f"\n🎥 Détails des vidéos:")
            for vid in media_data['videos']:
                print(f"  Video #{vid['index']}:")
                print(f"    - Controls: {vid['controls']}")
                print(f"    - Autoplay: {vid['autoplay']}")
                print(f"    - Captions: {vid['has_captions']}")
                print(f"    - ARIA label: {vid['attributes'].get('aria-label', 'Non défini')}")
        
        await browser.close()


if __name__ == "__main__":
    import asyncio
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main_test())
```

## 📝 Tâche 2 : Intégrer le détecteur dans le code existant

Localisez votre fichier principal d'audit (probablement dans `rgaa-section2-tester/`) et modifiez-le comme suit :

### Exemple d'intégration :

```python
from media_detector import MediaDetector

async def audit_page(page: Page, url: str) -> Dict[str, Any]:
    """
    Fonction principale d'audit d'une page web selon RGAA 4.1.2
    
    Args:
        page: Page Playwright
        url: URL de la page à auditer
        
    Returns:
        Dictionnaire avec les résultats d'audit
    """
    results = {}
    
    # 1. DÉTECTER TOUS LES MÉDIAS
    detector = MediaDetector()
    media_data = await detector.detect_all_media(page)
    
    # 2. CATÉGORISER LES MÉDIAS
    categories = detector.categorize_media_types(media_data)
    
    # 3. DÉTERMINER L'APPLICABILITÉ DES CRITÈRES
    
    # Critère 4.1 - Médias temporels pré-enregistrés
    if not categories['has_temporal_media']:
        results['4.1'] = {
            'status': 'NA',
            'reason': 'Aucun média temporel détecté sur la page',
            'media_count': 0
        }
    else:
        # Effectuer les tests du critère 4.1
        results['4.1'] = await test_criterion_4_1(page, media_data)
        results['4.1']['media_count'] = (
            len(media_data['videos']) + 
            len(media_data['audios'])
        )
    
    # Critère 4.3 - Sous-titres synchronisés
    if not categories['has_temporal_media']:
        results['4.3'] = {
            'status': 'NA',
            'reason': 'Aucun média temporel synchronisé détecté'
        }
    else:
        results['4.3'] = await test_criterion_4_3(page, media_data)
    
    # Critère 4.8 - Médias non temporels
    if not categories['has_non_temporal_media']:
        results['4.8'] = {
            'status': 'NA',
            'reason': 'Aucun média non temporel détecté'
        }
    else:
        results['4.8'] = await test_criterion_4_8(page, media_data)
    
    # Critère 4.10 - Son déclenché automatiquement
    if not categories['has_autoplay_media'] and not categories['has_bgsound']:
        results['4.10'] = {
            'status': 'NA',
            'reason': 'Aucun son déclenché automatiquement'
        }
    else:
        results['4.10'] = await test_criterion_4_10(page, media_data)
    
    # Ajouter le résumé des médias détectés
    results['_media_summary'] = MediaDetector.get_media_summary(media_data)
    results['_media_categories'] = categories
    
    return results
```

## 📝 Tâche 3 : Créer des tests unitaires

Créez le fichier `test_media_detector.py` :

```python
"""
Tests unitaires pour le MediaDetector
"""

import pytest
from playwright.async_api import async_playwright
from media_detector import MediaDetector


@pytest.mark.asyncio
async def test_detect_video_element():
    """Test de détection d'une balise <video>"""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        
        # Créer une page HTML de test avec une vidéo
        await page.set_content("""
            <html>
                <body>
                    <video controls>
                        <source src="movie.mp4" type="video/mp4">
                        <track kind="captions" src="captions.vtt" srclang="fr">
                    </video>
                </body>
            </html>
        """)
        
        detector = MediaDetector()
        media_data = await detector.detect_all_media(page)
        
        assert len(media_data['videos']) == 1
        assert media_data['videos'][0]['controls'] == True
        assert media_data['videos'][0]['has_captions'] == True
        assert media_data['total_count'] == 1
        
        await browser.close()


@pytest.mark.asyncio
async def test_detect_object_flash():
    """Test de détection d'un objet Flash"""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        
        await page.set_content("""
            <html>
                <body>
                    <object type="application/x-shockwave-flash" data="movie.swf">
                        <p>Contenu alternatif pour Flash</p>
                    </object>
                </body>
            </html>
        """)
        
        detector = MediaDetector()
        media_data = await detector.detect_all_media(page)
        
        assert len(media_data['objects']) == 1
        assert media_data['objects'][0]['type'] == 'application/x-shockwave-flash'
        assert media_data['objects'][0]['has_fallback'] == True
        
        await browser.close()


@pytest.mark.asyncio
async def test_categorize_temporal_media():
    """Test de catégorisation des médias temporels"""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        
        await page.set_content("""
            <html>
                <body>
                    <video src="movie.mp4"></video>
                    <audio src="sound.mp3"></audio>
                </body>
            </html>
        """)
        
        detector = MediaDetector()
        media_data = await detector.detect_all_media(page)
        categories = detector.categorize_media_types(media_data)
        
        assert categories['has_temporal_media'] == True
        assert categories['has_non_temporal_media'] == False
        
        await browser.close()


@pytest.mark.asyncio
async def test_hidden_media_detection():
    """Test que les médias cachés sont quand même détectés"""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        
        await page.set_content("""
            <html>
                <body>
                    <video style="display:none" src="hidden.mp4"></video>
                    <audio style="visibility:hidden" src="hidden.mp3"></audio>
                </body>
            </html>
        """)
        
        detector = MediaDetector()
        media_data = await detector.detect_all_media(page)
        
        # Les médias doivent être détectés même s'ils sont cachés
        assert len(media_data['videos']) == 1
        assert len(media_data['audios']) == 1
        assert media_data['videos'][0]['visibility']['display'] == False
        assert media_data['audios'][0]['visibility']['visibility'] == False
        
        await browser.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

## 📝 Tâche 4 : Mettre à jour le README

Ajoutez une section dans le README.md du projet :

```markdown
## 🔍 Détection des médias multimédias

Le module `media_detector.py` fournit une détection robuste de tous les éléments multimédias présents sur une page web, conformément au RGAA 4.1.2 Section 4.

### Éléments détectés

- `<video>` - Vidéos HTML5
- `<audio>` - Audio HTML5
- `<object>` - Objets embarqués (Flash, etc.)
- `<embed>` - Éléments embarqués
- `<canvas>` - Canvas HTML5
- `<svg>` - Images vectorielles
- `<bgsound>` - Sons d'arrière-plan (obsolète)

### Utilisation

```python
from media_detector import MediaDetector

# Dans votre fonction d'audit
detector = MediaDetector()
media_data = await detector.detect_all_media(page)

# Vérifier la présence de médias
if detector.has_media_elements(media_data):
    print(detector.get_media_summary(media_data))

# Catégoriser pour l'applicabilité RGAA
categories = detector.categorize_media_types(media_data)
if categories['has_temporal_media']:
    # Tester les critères 4.1, 4.2, 4.3, etc.
    pass
```

### Gestion des cas spéciaux

- **Chargement dynamique** : Attend `networkidle` + 1s pour capturer les médias chargés via JS
- **Éléments masqués** : Détecte même les médias avec `display:none` ou `visibility:hidden`
- **Attributs d'accessibilité** : Capture tous les attributs ARIA pour l'analyse
```

## ✅ Checklist de vérification

Après avoir implémenté les modifications, vérifiez :

- [ ] Le fichier `media_detector.py` est créé et fonctionne
- [ ] Les tests unitaires passent avec succès
- [ ] Le module est intégré dans le code d'audit existant
- [ ] Les critères NA sont correctement déterminés selon la présence de médias
- [ ] Le README est mis à jour avec la documentation
- [ ] Les logs de débogage sont activés pour tracer les détections

## 🧪 Tests de validation

Testez le détecteur sur ces cas d'usage :

1. **Page avec vidéo YouTube embarquée**
   ```
   https://www.youtube.com/watch?v=dQw4w9WgXcQ
   ```

2. **Page avec lecteur audio HTML5**
   ```html
   <audio controls src="audio.mp3"></audio>
   ```

3. **Page avec Canvas dynamique**
   ```html
   <canvas id="myCanvas"></canvas>
   <script>// Animation canvas</script>
   ```

4. **Page avec ancien contenu Flash**
   ```html
   <object type="application/x-shockwave-flash" data="animation.swf"></object>
   ```

## 📊 Rapport de résultats attendus

Après intégration, le rapport d'audit doit contenir :

```json
{
  "url": "https://example.com",
  "criteres": {
    "4.1": {
      "status": "NC",  // ou "C" ou "NA"
      "reason": "Détection de 2 vidéos sans transcription",
      "media_count": 2
    }
  },
  "_media_summary": "Total: 3 élément(s) multimédia\n  - 2 <video>\n  - 1 <svg>",
  "_media_categories": {
    "has_temporal_media": true,
    "has_non_temporal_media": false,
    "has_svg": true
  }
}
```

## 🐛 Debugging

Si des médias ne sont toujours pas détectés :

1. Augmentez le timeout : `await detector.detect_all_media(page, timeout=30000)`
2. Activez les logs : `logging.basicConfig(level=logging.DEBUG)`
3. Vérifiez si les médias sont dans des iframes (nécessite une détection séparée)
4. Inspectez `media_data` pour voir ce qui est réellement détecté

## 📞 Support

Pour toute question ou problème avec cette implémentation, documentez :
- L'URL testée
- Les médias attendus vs détectés
- Les logs de console
- La structure HTML de la page

---

**Fin des instructions - Bonne implémentation ! 🚀**
