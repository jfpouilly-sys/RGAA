#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RGAA Tester - Point d'entree principal

Application de test de conformite RGAA 4.1.2 avec interface graphique
et generation de rapports Markdown.

Modes :
    - GUI (defaut) : Interface graphique avec onglets Section 2 + ODS Audit
    - CLI Section 2 : Analyse cadres/frames en ligne de commande
    - CLI Focus 10.7 : Analyse Playwright de la visibilite du focus

Usage:
    python main.py                                    # Interface graphique
    python main.py --cli URL                          # Section 2 (cadres)
    python main.py --focus "P01|https://example.com"  # Focus 10.7 (Playwright)
    python main.py --help                             # Aide
"""

import argparse
import os
import sys
from datetime import datetime
from pathlib import Path

# Ajouter le repertoire parent au path si necessaire
sys.path.insert(0, str(Path(__file__).parent))


def mode_graphique():
    """Lance l'application en mode graphique."""
    try:
        from rgaa_tester.gui import lancer_application
        lancer_application()
    except ImportError as e:
        print(f"Erreur: Impossible de charger l'interface graphique: {e}")
        print("Verifiez que tkinter est installe sur votre systeme.")
        sys.exit(1)


def mode_cli(url: str, max_pages: int = 1, sortie: str = None):
    """
    Lance l'analyse en mode ligne de commande.

    Args:
        url: URL a analyser.
        max_pages: Nombre maximum de pages a crawler.
        sortie: Chemin du fichier de rapport (optionnel).
    """
    from rgaa_tester.config import get_config
    from rgaa_tester.crawler import Crawler
    from rgaa_tester.analyzer import AnalyseurRGAA, ResultatAnalyseGlobal
    from rgaa_tester.report_generator import GenerateurRapport
    from rgaa_tester.utils import normaliser_url, formater_date

    print("=" * 60)
    print("RGAA Section 2 Tester - Mode ligne de commande")
    print("=" * 60)
    print()

    config = get_config()
    crawler = Crawler(config)
    analyseur = AnalyseurRGAA(config)
    generateur = GenerateurRapport(config)

    # Configurer le callback de log
    crawler.definir_callback_log(lambda msg: print(f"  {msg}"))

    url = normaliser_url(url)
    print(f"URL de depart : {url}")
    print(f"Maximum de pages : {max_pages}")
    print()

    # Crawl
    print("[1/3] Recuperation des pages...")
    if max_pages == 1:
        page = crawler.crawl_page_unique(url)
        pages = [page] if page and page.html else []
    else:
        pages = crawler.crawl(url, max_pages)

    if not pages:
        print("Erreur: Aucune page recuperee.")
        sys.exit(1)

    print(f"  -> {len(pages)} page(s) recuperee(s)")
    print()

    # Analyse
    print("[2/3] Analyse RGAA Section 2...")
    resultat = ResultatAnalyseGlobal(
        url_depart=url,
        date_analyse=formater_date()
    )

    for page in pages:
        if page.html:
            resultat_page = analyseur.analyser_page(page.html, page.url)
            resultat.pages.append(resultat_page)
            print(f"  -> {page.url[:50]}... : {resultat_page.cadres_testes} cadre(s)")

    resultat.calculer_statistiques()
    print()

    # Afficher le resume
    print("=" * 60)
    print("RESUME DE L'ANALYSE")
    print("=" * 60)
    print(f"  Pages analysees      : {resultat.total_pages}")
    print(f"  Cadres detectes      : {resultat.total_cadres}")
    print(f"  Cadres testes        : {resultat.total_cadres_testes}")
    print(f"  Cadres exemptes      : {resultat.total_exemptes}")
    print()
    print("  CRITERE 2.1 - Presence de titre :")
    print(f"    Conformes          : {resultat.total_conformes_2_1}")
    print(f"    Non conformes      : {resultat.total_non_conformes_2_1}")
    print(f"    Taux de conformite : {resultat.taux_conformite_2_1:.1f}%")
    print()
    print("  CRITERE 2.2 - Pertinence du titre :")
    print(f"    A verifier         : {resultat.total_a_verifier_2_2}")
    print(f"    Alertes            : {resultat.total_alertes_2_2}")
    print()
    print(f"  STATUT GLOBAL : {resultat.statut_section_2}")
    print("=" * 60)
    print()

    # Generation du rapport
    print("[3/3] Generation du rapport...")
    chemin_rapport = generateur.generer_rapport(resultat, sortie)
    print(f"  -> Rapport genere : {chemin_rapport}")
    print()
    print("Termine.")


