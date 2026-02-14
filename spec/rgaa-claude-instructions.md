# RGAA 4.1.2 Section 2 Tester - Spécifications Projet

## Vue d'ensemble

Application Python avec interface graphique pour tester la conformité RGAA 4.1.2 Section 2 (Cadres/Frames) et générer des rapports Markdown exhaustifs.

## Structure de la documentation

Ce projet est documenté à travers plusieurs fichiers de spécifications :

### 📋 Fichiers de spécifications

1. **`01_SPECIFICATIONS_TECHNIQUES.md`** - Stack technique et architecture
2. **`02_SPECIFICATIONS_GUI.md`** - Interface utilisateur et fonctionnalités
3. **`03_FORMAT_RAPPORT.md`** - Structure complète du rapport Markdown
4. **`04_INSTALLATION.md`** - Guide d'installation détaillé
5. **`05_TESTS_QUALITE.md`** - Critères de qualité et validation

### 📚 Documents de référence à fournir

Placez ces documents dans le dossier `docs/` :

- **`RGAA_Section2_Extract.md`** - Extrait condensé Section 2 (CRITIQUE - FOURNI)
- **`ISIT-RGAA.pdf`** - Modèle de rapport de référence (IMPORTANT)

**Note importante** : Le fichier `RGAA_Section2_Extract.md` est un extrait condensé spécifiquement créé pour Claude Code, contenant UNIQUEMENT les informations nécessaires de la Section 2 du RGAA 4.1.2 (critères, tests, exemples, algorithmes). Ne fournissez PAS le RGAA complet qui est trop volumineux.

## Objectifs du projet

### Critères RGAA à implémenter

**Section 2 - Cadres (Frames) - RGAA 4.1.2 :**

- **Critère 2.1** : Chaque cadre a-t-il un titre de cadre ?
  - Test automatisé (détection + validation)
  - Vérification de `title`, `aria-label`, `aria-labelledby`
  
- **Critère 2.2** : Pour chaque cadre ayant un titre de cadre, ce titre de cadre est-il pertinent ?
  - Flagging pour vérification manuelle
  - Détection de titres génériques ou suspects

## Priorités de développement

### Phase 1 - MVP (Minimum Viable Product)
1. Détection de base des frames (iframe, frame)
2. Tests automatisés Critère 2.1
3. GUI minimale (URL + bouton lancer)
4. Rapport Markdown basique

### Phase 2 - Fonctionnalités complètes
5. Crawler multi-pages
6. Tests Critère 2.2 avec flagging
7. GUI complète avec progression
8. Rapport format ISIT complet

### Phase 3 - Finitions
9. Configuration persistante
10. Logs détaillés
11. Documentation d'installation
12. Tests et validation

## Démarrage rapide pour Claude Code

### Étape 1 : Lire les spécifications
Consultez les fichiers dans l'ordre :
```
01_SPECIFICATIONS_TECHNIQUES.md  → Architecture et stack
02_SPECIFICATIONS_GUI.md          → Interface utilisateur
03_FORMAT_RAPPORT.md              → Format du rapport
04_INSTALLATION.md                → Guide d'installation
05_TESTS_QUALITE.md               → Critères de validation
06_IMPLEMENTATION_COUVERTURE_RAPPORT.md → Implémentation couverture/limites
```

### Étape 2 : Consulter les références
Lisez attentivement :
- `specifications/RGAA_Section2_Extract.md` pour la méthodologie RGAA exacte
- `docs/ISIT-RGAA.pdf` pour le format de rapport à reproduire (si disponible)

### Étape 3 : Implémenter

Suivez les priorités de développement ci-dessus.

**⚠️ ATTENTION PARTICULIÈRE** : Le fichier **`06_IMPLEMENTATION_COUVERTURE_RAPPORT.md`** contient des instructions CRITIQUES pour implémenter :
- Les sections de couverture de l'audit (98-100% pour 2.1, 30-40% pour 2.2)
- Les avertissements sur les limites de l'automatisation
- Les mentions légales sur la responsabilité
- Le calcul des métriques et du temps de vérification manuelle

**Ces sections sont OBLIGATOIRES dans chaque rapport** pour la transparence et la conformité légale.

## Structure du projet attendue

```
rgaa-section2-tester/
├── docs/                           # Documentation de référence
│   ├── RGAA_Section2_Extract.md    # Extrait RGAA Section 2 (FOURNI)
│   ├── ISIT-RGAA.pdf               # Modèle de rapport
│   └── GUIDE_VERIFICATION_MANUELLE_Critere_2.2.md  # Guide pour auditeurs
├── specifications/                 # Spécifications techniques
│   ├── 01_SPECIFICATIONS_TECHNIQUES.md
│   ├── 02_SPECIFICATIONS_GUI.md
│   ├── 03_FORMAT_RAPPORT.md
│   ├── 04_INSTALLATION.md
│   ├── 05_TESTS_QUALITE.md
│   ├── 06_IMPLEMENTATION_COUVERTURE_RAPPORT.md
│   ├── RGAA_Section2_Extract.md    # Aussi ici pour référence
│   └── Exemple_Rapport_Avec_Couverture.md
├── main.py                         # Point d'entrée
├── rgaa_tester/                    # Package principal
│   ├── __init__.py
│   ├── gui.py
│   ├── crawler.py
│   ├── analyzer.py
│   ├── report_generator.py
│   ├── config.py
│   └── utils.py
├── requirements.txt
├── config.json
├── README.md
└── reports/                        # Rapports générés
```

## Livrables attendus

- [ ] Application Python complète et fonctionnelle
- [ ] Interface GUI avec tkinter
- [ ] Générateur de rapports Markdown (format ISIT)
- [ ] **Rapports incluant section "Couverture de l'audit" et "Limites"**
- [ ] `requirements.txt`
- [ ] `INSTALLATION.md` complet
- [ ] `README.md` avec guide d'utilisation
- [ ] Configuration par défaut (`config.json`)
- [ ] Exemples de rapports
- [ ] Code commenté en français

## Notes importantes

- **Langue** : Tout le code, commentaires, UI et rapports en FRANÇAIS
- **Standard** : Suivre strictement RGAA 4.1.2
- **Format rapport** : Reproduire exactement le format ISIT-RGAA.pdf
- **Qualité** : Privilégier la précision sur la vitesse
- **Conformité** : Tests doivent être conformes au référentiel officiel

## Ressources externes

- RGAA 4.1.2 officiel : https://www.numerique.gouv.fr/publications/rgaa-accessibilite/
- Critères Section 2 : https://accessibilite.numerique.gouv.fr/methode/criteres-et-tests/#topic2
- WCAG 2.1 Frames : https://www.w3.org/WAI/WCAG21/Understanding/

---

**Pour commencer** : Lisez `01_SPECIFICATIONS_TECHNIQUES.md` puis les autres fichiers dans l'ordre numérique.