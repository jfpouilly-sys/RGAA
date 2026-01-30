# RGAA 4.1.2 - Section 2 : Cadres (Frames) - Extrait technique

## Vue d'ensemble

**Thématique** : Cadres (Frames)
**Nombre de critères** : 2
**Niveau** : A (obligatoire)
**Base WCAG** : Critère 4.1.2 Name, Role, Value (Niveau A)

---

## Critère 2.1 : Chaque cadre a-t-il un titre de cadre ?

### Niveau
**A** (obligatoire)

### Éléments concernés
- `<frame>` (déprécié HTML5, mais encore présent sur anciens sites)
- `<iframe>`

### Méthodologie de test

#### Test 2.1.1
**Question** : Chaque élément `<frame>` a-t-il un attribut `title` ?

**Processus de test** :
1. Retrouver dans le document tous les éléments `<frame>`
2. Pour chaque élément `<frame>`, vérifier la présence d'un attribut `title`
3. Si c'est le cas, le test est validé

**Résultat** :
- ✅ **Conforme** : Tous les `<frame>` ont un attribut `title` non vide
- ❌ **Non conforme** : Au moins un `<frame>` n'a pas d'attribut `title` ou a un attribut `title` vide
- ⚪ **Non applicable** : Aucun élément `<frame>` dans la page

#### Test 2.1.2
**Question** : Chaque élément `<iframe>` a-t-il un attribut `title` ?

**Processus de test** :
1. Retrouver dans le document tous les éléments `<iframe>`
2. Pour chaque élément `<iframe>`, vérifier la présence d'un attribut `title`
3. Si c'est le cas, le test est validé

**Résultat** :
- ✅ **Conforme** : Tous les `<iframe>` ont un attribut `title` non vide
- ❌ **Non conforme** : Au moins un `<iframe>` n'a pas d'attribut `title` ou a un attribut `title` vide
- ⚪ **Non applicable** : Aucun élément `<iframe>` dans la page

### Cas particuliers

#### Cadres exemptés (non testés)
Les cadres suivants sont **exemptés** et ne doivent **PAS** être testés :
- Cadres avec `aria-hidden="true"`
- Cadres avec style `display: none` ou `visibility: hidden`
- Cadres avec attribut `hidden`
- Cadres de dimensions nulles (width="0" height="0")

**Important** : Ces cadres sont considérés comme cachés des technologies d'assistance et ne nécessitent pas de titre.

### Techniques WCAG associées

#### Techniques suffisantes :
- **H64** : Utiliser l'attribut `title` des éléments `<frame>` et `<iframe>`
- **ARIA16** : Utiliser `aria-labelledby` pour fournir un nom à des régions de la page
- **ARIA13** : Utiliser `aria-labelledby` pour nommer les régions et les zones

**Note** : Bien que les techniques ARIA soient mentionnées dans WCAG, le RGAA 4.1.2 exige spécifiquement l'attribut `title` pour les critères 2.1.

### Exemples de code

#### ✅ Conforme - avec title
```html
<iframe src="video.html" title="Vidéo de démonstration du produit"></iframe>
```

#### ✅ Conforme - cadre caché (exempté)
```html
<iframe src="tracking.html" style="display:none"></iframe>
<iframe src="analytics.html" aria-hidden="true"></iframe>
```

#### ❌ Non conforme - sans title
```html
<iframe src="content.html"></iframe>
```

#### ❌ Non conforme - title vide
```html
<iframe src="widget.html" title=""></iframe>
```

---

## Critère 2.2 : Pour chaque cadre ayant un titre de cadre, ce titre de cadre est-il pertinent ?

### Niveau
**A** (obligatoire)

### Méthodologie de test

#### Test 2.2.1
**Question** : Pour chaque élément `<frame>` ayant un attribut `title`, le contenu de cet attribut est-il pertinent ?

**Processus de test** :
1. Retrouver dans le document tous les éléments `<frame>` ayant un attribut `title`
2. Pour chaque élément `<frame>`, vérifier que le contenu de l'attribut `title` est pertinent
3. Si c'est le cas, le test est validé

**Vérification manuelle obligatoire** : La pertinence ne peut être évaluée automatiquement.