def mode_focus(urls_raw: list, site_name: str, output_dir: str, headless: bool):
    """
    Lance l'analyse de visibilite du focus (critere 10.7) via Playwright.

    Les resultats sont generes dans le meme format que les autres analyses :
    - Rapport Markdown dans le repertoire de sortie
    - Resultats affichables dans le journal

    Args:
        urls_raw: Liste de chaines "ID|URL" ou "URL"
        site_name: Nom du site audite
        output_dir: Repertoire de sortie
        headless: Mode headless (sans fenetre navigateur)
    """
    try:
        from criterion_10_7.focus_tester import FocusTester
        from criterion_10_7.report_generator import FocusReportGenerator
    except ImportError:
        print("Erreur: Le module criterion_10_7 requiert Playwright.")
        print("Installez avec: pip install playwright && playwright install chromium")
        sys.exit(1)

    # Parser les URLs
    urls = []
    for entry in urls_raw:
        entry = entry.strip()
        if '|' in entry:
            page_id, url = entry.split('|', 1)
            urls.append((url.strip(), page_id.strip()))
        else:
            urls.append((entry, f"P{len(urls)+1:02d}"))

    print("=" * 60)
    print("RGAA 10.7 — Test de visibilite du focus (Playwright)")
    print("=" * 60)
    print()
    print(f"Site      : {site_name}")
    print(f"Pages     : {len(urls)}")
    print(f"Headless  : {'Oui' if headless else 'Non'}")
    print(f"Sortie    : {output_dir}")
    print()

    with FocusTester(headless=headless) as tester:
        results = []

        for i, (url, page_id) in enumerate(urls):
            print(f"[{i+1}/{len(urls)}] {page_id} : {url}")

            def progress_cb(msg, pct):
                print(f"  {msg}")

            result = tester.test_page(url, page_id, progress_cb)
            results.append(result)

            print(
                f"  -> Statut : {result.suggested_status} "
                f"(confiance: {result.confidence})"
            )
            print(
                f"  -> C={result.total_conforme}, "
                f"NC={result.total_non_conforme}, "
                f"A verifier={result.total_a_verifier}"
            )
            print()

    # Generer le rapport
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_path = os.path.join(
        output_dir, f"rapport_10_7_{timestamp}.md"
    )

    generator = FocusReportGenerator()
    generator.generate(results, report_path, site_name)

    # Synthese
    print("=" * 60)
    print("SYNTHESE — Critere 10.7 (Focus visible)")
    print("=" * 60)
    total_c = sum(r.total_conforme for r in results)
    total_nc = sum(r.total_non_conforme for r in results)
    total_av = sum(r.total_a_verifier for r in results)
    total_el = sum(r.total_visible for r in results)
    print(f"  Elements analyses  : {total_el}")
    print(f"  Conformes (C)      : {total_c}")
    print(f"  Non conformes (NC) : {total_nc}")
    print(f"  A verifier         : {total_av}")
    print()

    for r in results:
        print(f"  {r.page_id}: {r.suggested_status} ({r.confidence}) — {r.details}")

    print()
    print(f"Rapport genere : {report_path}")
    print()
    print("Termine.")


def main():
    """Point d'entree principal."""
    parser = argparse.ArgumentParser(
        description="RGAA Tester - Testeur de conformite accessibilite RGAA 4.1.2",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples:
  python main.py                                               # Interface graphique
  python main.py --cli https://exemple.fr                      # Section 2 (cadres)
  python main.py --cli https://exemple.fr --max-pages 10       # Crawler multi-pages
  python main.py --focus "P01|https://exemple.fr/"             # Focus 10.7 (1 page)
  python main.py --focus "P01|https://exemple.fr/" "P02|https://exemple.fr/about"
  python main.py --focus "https://exemple.fr/" --site "Mon Site" --output ./rapports

Pour plus d'informations, consultez le README.md
"""
    )

    parser.add_argument(
        '--cli',
        metavar='URL',
        help="Mode Section 2 : analyse l'URL specifiee (cadres/frames)"
    )

    parser.add_argument(
        '--max-pages',
        type=int,
        default=1,
        help="Nombre maximum de pages a crawler (defaut: 1)"
    )

    parser.add_argument(
        '--focus',
        nargs='+',
        metavar='URL',
        help=(
            "Mode Focus 10.7 : teste la visibilite du focus via Playwright. "
            "URLs au format ID|URL ou URL seule"
        )
    )

    parser.add_argument(
        '--site',
        default="Site audite",
        help="Nom du site audite (pour --focus, defaut: Site audite)"
    )

    parser.add_argument(
        '--output', '-o',
        help=(
            "Chemin du fichier de rapport (--cli) ou repertoire de "
            "sortie (--focus, defaut: ~/rgaa-reports)"
        )
    )

    parser.add_argument(
        '--no-headless',
        action='store_true',
        help="Afficher le navigateur pendant l'analyse (--focus uniquement)"
    )

    parser.add_argument(
        '--version', '-v',
        action='version',
        version='RGAA Tester v1.1.0 (Section 2 + Focus 10.7)'
    )

    args = parser.parse_args()

    if args.focus:
        output = args.output or os.path.expanduser("~/rgaa-reports")
        mode_focus(args.focus, args.site, output, not args.no_headless)
    elif args.cli:
        mode_cli(args.cli, args.max_pages, args.output)
    else:
        mode_graphique()


if __name__ == "__main__":
    main()
