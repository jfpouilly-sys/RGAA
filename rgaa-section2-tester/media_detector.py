# -*- coding: utf-8 -*-
"""
Module de detection robuste des elements multimedias pour RGAA 4.1.2
Detecte : <object>, <embed>, <video>, <audio>, <canvas>, <svg>, <bgsound>

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
    """Detecteur d'elements multimedias pour audits RGAA Section 4"""

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
        Detecte tous les elements multimedias presents sur la page.

        Args:
            page: Page Playwright chargee
            timeout: Delai d'attente pour networkidle (ms)

        Returns:
            Dictionnaire contenant tous les medias detectes avec leurs proprietes

        Structure de retour:
            {
                'objects': [...],      # Liste des <object>
                'embeds': [...],       # Liste des <embed>
                'videos': [...],       # Liste des <video>
                'audios': [...],       # Liste des <audio>
                'canvas': [...],       # Liste des <canvas>
                'svg': [...],          # Liste des <svg>
                'bgsound': [...],      # Liste des <bgsound>
                'total_count': int     # Nombre total d'elements
            }
        """
        # Attendre que la page soit completement chargee (y compris JS dynamique)
        try:
            await page.wait_for_load_state('networkidle', timeout=timeout)
        except Exception as e:
            logger.warning(f"Timeout networkidle apres {timeout}ms: {e}")
            # Continuer quand meme pour detecter ce qui est deja charge

        # Pause supplementaire pour laisser le JS s'executer
        await page.wait_for_timeout(1000)

        # Executer la detection dans le contexte du navigateur
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

                // Fonction utilitaire pour verifier la visibilite
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

                // Detection des balises <object>
                document.querySelectorAll('object').forEach((obj, index) => {
                    const visibility = isVisible(obj);
                    const textContent = obj.textContent || '';
                    result.objects.push({
                        index: index,
                        type: obj.getAttribute('type') || 'non-defini',
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

                // Detection des balises <embed>
                document.querySelectorAll('embed').forEach((emb, index) => {
                    const visibility = isVisible(emb);
                    result.embeds.push({
                        index: index,
                        type: emb.getAttribute('type') || 'non-defini',
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

                // Detection des balises <video>
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

                // Detection des balises <audio>
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

                // Detection des balises <canvas>
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

                // Detection des balises <svg>
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
                            class: (svg.className && svg.className.baseVal) || null,
                            'aria-label': svg.getAttribute('aria-label'),
                            'aria-labelledby': svg.getAttribute('aria-labelledby'),
                            'aria-describedby': svg.getAttribute('aria-describedby'),
                            'aria-hidden': svg.getAttribute('aria-hidden'),
                            title: svg.getAttribute('title')
                        }
                    });
                });

                // Detection des balises <bgsound> (obsolete IE)
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

        logger.info(f"Detection medias terminee: {media_data['total_count']} elements au total")
        logger.debug(f"Detail: objects={len(media_data['objects'])}, embeds={len(media_data['embeds'])}, "
                    f"videos={len(media_data['videos'])}, audios={len(media_data['audios'])}, "
                    f"canvas={len(media_data['canvas'])}, svg={len(media_data['svg'])}")

        return media_data

    @staticmethod
    def has_media_elements(media_data: Dict[str, Any]) -> bool:
        """
        Verifie si des elements multimedias sont presents.

        Args:
            media_data: Donnees retournees par detect_all_media()

        Returns:
            True si au moins un element multimedia est present
        """
        return media_data.get('total_count', 0) > 0

    @staticmethod
    def categorize_media_types(media_data: Dict[str, Any]) -> Dict[str, bool]:
        """
        Categorise les types de medias presents pour determiner
        l'applicabilite des criteres RGAA Section 4.

        Args:
            media_data: Donnees retournees par detect_all_media()

        Returns:
            Dictionnaire indiquant la presence de chaque categorie de media:
            - has_temporal_media: medias temporels (video, audio)
            - has_non_temporal_media: medias non temporels (canvas, object image)
            - has_svg: images vectorielles SVG
            - has_object_tags: balises <object>
            - has_embed_tags: balises <embed>
            - has_bgsound: balises <bgsound>
            - has_autoplay_media: medias avec lecture automatique
        """
        # Detection des medias temporels
        has_video = len(media_data.get('videos', [])) > 0
        has_audio = len(media_data.get('audios', [])) > 0

        # Verifier les objects avec type video/audio
        objects_temporal = any(
            obj.get('type', '').startswith(('video/', 'audio/', 'application/x-shockwave-flash'))
            for obj in media_data.get('objects', [])
        )

        # Verifier les embeds avec type video/audio
        embeds_temporal = any(
            emb.get('type', '').startswith(('video/', 'audio/', 'application/x-shockwave-flash'))
            for emb in media_data.get('embeds', [])
        )

        # Detection des medias non temporels (images)
        has_canvas = len(media_data.get('canvas', [])) > 0

        objects_non_temporal = any(
            obj.get('type', '').startswith('image/')
            for obj in media_data.get('objects', [])
        )

        embeds_non_temporal = any(
            emb.get('type', '').startswith('image/')
            for emb in media_data.get('embeds', [])
        )

        # Detection de l'autoplay
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
        Genere un resume textuel des medias detectes.

        Args:
            media_data: Donnees retournees par detect_all_media()

        Returns:
            Chaine de caracteres formatee avec le resume
        """
        summary = []

        if media_data['total_count'] == 0:
            return "Aucun element multimedia detecte sur la page."

        summary.append(f"Total: {media_data['total_count']} element(s) multimedia detecte(s)")

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
    """Fonction de test pour verifier le detecteur"""
    from playwright.async_api import async_playwright

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        # URL de test - Remplacer par une URL reelle
        test_url = input("Entrez l'URL a tester (ou Entree pour exemple): ").strip()
        if not test_url:
            test_url = "https://www.youtube.com"

        print(f"\nAnalyse de: {test_url}")
        await page.goto(test_url, wait_until='domcontentloaded')

        detector = MediaDetector()
        media_data = await detector.detect_all_media(page)

        print(f"\n{'='*60}")
        print(MediaDetector.get_media_summary(media_data))
        print(f"{'='*60}")

        categories = detector.categorize_media_types(media_data)
        print(f"\nCategorisation (applicabilite RGAA):")
        for cat, present in categories.items():
            status = "OUI" if present else "NON"
            print(f"  {cat}: {status}")

        # Afficher les details des videos si presentes
        if media_data['videos']:
            print(f"\nDetails des videos:")
            for vid in media_data['videos']:
                print(f"  Video #{vid['index']}:")
                print(f"    - Controls: {vid['controls']}")
                print(f"    - Autoplay: {vid['autoplay']}")
                print(f"    - Captions: {vid['has_captions']}")
                print(f"    - ARIA label: {vid['attributes'].get('aria-label', 'Non defini')}")

        await browser.close()


if __name__ == "__main__":
    import asyncio
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main_test())
