# -*- coding: utf-8 -*-
"""
Tests unitaires pour le module image_alt_checker (Critere 1.1 RGAA)
"""

import pytest
from playwright.async_api import async_playwright
from image_alt_checker import ImageAltChecker, audit_criterion_1_1, generate_ods_entries


@pytest.mark.asyncio
async def test_img_with_alt():
    """Image avec alt correct doit etre detectee conforme"""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        await page.set_content("""
            <html><body>
                <img src="logo.png" alt="Logo de l'entreprise">
            </body></html>
        """)

        checker = ImageAltChecker()
        results = await checker.check_all_images(page)

        assert results['test_1_1_1']['total'] == 1
        assert results['test_1_1_1']['with_alt'] == 1
        assert results['test_1_1_1']['without_alt'] == 0
        assert results['test_1_1_1']['images'][0]['accessible_name'] == "Logo de l'entreprise"
        assert results['test_1_1_1']['images'][0]['alt_source'] == 'alt'

        await browser.close()


@pytest.mark.asyncio
async def test_img_without_alt():
    """Image sans alt doit etre detectee NC"""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        await page.set_content("""
            <html><body>
                <img src="photo.jpg">
            </body></html>
        """)

        checker = ImageAltChecker()
        results = await checker.check_all_images(page)

        assert results['test_1_1_1']['total'] == 1
        assert results['test_1_1_1']['with_alt'] == 0
        assert results['test_1_1_1']['without_alt'] == 1
        assert results['test_1_1_1']['images'][0]['accessible_name'] is None
        assert results['summary']['status'] == 'NC'

        await browser.close()


@pytest.mark.asyncio
async def test_img_decorative():
    """Image decorative (alt='') doit etre conforme"""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        await page.set_content("""
            <html><body>
                <img src="deco.gif" alt="">
            </body></html>
        """)

        checker = ImageAltChecker()
        results = await checker.check_all_images(page)

        assert results['test_1_1_1']['total'] == 1
        assert results['test_1_1_1']['with_alt'] == 1
        assert results['test_1_1_1']['images'][0]['is_decorative'] is True
        assert results['summary']['status'] == 'C'

        await browser.close()


@pytest.mark.asyncio
async def test_img_aria_hidden():
    """Image avec aria-hidden='true' doit etre decorative"""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        await page.set_content("""
            <html><body>
                <img src="icon.png" aria-hidden="true">
            </body></html>
        """)

        checker = ImageAltChecker()
        results = await checker.check_all_images(page)

        assert results['test_1_1_1']['images'][0]['is_decorative'] is True
        assert results['test_1_1_1']['with_alt'] == 1

        await browser.close()


@pytest.mark.asyncio
async def test_img_role_presentation():
    """Image avec role='presentation' doit etre decorative"""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        await page.set_content("""
            <html><body>
                <img src="spacer.gif" role="presentation">
            </body></html>
        """)

        checker = ImageAltChecker()
        results = await checker.check_all_images(page)

        assert results['test_1_1_1']['images'][0]['is_decorative'] is True

        await browser.close()


@pytest.mark.asyncio
async def test_accessible_name_priority():
    """Verifier l'ordre de priorite aria-labelledby > aria-label > alt"""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        # aria-labelledby doit avoir la priorite
        await page.set_content("""
            <html><body>
                <span id="desc1">Description via labelledby</span>
                <img src="img.png"
                     aria-labelledby="desc1"
                     aria-label="Description via aria-label"
                     alt="Description via alt">
            </body></html>
        """)

        checker = ImageAltChecker()
        results = await checker.check_all_images(page)

        assert results['test_1_1_1']['images'][0]['accessible_name'] == "Description via labelledby"
        assert results['test_1_1_1']['images'][0]['alt_source'] == 'aria-labelledby'

        await browser.close()


@pytest.mark.asyncio
async def test_aria_label_over_alt():
    """aria-label doit avoir priorite sur alt"""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        await page.set_content("""
            <html><body>
                <img src="img.png"
                     aria-label="Description via aria-label"
                     alt="Description via alt">
            </body></html>
        """)

        checker = ImageAltChecker()
        results = await checker.check_all_images(page)

        assert results['test_1_1_1']['images'][0]['accessible_name'] == "Description via aria-label"
        assert results['test_1_1_1']['images'][0]['alt_source'] == 'aria-label'

        await browser.close()


@pytest.mark.asyncio
async def test_svg_without_role():
    """SVG sans role='img' doit etre detecte NC"""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        await page.set_content("""
            <html><body>
                <svg><title>Diagramme</title></svg>
            </body></html>
        """)

        checker = ImageAltChecker()
        results = await checker.check_all_images(page)

        assert results['test_1_1_5']['total'] == 1
        assert results['test_1_1_5']['without_alt'] == 1
        # Should have SVG_MISSING_ROLE issue
        issues = results['test_1_1_5']['svgs'][0]['issues']
        issue_types = [i['type'] for i in issues]
        assert 'SVG_MISSING_ROLE' in issue_types

        await browser.close()


