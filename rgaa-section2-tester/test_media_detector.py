# -*- coding: utf-8 -*-
"""
Tests unitaires pour le MediaDetector
"""

import pytest
from playwright.async_api import async_playwright
from media_detector import MediaDetector


@pytest.mark.asyncio
async def test_detect_video_element():
    """Test de detection d'une balise <video>"""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        # Creer une page HTML de test avec une video
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
        assert media_data['videos'][0]['controls'] is True
        assert media_data['videos'][0]['has_captions'] is True
        assert media_data['total_count'] == 1

        await browser.close()


@pytest.mark.asyncio
async def test_detect_object_flash():
    """Test de detection d'un objet Flash"""
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
        assert media_data['objects'][0]['has_fallback'] is True

        await browser.close()


@pytest.mark.asyncio
async def test_categorize_temporal_media():
    """Test de categorisation des medias temporels"""
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

        assert categories['has_temporal_media'] is True
        assert categories['has_non_temporal_media'] is False

        await browser.close()


@pytest.mark.asyncio
async def test_hidden_media_detection():
    """Test que les medias caches sont quand meme detectes"""
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

        # Les medias doivent etre detectes meme s'ils sont caches
        assert len(media_data['videos']) == 1
        assert len(media_data['audios']) == 1
        assert media_data['videos'][0]['visibility']['display'] is False
        assert media_data['audios'][0]['visibility']['visibility'] is False

        await browser.close()


@pytest.mark.asyncio
async def test_detect_canvas():
    """Test de detection d'un canvas"""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        await page.set_content("""
            <html>
                <body>
                    <canvas id="myCanvas" width="400" height="300"
                            aria-label="Graphique des ventes">
                        Contenu alternatif du canvas
                    </canvas>
                </body>
            </html>
        """)

        detector = MediaDetector()
        media_data = await detector.detect_all_media(page)

        assert len(media_data['canvas']) == 1
        assert media_data['canvas'][0]['has_fallback'] is True
        assert media_data['canvas'][0]['attributes']['aria-label'] == 'Graphique des ventes'

        categories = detector.categorize_media_types(media_data)
        assert categories['has_non_temporal_media'] is True

        await browser.close()


@pytest.mark.asyncio
async def test_detect_svg():
    """Test de detection d'un SVG"""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        await page.set_content("""
            <html>
                <body>
                    <svg role="img" aria-label="Logo">
                        <title>Logo de l'entreprise</title>
                        <desc>Un cercle bleu</desc>
                        <circle cx="50" cy="50" r="40" fill="blue"/>
                    </svg>
                </body>
            </html>
        """)

        detector = MediaDetector()
        media_data = await detector.detect_all_media(page)

        assert len(media_data['svg']) == 1
        assert media_data['svg'][0]['has_title'] is True
        assert media_data['svg'][0]['has_desc'] is True
        assert media_data['svg'][0]['role'] == 'img'

        categories = detector.categorize_media_types(media_data)
        assert categories['has_svg'] is True

        await browser.close()


@pytest.mark.asyncio
async def test_detect_embed():
    """Test de detection d'un embed"""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        await page.set_content("""
            <html>
                <body>
                    <embed type="video/mp4" src="video.mp4" width="640" height="480">
                </body>
            </html>
        """)

        detector = MediaDetector()
        media_data = await detector.detect_all_media(page)

        assert len(media_data['embeds']) == 1
        assert media_data['embeds'][0]['type'] == 'video/mp4'

        categories = detector.categorize_media_types(media_data)
        assert categories['has_temporal_media'] is True
        assert categories['has_embed_tags'] is True

        await browser.close()


@pytest.mark.asyncio
async def test_detect_autoplay_media():
    """Test de detection de medias avec autoplay"""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        await page.set_content("""
            <html>
                <body>
                    <video autoplay muted src="bg-video.mp4"></video>
                </body>
            </html>
        """)

        detector = MediaDetector()
        media_data = await detector.detect_all_media(page)

        assert len(media_data['videos']) == 1
        assert media_data['videos'][0]['autoplay'] is True
        assert media_data['videos'][0]['muted'] is True

        categories = detector.categorize_media_types(media_data)
        assert categories['has_autoplay_media'] is True

        await browser.close()


@pytest.mark.asyncio
async def test_no_media():
    """Test d'une page sans medias"""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        await page.set_content("""
            <html>
                <body>
                    <h1>Page sans medias</h1>
                    <p>Juste du texte.</p>
                </body>
            </html>
        """)

        detector = MediaDetector()
        media_data = await detector.detect_all_media(page)

        assert media_data['total_count'] == 0
        assert detector.has_media_elements(media_data) is False

        summary = detector.get_media_summary(media_data)
        assert "Aucun" in summary

        await browser.close()


@pytest.mark.asyncio
async def test_media_summary():
    """Test du resume des medias"""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        await page.set_content("""
            <html>
                <body>
                    <video controls src="movie.mp4"></video>
                    <audio controls src="sound.mp3"></audio>
                    <canvas id="chart" width="400" height="300"></canvas>
                </body>
            </html>
        """)

        detector = MediaDetector()
        media_data = await detector.detect_all_media(page)

        summary = detector.get_media_summary(media_data)
        assert "3 element(s)" in summary
        assert "<video>" in summary
        assert "<audio>" in summary
        assert "<canvas>" in summary

        await browser.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
