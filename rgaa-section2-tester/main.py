#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RGAA Section 2 Tester - Point d'entrée principal

Application de test de conformité RGAA 4.1.2 Section 2 (Cadres/Frames)
avec interface graphique et génération de rapports Markdown.

Usage:
    python main.py              # Lance l'interface graphique
    python main.py --cli URL    # Mode ligne de commande
    python main.py --help       # Affiche l'aide

Auteur: RGAA Tester
Version: 1.0.0
"""

import argparse
import sys
from pathlib import Path

# Ajouter le répertoire parent au path si nécessaire
sys.path.insert(0, str(Path(__file__).parent))


def mode_graphique():
    """Lance l'application en mode graphique."""
    try:
        from rgaa_tester.gui import lancer_application
        lancer_application()
    except ImportError as e:
        print(f"Erreur: Impossible de charger l'interface graphique: {e}")
        print("Vérifiez que tkinter est installé sur votre système.")
        sys.exit(1)


def mode_cli(url: str, max_pages: int = 1, sortie: str = None):
    """
    Lance l'analyse en mode ligne de commande.

    Args:
        url: URL à analyser.
        max_pages: Nombre maximum de pages à crawler.
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
    print(f"URL de départ : {url}")
    print(f"Maximum de pages : {max_pages}")
    print()

    # Crawl
    print("[1/3] Récupération des pages...")
    if max_pages == 1:
        page = crawler.crawl_page_unique(url)
        pages = [page] if page and page.html else []
    else:
        pages = crawler.crawl(url, max_pages)

    if not pages:
        print("Erreur: Aucune page récupérée.")
        sys.exit(1)

    print(f"  -> {len(pages)} page(s) récupérée(s)")
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

    # Afficher le résumé
    print("=" * 60)
    print("RÉSUMÉ DE L'ANALYSE")
    print("=" * 60)
    print(f"  Pages analysées      : {resultat.total_pages}")
    print(f"  Cadres détectés      : {resultat.total_cadres}")
    print(f"  Cadres testés        : {resultat.total_cadres_testes}")
    print(f"  Cadres exemptés      : {resultat.total_exemptes}")
    print()
    print("  CRITÈRE 2.1 - Présence de titre :")
    print(f"    Conformes          : {resultat.total_conformes_2_1}")
    print(f"    Non conformes      : {resultat.total_non_conformes_2_1}")
    print(f"    Taux de conformité : {resultat.taux_conformite_2_1:.1f}%")
    print()
    print("  CRITÈRE 2.2 - Pertinence du titre :")
    print(f"    À vérifier         : {resultat.total_a_verifier_2_2}")
    print(f"    Alertes            : {resultat.total_alertes_2_2}")
    print()
    print(f"  STATUT GLOBAL : {resultat.statut_section_2}")
    print("=" * 60)
    print()

    # Génération du rapport
    print("[3/3] Génération du rapport...")
    chemin_rapport = generateur.generer_rapport(resultat, sortie)
    print(f"  -> Rapport généré : {chemin_rapport}")
    print()
    print("Terminé.")


def main():
    """Point d'entrée principal."""
    parser = argparse.ArgumentParser(
        description="RGAA Section 2 Tester - Testeur de conformité accessibilité",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples:
  python main.py                          # Interface graphique
  python main.py --cli https://exemple.fr # Analyse une page
  python main.py --cli https://exemple.fr --max-pages 10  # Crawler
  python main.py --cli https://exemple.fr --output rapport.md

Pour plus d'informations, consultez le README.md
"""
    )

    parser.add_argument(
        '--cli',
        metavar='URL',
        help="Mode ligne de commande : analyse l'URL spécifiée"
    )

    parser.add_argument(
        '--max-pages',
        type=int,
        default=1,
        help="Nombre maximum de pages à crawler (défaut: 1)"
    )

    parser.add_argument(
        '--output', '-o',
        help="Chemin du fichier de rapport (défaut: auto-généré)"
    )

    parser.add_argument(
        '--version', '-v',
        action='version',
        version='RGAA Section 2 Tester v1.0.0'
    )

    args = parser.parse_args()

    if args.cli:
        mode_cli(args.cli, args.max_pages, args.output)
    else:
        mode_graphique()


if __name__ == "__main__":
    main()