@pytest.mark.asyncio
async def test_svg_correct():
    """SVG avec role='img' et aria-label doit etre conforme"""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        await page.set_content("""
            <html><body>
                <svg role="img" aria-label="Graphique des ventes"></svg>
            </body></html>
        """)

        checker = ImageAltChecker()
        results = await checker.check_all_images(page)

        assert results['test_1_1_5']['total'] == 1
        assert results['test_1_1_5']['with_alt'] == 1
        assert results['test_1_1_5']['svgs'][0]['accessible_name'] == "Graphique des ventes"

        await browser.close()


@pytest.mark.asyncio
async def test_svg_with_title():
    """SVG avec role='img' et <title> doit etre conforme"""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        await page.set_content("""
            <html><body>
                <svg role="img"><title>Logo entreprise</title></svg>
            </body></html>
        """)

        checker = ImageAltChecker()
        results = await checker.check_all_images(page)

        assert results['test_1_1_5']['with_alt'] == 1
        assert results['test_1_1_5']['svgs'][0]['accessible_name'] == "Logo entreprise"
        assert results['test_1_1_5']['svgs'][0]['alt_source'] == 'svg-title'

        await browser.close()


@pytest.mark.asyncio
async def test_svg_decorative():
    """SVG decoratif avec aria-hidden doit etre conforme"""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        await page.set_content("""
            <html><body>
                <svg aria-hidden="true"><circle cx="50" cy="50" r="40"/></svg>
            </body></html>
        """)

        checker = ImageAltChecker()
        results = await checker.check_all_images(page)

        assert results['test_1_1_5']['svgs'][0]['is_decorative'] is True
        assert results['test_1_1_5']['with_alt'] == 1

        await browser.close()


@pytest.mark.asyncio
async def test_area_with_alt():
    """Zone <area> avec alt doit etre conforme"""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        await page.set_content("""
            <html><body>
                <map name="navigation">
                    <area href="/page1" alt="Page 1" shape="rect" coords="0,0,100,50">
                    <area href="/page2" alt="Page 2" shape="rect" coords="100,0,200,50">
                </map>
            </body></html>
        """)

        checker = ImageAltChecker()
        results = await checker.check_all_images(page)

        assert results['test_1_1_2']['total'] == 2
        assert results['test_1_1_2']['with_alt'] == 2
        assert results['test_1_1_2']['without_alt'] == 0

        await browser.close()


@pytest.mark.asyncio
async def test_area_without_alt():
    """Zone <area> sans alt doit etre NC"""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        await page.set_content("""
            <html><body>
                <map name="navigation">
                    <area href="/page1" shape="rect" coords="0,0,100,50">
                </map>
            </body></html>
        """)

        checker = ImageAltChecker()
        results = await checker.check_all_images(page)

        assert results['test_1_1_2']['total'] == 1
        assert results['test_1_1_2']['without_alt'] == 1
        assert results['summary']['status'] == 'NC'

        await browser.close()


@pytest.mark.asyncio
async def test_input_image_with_alt():
    """Input type='image' avec alt doit etre conforme"""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        await page.set_content("""
            <html><body>
                <input type="image" src="submit.png" alt="Soumettre">
            </body></html>
        """)

        checker = ImageAltChecker()
        results = await checker.check_all_images(page)

        assert results['test_1_1_3']['total'] == 1
        assert results['test_1_1_3']['with_alt'] == 1
        assert results['test_1_1_3']['buttons'][0]['accessible_name'] == "Soumettre"

        await browser.close()


@pytest.mark.asyncio
async def test_input_image_without_alt():
    """Input type='image' sans alt doit etre NC"""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        await page.set_content("""
            <html><body>
                <input type="image" src="submit.png">
            </body></html>
        """)

        checker = ImageAltChecker()
        results = await checker.check_all_images(page)

        assert results['test_1_1_3']['total'] == 1
        assert results['test_1_1_3']['without_alt'] == 1
        assert results['summary']['status'] == 'NC'

        await browser.close()


@pytest.mark.asyncio
async def test_canvas_with_aria_label():
    """Canvas avec aria-label doit etre conforme"""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        await page.set_content("""
            <html><body>
                <canvas id="chart" aria-label="Graphique des ventes 2024"></canvas>
            </body></html>
        """)

        checker = ImageAltChecker()
        results = await checker.check_all_images(page)

        assert results['test_1_1_8']['total'] == 1
        assert results['test_1_1_8']['with_alt'] == 1
        assert results['test_1_1_8']['canvas'][0]['accessible_name'] == "Graphique des ventes 2024"

        await browser.close()


