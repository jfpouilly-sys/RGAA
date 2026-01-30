# -*- coding: utf-8 -*-
"""
Module d'analyse RGAA Section 2 - Cadres (Frames)

Implémente les tests de conformité pour les critères 2.1 et 2.2 du RGAA 4.1.2.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional
from bs4 import BeautifulSoup, Tag

from .config import get_config
from .utils import (
    est_element_cache,
    nettoyer_texte,
    obtenir_emoji_statut
)


class ResultatTest(Enum):
    """Résultats possibles pour un test RGAA."""
    CONFORME = "Conforme"
    NON_CONFORME = "Non conforme"
    NON_APPLICABLE = "Non applicable"
    A_VERIFIER = "À vérifier"


class PrioriteCorrection(Enum):
    """Priorité de correction des problèmes détectés."""
    P1_CRITIQUE = "P1 - Critique"
    P2_IMPORTANT = "P2 - Important"
    P3_AMELIORATION = "P3 - Amélioration"


@dataclass
class DonnesCadre:
    """Structure de données pour un cadre analysé."""
    # Informations de base
    type_element: str  # 'iframe' ou 'frame'
    id_element: Optional[str] = None
    classe: Optional[str] = None
    src: Optional[str] = None

    # Attributs de titre
    title: Optional[str] = None
    longueur_titre: int = 0

    # Attributs ARIA (pour référence)
    aria_label: Optional[str] = None
    aria_labelledby: Optional[str] = None

    # Statut de visibilité
    est_cache: bool = False
    raison_cache: str = ""
    aria_hidden: Optional[str] = None

    # Résultats des tests
    resultat_test_2_1: ResultatTest = ResultatTest.NON_APPLICABLE
    resultat_test_2_2: ResultatTest = ResultatTest.NON_APPLICABLE
    necessite_verification_2_2: bool = False
    alertes_2_2: List[str] = field(default_factory=list)

    # Priorité de correction
    priorite: Optional[PrioriteCorrection] = None

    # Contexte
    url_page: str = ""
    code_html: str = ""
    numero_ligne: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convertit les données en dictionnaire."""
        return {
            'type_element': self.type_element,
            'id': self.id_element,
            'class': self.classe,
            'src': self.src,
            'title': self.title,
            'longueur_titre': self.longueur_titre,
            'aria_label': self.aria_label,
            'aria_labelledby': self.aria_labelledby,
            'est_cache': self.est_cache,
            'raison_cache': self.raison_cache,
            'resultat_2_1': self.resultat_test_2_1.value,
            'resultat_2_2': self.resultat_test_2_2.value,
            'necessite_verification': self.necessite_verification_2_2,
            'alertes': self.alertes_2_2,
            'priorite': self.priorite.value if self.priorite else None,
            'url_page': self.url_page,
            'code_html': self.code_html
        }


@dataclass
class ResultatPage:
    """Résultat d'analyse pour une page."""
    url: str
    titre_page: str = ""
    cadres: List[DonnesCadre] = field(default_factory=list)

    # Compteurs
    total_cadres: int = 0
    cadres_exemptes: int = 0
    cadres_testes: int = 0

    # Résultats Critère 2.1
    conformes_2_1: int = 0
    non_conformes_2_1: int = 0

    # Résultats Critère 2.2
    a_verifier_2_2: int = 0
    alertes_2_2: int = 0

    # Statut global
    statut_2_1: ResultatTest = ResultatTest.NON_APPLICABLE
    statut_2_2: ResultatTest = ResultatTest.NON_APPLICABLE

    def calculer_statistiques(self) -> None:
        """Calcule les statistiques basées sur les cadres analysés."""
        self.total_cadres = len(self.cadres)
        self.cadres_exemptes = sum(1 for c in self.cadres if c.est_cache)
        self.cadres_testes = self.total_cadres - self.cadres_exemptes

        cadres_testables = [c for c in self.cadres if not c.est_cache]

        self.conformes_2_1 = sum(
            1 for c in cadres_testables
            if c.resultat_test_2_1 == ResultatTest.CONFORME
        )
        self.non_conformes_2_1 = sum(
            1 for c in cadres_testables
            if c.resultat_test_2_1 == ResultatTest.NON_CONFORME
        )
        self.a_verifier_2_2 = sum(
            1 for c in cadres_testables
            if c.necessite_verification_2_2
        )
        self.alertes_2_2 = sum(
            len(c.alertes_2_2) for c in cadres_testables
        )

        # Déterminer le statut global du critère 2.1
        if self.cadres_testes == 0:
            self.statut_2_1 = ResultatTest.NON_APPLICABLE
        elif self.non_conformes_2_1 == 0:
            self.statut_2_1 = ResultatTest.CONFORME
        else:
            self.statut_2_1 = ResultatTest.NON_CONFORME

        # Déterminer le statut global du critère 2.2
        if self.a_verifier_2_2 == 0:
            self.statut_2_2 = ResultatTest.NON_APPLICABLE
        else:
            self.statut_2_2 = ResultatTest.A_VERIFIER


