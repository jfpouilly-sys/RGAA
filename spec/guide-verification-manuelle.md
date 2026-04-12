# Guide de vérification manuelle - Critère 2.2 RGAA
## Pertinence des titres de cadres

**Version** : 1.0.0  
**Date** : Janvier 2026  
**Public cible** : Auditeurs accessibilité RGAA

---

## Table des matières

1. [Introduction](#introduction)
2. [Prérequis](#prérequis)
3. [Comprendre le rapport automatique](#comprendre-le-rapport-automatique)
4. [Méthodologie de vérification](#méthodologie-de-vérification)
5. [Critères de décision](#critères-de-décision)
6. [Utilisation d'un lecteur d'écran](#utilisation-dun-lecteur-décran)
7. [Cas pratiques et exemples](#cas-pratiques-et-exemples)
8. [Compléter le rapport](#compléter-le-rapport)
9. [Modèle de tableau de validation](#modèle-de-tableau-de-validation)
10. [FAQ](#faq)

---

## Introduction

### Objectif de ce guide

Ce guide vous aide à **compléter la vérification manuelle du critère 2.2** du RGAA 4.1.2 après avoir utilisé l'outil automatique RGAA Section 2 Tester.

**Rappel du critère 2.2** :
> Pour chaque cadre ayant un titre de cadre, ce titre de cadre est-il pertinent ?

### Pourquoi la vérification manuelle est obligatoire

L'outil automatique **ne peut PAS** déterminer la pertinence d'un titre car cela nécessite :
- Comprendre le **contenu réel** du cadre
- Évaluer le **contexte** de la page
- Juger si le titre est **suffisamment descriptif**
- Vérifier que le titre permet une **identification claire**

➡️ **Seul un auditeur humain peut faire ces jugements contextuels.**

### Temps estimé

- **5-10 minutes de préparation** (lecture du rapport, installation outils)
- **1-2 minutes par cadre** à vérifier
- **10-15 minutes** pour compléter le rapport final

**Exemple** : Pour 20 cadres → environ **45 minutes** au total

---

## Prérequis

### Compétences requises

- ✅ Connaissance du RGAA 4.1.2 Section 2
- ✅ Expérience avec les lecteurs d'écran (NVDA ou JAWS)
- ✅ Capacité à inspecter le code HTML
- ✅ Compréhension des technologies d'assistance

### Outils nécessaires

#### 1. Lecteur d'écran
**NVDA (recommandé - gratuit)** :
- Télécharger : https://www.nvaccess.org/download/
- Installation : 5 minutes
- Commandes de base à connaître

**Ou JAWS (payant)** :
- Version d'essai disponible
- Plus utilisé en entreprise

#### 2. Navigateur
- **Firefox** (recommandé avec NVDA)
- **Chrome** (alternatif)

#### 3. Outils de développement
- **Inspecteur du navigateur** (F12)
- Extension **Web Developer** (optionnel)

---

## Comprendre le rapport automatique

### Structure du rapport

Le rapport automatique contient plusieurs sections clés :

#### 1. Section "Actions requises pour finaliser l'audit"

```markdown
> 🔴 VÉRIFICATION MANUELLE OBLIGATOIRE
> 
> 2. ⚠️ Critère 2.2 : Vérification manuelle requise pour 18 cadre(s)
>    - Ouvrir chaque page concernée dans un navigateur
>    - Vérifier que chaque titre de cadre décrit précisément son contenu
>    - Temps estimé : ~25 minutes
```

**➡️ Cette section vous indique combien de cadres nécessitent votre attention.**

#### 2. Tableau des résultats par page

```markdown
| # | Élément | Titre actuel | Évaluation auto | À vérifier | Notes |
|---|---------|--------------|-----------------|------------|-------|
| 1 | iframe | "widget" | ⚠️ Suspect | ✅ OUI | Titre générique |
| 2 | iframe | "Vidéo démo" | ✅ Semble OK | ⚠️ Recommandé | Descriptif |
```

**Légende des évaluations automatiques** :
- ✅ **Semble pertinent** : Titre descriptif, mais à vérifier quand même
- ⚠️ **Suspect** : Titre générique ou très court - VÉRIFICATION PRIORITAIRE
- ❓ **À vérifier** : L'outil ne peut pas évaluer

#### 3. Éléments nécessitant vérification prioritaire

```markdown
**Cadre #1** : iframe.widget-container
- Titre actuel : "widget"
- Raison du signalement : Titre générique détecté
- Contenu du cadre : https://widgets.example.com/filter
- Recommandation : Vérifier le contenu réel
```

**➡️ Commencez par ces cadres signalés comme "Suspects".**

### Ce que l'outil a déjà validé

✅ **Critère 2.1** : Tous les cadres ont bien un titre (ou sont exemptés)
✅ **Détection** : Titres génériques, courts ou suspects sont signalés
✅ **Code HTML** : Fourni pour chaque cadre

### Ce que VOUS devez faire

❌ **Valider** : Que chaque titre décrit bien le contenu/fonction du cadre
❌ **Décider** : Conforme ou Non conforme pour chaque cadre
❌ **Proposer** : Des corrections pour les titres non pertinents

---

## Méthodologie de vérification

### Processus étape par étape

#### Étape 1 : Préparer l'environnement

```
1. Ouvrir le rapport automatique (format Markdown)
2. Lancer le navigateur (Firefox recommandé)
3. Démarrer le lecteur d'écran (NVDA)
4. Ouvrir un éditeur de texte pour prendre des notes
5. Créer un tableau de validation (voir modèle ci-dessous)
```

#### Étape 2 : Identifier les pages à vérifier

Dans le rapport, repérer :
- Les pages qui contiennent des cadres
- Le nombre de cadres par page
- Les cadres signalés comme "Suspects" (priorité)

**Exemple de liste** :
```
Page 1 : Accueil → 3 cadres (1 suspect)
Page 5 : Catégorie électronique → 4 cadres (3 suspects)
Page 8 : Panier → 1 cadre (0 suspect)
```

#### Étape 3 : Pour chaque page

##### A. Ouvrir la page dans le navigateur

```
1. Copier l'URL depuis le rapport
2. Ouvrir dans Firefox
3. Attendre le chargement complet (important pour les iframes)
```

##### B. Localiser le cadre à vérifier

**Méthode 1 - Avec l'inspecteur** :
```
1. Appuyer sur F12 (ouvrir DevTools)
2. Cliquer sur l'icône "Sélectionner un élément" (Ctrl+Shift+C)
3. Survoler la zone du cadre dans la page
4. Le code HTML s'affiche automatiquement
```

**Méthode 2 - Recherche dans le code** :
```
1. F12 → Onglet "Inspecteur"
2. Ctrl+F pour rechercher
3. Chercher le titre du cadre (ex: "widget")
4. Naviguer jusqu'à l'élément <iframe>
```

##### C. Examiner le cadre

**Questions à se poser** :

1. **Quel est le contenu visible du cadre ?**
   - Une vidéo ? Une publicité ? Un formulaire ? Une carte ?
   - Observer visuellement le rendu

2. **Quelle est la fonction du cadre ?**
   - Informatif (vidéo, actualités)
   - Interactif (formulaire, carte interactive)
   - Commercial (publicité)
   - Technique (tracking, analytics)

3. **Le titre actuel décrit-il bien ce contenu/fonction ?**
   - Est-ce clair et précis ?
   - Un utilisateur aveugle comprendrait-il de quoi il s'agit ?

4. **Y a-t-il d'autres cadres similaires sur la page ?**
   - Si oui, les titres permettent-ils de les distinguer ?

##### D. Tester avec le lecteur d'écran

**Avec NVDA** :
```
1. Activer NVDA (Ctrl+Alt+N si configuré)
2. Sur la page, naviguer vers le cadre :
   - Touche D (navigate by landmark/region)
   - Ou naviguer avec les flèches
3. NVDA annonce : "Cadre [titre du cadre]"
4. Se demander : "Cette annonce est-elle claire ?"
```

**Commandes NVDA utiles** :
- `D` : Passer au cadre suivant (frame)
- `Shift+D` : Cadre précédent
- `Insert+F7` : Liste des éléments (choisir "Frames")
- `Insert+Barre espace` : Mode formulaire (pour interagir)

**Ce que vous devez entendre** :
```
✅ BON : "Cadre - Vidéo de démonstration du produit X"
❌ MAUVAIS : "Cadre - widget"
❌ MAUVAIS : "Cadre - frame"
```

##### E. Prendre la décision

**Le titre est PERTINENT si** :
- ✅ Il décrit **précisément** le contenu OU la fonction
- ✅ Il permet à l'utilisateur de **décider** s'il veut y accéder
- ✅ Il est **suffisamment distinctif** (si plusieurs cadres)
- ✅ Un utilisateur aveugle peut **identifier** le cadre

**Le titre est NON PERTINENT si** :
- ❌ Il est trop **générique** ("widget", "frame", "iframe")
- ❌ Il est trop **vague** ("vidéo" alors qu'il y en a 5)
- ❌ Il ne correspond **pas au contenu** réel
- ❌ Il est **trompeur** ou inexact

**CAS PARTICULIER - Publicités** :
```
✅ Pertinent : "Publicité pour notre partenaire TechCorp"
✅ Pertinent : "Bannière publicitaire - Offre spéciale"
❌ Non pertinent : "Pub"
❌ Non pertinent : "Ad"
```

##### F. Noter la décision

Dans votre tableau de validation :
```
Page : Accueil
Cadre #2 : iframe.ad-banner
Titre actuel : "widget"
Contenu réel : Filtre de recherche de produits
Décision : NON PERTINENT
Titre proposé : "Filtres de recherche par catégorie et prix"
Justification : Le titre "widget" ne permet pas d'identifier 
               la fonction de filtre de recherche
```

---

## Critères de décision

### Grille d'évaluation de la pertinence

| Critère | Question | Poids |
|---------|----------|-------|
| **Précision** | Le titre décrit-il exactement le contenu ? | 🔴 Critique |
| **Clarté** | Un utilisateur comprend-il immédiatement ? | 🔴 Critique |
| **Distinction** | Le titre permet-il de différencier ce cadre des autres ? | 🟠 Important |
| **Concision** | Le titre est-il concis tout en étant descriptif ? | 🟡 Souhaitable |
| **Contexte** | Le titre a-t-il du sens dans le contexte de la page ? | 🟠 Important |

### Matrice de décision rapide

```
┌─────────────────────────────────────────────────┐
│ LE TITRE DÉCRIT-IL LE CONTENU/FONCTION ?       │
├─────────────────────────────────────────────────┤
│                                                  │
│  OUI, précisément → PERTINENT ✅                │
│                                                  │
│  OUI, mais trop vague → Contexte ?              │
│    ├─ Un seul cadre de ce type → PERTINENT ⚠️  │
│    └─ Plusieurs cadres → NON PERTINENT ❌       │
│                                                  │
│  NON ou partiellement → NON PERTINENT ❌        │
│                                                  │
│  Générique (frame/widget) → NON PERTINENT ❌    │
│                                                  │
└─────────────────────────────────────────────────┘
```

### Exemples de décisions

#### Exemple 1 : Page avec une seule vidéo

**Contexte** : Page produit, 1 iframe de vidéo

**Titre actuel** : "Vidéo"

**Décision** : ⚠️ **ACCEPTABLE** (mais peut être amélioré)

**Justification** :
- Il n'y a qu'une vidéo sur la page → pas d'ambiguïté
- Le titre indique qu'il s'agit d'une vidéo
- Contexte clair pour l'utilisateur

**Recommandation** : Améliorer en "Vidéo de démonstration du produit"

---

#### Exemple 2 : Page avec plusieurs vidéos

**Contexte** : Page tutoriels, 5 iframes de vidéos

**Titres actuels** : Toutes "Vidéo"

**Décision** : ❌ **NON PERTINENT**

**Justification** :
- 5 cadres avec le même titre → impossible de les distinguer
- L'utilisateur ne peut pas savoir quelle vidéo consulter
- Violation du principe de distinction

**Correction requise** :
```
Vidéo 1 : "Vidéo tutoriel - Installation du logiciel"
Vidéo 2 : "Vidéo tutoriel - Configuration initiale"
Vidéo 3 : "Vidéo tutoriel - Première utilisation"
...
```

---

#### Exemple 3 : Cadre de publicité

**Contexte** : Bannière publicitaire

**Titre actuel** : "iframe"

**Décision** : ❌ **NON PERTINENT**

**Justification** :
- "iframe" est juste le type d'élément technique
- Ne décrit ni le contenu ni la fonction
- L'utilisateur ne sait pas qu'il s'agit d'une publicité

**Correction requise** : "Publicité pour [nom partenaire ou produit]"

---

#### Exemple 4 : Carte interactive

**Contexte** : Page "Nous trouver"

**Titre actuel** : "Carte"

**Décision** : ⚠️ **ACCEPTABLE** (mais peut être amélioré)

**Justification** :
- Une seule carte sur la page
- Le titre indique qu'il s'agit d'une carte
- Contexte de la page clair ("Nous trouver")

**Recommandation** : "Carte interactive de nos magasins en France"

---

#### Exemple 5 : Widget de recherche

**Contexte** : Site e-commerce

**Titre actuel** : "widget"

**Décision** : ❌ **NON PERTINENT**

**Justification** :
- "widget" est un terme technique générique
- Ne décrit pas la fonction (recherche de produits)
- L'utilisateur ne sait pas à quoi sert ce cadre

**Correction requise** : "Moteur de recherche de produits"

---

## Utilisation d'un lecteur d'écran

### Installation et configuration de NVDA

#### Installation (Windows)

```
1. Télécharger NVDA : https://www.nvaccess.org/download/
2. Exécuter l'installateur
3. Choisir "Installer NVDA sur cet ordinateur"
4. Suivre les étapes
5. Au premier lancement, choisir la voix française
```

#### Commandes essentielles

| Action | Commande | Description |
|--------|----------|-------------|
| Démarrer NVDA | Ctrl+Alt+N | Après configuration |
| Arrêter NVDA | Insert+Q | Puis Entrée |
| Activer/désactiver voix | Insert+S | Toggle parole |
| Navigation par frames | D | Cadre suivant |
| Navigation frames arrière | Shift+D | Cadre précédent |
| Liste des éléments | Insert+F7 | Choisir "Frames" |
| Lire le contexte | Insert+Flèche haut | Ligne courante |

**Note** : `Insert` = touche `Insertion` (souvent au-dessus des flèches)

### Procédure de test avec NVDA

#### 1. Préparer la page

```
1. Ouvrir la page à tester dans Firefox
2. Laisser charger complètement (important pour iframes)
3. Vérifier visuellement que les cadres sont bien affichés
```

#### 2. Démarrer NVDA

```
1. Lancer NVDA (Ctrl+Alt+N)
2. NVDA annonce : "NVDA démarré"
3. Attendre que la voix se stabilise
```

#### 3. Naviguer vers les cadres

**Méthode 1 - Navigation séquentielle** :
```
1. Se placer en haut de la page (Ctrl+Home)
2. Appuyer sur D plusieurs fois
3. NVDA annonce chaque cadre rencontré
4. Noter les titres annoncés
```

**Méthode 2 - Liste des éléments** :
```
1. Appuyer sur Insert+F7
2. Dans la fenêtre, sélectionner "Frames"
3. La liste de tous les cadres s'affiche
4. Naviguer avec les flèches
5. NVDA lit le titre de chaque cadre
```

#### 4. Évaluer l'annonce

**Questions à se poser** :
- L'annonce de NVDA est-elle claire ?
- Un utilisateur aveugle comprendrait-il le contenu ?
- Le titre permet-il de décider d'entrer dans le cadre ?

**Exemples d'annonces** :

```
✅ CLAIR : "Cadre - Formulaire de contact client"
→ L'utilisateur sait qu'il s'agit d'un formulaire de contact

❌ CONFUS : "Cadre - widget"
→ L'utilisateur ne sait pas de quoi il s'agit

✅ CLAIR : "Cadre - Publicité pour notre partenaire TechCorp"
→ L'utilisateur peut choisir de sauter la publicité

❌ AMBIGU : "Cadre - Vidéo" (alors qu'il y en a 5)
→ L'utilisateur ne sait pas quelle vidéo c'est
```

#### 5. Tester l'interaction (optionnel)

Si le cadre est interactif :
```
1. Naviguer jusqu'au cadre (D)
2. Appuyer sur Entrée pour entrer dans le cadre
3. Utiliser Tab pour naviguer dans le contenu
4. Vérifier que l'interaction fonctionne
5. Échap pour sortir du cadre
```

### Cas particuliers

#### Cadres imbriqués (nested iframes)

```
Page principale
  └─ Iframe 1 : "Contenu externe"
       └─ Iframe 2 : "Publicité"
```

**Test** :
- Naviguer dans l'ordre avec D
- Vérifier que chaque niveau a un titre distinct
- S'assurer qu'on peut revenir en arrière (Shift+D)

#### Cadres chargés dynamiquement

```
Problème : Le cadre n'apparaît qu'après une action (clic, scroll)
Solution : 
1. Effectuer l'action déclencheuse
2. Attendre le chargement
3. Rafraîchir la liste des cadres (Insert+F7)
```

---

## Cas pratiques et exemples

### Cas 1 : Site e-commerce avec filtres

**Page** : Catégorie "Électronique"

**Cadres détectés** :
```
1. iframe.product-filters - Titre : "widget"
2. iframe.video-demo - Titre : "Vidéo"
3. iframe.customer-reviews - Titre : "Reviews"
4. iframe.ad-banner - Titre : "Pub"
```

**Vérification** :

**Cadre 1 - Filtres** :
- Contenu réel : Filtres de recherche (prix, marque, note)
- Titre actuel : "widget"
- **Décision** : ❌ NON PERTINENT
- **Correction** : "Filtres de recherche par prix, marque et note"
- **Justification** : "widget" ne décrit pas la fonction de filtrage

**Cadre 2 - Vidéo** :
- Contenu réel : Vidéo de comparaison de produits
- Titre actuel : "Vidéo"
- **Décision** : ⚠️ LIMITE (amélioration recommandée)
- **Correction suggérée** : "Vidéo de comparaison - Top 5 smartphones 2026"
- **Justification** : Il y a 3 vidéos sur la page, "Vidéo" seul est insuffisant

**Cadre 3 - Avis** :
- Contenu réel : Widget d'avis clients Trustpilot
- Titre actuel : "Reviews"
- **Décision** : ⚠️ ACCEPTABLE (mais en anglais)
- **Correction suggérée** : "Avis clients Trustpilot"
- **Justification** : Descriptif mais préférer le français

**Cadre 4 - Publicité** :
- Contenu réel : Bannière publicitaire pour casque audio
- Titre actuel : "Pub"
- **Décision** : ⚠️ LIMITE (trop court)
- **Correction** : "Publicité - Casque audio sans fil BrandX"
- **Justification** : "Pub" est trop court, manque de contexte

---

### Cas 2 : Page d'actualités avec multiples contenus

**Page** : Blog/Actualités

**Cadres détectés** :
```
1. iframe - Titre : "Lecteur vidéo"
2. iframe - Titre : "Lecteur vidéo"
3. iframe - Titre : "Lecteur vidéo"
4. iframe - Titre : "Carte"
5. iframe - Titre : "Commentaires"
```

**Problème** : 3 cadres avec le même titre "Lecteur vidéo"

**Vérification** :

**Cadres 1-2-3 - Vidéos** :
- Contenu réel :
  - Cadre 1 : Interview du CEO
  - Cadre 2 : Présentation nouveau produit
  - Cadre 3 : Tutoriel d'utilisation
- Titre actuel : Tous "Lecteur vidéo"
- **Décision** : ❌ NON PERTINENT (impossibilité de distinguer)
- **Corrections requises** :
  ```
  1. "Vidéo - Interview du CEO Jean Dupont"
  2. "Vidéo - Présentation du nouveau produit XYZ"
  3. "Vidéo - Tutoriel d'utilisation du produit"
  ```
- **Justification** : Titres identiques ne permettent pas la distinction

**Cadre 4 - Carte** :
- Contenu réel : Carte des événements à venir
- Titre actuel : "Carte"
- **Décision** : ⚠️ LIMITE
- **Correction** : "Carte interactive des événements à venir"
- **Justification** : "Carte" manque de contexte

**Cadre 5 - Commentaires** :
- Contenu réel : Widget de commentaires Disqus
- Titre actuel : "Commentaires"
- **Décision** : ✅ PERTINENT
- **Justification** : Clair, précis, un seul widget de ce type

---

### Cas 3 : Application web complexe

**Page** : Dashboard utilisateur

**Cadres détectés** :
```
1. iframe - Titre : "content"
2. iframe - Titre : "external-widget"
3. iframe - Titre : "Graphique de performance"
4. iframe - Titre : ""  (vide - déjà corrigé par critère 2.1)
```

**Vérification** :

**Cadre 1** :
- Contenu réel : Tableau de bord des statistiques
- Titre actuel : "content"
- **Décision** : ❌ NON PERTINENT
- **Correction** : "Tableau de bord - Statistiques mensuelles"

**Cadre 2** :
- Contenu réel : Calendrier de rendez-vous
- Titre actuel : "external-widget"
- **Décision** : ❌ NON PERTINENT
- **Correction** : "Calendrier de vos rendez-vous"

**Cadre 3** :
- Contenu réel : Graphique avec évolution des ventes
- Titre actuel : "Graphique de performance"
- **Décision** : ✅ PERTINENT
- **Justification** : Descriptif et précis

---

## Compléter le rapport

### Ajouter vos conclusions au rapport

#### 1. Créer un fichier de validation

Créez un fichier : `Validation_Manuelle_Critere_2.2.md`

```markdown
# Validation manuelle - Critère 2.2
## Site : www.example-eshop.fr
## Date : 30 janvier 2026
## Auditeur : [Votre nom]

### Résumé

- Total de cadres vérifiés : 18
- Cadres conformes : 5 (28%)
- Cadres non conformes : 13 (72%)
- Temps de vérification : 35 minutes

### Détails par page

[Voir tableaux ci-dessous]

### Conclusion critère 2.2

❌ Le critère 2.2 est **NON CONFORME**

13 cadres sur 18 ont des titres non pertinents qui nécessitent 
des corrections pour permettre une identification claire par les 
utilisateurs de technologies d'assistance.

### Recommandations prioritaires

[Liste des corrections à apporter]
```

#### 2. Utiliser le modèle de tableau

Pour chaque page, remplissez un tableau :

```markdown
#### Page : Accueil (www.example.com/)

| # | Élément | Titre actuel | Contenu réel | Conforme | Titre proposé | Notes |
|---|---------|--------------|--------------|----------|---------------|-------|
| 1 | iframe#video | Vidéo de présentation | Présentation produits | ✅ Oui | - | Clair et précis |
| 2 | iframe.ad | iframe | Publicité | ❌ Non | "Publicité partenaire X" | Générique |
| 3 | iframe.trust | Avis Trustpilot | Widget avis | ✅ Oui | - | Descriptif |

**Résultat page** : 2/3 conformes (66%)
```

#### 3. Synthétiser les problèmes

Regroupez les problèmes par type :

```markdown
### Types de non-conformités identifiées

1. **Titres génériques** (8 occurrences)
   - "widget", "iframe", "content", "frame"
   - Impact : Impossible d'identifier le contenu
   - Action : Remplacer par description précise

2. **Titres trop vagues** (3 occurrences)
   - "Vidéo" (sans précision, plusieurs vidéos présentes)
   - Impact : Impossible de distinguer les cadres
   - Action : Ajouter contexte spécifique

3. **Titres en anglais** (2 occurrences)
   - "Reviews", "Map"
   - Impact : Barrière linguistique
   - Action : Traduire en français
```

#### 4. Proposer un plan d'action

```markdown
### Plan d'action recommandé

#### Phase 1 - Urgent (Semaine 1)
- [ ] Remplacer tous les titres génériques (8 cadres)
- [ ] Corriger les titres vides déjà identifiés

#### Phase 2 - Important (Semaine 2)
- [ ] Améliorer les titres trop vagues (3 cadres)
- [ ] Traduire les titres en anglais (2 cadres)

#### Phase 3 - Validation (Semaine 3)
- [ ] Re-tester avec lecteur d'écran
- [ ] Valider avec utilisateurs
```

---

## Modèle de tableau de validation

### Template Excel/Google Sheets

```
| Page | URL | Cadre # | Sélecteur CSS | Titre actuel | Contenu réel | Pertinent ? | Titre proposé | Justification | Priorité | Testélecteur d'écran ? |
|------|-----|---------|---------------|--------------|--------------|-------------|---------------|---------------|----------|---------|
| Accueil | https://... | 1 | iframe#video | Vidéo | Démo produit | Oui | - | Clair | - | Oui |
| Accueil | https://... | 2 | iframe.ad | widget | Publicité | Non | Pub partenaire X | Générique | P1 | Oui |
```

**Colonnes essentielles** :
- **Pertinent ?** : Oui / Non / Limite
- **Priorité** : P1 (Critique) / P2 (Important) / P3 (Amélioration)
- **Testé lecteur d'écran ?** : Oui / Non

### Template Markdown simplifié

```markdown
### Page : [Nom de la page]
**URL** : [URL complète]

| Cadre | Titre | Pertinent | Correction | Priorité |
|-------|-------|-----------|------------|----------|
| #1 iframe.video | Vidéo de démo | ✅ | - | - |
| #2 iframe.ad | widget | ❌ | Publicité X | P1 |
| #3 iframe.map | Carte | ⚠️ | Carte magasins | P2 |

**Taux page** : 1/3 conformes (33%)
**Action requise** : Corriger 2 cadres
```

---

## FAQ

### Questions fréquentes

#### Q1 : Dois-je vérifier TOUS les cadres ou seulement ceux signalés ?

**R :** Vous devez vérifier **TOUS les cadres avec un titre**.

Le critère 2.2 s'applique à "chaque cadre ayant un titre de cadre". L'outil signale les cas suspects, mais même un cadre noté "✅ Semble pertinent" doit être vérifié manuellement.

**Priorisation recommandée** :
1. Cadres signalés "⚠️ Suspect" (priorité haute)
2. Cadres signalés "❓ À vérifier"
3. Cadres signalés "✅ Semble pertinent"

---

#### Q2 : Comment savoir si un titre "Vidéo" est suffisant ?

**R :** Cela dépend du contexte de la page.

**Test simple** :
- **Une seule vidéo sur la page** → "Vidéo" peut être acceptable (mais amélioration recommandée)
- **Plusieurs vidéos sur la page** → "Vidéo" est insuffisant (non conforme)

**Meilleure pratique** : Toujours être plus descriptif
- ✅ "Vidéo de démonstration du produit X"
- ✅ "Vidéo tutoriel - Installation"

---

#### Q3 : Les publicités ont-elles besoin d'un titre pertinent ?

**R :** **OUI, absolument.**

Les utilisateurs de lecteurs d'écran ont le droit de savoir qu'il s'agit d'une publicité et de pouvoir la sauter facilement.

**Exemples** :
- ✅ "Publicité pour notre partenaire TechCorp"
- ✅ "Bannière publicitaire - Offre spéciale smartphones"
- ❌ "Ad" (trop court, en anglais)
- ❌ "widget" (ne mentionne pas qu'il s'agit d'une pub)

---

#### Q4 : Que faire si je ne peux pas voir le contenu du cadre ?

**Situations possibles** :

**A. Cadre bloqué par bloqueur de publicités**
```
Solution :
1. Désactiver temporairement le bloqueur
2. Recharger la page
3. Vérifier le contenu
4. Ré-activer le bloqueur après
```

**B. Cadre nécessitant une authentification**
```
Solution :
1. Créer un compte test si possible
2. Se connecter et vérifier
3. Ou analyser le code source (attribut src)
```

**C. Cadre avec contenu dynamique (API)**
```
Solution :
1. Inspecter le code (F12)
2. Observer les requêtes réseau
3. Déduire le contenu de l'URL source
4. Documenter dans les notes
```

**D. Cadre cassé/erreur 404**
```
Solution :
1. Noter "Cadre non fonctionnel"
2. Signaler le problème technique
3. Si possible, consulter une version de dev/staging
```

---

#### Q5 : Un titre peut-il être trop long ?

**R :** Oui, mais c'est rarement un problème.

**Recommandations** :
- **Idéal** : 5-15 mots
- **Acceptable** : Jusqu'à 20-25 mots
- **Trop long** : > 30 mots (devient confus)

**Exemples** :
```
✅ BIEN : "Formulaire de contact pour le service client"  (7 mots)

✅ ACCEPTABLE : "Vidéo de démonstration du processus complet d'installation du logiciel sur Windows"  (12 mots)

❌ TROP LONG : "Cadre iframe contenant une vidéo YouTube qui présente de manière détaillée le processus complet d'installation du logiciel de comptabilité sur les systèmes d'exploitation Windows 10 et Windows 11"  (28 mots)
→ Simplifier en : "Vidéo - Installation du logiciel sur Windows 10/11"
```

**Principe** : Descriptif mais concis

---

#### Q6 : Dois-je utiliser un lecteur d'écran pour CHAQUE cadre ?

**R :** Non, mais c'est recommandé pour les cas ambigus.

**Approche pragmatique** :

**Tester au lecteur d'écran** :
- ✅ Cadres signalés "Suspect"
- ✅ Cas où vous hésitez sur la décision
- ✅ Au moins 2-3 cadres par page en échantillon

**Pas obligatoire au lecteur d'écran** :
- ⚠️ Cas évidents (titre "iframe" → clairement non pertinent)
- ⚠️ Cas excellents (titre très descriptif → clairement pertinent)

**Bonne pratique** : Testez au moins 30% des cadres au lecteur d'écran pour vous assurer de votre évaluation.

---

#### Q7 : Comment gérer les iframes de tracking/analytics ?

**R :** Ces cadres doivent normalement être **cachés** et donc **exemptés** du critère 2.2.

**Vérification** :
```html
<!-- Cadre analytics - DOIT être caché -->
<iframe src="analytics.com/track" 
        aria-hidden="true" 
        style="display:none">
</iframe>
```

**Si le cadre de tracking est visible et a un titre** :
- C'est probablement une erreur de développement
- Signaler le problème technique
- Le titre devrait être quelque chose comme "Pixel de suivi analytics" si vraiment nécessaire

**Si le cadre est caché** :
- Il est exempté du test
- Vérifier qu'il a bien `aria-hidden="true"` ou `display:none`

---

#### Q8 : Combien de temps cette vérification prend-elle vraiment ?

**R :** Estimation réaliste :

**Préparation** (première fois) : 10-15 minutes
- Installation NVDA : 5 min
- Configuration navigateur : 3 min
- Lecture du rapport : 5 min

**Par cadre** : 1-2 minutes
- Localiser le cadre : 20 sec
- Observer le contenu : 30 sec
- Tester au lecteur d'écran : 30 sec (optionnel)
- Prendre décision et noter : 20 sec

**Exemple pour 20 cadres** :
- Préparation : 10 min (si déjà fait : 0 min)
- 20 cadres × 1.5 min : 30 min
- Synthèse et rapport : 10 min
- **Total : ~50 minutes**

**Après expérience** : ~30-35 minutes pour 20 cadres

---

#### Q9 : Que faire si le site change après mon audit ?

**R :** Documenter clairement la date et la version.

**Dans votre rapport** :
```markdown
### Portée de la validation

**Date de vérification** : 30 janvier 2026
**Pages vérifiées** : Version en production au 30/01/2026
**Navigateur** : Firefox 122.0
**Lecteur d'écran** : NVDA 2024.1

**Note** : Cette validation concerne l'état du site à la date 
indiquée. Toute modification ultérieure nécessite une re-validation.
```

**Recommandation** : Prévoir un audit de suivi tous les 6-12 mois

---

#### Q10 : Puis-je automatiser partiellement cette vérification ?

**R :** Non, la vérification manuelle est obligatoire selon le RGAA.

**Ce que vous NE POUVEZ PAS faire** :
- ❌ Utiliser un outil IA pour décider de la pertinence
- ❌ Automatiser la décision Conforme/Non conforme
- ❌ Sauter la vérification pour certains cadres

**Ce que vous POUVEZ faire** :
- ✅ Utiliser des outils pour faciliter la navigation (DevTools)
- ✅ Créer des templates/tableaux pour gagner du temps
- ✅ Utiliser le lecteur d'écran en mode semi-automatique (liste des cadres)

**Pourquoi** : Le jugement de pertinence est par nature subjectif et contextuel. Seul un humain peut :
- Comprendre le contenu réel
- Évaluer le contexte de la page
- Se mettre à la place de l'utilisateur

---

## Ressources complémentaires

### Documentation RGAA

- **RGAA 4.1.2 officiel** : https://www.numerique.gouv.fr/publications/rgaa-accessibilite/
- **Critères Section 2** : https://accessibilite.numerique.gouv.fr/methode/criteres-et-tests/#topic2
- **Guide méthodologique** : https://accessibilite.numerique.gouv.fr/methode/

### Outils

- **NVDA** : https://www.nvaccess.org/
- **JAWS** (version d'essai) : https://www.freedomscientific.com/
- **Guide NVDA en français** : https://www.nvda-fr.org/

### Formation

- **Formation RGAA** : https://design.numerique.gouv.fr/formations/
- **Tutoriels NVDA** : https://www.nvda-fr.org/documentation/

---

**Version du guide** : 1.0.0  
**Dernière mise à jour** : Janvier 2026  
**Auteur** : RGAA Section 2 Tester Project