@pytest.mark.asyncio
async def test_canvas_with_content():
    """Canvas avec contenu alternatif entre les balises"""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        await page.set_content("""
            <html><body>
                <canvas id="chart">Graphique: ventes en hausse de 15%</canvas>
            </body></html>
        """)

        checker = ImageAltChecker()
        results = await checker.check_all_images(page)

        assert results['test_1_1_8']['total'] == 1
        assert results['test_1_1_8']['with_alt'] == 1
        assert results['test_1_1_8']['canvas'][0]['alt_source'] == 'canvas-content'

        await browser.close()


@pytest.mark.asyncio
async def test_canvas_without_alt():
    """Canvas sans alternative doit etre NC"""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        await page.set_content("""
            <html><body>
                <canvas id="myCanvas"></canvas>
            </body></html>
        """)

        checker = ImageAltChecker()
        results = await checker.check_all_images(page)

        assert results['test_1_1_8']['total'] == 1
        assert results['test_1_1_8']['without_alt'] == 1
        assert results['summary']['status'] == 'NC'

        await browser.close()


@pytest.mark.asyncio
async def test_object_image():
    """Object type image avec aria-label doit etre conforme"""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        await page.set_content("""
            <html><body>
                <object type="image/png" data="photo.png"
                        role="img" aria-label="Photo de groupe"></object>
            </body></html>
        """)

        checker = ImageAltChecker()
        results = await checker.check_all_images(page)

        assert results['test_1_1_6']['total'] == 1
        assert results['test_1_1_6']['with_alt'] == 1
        assert results['test_1_1_6']['objects'][0]['accessible_name'] == "Photo de groupe"

        await browser.close()


@pytest.mark.asyncio
async def test_embed_image():
    """Embed type image avec aria-label doit etre conforme"""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        await page.set_content("""
            <html><body>
                <embed type="image/svg+xml" src="diagram.svg"
                       role="img" aria-label="Diagramme de flux">
            </body></html>
        """)

        checker = ImageAltChecker()
        results = await checker.check_all_images(page)

        assert results['test_1_1_7']['total'] == 1
        assert results['test_1_1_7']['with_alt'] == 1
        assert results['test_1_1_7']['embeds'][0]['accessible_name'] == "Diagramme de flux"

        await browser.close()


@pytest.mark.asyncio
async def test_role_img_element():
    """Element avec role='img' doit etre detecte dans test 1.1.1"""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        await page.set_content("""
            <html><body>
                <div role="img" aria-label="Emoticone souriant">:-)</div>
            </body></html>
        """)

        checker = ImageAltChecker()
        results = await checker.check_all_images(page)

        assert results['test_1_1_1']['total'] == 1
        assert results['test_1_1_1']['with_alt'] == 1
        assert results['test_1_1_1']['images'][0]['accessible_name'] == "Emoticone souriant"

        await browser.close()


@pytest.mark.asyncio
async def test_generic_alt_warning():
    """Alternative generique doit generer un avertissement"""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        await page.set_content("""
            <html><body>
                <img src="photo.jpg" alt="image">
            </body></html>
        """)

        checker = ImageAltChecker()
        results = await checker.check_all_images(page)

        issues = results['test_1_1_1']['images'][0]['issues']
        issue_types = [i['type'] for i in issues]
        assert 'GENERIC_ALT' in issue_types
        assert results['summary']['total_warnings'] >= 1

        await browser.close()


@pytest.mark.asyncio
async def test_filename_as_alt_error():
    """Nom de fichier comme alt doit generer une erreur"""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        await page.set_content("""
            <html><body>
                <img src="photo.jpg" alt="DSC_1234.jpg">
            </body></html>
        """)

        checker = ImageAltChecker()
        results = await checker.check_all_images(page)

        issues = results['test_1_1_1']['images'][0]['issues']
        issue_types = [i['type'] for i in issues]
        assert 'FILENAME_AS_ALT' in issue_types
        assert results['summary']['total_errors'] >= 1

        await browser.close()


@pytest.mark.asyncio
async def test_alt_too_long_warning():
    """Alternative trop longue doit generer un avertissement"""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        long_alt = "A" * 100
        await page.set_content(f"""
            <html><body>
                <img src="photo.jpg" alt="{long_alt}">
            </body></html>
        """)

        checker = ImageAltChecker()
        results = await checker.check_all_images(page)

        issues = results['test_1_1_1']['images'][0]['issues']
        issue_types = [i['type'] for i in issues]
        assert 'ALT_TOO_LONG' in issue_types

        await browser.close()


@pytest.mark.asyncio
async def test_no_images():
    """Page sans images doit retourner NA"""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        await page.set_content("""
            <html><body>
                <h1>Page sans images</h1>
                <p>Juste du texte.</p>
            </body></html>
        """)

        checker = ImageAltChecker()
        results = await checker.check_all_images(page)

        assert results['summary']['total_images'] == 0
        assert results['summary']['compliance_rate'] == 0

        await browser.close()


