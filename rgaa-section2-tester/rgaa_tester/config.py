# -*- coding: utf-8 -*-
"""
Module de configuration pour RGAA Section 2 Tester

Gère le chargement, la sauvegarde et l'accès aux paramètres de configuration.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional


class Config:
    """Gestionnaire de configuration de l'application."""

    # Configuration par défaut
    DEFAULT_CONFIG: Dict[str, Any] = {
        # Paramètres généraux
        "version": "1.0.0",
        "langue": "fr",

        # Paramètres de crawl
        "crawler": {
            "max_pages": 50,
            "timeout": 30,
            "user_agent": "RGAA-Tester/1.0 (Accessibility Checker)",
            "respecter_robots_txt": True,
            "delai_entre_requetes": 1.0,  # Secondes
            "suivre_liens_externes": False
        },

        # Paramètres d'analyse
        "analyse": {
            "inclure_cadres_caches": False,
            "longueur_titre_minimum": 3,
            "detecter_titres_generiques": True
        },

        # Titres génériques à détecter (critère 2.2)
        "titres_generiques": [
            "frame",
            "iframe",
            "cadre",
            "content",
            "contenu",
            "widget",
            "embed",
            "externe",
            "external"
        ],

        # Paramètres de rapport
        "rapport": {
            "dossier_sortie": "reports",
            "format_date": "%Y-%m-%d_%H-%M-%S",
            "inclure_code_html": True,
            "inclure_captures": False
        },

        # Interface graphique
        "gui": {
            "theme": "default",
            "largeur_fenetre": 900,
            "hauteur_fenetre": 700
        }
    }

    def __init__(self, chemin_config: Optional[str] = None):
        """
        Initialise le gestionnaire de configuration.

        Args:
            chemin_config: Chemin vers le fichier de configuration JSON.
                          Si None, utilise config.json dans le répertoire courant.
        """
        self._config: Dict[str, Any] = self.DEFAULT_CONFIG.copy()

        if chemin_config is None:
            # Chercher dans le répertoire de l'application
            app_dir = Path(__file__).parent.parent
            self._chemin_config = app_dir / "config.json"
        else:
            self._chemin_config = Path(chemin_config)

        self._charger()

    def _charger(self) -> None:
        """Charge la configuration depuis le fichier JSON."""
        if self._chemin_config.exists():
            try:
                with open(self._chemin_config, 'r', encoding='utf-8') as f:
                    config_fichier = json.load(f)
                    self._fusionner_config(config_fichier)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Avertissement: Impossible de charger la configuration: {e}")
                print("Utilisation de la configuration par défaut.")

    def _fusionner_config(self, config_nouvelle: Dict[str, Any]) -> None:
        """
        Fusionne une nouvelle configuration avec la configuration existante.

        Args:
            config_nouvelle: Dictionnaire de configuration à fusionner.
        """
        def fusionner_recursive(base: Dict, nouvelle: Dict) -> Dict:
            """Fusion récursive de deux dictionnaires."""
            resultat = base.copy()
            for cle, valeur in nouvelle.items():
                if cle in resultat and isinstance(resultat[cle], dict) and isinstance(valeur, dict):
                    resultat[cle] = fusionner_recursive(resultat[cle], valeur)
                else:
                    resultat[cle] = valeur
            return resultat

        self._config = fusionner_recursive(self._config, config_nouvelle)

    def sauvegarder(self) -> bool:
        """
        Sauvegarde la configuration dans le fichier JSON.

        Returns:
            True si la sauvegarde a réussi, False sinon.
        """
        try:
            # Créer le répertoire parent si nécessaire
            self._chemin_config.parent.mkdir(parents=True, exist_ok=True)

            with open(self._chemin_config, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=4, ensure_ascii=False)
            return True
        except IOError as e:
            print(f"Erreur lors de la sauvegarde de la configuration: {e}")
            return False

    def get(self, cle: str, defaut: Any = None) -> Any:
        """
        Récupère une valeur de configuration.

        Supporte la notation pointée pour les clés imbriquées:
        config.get("crawler.max_pages") retourne config["crawler"]["max_pages"]

        Args:
            cle: Clé de configuration (peut être imbriquée avec des points).
            defaut: Valeur par défaut si la clé n'existe pas.

        Returns:
            La valeur de configuration ou la valeur par défaut.
        """
        parties = cle.split('.')
        valeur = self._config

        for partie in parties:
            if isinstance(valeur, dict) and partie in valeur:
                valeur = valeur[partie]
            else:
                return defaut

        return valeur

    def set(self, cle: str, valeur: Any) -> None:
        """
        Définit une valeur de configuration.

        Supporte la notation pointée pour les clés imbriquées.

        Args:
            cle: Clé de configuration (peut être imbriquée avec des points).
            valeur: Valeur à définir.
        """
        parties = cle.split('.')
        config = self._config

        for partie in parties[:-1]:
            if partie not in config or not isinstance(config[partie], dict):
                config[partie] = {}
            config = config[partie]

        config[parties[-1]] = valeur

    @property
    def titres_generiques(self) -> list:
        """Retourne la liste des titres génériques à détecter."""
        return self.get("titres_generiques", [])

    @property
    def crawler_config(self) -> Dict[str, Any]:
        """Retourne la configuration du crawler."""
        return self.get("crawler", {})

    @property
    def analyse_config(self) -> Dict[str, Any]:
        """Retourne la configuration d'analyse."""
        return self.get("analyse", {})

    @property
    def rapport_config(self) -> Dict[str, Any]:
        """Retourne la configuration des rapports."""
        return self.get("rapport", {})

    def to_dict(self) -> Dict[str, Any]:
        """Retourne la configuration complète sous forme de dictionnaire."""
        return self._config.copy()


# Instance globale de configuration
_config_instance: Optional[Config] = None


def get_config(chemin: Optional[str] = None) -> Config:
    """
    Retourne l'instance de configuration globale.

    Args:
        chemin: Chemin vers le fichier de configuration (optionnel).

    Returns:
        Instance de Config.
    """
    global _config_instance

    if _config_instance is None:
        _config_instance = Config(chemin)

    return _config_instance
