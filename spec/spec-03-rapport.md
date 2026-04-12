# Format du rapport Markdown - RGAA Section 2

## Structure complète du rapport

Le rapport doit reproduire EXACTEMENT le format du document de référence ISIT-RGAA.pdf.

---

## Template complet Markdown

```markdown
# Rapport d'audit d'accessibilité RGAA 4.1.2
## Section 2 : Cadres (Frames)

### Informations sur l'audit

**Site audité** : {URL_SITE}
**Date de l'audit** : {DATE_AUDIT_FR}
**Version RGAA** : 4.1.2
**Section testée** : Section 2 - Cadres
**Nombre de pages testées** : {N_PAGES}

### Environnement de test

- **Système d'exploitation** : {OS_NAME} {OS_VERSION}
- **Navigateur** : {BROWSER_NAME} {BROWSER_VERSION}
- **Outil d'audit** : RGAA Section 2 Tester v{APP_VERSION}
- **Date du référentiel** : RGAA 4.1.2 (depuis le 16 septembre 2019)

---

## Synthèse des résultats

### Taux de conformité - Section 2

| Critère | Statut | Taux de conformité | Pages conformes | Pages non conformes | Pages NA |
|---------|--------|-------------------|-----------------|---------------------|----------|
| 2.1 - Présence d'un titre de cadre | {STATUT_2_1} | {TAUX_2_1}% | {PAGES_CONF_2_1}/{N_PAGES} | {PAGES_NC_2_1}/{N_PAGES} | {PAGES_NA_2_1}/{N_PAGES} |
| 2.2 - Pertinence du titre de cadre | {STATUT_2_2} | {TAUX_2_2}% | {PAGES_CONF_2_2}/{N_PAGES} | {PAGES_NC_2_2}/{N_PAGES} | {PAGES_NA_2_2}/{N_PAGES} |
| **Total Section 2** | **{STATUT_GLOBAL}** | **{TAUX_GLOBAL}%** | **{PAGES_CONF_TOTAL}/{N_PAGES}** | **{PAGES_NC_TOTAL}/{N_PAGES}** | **{PAGES_NA_TOTAL}/{N_PAGES}** |

**Légende** : 
- C = Conforme (tous les tests passent)
- NC = Non conforme (au moins un test échoue)
- NA = Non applicable (aucun cadre détecté)

### Synthèse globale

{IF STATUT_GLOBAL == "C"}
✅ **Le site est conforme** à la section 2 du RGAA 4.1.2.
Tous les cadres présents possèdent un titre pertinent et accessible.
{ENDIF}

{IF STATUT_GLOBAL == "NC"}
❌ **Le site n'est pas conforme** à la section 2 du RGAA 4.1.2.
Des non-conformités ont été identifiées concernant les titres de cadres.

**Résumé des problèmes** :
- {N_FRAMES_NO_TITLE} cadre(s) sans titre
- {N_FRAMES_EMPTY_TITLE} cadre(s) avec titre vide
- {N_FRAMES_GENERIC} cadre(s) avec titre générique
- {N_FRAMES_TO_CHECK} cadre(s) à vérifier manuellement
{ENDIF}

{IF STATUT_GLOBAL == "NA"}
ℹ️ **La section 2 n'est pas applicable** à ce site.
Aucun cadre (frame ou iframe) n'a été détecté sur les pages testées.
{ENDIF}

---

## Détails des tests

### Critère 2.1 : Chaque cadre a-t-il un titre de cadre ?

**Niveau RGAA** : A (obligatoire)
**Test automatisé** : Oui
**Vérification manuelle requise** : Non

#### Méthode de test

Pour chaque cadre (élément `<frame>` ou `<iframe>`) :
1. Vérifier la présence d'un attribut `title` non vide
2. Ou vérifier la présence d'un attribut `aria-label` non vide
3. Ou vérifier la présence d'un attribut `aria-labelledby` référençant un élément existant

**Résultat** : Conforme si au moins une de ces conditions est remplie.

#### Résultats par page

{FOR EACH PAGE}
##### Page {PAGE_NUMBER} : {PAGE_TITLE}

**URL** : {PAGE_URL}
**Cadres détectés** : {N_FRAMES_PAGE}
**Statut page** : {STATUT_PAGE_2_1}

{IF N_FRAMES_PAGE > 0}
| # | Élément | Type | Titre présent | Attribut utilisé | Valeur | Statut | Action requise |
|---|---------|------|---------------|------------------|--------|--------|----------------|
{FOR EACH FRAME}
| {FRAME_INDEX} | {FRAME_TAG} | {FRAME_TYPE} | {HAS_TITLE} | {TITLE_ATTR} | "{TITLE_VALUE}" | {FRAME_STATUS} | {RECOMMENDATION} |
{END FOR}
{ENDIF}

{IF HAS_ISSUES}
**⚠️ Problèmes identifiés sur cette page** :

{FOR EACH ISSUE}
**Problème #{ISSUE_NUMBER}** : {ISSUE_TITLE}

- **Élément concerné** : `{FRAME_SELECTOR}`
- **Description** : {ISSUE_DESCRIPTION}
- **Impact utilisateur** : {IMPACT_DESCRIPTION}
- **Niveau de priorité** : {PRIORITY_LEVEL}

**Code HTML actuel** :
```html
{CURRENT_HTML_CODE}
```

**Code HTML corrigé recommandé** :
```html
{FIXED_HTML_CODE}
```

**Explication de la correction** :
{FIX_EXPLANATION}

{END FOR}
{ENDIF}

{IF NO_ISSUES}
✅ **Aucun problème détecté sur cette page**
{ENDIF}

---

{END FOR PAGES}

---

### Critère 2.2 : Pour chaque cadre ayant un titre de cadre, ce titre de cadre est-il pertinent ?

**Niveau RGAA** : A (obligatoire)
**Test automatisé** : Partiel (détection de titres suspects)
**Vérification manuelle requise** : Oui (obligatoire)

#### Méthode de test

Pour chaque cadre possédant un titre :
1. **Test automatique** : Détecter les titres génériques ou trop courts
2. **Vérification manuelle requise** : Valider que le titre décrit précisément le contenu ou la fonction du cadre

**Note importante** : La pertinence d'un titre ne peut être évaluée que par un auditeur humain. Les résultats ci-dessous sont des indicateurs automatiques nécessitant une vérification.

#### Résultats par page

{FOR EACH PAGE}
##### Page {PAGE_NUMBER} : {PAGE_TITLE}

**URL** : {PAGE_URL}
**Cadres avec titre** : {N_FRAMES_WITH_TITLE}

{IF N_FRAMES_WITH_TITLE > 0}
| # | Élément | Titre actuel | Évaluation automatique | À vérifier manuellement | Notes |
|---|---------|--------------|------------------------|-------------------------|-------|
{FOR EACH FRAME WITH TITLE}
| {FRAME_INDEX} | {FRAME_TAG} | "{TITLE_VALUE}" | {AUTO_EVAL} | {MANUAL_CHECK_NEEDED} | {NOTES} |
{END FOR}

**Légende évaluation automatique** :
- ✅ Semble pertinent : Titre descriptif et spécifique
- ⚠️ Suspect : Titre générique ou très court
- ❓ À vérifier : Impossible d'évaluer automatiquement

**⚠️ Éléments nécessitant une vérification manuelle prioritaire** :

{FOR EACH SUSPICIOUS_FRAME}
**Cadre #{FRAME_INDEX}** : `{FRAME_SELECTOR}`
- **Titre actuel** : "{TITLE_VALUE}"
- **Raison du signalement** : {REASON}
- **Contenu du cadre** : {FRAME_SRC}
- **Recommandation** : {MANUAL_CHECK_RECOMMENDATION}
{END FOR}

{ENDIF}

{IF NO_FRAMES_WITH_TITLE}
ℹ️ Aucun cadre avec titre détecté sur cette page (tous les cadres sont non conformes au critère 2.1).
{ENDIF}

---

{END FOR PAGES}

---

## Recommandations prioritaires

### 🔴 Priorité 1 - Critique (blocage majeur)

{FOR EACH P1_RECOMMENDATION}
- [ ] **{RECOMMENDATION_TITLE}**
  - **Pages concernées** : {AFFECTED_PAGES}
  - **Description** : {DESCRIPTION}
  - **Impact utilisateur** : {IMPACT}
  - **Solution** : {SOLUTION}
  - **Effort estimé** : {EFFORT}
{END FOR}

### 🟠 Priorité 2 - Important (amélioration significative)

{FOR EACH P2_RECOMMENDATION}
- [ ] **{RECOMMENDATION_TITLE}**
  - **Pages concernées** : {AFFECTED_PAGES}
  - **Description** : {DESCRIPTION}
  - **Impact utilisateur** : {IMPACT}
  - **Solution** : {SOLUTION}
  - **Effort estimé** : {EFFORT}
{END FOR}

### 🟡 Priorité 3 - Amélioration (optimisation)

{FOR EACH P3_RECOMMENDATION}
- [ ] **{RECOMMENDATION_TITLE}**
  - **Pages concernées** : {AFFECTED_PAGES}
  - **Description** : {DESCRIPTION}
  - **Impact utilisateur** : {IMPACT}
  - **Solution** : {SOLUTION}
  - **Effort estimé** : {EFFORT}
{END FOR}

---

## Plan de remédiation

### Phase 1 : Corrections critiques (Semaine 1-2)

**Objectif** : Résoudre tous les problèmes de Priorité 1

**Actions** :
1. {ACTION_1_P1}
2. {ACTION_2_P1}
3. {ACTION_3_P1}

**Livrables** :
- Tous les cadres possèdent un titre
- Élimination des titres vides

**Validation** : Test automatique avec RGAA Tester

---

### Phase 2 : Corrections importantes (Semaine 3-4)

**Objectif** : Améliorer la pertinence des titres

**Actions** :
1. {ACTION_1_P2}
2. {ACTION_2_P2}
3. {ACTION_3_P2}

**Livrables** :
- Remplacement des titres génériques
- Titres descriptifs et spécifiques

**Validation** : Revue manuelle par expert accessibilité

---

### Phase 3 : Vérifications manuelles et optimisations (Semaine 5)

**Objectif** : Valider la pertinence finale de tous les titres

**Actions** :
1. Vérifier manuellement chaque titre de cadre
2. Optimiser les titres pour lecteurs d'écran
3. Documenter les choix de titres

**Livrables** :
- Documentation des titres validés
- Guide de bonnes pratiques interne

**Validation** : Test utilisateur avec lecteur d'écran

---

## Annexes

### Annexe A : Liste complète des pages testées

| # | Titre de la page | URL | Cadres | Statut 2.1 | Statut 2.2 |
|---|------------------|-----|--------|------------|------------|
{FOR EACH PAGE}
| {PAGE_NUMBER} | {PAGE_TITLE} | {PAGE_URL} | {N_FRAMES} | {STATUS_2_1} | {STATUS_2_2} |
{END FOR}

**Total** : {N_PAGES} pages testées

---

### Annexe B : Méthodologie de test détaillée

#### Environnement technique

L'audit a été réalisé avec les outils suivants :
- **Outil principal** : RGAA Section 2 Tester v{APP_VERSION}
- **Technologie** : Python {PYTHON_VERSION} avec Selenium {SELENIUM_VERSION}
- **Navigateur** : {BROWSER_FULL_INFO}
- **Système** : {OS_FULL_INFO}

#### Processus d'audit

1. **Crawling** : Exploration du site jusqu'à {CRAWL_DEPTH} niveaux de profondeur
2. **Détection** : Identification de tous les éléments `<frame>` et `<iframe>`
3. **Analyse automatique** :
   - Vérification présence attributs title/aria-label/aria-labelledby
   - Détection titres vides ou génériques
   - Identification frames cachées (exclusion du test)
4. **Flagging manuel** : Marquage titres nécessitant vérification humaine
5. **Génération rapport** : Compilation résultats au format Markdown

#### Critères de conformité

**Critère 2.1** :
- ✅ Conforme : Titre présent via title, aria-label ou aria-labelledby
- ❌ Non conforme : Aucun titre fourni ou titre vide
- ⚪ NA : Cadre décoratif caché (aria-hidden="true" ou display:none)

**Critère 2.2** :
- ✅ Pertinent : Titre descriptif du contenu (validation manuelle)
- ⚠️ Suspect : Titre générique ("frame", "iframe", "widget"...)
- ❓ À vérifier : Titre présent mais pertinence incertaine

---

### Annexe C : Glossaire RGAA Section 2

**Cadre (Frame)** : 
Élément HTML `<frame>` (déprécié) ou `<iframe>` permettant d'inclure un document HTML dans un autre document.

**Titre de cadre** :
Texte associé à un cadre via :
- L'attribut `title` de l'élément frame/iframe
- L'attribut `aria-label` de l'élément frame/iframe  
- L'attribut `aria-labelledby` référençant un élément contenant le texte du titre

**Cadre décoratif** :
Cadre qui n'apporte pas d'information et qui peut être ignoré par les technologies d'assistance (généralement marqué avec `aria-hidden="true"`).

**Titre pertinent** :
Un titre de cadre est pertinent s'il permet d'identifier précisément le contenu ou la fonction du cadre pour les utilisateurs de technologies d'assistance.

**Exemples de titres pertinents** :
- ✅ "Vidéo de démonstration du produit"
- ✅ "Formulaire de contact client"
- ✅ "Publicité pour partenaire XYZ"

**Exemples de titres non pertinents** :
- ❌ "Frame" ou "iframe"
- ❌ "Widget" ou "Contenu"
- ❌ "Externe" ou "Embed"

---

### Annexe D : Références

- **RGAA 4.1.2 officiel** : https://www.numerique.gouv.fr/publications/rgaa-accessibilite/
- **Critères Section 2** : https://accessibilite.numerique.gouv.fr/methode/criteres-et-tests/#topic2
- **WCAG 2.1 - Critère 4.1.2** : https://www.w3.org/WAI/WCAG21/Understanding/name-role-value.html
- **WCAG 2.1 - Technique H64** : https://www.w3.org/WAI/WCAG21/Techniques/html/H64

---

**Rapport généré le** : {DATE_GENERATION_COMPLETE}
**Outil** : RGAA Section 2 Tester v{APP_VERSION}
**Licence** : Audit réalisé conformément au RGAA 4.1.2

---

## Mentions légales

Ce rapport d'audit a été généré automatiquement par l'outil RGAA Section 2 Tester.
Les résultats des tests automatisés doivent être complétés par une vérification manuelle,
notamment pour le critère 2.2 (pertinence des titres).

L'outil est conforme à la méthodologie du RGAA 4.1.2 publiée par la DINUM
(Direction Interministérielle du Numérique).
```

