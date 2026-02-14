"""
Module d'analyse automatisee du critere RGAA 10.7 — Visibilite du focus.

Ce module teste si les elements focusables d'une page web ont un indicateur
de focus visible, conformement au critere RGAA 10.7 (WCAG 2.4.7 Focus Visible).

Modules :
    - constants : Constantes, selecteurs et classifications
    - focus_detector : Detection des elements focusables via Playwright
    - css_analyzer : Analyse des styles CSS appliques au focus
    - focus_tester : Orchestrateur principal du test
    - report_generator : Generation du rapport Markdown
    - ods_updater : Mise a jour de la grille ODS d'audit
"""

__version__ = "1.0.0"