@pytest.mark.asyncio
async def test_mixed_compliance():
    """Page avec images conformes et non conformes"""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        await page.set_content("""
            <html><body>
                <img src="logo.png" alt="Logo">
                <img src="photo.jpg">
                <img src="deco.gif" alt="">
            </body></html>
        """)

        checker = ImageAltChecker()
        results = await checker.check_all_images(page)

        assert results['test_1_1_1']['total'] == 3
        assert results['test_1_1_1']['with_alt'] == 2
        assert results['test_1_1_1']['without_alt'] == 1
        assert results['summary']['status'] == 'NC'

        await browser.close()


@pytest.mark.asyncio
async def test_aria_labelledby_multiple_ids():
    """aria-labelledby avec plusieurs IDs doit concatener les textes"""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        await page.set_content("""
            <html><body>
                <span id="part1">Premiere partie</span>
                <span id="part2">Deuxieme partie</span>
                <img src="img.png" aria-labelledby="part1 part2">
            </body></html>
        """)

        checker = ImageAltChecker()
        results = await checker.check_all_images(page)

        assert results['test_1_1_1']['images'][0]['accessible_name'] == "Premiere partie Deuxieme partie"

        await browser.close()


@pytest.mark.asyncio
async def test_audit_criterion_1_1_function():
    """Test de la fonction d'audit complete"""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        await page.set_content("""
            <html><body>
                <img src="logo.png" alt="Logo">
                <img src="photo.jpg">
            </body></html>
        """)

        audit = await audit_criterion_1_1(page)

        assert audit['criterion'] == '1.1'
        assert audit['status'] == 'NC'
        assert audit['automated_coverage'] == '60%'
        assert audit['total_images'] == 2
        assert audit['errors'] >= 1
        assert 'report' in audit
        assert len(audit['manual_checks_needed']) > 0

        await browser.close()


@pytest.mark.asyncio
async def test_audit_criterion_1_1_na():
    """Test audit NA quand aucune image"""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        await page.set_content("""
            <html><body>
                <h1>Page sans images</h1>
            </body></html>
        """)

        audit = await audit_criterion_1_1(page)

        assert audit['criterion'] == '1.1'
        assert audit['status'] == 'NA'
        assert audit['total_images'] == 0

        await browser.close()


@pytest.mark.asyncio
async def test_generate_ods_entries():
    """Test de la generation des entrees ODS"""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        await page.set_content("""
            <html><body>
                <img src="logo.png" alt="Logo">
                <img src="photo.jpg">
            </body></html>
        """)

        audit = await audit_criterion_1_1(page)
        entries = generate_ods_entries(audit)

        assert len(entries) == 1
        assert entries[0]['critere'] == '1.1'
        assert entries[0]['statut'] == 'NC'
        assert '2 images' in entries[0]['commentaire']

        await browser.close()


@pytest.mark.asyncio
async def test_format_report():
    """Test du formatage du rapport"""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        await page.set_content("""
            <html><body>
                <img src="logo.png" alt="Logo">
                <img src="photo.jpg">
                <svg role="img" aria-label="Chart"></svg>
            </body></html>
        """)

        checker = ImageAltChecker()
        results = await checker.check_all_images(page)
        report = checker.format_report(results)

        assert "RAPPORT CRITERE 1.1" in report
        assert "RESUME GLOBAL" in report
        assert "COUVERTURE AUTOMATIQUE : 60%" in report
        assert "VERIFICATION MANUELLE OBLIGATOIRE" in report

        await browser.close()


@pytest.mark.asyncio
async def test_object_without_alt():
    """Object image sans alternative doit etre NC"""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        await page.set_content("""
            <html><body>
                <object type="image/png" data="photo.png"></object>
            </body></html>
        """)

        checker = ImageAltChecker()
        results = await checker.check_all_images(page)

        assert results['test_1_1_6']['total'] == 1
        assert results['test_1_1_6']['without_alt'] == 1
        assert results['summary']['status'] == 'NC'

        await browser.close()


@pytest.mark.asyncio
async def test_img_with_title_fallback():
    """Image avec title (sans alt) doit utiliser title comme fallback"""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        await page.set_content("""
            <html><body>
                <img src="info.png" title="Information importante">
            </body></html>
        """)

        checker = ImageAltChecker()
        results = await checker.check_all_images(page)

        # title is checked after alt for img, but since no alt attr at all,
        # getAccessibleName returns null for alt step (alt is null, not "")
        # then falls through to title
        assert results['test_1_1_1']['images'][0]['accessible_name'] == "Information importante"
        assert results['test_1_1_1']['images'][0]['alt_source'] == 'title'

        await browser.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
