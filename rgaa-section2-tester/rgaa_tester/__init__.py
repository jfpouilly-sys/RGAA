# -*- coding: utf-8 -*-
"""
RGAA Audit Complet - Package principal

Application de test de conformité RGAA 4.1.2 - 106 critères complets
Génère des rapports Markdown pour l'analyse d'accessibilité.
Supporte également l'analyse via fichiers ODS (grilleAudit.ods).

Version: 2.0.0
"""

__version__ = "2.0.0"
__author__ = "RGAA Tester"

# Export main modules
from .analyzer import AnalyseurRGAA
from .crawler import Crawler
from .report_generator import GenerateurRapport
from .config import get_config

# Export full RGAA tester (106 criteria)
from .full_rgaa_tester import FullRGAATester, WebPageAnalyzer, TestResult, run_full_rgaa_test

# Export ODS modules (optional feature)
try:
    from .ods_models import Status, Derogation, AuditCriterion, PageAudit, AuditFile
    from .ods_handler import RGAAAuditODSHandler
    from .ods_analyzer import ODSAuditAnalyzer
    from .ods_gui import ODSAuditFrame
    __all__ = [
        'AnalyseurRGAA',
        'Crawler',
        'GenerateurRapport',
        'get_config',
        'FullRGAATester',
        'WebPageAnalyzer',
        'TestResult',
        'run_full_rgaa_test',
        'Status',
        'Derogation',
        'AuditCriterion',
        'PageAudit',
        'AuditFile',
        'RGAAAuditODSHandler',
        'ODSAuditAnalyzer',
        'ODSAuditFrame'
    ]
except ImportError:
    # ODS modules not available (odfpy not installed)
    __all__ = [
        'AnalyseurRGAA',
        'Crawler',
        'GenerateurRapport',
        'get_config',
        'FullRGAATester',
        'WebPageAnalyzer',
        'TestResult',
        'run_full_rgaa_test'
    ]
