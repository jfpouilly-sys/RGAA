# -*- coding: utf-8 -*-
"""
Module de génération de rapports pour RGAA Section 2 Tester

Génère des rapports Markdown détaillés conformes au format ISIT-RGAA.
"""

import os
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from .analyzer import (
    AnalyseurRGAA,
    DonnesCadre,
    PrioriteCorrection,
    ResultatAnalyseGlobal,
    ResultatPage,
    ResultatTest
)
from .config import get_config
from .utils import (
    formater_date,
    formater_taux_conformite,
    generer_nom_fichier_rapport,
    obtenir_emoji_statut,
    tronquer_texte
)


class GenerateurRapport:
    """
    Générateur de rapports Markdown pour l'analyse RGAA Section 2.

    Produit des rapports détaillés conformes au format ISIT-RGAA.
    """

    def __init__(self, config=None):
        """
        Initialise le générateur de rapports.

        Args:
            config: Instance de configuration (optionnel).
        """
        self.config = config or get_config()
        self._dossier_sortie = self.config.get("rapport.dossier_sortie", "reports")
        self._inclure_code = self.config.get("rapport.inclure_code_html", True)
        self._analyseur = AnalyseurRGAA(config)

    def generer_rapport(self, resultat: ResultatAnalyseGlobal, chemin_sortie: Optional[str] = None) -> str:
        """
        Génère un rapport Markdown complet.

        Args:
            resultat: Résultat de l'analyse globale.
            chemin_sortie: Chemin du fichier de sortie (optionnel).

        Returns:
            Chemin du fichier de rapport généré.
        """
        # Calculer les statistiques si nécessaire
        resultat.calculer_statistiques()

        # Générer le contenu du rapport
        contenu = self._generer_contenu(resultat)

        # Déterminer le chemin de sortie
        if chemin_sortie is None:
            nom_fichier = generer_nom_fichier_rapport(resultat.url_depart)
            dossier = Path(self._dossier_sortie)
            dossier.mkdir(parents=True, exist_ok=True)
            chemin_sortie = str(dossier / nom_fichier)

        # Écrire le fichier
        with open(chemin_sortie, 'w', encoding='utf-8') as f:
            f.write(contenu)

        return chemin_sortie

    def _generer_contenu(self, resultat: ResultatAnalyseGlobal) -> str:
        """
        Génère le contenu Markdown du rapport.

        Args:
            resultat: Résultat de l'analyse globale.

        Returns:
            Contenu Markdown du rapport.
        """
        sections = [
            self._generer_en_tete(resultat),
            self._generer_resume_executif(resultat),
            self._generer_synthese_conformite(resultat),
            self._generer_detail_critere_2_1(resultat),
            self._generer_detail_critere_2_2(resultat),
            self._generer_detail_pages(resultat),
            self._generer_recommandations(resultat),
            self._generer_annexes(resultat),
            self._generer_pied_page(resultat)
        ]

        return '\n\n'.join(sections)

    def _generer_en_tete(self, resultat: ResultatAnalyseGlobal) -> str:
        """Génère l'en-tête du rapport."""
        date = formater_date(format_str="%d/%m/%Y à %H:%M")

        return f"""# Rapport d'Audit RGAA 4.1.2 - Section 2 : Cadres (Frames)

---

**Site analysé** : {resultat.url_depart}
**Date de l'audit** : {date}
**Référentiel** : RGAA 4.1.2 (Référentiel Général d'Amélioration de l'Accessibilité)
**Section évaluée** : Thématique 2 - Cadres (Frames)
**Outil** : RGAA Section 2 Tester v1.0

---"""

    def _generer_resume_executif(self, resultat: ResultatAnalyseGlobal) -> str:
        """Génère le résumé exécutif."""
        emoji_statut = obtenir_emoji_statut(
            "Conforme" if resultat.total_non_conformes_2_1 == 0 else "Non conforme"
        )

        taux = formater_taux_conformite(resultat.taux_conformite_2_1)

        return f"""## Résumé Exécutif

### Statut Global de la Section 2

{emoji_statut} **{resultat.statut_section_2}**

### Chiffres Clés

| Métrique | Valeur |
|----------|--------|
| Pages analysées | {resultat.total_pages} |
| Cadres détectés | {resultat.total_cadres} |
| Cadres testés | {resultat.total_cadres_testes} |
| Cadres exemptés (cachés) | {resultat.total_exemptes} |
| Taux de conformité (Critère 2.1) | {taux} |

### Résumé des Critères

| Critère | Description | Statut |
|---------|-------------|--------|
| 2.1 | Chaque cadre a-t-il un titre de cadre ? | {obtenir_emoji_statut("Conforme" if resultat.total_non_conformes_2_1 == 0 else "Non conforme")} {resultat.total_conformes_2_1}/{resultat.total_cadres_testes} conformes |
| 2.2 | Pour chaque cadre ayant un titre, ce titre est-il pertinent ? | {obtenir_emoji_statut("À vérifier")} {resultat.total_a_verifier_2_2} à vérifier manuellement |"""

    def _generer_synthese_conformite(self, resultat: ResultatAnalyseGlobal) -> str:
        """Génère la synthèse de conformité."""
        return f"""## Synthèse de Conformité

### Critère 2.1 : Présence des titres de cadres

**Niveau WCAG** : A (Obligatoire)
**Conformité automatique possible** : Oui

| Résultat | Nombre | Pourcentage |
|----------|--------|-------------|
| ✅ Conformes | {resultat.total_conformes_2_1} | {formater_taux_conformite(resultat.taux_conformite_2_1)} |
| ❌ Non conformes | {resultat.total_non_conformes_2_1} | {formater_taux_conformite(100 - resultat.taux_conformite_2_1) if resultat.total_cadres_testes > 0 else "0%"} |
| ⚪ Non applicable | {resultat.total_exemptes} | - |

### Critère 2.2 : Pertinence des titres de cadres

**Niveau WCAG** : A (Obligatoire)
**Conformité automatique possible** : Non (vérification manuelle requise)

| Indicateur | Valeur |
|------------|--------|
| Cadres avec titre à vérifier | {resultat.total_a_verifier_2_2} |
| Alertes de titres suspects | {resultat.total_alertes_2_2} |

> **Note** : Le critère 2.2 nécessite une vérification manuelle. L'outil signale les titres potentiellement problématiques mais seul un audit humain peut confirmer la pertinence."""

    def _generer_detail_critere_2_1(self, resultat: ResultatAnalyseGlobal) -> str:
        """Génère le détail du critère 2.1."""
        contenu = """## Détail du Critère 2.1

### Description

> Chaque cadre a-t-il un titre de cadre ?

Ce critère vérifie que tous les éléments `<iframe>` et `<frame>` visibles disposent d'un attribut `title` non vide.

### Cadres Non Conformes (sans titre)

"""
        # Collecter tous les cadres non conformes
        cadres_nc = []
        for page in resultat.pages:
            for cadre in page.cadres:
                if cadre.resultat_test_2_1 == ResultatTest.NON_CONFORME:
                    cadres_nc.append((page.url, cadre))

        if not cadres_nc:
            contenu += "> ✅ Aucun cadre non conforme détecté.\n"
        else:
            contenu += f"**{len(cadres_nc)} cadre(s) sans titre détecté(s) :**\n\n"

            for i, (url_page, cadre) in enumerate(cadres_nc, 1):
                contenu += f"""#### Problème #{i}

**Page** : `{url_page}`
**Élément** : `<{cadre.type_element}>`
**Source** : `{tronquer_texte(cadre.src or 'Non spécifiée', 80)}`
**ID** : `{cadre.id_element or 'Non défini'}`
**Priorité** : {cadre.priorite.value if cadre.priorite else 'Non définie'}

"""
                if self._inclure_code and cadre.code_html:
                    contenu += f"""**Code HTML** :
```html
{cadre.code_html}
```

"""
                contenu += f"""**Recommandation** : {self._analyseur.generer_recommandation(cadre)}

---

"""

        return contenu

    def _generer_detail_critere_2_2(self, resultat: ResultatAnalyseGlobal) -> str:
        """Génère le détail du critère 2.2."""
        contenu = """## Détail du Critère 2.2

### Description

> Pour chaque cadre ayant un titre de cadre, ce titre de cadre est-il pertinent ?

Ce critère vérifie que les titres des cadres sont suffisamment descriptifs pour permettre aux utilisateurs de technologies d'assistance de comprendre leur contenu.

### Cadres à Vérifier (avec alertes)

"""
        # Collecter tous les cadres avec alertes
        cadres_alertes = []
        for page in resultat.pages:
            for cadre in page.cadres:
                if cadre.alertes_2_2:
                    cadres_alertes.append((page.url, cadre))

        if not cadres_alertes:
            contenu += "> ✅ Aucune alerte sur les titres de cadres.\n"
        else:
            contenu += f"**{len(cadres_alertes)} cadre(s) avec alerte(s) :**\n\n"

            for i, (url_page, cadre) in enumerate(cadres_alertes, 1):
                alertes_str = '\n'.join([f"  - ⚠️ {a}" for a in cadre.alertes_2_2])
                contenu += f"""#### Alerte #{i}

**Page** : `{url_page}`
**Élément** : `<{cadre.type_element}>`
**Titre actuel** : `{cadre.title}`
**Source** : `{tronquer_texte(cadre.src or 'Non spécifiée', 80)}`

**Alertes détectées** :
{alertes_str}

**Recommandation** : {self._analyseur.generer_recommandation(cadre)}

---

"""

        # Lister tous les cadres à vérifier manuellement
        contenu += """### Tous les Cadres à Vérifier Manuellement

| Page | Type | Titre | Source |
|------|------|-------|--------|
"""
        for page in resultat.pages:
            for cadre in page.cadres:
                if cadre.necessite_verification_2_2:
                    titre_display = tronquer_texte(cadre.title or "", 40)
                    src_display = tronquer_texte(cadre.src or "", 40)
                    contenu += f"| {tronquer_texte(page.url, 30)} | `{cadre.type_element}` | {titre_display} | {src_display} |\n"

        return contenu

    def _generer_detail_pages(self, resultat: ResultatAnalyseGlobal) -> str:
        """Génère le détail par page."""
        contenu = """## Détail par Page

"""
        for i, page in enumerate(resultat.pages, 1):
            emoji_page = obtenir_emoji_statut(page.statut_2_1.value)

            contenu += f"""### Page {i} : {tronquer_texte(page.titre_page, 50)}

**URL** : `{page.url}`
**Statut Critère 2.1** : {emoji_page} {page.statut_2_1.value}
**Cadres testés** : {page.cadres_testes}
**Conformes** : {page.conformes_2_1}
**Non conformes** : {page.non_conformes_2_1}
**À vérifier (2.2)** : {page.a_verifier_2_2}

"""
            if page.cadres:
                contenu += "| Type | ID | Titre | Statut 2.1 | Alertes 2.2 |\n"
                contenu += "|------|-----|-------|------------|-------------|\n"

                for cadre in page.cadres:
                    if cadre.est_cache:
                        continue
                    statut_emoji = obtenir_emoji_statut(cadre.resultat_test_2_1.value)
                    id_display = cadre.id_element or "-"
                    titre_display = tronquer_texte(cadre.title or "(vide)", 30)
                    alertes = len(cadre.alertes_2_2)
                    alertes_display = f"⚠️ {alertes}" if alertes > 0 else "✅"

                    contenu += f"| `{cadre.type_element}` | {id_display} | {titre_display} | {statut_emoji} | {alertes_display} |\n"

            contenu += "\n---\n\n"

        return contenu

    def _generer_recommandations(self, resultat: ResultatAnalyseGlobal) -> str:
        """Génère la section des recommandations."""
        contenu = """## Recommandations de Correction

### Priorité 1 - Critique (Blocage utilisateur)

"""
        # Collecter les problèmes P1
        p1 = []
        for page in resultat.pages:
            for cadre in page.cadres:
                if cadre.priorite == PrioriteCorrection.P1_CRITIQUE:
                    p1.append((page.url, cadre))

        if not p1:
            contenu += "> ✅ Aucun problème critique détecté.\n\n"
        else:
            for url, cadre in p1:
                contenu += f"""- **Page** : `{tronquer_texte(url, 50)}`
  - Élément `<{cadre.type_element}>` sans titre
  - Action : Ajouter un attribut `title` descriptif

"""

        contenu += """### Priorité 2 - Important (Expérience dégradée)

"""
        # Collecter les problèmes P2
        p2 = []
        for page in resultat.pages:
            for cadre in page.cadres:
                if cadre.priorite == PrioriteCorrection.P2_IMPORTANT:
                    p2.append((page.url, cadre))

        if not p2:
            contenu += "> ✅ Aucun problème important détecté.\n\n"
        else:
            for url, cadre in p2:
                contenu += f"""- **Page** : `{tronquer_texte(url, 50)}`
  - Élément `<{cadre.type_element}>` avec titre générique : `{cadre.title}`
  - Action : Remplacer par un titre descriptif du contenu

"""

        contenu += """### Priorité 3 - Amélioration (Optimisation)

"""
        p3 = []
        for page in resultat.pages:
            for cadre in page.cadres:
                if cadre.priorite == PrioriteCorrection.P3_AMELIORATION:
                    p3.append((page.url, cadre))

        if not p3:
            contenu += "> ✅ Aucune amélioration suggérée.\n"
        else:
            contenu += "Vérifier manuellement la pertinence des titres suivants :\n\n"
            for url, cadre in p3[:10]:  # Limiter à 10
                contenu += f"- `{cadre.title}` sur `{tronquer_texte(url, 40)}`\n"

            if len(p3) > 10:
                contenu += f"\n... et {len(p3) - 10} autres à vérifier.\n"

        return contenu

    def _generer_annexes(self, resultat: ResultatAnalyseGlobal) -> str:
        """Génère les annexes du rapport."""
        return f"""## Annexes

### A. Méthodologie de Test

#### Critère 2.1 - Tests automatisés

1. Détection de tous les éléments `<iframe>` et `<frame>` dans le DOM
2. Exclusion des cadres cachés :
   - `aria-hidden="true"`
   - `display: none` ou `visibility: hidden`
   - Attribut `hidden`
   - Dimensions nulles (`width="0" height="0"`)
3. Vérification de la présence d'un attribut `title` non vide

#### Critère 2.2 - Signalement automatique

1. Détection des titres génériques (frame, iframe, widget, etc.)
2. Signalement des titres très courts (< 3 caractères)
3. Signalement des titres numériques uniquement
4. Tous les titres sont marqués pour vérification manuelle

### B. Références

- **RGAA 4.1.2** : [Critères Section 2](https://accessibilite.numerique.gouv.fr/methode/criteres-et-tests/#topic2)
- **WCAG 2.1** : Critère 4.1.2 Nom, rôle et valeur (Niveau A)
- **Technique H64** : Utilisation de l'attribut title des éléments frame et iframe

### C. Glossaire

| Terme | Définition |
|-------|------------|
| Cadre | Élément HTML (`<frame>` ou `<iframe>`) permettant d'inclure un document externe |
| Titre de cadre | Texte fourni via l'attribut `title` identifiant le contenu du cadre |
| Conforme | Le cadre respecte le critère RGAA testé |
| Non conforme | Le cadre ne respecte pas le critère RGAA testé |
| Non applicable | Le critère ne s'applique pas (aucun cadre ou cadre caché) |"""

    def _generer_pied_page(self, resultat: ResultatAnalyseGlobal) -> str:
        """Génère le pied de page du rapport."""
        date = formater_date(format_str="%d/%m/%Y %H:%M:%S")

        return f"""---

## Informations sur le Rapport

**Généré le** : {date}
**Outil** : RGAA Section 2 Tester v1.0
**Référentiel** : RGAA 4.1.2
**URL de départ** : {resultat.url_depart}
**Pages analysées** : {resultat.total_pages}
**Cadres analysés** : {resultat.total_cadres}

---

*Ce rapport a été généré automatiquement. Pour toute question sur la méthodologie, consultez la documentation RGAA officielle.*"""