#### Test 2.2.2
**Question** : Pour chaque élément `<iframe>` ayant un attribut `title`, le contenu de cet attribut est-il pertinent ?

**Processus de test** :
1. Retrouver dans le document tous les éléments `<iframe>` ayant un attribut `title`
2. Pour chaque élément `<iframe>`, vérifier que le contenu de l'attribut `title` est pertinent
3. Si c'est le cas, le test est validé

**Vérification manuelle obligatoire** : La pertinence ne peut être évaluée automatiquement.

### Définition de "pertinent"

Un titre de cadre est **pertinent** s'il permet d'**identifier précisément** :
- Le contenu du cadre
- OU la fonction du cadre

Le titre doit être suffisamment **descriptif** pour qu'un utilisateur de lecteur d'écran puisse :
- Comprendre ce que contient le cadre
- Décider s'il souhaite y accéder
- Distinguer ce cadre des autres cadres de la page

### Indicateurs de non-pertinence (détection automatique)

Un outil automatique peut **signaler** (mais ne peut pas **invalider** automatiquement) les titres suivants comme **suspects** :

#### Titres génériques à signaler
- "frame"
- "iframe"
- "cadre"
- "content"
- "contenu"
- "widget"
- "embed"
- "externe"
- "external"

#### Titres trop courts
- Moins de 3 caractères
- Un seul mot sans contexte (ex: "Vidéo", "Carte", "Menu")

**Note importante** : Ces indicateurs nécessitent une **vérification manuelle**. Un titre comme "Menu" pourrait être acceptable s'il n'y a qu'un seul menu dans la page.

### Exemples de titres

#### ✅ Titres pertinents
```html
<!-- Descriptif et spécifique -->
<iframe src="demo.mp4" title="Vidéo de démonstration du produit X"></iframe>

<!-- Identifie la fonction -->
<iframe src="contact.html" title="Formulaire de contact client"></iframe>

<!-- Contexte clair -->
<iframe src="map.html" title="Carte interactive de nos magasins en France"></iframe>

<!-- Publicité identifiée -->
<iframe src="ad.html" title="Publicité pour notre partenaire TechCorp"></iframe>
```

#### ⚠️ Titres suspects (vérification manuelle requise)
```html
<!-- Générique -->
<iframe src="widget.html" title="Widget"></iframe>

<!-- Trop vague -->
<iframe src="video.mp4" title="Vidéo"></iframe>

<!-- Pas assez descriptif -->
<iframe src="external.html" title="Contenu externe"></iframe>
```

#### ❌ Titres non pertinents
```html
<!-- Juste le type d'élément -->
<iframe src="content.html" title="iframe"></iframe>

<!-- Sans rapport avec le contenu -->
<iframe src="produits.html" title="Section de la page"></iframe>

<!-- Titre technique non descriptif -->
<iframe src="app.html" title="Frame-1"></iframe>
```

---

## Glossaire technique

### Cadre (Frame)
**Définition** : Élément HTML (`<frame>` ou `<iframe>`) permettant d'inclure un document HTML externe dans une page HTML.

**Types** :
- **Frame** : `<frame>` - Élément déprécié depuis HTML5
- **IFrame** : `<iframe>` - Élément standard moderne

### Titre de cadre
**Définition** : Texte fourni via l'attribut `title` d'un élément `<frame>` ou `<iframe>`.

**Fonction** : Permet aux utilisateurs de technologies d'assistance (lecteurs d'écran) d'identifier le contenu du cadre sans avoir à y entrer.

### Cadre décoratif / technique
**Définition** : Cadre qui n'apporte pas d'information à l'utilisateur et qui est utilisé uniquement à des fins techniques (tracking, analytics, pixels de conversion).

**Traitement** : Ces cadres doivent être cachés des technologies d'assistance via :
- `aria-hidden="true"`
- `style="display: none"`
- `style="visibility: hidden"`
- Dimensions nulles : `width="0" height="0"`

---

## Implémentation pour outil automatique

### Algorithme de test - Critère 2.1