class AnalyseurRGAA:
    """Analyseur de conformité RGAA Section 2 (Cadres)."""

    def __init__(self, config=None):
        """
        Initialise l'analyseur.

        Args:
            config: Instance de configuration (optionnel).
        """
        self.config = config or get_config()
        self._titres_generiques = self.config.titres_generiques
        self._longueur_min_titre = self.config.get("analyse.longueur_titre_minimum", 3)
        self._detecter_generiques = self.config.get("analyse.detecter_titres_generiques", True)

    def analyser_page(self, html: str, url: str) -> ResultatPage:
        """
        Analyse une page HTML pour les critères RGAA Section 2.

        Args:
            html: Contenu HTML de la page.
            url: URL de la page.

        Returns:
            Résultat d'analyse de la page.
        """
        soup = BeautifulSoup(html, 'lxml')
        resultat = ResultatPage(url=url)

        # Extraire le titre de la page
        titre_tag = soup.find('title')
        resultat.titre_page = titre_tag.get_text().strip() if titre_tag else "Sans titre"

        # Trouver tous les cadres (iframe et frame)
        cadres_html = soup.find_all(['iframe', 'frame'])

        for cadre in cadres_html:
            donnees = self._analyser_cadre(cadre, url)
            resultat.cadres.append(donnees)

        # Calculer les statistiques
        resultat.calculer_statistiques()

        return resultat

    def _analyser_cadre(self, element: Tag, url_page: str) -> DonnesCadre:
        """
        Analyse un élément cadre individuel.

        Args:
            element: Élément BeautifulSoup (iframe ou frame).
            url_page: URL de la page contenant le cadre.

        Returns:
            Données d'analyse du cadre.
        """
        donnees = DonnesCadre(
            type_element=element.name,
            url_page=url_page
        )

        # Extraire les attributs de base
        donnees.id_element = element.get('id')
        donnees.classe = element.get('class')
        if isinstance(donnees.classe, list):
            donnees.classe = ' '.join(donnees.classe)
        donnees.src = element.get('src')

        # Extraire les attributs de titre
        donnees.title = element.get('title')
        if donnees.title:
            donnees.title = nettoyer_texte(donnees.title)
            donnees.longueur_titre = len(donnees.title)

        # Extraire les attributs ARIA (pour information)
        donnees.aria_label = element.get('aria-label')
        donnees.aria_labelledby = element.get('aria-labelledby')
        donnees.aria_hidden = element.get('aria-hidden')

        # Vérifier si le cadre est caché
        est_cache, raison = est_element_cache(
            style=element.get('style'),
            aria_hidden=donnees.aria_hidden,
            hidden=element.has_attr('hidden'),
            width=element.get('width'),
            height=element.get('height')
        )
        donnees.est_cache = est_cache
        donnees.raison_cache = raison

        # Générer le code HTML pour le rapport
        donnees.code_html = str(element)
        # Tronquer si trop long
        if len(donnees.code_html) > 500:
            donnees.code_html = donnees.code_html[:500] + "..."

        # Exécuter les tests si le cadre n'est pas caché
        if not donnees.est_cache:
            self._executer_test_2_1(donnees)
            self._executer_test_2_2(donnees)
            self._determiner_priorite(donnees)

        return donnees

    def _executer_test_2_1(self, donnees: DonnesCadre) -> None:
        """
        Exécute le test 2.1 : présence d'un titre de cadre.

        Critère 2.1: Chaque cadre a-t-il un titre de cadre ?
        - Test 2.1.1: Chaque élément <frame> a-t-il un attribut title ?
        - Test 2.1.2: Chaque élément <iframe> a-t-il un attribut title ?
        """
        if donnees.title and donnees.longueur_titre > 0:
            donnees.resultat_test_2_1 = ResultatTest.CONFORME
        else:
            donnees.resultat_test_2_1 = ResultatTest.NON_CONFORME

    def _executer_test_2_2(self, donnees: DonnesCadre) -> None:
        """
        Exécute le test 2.2 : pertinence du titre de cadre.

        Critère 2.2: Pour chaque cadre ayant un titre de cadre, ce titre est-il pertinent ?
        - Test 2.2.1: Pour chaque élément <frame> ayant un attribut title, ce titre est-il pertinent ?
        - Test 2.2.2: Pour chaque élément <iframe> ayant un attribut title, ce titre est-il pertinent ?

        Note: Ce test génère des signalements pour vérification manuelle.
        """
        # Si pas de titre, le test 2.2 n'est pas applicable
        if not donnees.title:
            donnees.resultat_test_2_2 = ResultatTest.NON_APPLICABLE
            return

        # Tout titre existant nécessite une vérification manuelle
        donnees.necessite_verification_2_2 = True
        donnees.resultat_test_2_2 = ResultatTest.A_VERIFIER
        alertes = []

        titre_lower = donnees.title.lower()

        # Vérifier les titres génériques
        if self._detecter_generiques:
            for generique in self._titres_generiques:
                if titre_lower == generique.lower():
                    alertes.append(f"Titre générique détecté : \"{donnees.title}\"")
                    break

        # Vérifier la longueur du titre
        if donnees.longueur_titre < self._longueur_min_titre:
            alertes.append(f"Titre très court ({donnees.longueur_titre} caractères)")

        # Vérifier si le titre contient uniquement des chiffres
        if donnees.title.isdigit():
            alertes.append("Titre contient uniquement des chiffres")

        # Vérifier les titres techniques (Frame-1, iframe_2, etc.)
        import re
        if re.match(r'^(frame|iframe|cadre)[_-]?\d*$', titre_lower):
            alertes.append("Titre technique non descriptif")

        donnees.alertes_2_2 = alertes

    def _determiner_priorite(self, donnees: DonnesCadre) -> None:
        """
        Détermine la priorité de correction pour un cadre problématique.

        P1 - Critique: Cadres visibles sans aucun titre ou titre vide
        P2 - Important: Titres génériques ou très courts
        P3 - Amélioration: Titres corrects mais pouvant être améliorés
        """
        if donnees.resultat_test_2_1 == ResultatTest.NON_CONFORME:
            donnees.priorite = PrioriteCorrection.P1_CRITIQUE
        elif donnees.alertes_2_2:
            donnees.priorite = PrioriteCorrection.P2_IMPORTANT
        elif donnees.necessite_verification_2_2:
            donnees.priorite = PrioriteCorrection.P3_AMELIORATION

    def generer_recommandation(self, donnees: DonnesCadre) -> str:
        """
        Génère une recommandation de correction pour un cadre.

        Args:
            donnees: Données du cadre à corriger.

        Returns:
            Texte de recommandation.
        """
        if donnees.resultat_test_2_1 == ResultatTest.NON_CONFORME:
            return (
                f"Ajouter un attribut `title` descriptif à cet élément `<{donnees.type_element}>`. "
                f"Le titre doit décrire le contenu ou la fonction du cadre. "
                f"Exemple : `<{donnees.type_element} src=\"...\" title=\"Description du contenu\">`"
            )

        if donnees.alertes_2_2:
            if any("générique" in a.lower() for a in donnees.alertes_2_2):
                return (
                    f"Remplacer le titre générique \"{donnees.title}\" par une description "
                    f"précise du contenu ou de la fonction du cadre. "
                    f"Un titre pertinent permet aux utilisateurs de technologies d'assistance "
                    f"de comprendre ce que contient le cadre."
                )
            if any("court" in a.lower() for a in donnees.alertes_2_2):
                return (
                    f"Enrichir le titre \"{donnees.title}\" avec plus de détails sur le contenu. "
                    f"Un titre de 3 caractères minimum est recommandé, mais il doit surtout "
                    f"être suffisamment descriptif."
                )

        return (
            "Vérifier manuellement que le titre est suffisamment descriptif pour permettre "
            "aux utilisateurs de technologies d'assistance de comprendre le contenu du cadre."
        )


