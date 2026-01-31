# Guide rapide de vérification manuelle - Critère 2.2

**⏱️ Temps de lecture : 3 minutes | Temps d'application : ~1-2 min/cadre**

---

## 🎯 Votre mission

Vérifier que chaque titre de cadre décrit **précisément** son contenu ou sa fonction.

## 🚀 Démarrage rapide (5 étapes)

### 1️⃣ Installer NVDA (lecteur d'écran gratuit)
```
→ https://www.nvaccess.org/download/
→ 5 minutes d'installation
→ Choisir la voix française
```

### 2️⃣ Ouvrir la page à vérifier
```
→ Copier l'URL depuis le rapport
→ Ouvrir dans Firefox
→ Laisser charger complètement
```

### 3️⃣ Naviguer vers le cadre
```
→ Appuyer sur D (passer au cadre suivant)
→ NVDA annonce : "Cadre - [titre du cadre]"
→ Ou : Insert+F7 → choisir "Frames"
```

### 4️⃣ Poser la question clé
```
L'annonce de NVDA est-elle claire et précise ?
→ OUI = ✅ Pertinent
→ NON = ❌ Non pertinent
```

### 5️⃣ Noter votre décision
```
→ Remplir le tableau de validation
→ Proposer un meilleur titre si nécessaire
```

---

## ✅ Titre PERTINENT si...

- ✅ Décrit précisément le contenu ("Vidéo de démonstration produit X")
- ✅ Indique clairement la fonction ("Formulaire de contact client")
- ✅ Permet de distinguer si plusieurs cadres similaires
- ✅ Un utilisateur aveugle comprend de quoi il s'agit

## ❌ Titre NON PERTINENT si...

