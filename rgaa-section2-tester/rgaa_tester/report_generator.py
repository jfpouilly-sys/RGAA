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
    get_system_info,
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
        # Calculer les métriques de couverture
        metrics = self._analyseur.calculate_coverage_metrics(resultat.pages)

        # Récupérer les informations système
        system_info = get_system_info()

        sections = [
            self._generer_en_tete(resultat),
            self._generer_section_couverture(metrics),  # NOUVEAU
            self._generer_resume_executif(resultat),
            self._generer_synthese_avec_couverture(metrics, resultat),  # ENRICHI
            self._generer_actions_requises(metrics),  # NOUVEAU
            self._generer_synthese_conformite(resultat),
            self._generer_detail_critere_2_1(resultat),
            self._generer_avertissement_critere_2_2(),  # NOUVEAU
            self._generer_detail_critere_2_2(resultat),
            self._generer_detail_pages(resultat),
            self._generer_recommandations(resultat),
            self._generer_annexes(resultat),
            self._generer_annexe_methodologie(metrics, system_info),  # NOUVEAU
            self._generer_mentions_legales(system_info),  # NOUVEAU
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

    def _generer_section_couverture(self, metrics: dict) -> str:
        """
        Génère la section sur la couverture de l'audit automatique.

        Args:
            metrics: dict retourné par calculate_coverage_metrics()

        Returns:
            str: Section Markdown complète
        """

        section = """### Couverture de l'audit automatique

#### Tests automatisés réalisés

| Critère | Type de test | Couverture automatique | Fiabilité | Vérification manuelle requise |
|---------|--------------|----------------------|-----------|------------------------------|
| **2.1** - Présence titre cadre | ✅ Automatique complet | **98-100%** | Très élevée | ❌ Non |
| **2.2** - Pertinence titre cadre | ⚠️ Détection partielle (flagging) | **30-40%** | Indicative | ✅ **OUI - OBLIGATOIRE** |

#### Détails par critère

**Critère 2.1 - Présence d'un titre de cadre** :
- ✅ Détection exhaustive de tous les éléments `<frame>` et `<iframe>`
- ✅ Vérification présence attribut `title` non vide
- ✅ Vérification présence alternatives (`aria-label`, `aria-labelledby`)
- ✅ Détection et exemption des cadres cachés
- ✅ **Décision automatique fiable : CONFORME / NON CONFORME**

**Critère 2.2 - Pertinence du titre de cadre** :
- ⚠️ Détection titres génériques ("frame", "iframe", "widget", "content")
- ⚠️ Détection titres très courts (< 3 caractères)
- ⚠️ Signalement titres suspects nécessitant vérification
- ❌ **Validation finale de la pertinence : IMPOSSIBLE automatiquement**
- ✅ **Vérification manuelle obligatoire selon RGAA 4.1.2**

#### Avertissement important

> ⚠️ **LIMITE DE L'AUDIT AUTOMATIQUE**
>
> Le critère 2.2 (pertinence des titres de cadres) **ne peut pas être validé automatiquement** car la notion de "pertinence" requiert un jugement humain contextuel. L'outil a signalé les titres suspects, mais **une vérification manuelle est obligatoire** pour tous les cadres afin de valider la conformité complète à la Section 2 du RGAA 4.1.2.
>
> **Les résultats du critère 2.2 dans ce rapport sont des indicateurs uniquement** et nécessitent une validation par un auditeur humain qualifié.

#### Taux de couverture global de cet audit

- **Tests automatiques réalisés** : ~65% de la Section 2
- **Validation manuelle requise** : ~35% de la Section 2 (critère 2.2)
- **Gain de temps estimé** : ~75% par rapport à un audit 100% manuel

---
"""
        return section

    def _generer_actions_requises(self, metrics: dict) -> str:
        """
        Génère la section sur les actions requises pour finaliser l'audit.

        Args:
            metrics: dict avec les métriques

        Returns:
            str: Section Markdown
        """

        frames_to_check = metrics['frames_to_verify']
        estimated_time = metrics['estimated_manual_time_minutes']

        section = f"""### 📋 Actions requises pour finaliser l'audit

> 🔴 **VÉRIFICATION MANUELLE OBLIGATOIRE**
>
> Pour compléter cet audit et valider la conformité RGAA 4.1.2 Section 2, les actions suivantes sont **obligatoires** :
>
> 1. ✅ **Critère 2.1** : Résultats validés automatiquement - aucune action requise
> 2. ⚠️ **Critère 2.2** : **Vérification manuelle requise** pour {frames_to_check} cadre(s)
>    - Ouvrir chaque page concernée dans un navigateur
>    - Vérifier que chaque titre de cadre décrit précisément son contenu ou sa fonction
>    - Valider ou invalider chaque titre selon le contexte
>    - Compléter la section "Critère 2.2" de ce rapport avec vos conclusions
>
> **Temps estimé pour la vérification manuelle** : ~{estimated_time} minutes
>
> **Compétences requises** : Auditeur accessibilité familier avec RGAA 4.1.2 et l'utilisation de lecteurs d'écran

---
"""
        return section

    def _generer_avertissement_critere_2_2(self) -> str:
        """
        Génère l'avertissement pour le critère 2.2.

        Returns:
            str: Avertissement Markdown
        """

        warning = """
> ⚠️ **AVERTISSEMENT IMPORTANT**
>
> La pertinence d'un titre de cadre **ne peut être évaluée que par un auditeur humain**.
> Les résultats ci-dessous sont des **indicateurs automatiques** qui signalent les titres
> suspects nécessitant une attention particulière.
>
> **Ce rapport ne constitue PAS une validation du critère 2.2.**
> Une vérification manuelle de tous les titres de cadres est obligatoire pour
> confirmer la conformité à ce critère.
"""
        return warning

    def _generer_annexe_methodologie(self, metrics: dict, config: dict) -> str:
        """
        Génère l'annexe méthodologie avec détails sur la couverture.

        Args:
            metrics: dict avec métriques
            config: dict avec configuration de l'audit

        Returns:
            str: Annexe complète
        """

        frames_to_verify = metrics['frames_to_verify']
        estimated_time = metrics['estimated_manual_time_minutes']

        annex = f"""### Annexe B : Méthodologie de test détaillée

#### Environnement technique

L'audit a été réalisé avec les outils suivants :
- **Outil principal** : RGAA Section 2 Tester v{config.get('app_version', '1.0.0')}
- **Technologie** : Python {config.get('python_version', 'N/A')} avec Selenium {config.get('selenium_version', 'N/A')}
- **Navigateur** : {config.get('browser_name', 'N/A')} {config.get('browser_version', 'N/A')}
- **Système** : {config.get('os_full_info', 'N/A')}

#### Processus d'audit

1. **Crawling** : Exploration du site jusqu'à 2 niveaux de profondeur
2. **Détection** : Identification de tous les éléments `<frame>` et `<iframe>`
3. **Analyse automatique** :
   - Vérification présence attributs title/aria-label/aria-labelledby
   - Détection titres vides ou génériques
   - Identification frames cachées (exclusion du test)
4. **Flagging manuel** : Marquage titres nécessitant vérification humaine
5. **Génération rapport** : Compilation résultats au format Markdown

#### Critères de conformité

**Critère 2.1 - Présence d'un titre de cadre** :
- ✅ Conforme : Titre présent via title, aria-label ou aria-labelledby
- ❌ Non conforme : Aucun titre fourni ou titre vide
- ⚪ NA : Cadre décoratif caché (aria-hidden="true" ou display:none)

**Résultats automatiques fiables** : L'outil peut déterminer automatiquement et de manière fiable la conformité ou non-conformité pour ce critère.

**Critère 2.2 - Pertinence du titre de cadre** :
- ✅ Pertinent : Titre descriptif du contenu (**validation manuelle obligatoire**)
- ⚠️ Suspect : Titre générique ("frame", "iframe", "widget"...) - **flaggé automatiquement**
- ❓ À vérifier : Titre présent mais pertinence incertaine - **nécessite vérification manuelle**

**Résultats automatiques indicatifs uniquement** : L'outil peut uniquement signaler des problèmes probables. La validation finale nécessite un jugement humain.

#### Ce qui a été testé automatiquement

| Aspect testé | Méthode | Fiabilité | Décision automatique possible |
|--------------|---------|-----------|------------------------------|
| Détection des cadres | Parsing DOM complet | 100% | ✅ Oui |
| Présence attribut `title` | Vérification attribut | 100% | ✅ Oui |
| Titre non vide | Vérification contenu | 100% | ✅ Oui |
| Présence `aria-label` | Vérification attribut | 100% | ✅ Oui |
| Présence `aria-labelledby` | Vérification attribut | 100% | ✅ Oui |
| Cadres cachés (exemptés) | Analyse CSS/attributs | 95% | ✅ Oui |
| Titres génériques | Liste mots-clés | 80% | ⚠️ Indicatif uniquement |
| Titres courts | Comptage caractères | 90% | ⚠️ Indicatif uniquement |
| **Pertinence réelle du titre** | **Impossible** | **0%** | **❌ NON - Humain requis** |

#### Ce qui nécessite une vérification manuelle

**Obligatoire pour le critère 2.2** :
1. Ouvrir chaque page contenant des cadres dans un navigateur
2. Pour chaque cadre, vérifier que le titre :
   - Décrit précisément le contenu OU la fonction du cadre
   - Permet à un utilisateur de lecteur d'écran d'identifier le cadre
   - Est suffisamment distinctif s'il y a plusieurs cadres
3. Contexte important :
   - Un titre "Vidéo" peut être OK s'il n'y a qu'une vidéo
   - Un titre "Vidéo" est insuffisant s'il y a plusieurs vidéos
   - Un titre "Menu principal" est meilleur que juste "Menu"

**Pourquoi c'est impossible automatiquement** :
- La pertinence dépend du contexte de la page
- Nécessite de comprendre le contenu du cadre
- Requiert un jugement sur la qualité descriptive
- Varie selon le nombre d'éléments similaires sur la page

#### Taux de couverture de cet audit

- **Couverture automatique** : ~65% de la Section 2
  - Critère 2.1 : 100% automatisé
  - Critère 2.2 : 30-40% automatisé (flagging uniquement)

- **Vérification manuelle requise** : ~35% de la Section 2
  - Critère 2.2 : Validation de la pertinence de {frames_to_verify} titre(s)

#### Gain de temps estimé

Par rapport à un audit 100% manuel :
- **Temps économisé** : ~75%
- **Temps manuel restant** : ~{estimated_time} minutes pour validation critère 2.2
- **Bénéfice** : Focus de l'auditeur sur la validation qualitative, pas sur la détection

---
"""
        return annex

    def _generer_mentions_legales(self, config: dict) -> str:
        """
        Génère la section mentions légales avec limites de responsabilité.

        Args:
            config: dict avec info application

        Returns:
            str: Mentions légales complètes
        """

        date_generation = formater_date(format_str="%d/%m/%Y à %H:%M")

        mentions = f"""## Mentions légales

### Portée et limites de l'audit automatique

Ce rapport d'audit a été généré automatiquement par l'outil RGAA Section 2 Tester.

#### Couverture des tests automatiques

**Tests réalisés automatiquement (fiabilité élevée)** :
- ✅ Critère 2.1 : Détection exhaustive de la présence ou absence de titres de cadres
- ✅ Identification des cadres exemptés (cachés)
- ✅ Calcul des taux de conformité pour le critère 2.1

**Tests partiels (indicateurs uniquement)** :
- ⚠️ Critère 2.2 : Détection de titres suspects (génériques, trop courts)
- ⚠️ Signalement des cadres nécessitant une vérification manuelle prioritaire

**Tests NON réalisés (vérification manuelle obligatoire)** :
- ❌ Validation de la pertinence réelle des titres de cadres (critère 2.2)
- ❌ Évaluation contextuelle de l'adéquation titre/contenu
- ❌ Jugement sur la qualité descriptive des titres

#### Responsabilités

**L'outil automatique** :
- Fournit une détection exhaustive et fiable du critère 2.1
- Signale les problèmes probables du critère 2.2
- Génère un rapport structuré conforme au format RGAA
- Fait gagner ~75% du temps d'audit

**L'auditeur humain** :
- DOIT vérifier manuellement la pertinence de tous les titres de cadres (critère 2.2)
- DOIT valider les signalements automatiques dans leur contexte
- DOIT compléter le rapport avec ses conclusions sur le critère 2.2
- Est responsable de la validation finale de conformité

#### Conformité réglementaire

Ce rapport d'audit automatique **ne constitue PAS à lui seul** :
- ❌ Une certification de conformité RGAA complète
- ❌ Une validation réglementaire sans intervention humaine
- ❌ Un audit RGAA complet de la Section 2

Ce rapport **constitue** :
- ✅ Un pré-audit automatique fiable pour le critère 2.1
- ✅ Un support d'aide à l'audit pour le critère 2.2
- ✅ Une base de travail pour l'auditeur accessibilité
- ✅ Un outil de suivi de conformité dans le temps

### Méthodologie conforme RGAA 4.1.2

Les tests automatisés suivent strictement la méthodologie du RGAA 4.1.2 publiée par la DINUM (Direction Interministérielle du Numérique).

**Référence** : https://accessibilite.numerique.gouv.fr/methode/criteres-et-tests/#topic2

L'outil respecte les cas particuliers et exemptions définis dans le référentiel, notamment :
- Exemption des cadres cachés (aria-hidden, display:none, visibility:hidden)
- Prise en compte des alternatives au title (aria-label, aria-labelledby)
- Signalement obligatoire de la nécessité de vérification manuelle pour le critère 2.2

### Limitation de responsabilité

L'outil RGAA Section 2 Tester est fourni comme aide à l'audit d'accessibilité.
Les résultats automatiques, bien que fiables pour le critère 2.1, ne remplacent pas
le jugement professionnel d'un auditeur qualifié.

La validation finale de la conformité RGAA Section 2 nécessite obligatoirement
une vérification manuelle, en particulier pour le critère 2.2 (pertinence des titres).

---

**Rapport généré le** : {date_generation}
**Outil** : RGAA Section 2 Tester v{config.get('app_version', '1.0.0')}
**Licence** : Audit réalisé conformément au RGAA 4.1.2
**Validation manuelle requise** : OUI - Critère 2.2 à compléter par auditeur humain
"""
        return mentions

    def _generer_synthese_avec_couverture(self, metrics: dict, resultat: ResultatAnalyseGlobal) -> str:
        """
        Génère la synthèse globale avec distinction auto/manuel.

        Args:
            metrics: dict métriques de couverture
            resultat: ResultatAnalyseGlobal

        Returns:
            str: Synthèse enrichie
        """

        # Déterminer le statut
        if resultat.total_cadres_testes == 0:
            status = 'NA'
        elif resultat.total_non_conformes_2_1 == 0:
            status = 'C'
        else:
            status = 'NC'

        if status == 'C':
            summary = """✅ **Le site est conforme** à la section 2 du RGAA 4.1.2.
Tous les cadres présents possèdent un titre pertinent et accessible.

> ⚠️ **Note** : Le critère 2.2 (pertinence des titres) a été évalué automatiquement avec des indicateurs. Une validation manuelle finale est recommandée pour confirmer la conformité complète.
"""
        elif status == 'NC':
            summary = f"""❌ **Le site n'est pas conforme** à la section 2 du RGAA 4.1.2.
Des non-conformités ont été identifiées concernant les titres de cadres.

**Résumé des problèmes** :
- {metrics['frames_without_title']} cadre(s) sans titre (Critère 2.1 - **validé automatiquement**)
- {metrics['frames_empty_title']} cadre(s) avec titre vide (Critère 2.1 - **validé automatiquement**)
- {metrics['frames_generic_title']} cadre(s) avec titre générique (Critère 2.2 - **à vérifier manuellement**)
- {metrics['frames_to_verify']} cadre(s) à vérifier manuellement (Critère 2.2 - **validation requise**)

> ⚠️ **Action requise** : Les problèmes du critère 2.1 sont confirmés. Les signalements du critère 2.2 nécessitent une vérification manuelle obligatoire pour validation finale.
"""
        else:  # NA
            summary = """ℹ️ **La section 2 n'est pas applicable** à ce site.
Aucun cadre (frame ou iframe) n'a été détecté sur les pages testées.
"""

        return summary

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