@dataclass
class ResultatAnalyseGlobal:
    """Résultat global d'analyse pour un site complet."""
    url_depart: str
    pages: List[ResultatPage] = field(default_factory=list)
    date_analyse: str = ""

    # Statistiques globales
    total_pages: int = 0
    total_cadres: int = 0
    total_cadres_testes: int = 0
    total_exemptes: int = 0

    # Conformité Critère 2.1
    total_conformes_2_1: int = 0
    total_non_conformes_2_1: int = 0
    taux_conformite_2_1: float = 0.0

    # Critère 2.2
    total_a_verifier_2_2: int = 0
    total_alertes_2_2: int = 0

    # Statut global
    statut_section_2: str = ""

    def calculer_statistiques(self) -> None:
        """Calcule les statistiques globales."""
        self.total_pages = len(self.pages)

        for page in self.pages:
            self.total_cadres += page.total_cadres
            self.total_cadres_testes += page.cadres_testes
            self.total_exemptes += page.cadres_exemptes
            self.total_conformes_2_1 += page.conformes_2_1
            self.total_non_conformes_2_1 += page.non_conformes_2_1
            self.total_a_verifier_2_2 += page.a_verifier_2_2
            self.total_alertes_2_2 += page.alertes_2_2

        # Calculer le taux de conformité
        if self.total_cadres_testes > 0:
            self.taux_conformite_2_1 = round(
                (self.total_conformes_2_1 / self.total_cadres_testes) * 100, 2
            )
        else:
            self.taux_conformite_2_1 = 100.0

        # Déterminer le statut global de la Section 2
        if self.total_cadres_testes == 0:
            self.statut_section_2 = "Non applicable"
        elif self.total_non_conformes_2_1 == 0:
            self.statut_section_2 = "Conforme (vérification manuelle critère 2.2 requise)"
        else:
            self.statut_section_2 = "Non conforme"