- ❌ Générique : "widget", "frame", "iframe", "content"
- ❌ Trop vague : "Vidéo" (alors qu'il y en a 5)
- ❌ Ne correspond pas au contenu réel
- ❌ Trop court : "Pub", "Map", "Vid"

---

## 🔍 Tests rapides

### Test 1 : L'annonce NVDA
**Question** : Si j'étais aveugle, je comprendrais quoi ?

```
✅ "Cadre - Formulaire de contact" → CLAIR
❌ "Cadre - widget" → CONFUS
```

### Test 2 : Le contexte
**Question** : Y a-t-il d'autres cadres similaires ?

```
1 seule vidéo → "Vidéo" peut suffire ⚠️
5 vidéos → "Vidéo" est insuffisant ❌
```

### Test 3 : Le contenu
**Question** : Le titre correspond-il au contenu ?

```
Titre : "Carte" | Contenu : Google Maps → ✅
Titre : "widget" | Contenu : Filtre de recherche → ❌
```

---

## 📋 Décision rapide (30 secondes)

```
┌─────────────────────────────────────────┐
│ Le titre décrit-il le contenu ?        │
│                                         │
│ OUI, précisément → ✅ PERTINENT        │
│                                         │
│ OUI mais vague + plusieurs cadres      │
│                  → ❌ NON PERTINENT     │
│                                         │
│ Générique (frame/widget/content)       │
│                  → ❌ NON PERTINENT     │
│                                         │
│ NON / Partiellement                     │
│                  → ❌ NON PERTINENT     │
└─────────────────────────────────────────┘
```

---

## 💡 Exemples express

| Titre actuel | Contenu | Décision | Titre proposé |
|--------------|---------|----------|---------------|
| "widget" | Filtre de prix | ❌ | "Filtres de recherche par prix" |
| "Vidéo" | 1 seule vidéo | ⚠️ | "Vidéo de démonstration" (amélioration) |
| "Vidéo" | 5 vidéos | ❌ | "Vidéo - Tutoriel installation" |
| "iframe" | Publicité | ❌ | "Publicité partenaire X" |
| "Formulaire de contact" | Formulaire | ✅ | - |
| "Carte interactive magasins" | Google Maps | ✅ | - |

---

## 🎓 Commandes NVDA essentielles

| Action | Touche | Effet |
|--------|--------|-------|
| Cadre suivant | `D` | Passe au cadre suivant |
| Cadre précédent | `Shift+D` | Retour au cadre précédent |
| Liste des cadres | `Insert+F7` | Affiche tous les cadres |
| Arrêter la voix | `Insert+S` | Toggle parole on/off |
| Quitter NVDA | `Insert+Q` | Ferme NVDA |

**Note** : `Insert` = touche `Insertion` (au-dessus des flèches)

---

## 📝 Tableau de validation (template)

```markdown
### Page : [Nom]
URL : [URL complète]

| # | Titre actuel | Pertinent ? | Titre proposé | Priorité |
|---|--------------|-------------|---------------|----------|
| 1 | Vidéo démo   | ✅          | -             | -        |
| 2 | widget       | ❌          | Filtre prix   | P1       |
| 3 | Carte        | ⚠️          | Carte magasins| P2       |

Résultat : 1/3 conformes (33%)
```

**Priorités** :
- **P1** : Critique (titres génériques, absents)
- **P2** : Important (titres vagues, courts)
- **P3** : Amélioration (optimisation)

---

## 🚨 Pièges fréquents

### Piège 1 : "Le titre semble OK visuellement"
❌ **Erreur** : Juger sans lecteur d'écran
✅ **Correct** : Toujours tester avec NVDA

### Piège 2 : "Un seul mot suffit"
❌ "Vidéo", "Carte", "Menu" → Souvent trop vague
✅ Ajouter du contexte : "Vidéo de démonstration"

### Piège 3 : "C'est technique, ça ne compte pas"
❌ Les cadres de tracking visibles doivent avoir un titre
✅ Ou être cachés (`display:none`, `aria-hidden="true"`)

### Piège 4 : "Ça prend trop de temps"
❌ Sauter des cadres
✅ Tous les cadres avec titre doivent être vérifiés (RGAA obligatoire)

---

## ⏱️ Gain de temps

### Sans outil automatique
- Trouver tous les cadres manuellement : **2h**
- Vérifier la pertinence : **1h**
- Rédiger le rapport : **1h**
- **Total : 4h pour 50 pages**

### Avec outil automatique
- L'outil trouve tout : **10 min**
- Vous vérifiez seulement la pertinence : **30 min**
- Rapport généré automatiquement : **0 min**
- **Total : 40 min pour 50 pages**

**➡️ Vous économisez 80% du temps !**

---

## 📚 Ressources

### Documentation complète
**→ `GUIDE_VERIFICATION_MANUELLE_Critere_2.2.md`**
- 50 pages de détails
- Cas pratiques complets
- FAQ de 10 questions

### Outils
- **NVDA** : https://www.nvaccess.org/
- **RGAA 4.1.2** : https://accessibilite.numerique.gouv.fr/

### Support
- **Questions** : Consulter la FAQ du guide complet
- **Formation NVDA** : https://www.nvda-fr.org/

---

## ✔️ Checklist finale

Avant de valider votre audit :

- [ ] J'ai vérifié **TOUS** les cadres avec titre (pas seulement les suspects)
- [ ] J'ai testé au moins 30% des cadres avec NVDA
- [ ] J'ai rempli le tableau de validation
- [ ] J'ai proposé des corrections pour les titres non pertinents
- [ ] J'ai estimé les priorités (P1/P2/P3)
- [ ] J'ai documenté ma méthodologie
- [ ] J'ai indiqué la date de vérification

---

**🎯 Résultat attendu** : Un audit complet et conforme au RGAA 4.1.2, avec validation humaine du critère 2.2.

**⏱️ Temps total estimé** : ~1-2 minutes par cadre + 15 min de synthèse

**📞 Besoin d'aide ?** Consultez le guide complet dans `docs/GUIDE_VERIFICATION_MANUELLE_Critere_2.2.md`

---

**Version** : 1.0.0 | **Dernière mise à jour** : Janvier 2026