---

## Variables à remplacer

### Variables principales
- `{URL_SITE}` : URL du site audité
- `{DATE_AUDIT_FR}` : Date format français (ex: "30 janvier 2026")
- `{N_PAGES}` : Nombre total de pages testées

### Variables environnement
- `{OS_NAME}` : Nom OS (Windows, macOS, Linux)
- `{OS_VERSION}` : Version OS
- `{BROWSER_NAME}` : Nom navigateur (Chrome, Firefox)
- `{BROWSER_VERSION}` : Version navigateur
- `{APP_VERSION}` : Version application

### Variables résultats
- `{STATUT_2_1}` : C / NC / NA
- `{TAUX_2_1}` : Pourcentage 0-100
- `{PAGES_CONF_2_1}` : Nombre pages conformes
- `{PAGES_NC_2_1}` : Nombre pages non conformes
- `{PAGES_NA_2_1}` : Nombre pages non applicables

### Variables cadres
- `{N_FRAMES_NO_TITLE}` : Nombre cadres sans titre
- `{N_FRAMES_EMPTY_TITLE}` : Nombre cadres titre vide
- `{N_FRAMES_GENERIC}` : Nombre cadres titre générique

---

**Note importante** : Le rapport doit être généré en UTF-8 et respecter strictement cette structure pour être conforme au format ISIT.