```
POUR chaque élément <frame> ou <iframe> dans le DOM :
    SI élément a aria-hidden="true" :
        → Ignorer (exempté)
    SINON SI élément a display:none ou visibility:hidden :
        → Ignorer (exempté)
    SINON SI élément a width="0" ET height="0" :
        → Ignorer (exempté)
    SINON :
        SI élément a attribut title NON VIDE :
            → CONFORME
        SINON :
            → NON CONFORME
        FIN SI
    FIN SI
FIN POUR
```

### Algorithme de flagging - Critère 2.2

```
titres_génériques = ["frame", "iframe", "cadre", "content", "contenu", 
                     "widget", "embed", "externe", "external"]

POUR chaque élément <frame> ou <iframe> avec attribut title :
    titre = valeur de l'attribut title
    titre_lower = titre en minuscules
    
    SI titre_lower dans titres_génériques :
        → SIGNALER : "Titre générique détecté"
    SINON SI longueur(titre) < 3 :
        → SIGNALER : "Titre très court"
    SINON SI titre contient uniquement des chiffres :
        → SIGNALER : "Titre non descriptif"
    SINON :
        → OK (mais vérification manuelle recommandée)
    FIN SI
FIN POUR

IMPORTANT : Tous les cadres avec titre nécessitent une vérification manuelle
```

### Structure de données recommandée

```python
frame_data = {
    'element_type': 'iframe',  # ou 'frame'
    'id': 'video-player',
    'class': 'embed-responsive',
    'src': 'https://example.com/video.mp4',
    
    # Attributs de titre
    'title': 'Vidéo de démonstration',
    'title_length': 24,
    
    # Statut visibilité
    'is_hidden': False,
    'aria_hidden': False,
    'display_none': False,
    'zero_dimensions': False,
    
    # Résultats tests
    'test_2_1_result': 'Conforme',  # Conforme / Non conforme / NA
    'test_2_2_needs_check': True,   # True / False
    'test_2_2_flags': ['Titre court'],  # Liste des signalements
    
    # Contexte
    'page_url': 'https://example.com/page.html',
    'html_code': '<iframe src="..." title="..."></iframe>'
}
```

---

## Calcul du taux de conformité

### Par critère

**Critère 2.1** :
```
Taux = (Nombre de cadres conformes / Nombre total de cadres testés) × 100
```

**Note** : Les cadres exemptés (cachés) ne sont PAS comptés dans le total.

**Critère 2.2** :
```
La conformité du critère 2.2 nécessite une validation manuelle.
L'outil peut uniquement signaler les titres suspects.
```

### Global Section 2

```
SI tous les cadres sont conformes au critère 2.1 
   ET aucun problème de pertinence identifié manuellement (2.2) :
   → Section 2 CONFORME

SI au moins un cadre non conforme au critère 2.1 
   OU problème de pertinence confirmé (2.2) :
   → Section 2 NON CONFORME

SI aucun cadre présent (hors cadres exemptés) :
   → Section 2 NON APPLICABLE
```

---

## Recommandations de correction

### Pour critère 2.1 - Cadre sans titre

**Problème** : `<iframe src="video.html"></iframe>`

**Solution** :
```html
<iframe src="video.html" title="Vidéo explicative du processus d'inscription"></iframe>
```

**Explication** : Ajouter un attribut `title` descriptif du contenu ou de la fonction.

### Pour critère 2.2 - Titre générique

**Problème** : `<iframe src="content.html" title="iframe"></iframe>`

**Solution** :
```html
<iframe src="content.html" title="Actualités et événements de l'entreprise"></iframe>
```

**Explication** : Remplacer le titre générique par une description précise du contenu.

---

## Priorités de correction

### P1 - Critique (blocage utilisateur)
- Cadres visibles sans aucun titre
- Cadres avec titre vide

### P2 - Important (expérience dégradée)
- Titres génériques ("frame", "iframe", "widget")
- Titres très courts sans contexte

### P3 - Amélioration (optimisation)
- Titres corrects mais pouvant être plus descriptifs
- Harmonisation des titres sur le site

---

**Version** : RGAA 4.1.2 (16 septembre 2019)
**Source** : https://accessibilite.numerique.gouv.fr/methode/criteres-et-tests/#topic2