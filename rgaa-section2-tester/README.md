# RGAA Section 2 Tester

Application Python de test de conformité RGAA 4.1.2 Section 2 (Cadres/Frames) avec interface graphique et génération de rapports Markdown.

## Fonctionnalités

- **Test automatisé du Critère 2.1** : Détection des cadres sans attribut `title`
- **Signalement pour le Critère 2.2** : Identification des titres potentiellement non pertinents
- **Interface graphique** : Application tkinter conviviale
- **Mode ligne de commande** : Pour l'intégration dans des pipelines CI/CD
- **Crawler multi-pages** : Analyse de sites complets
- **Rapports Markdown détaillés** : Format compatible ISIT-RGAA

## Critères RGAA testés

### Critère 2.1 : Chaque cadre a-t-il un titre de cadre ?

- Test 2.1.1 : Vérification des éléments `<frame>` (attribut `title`)
- Test 2.1.2 : Vérification des éléments `<iframe>` (attribut `title`)

### Critère 2.2 : Le titre de cadre est-il pertinent ?

- Test 2.2.1 : Pertinence des titres `<frame>` (signalement automatique)
- Test 2.2.2 : Pertinence des titres `<iframe>` (signalement automatique)

## Installation

Voir [INSTALLATION.md](INSTALLATION.md) pour les instructions détaillées.

### Installation rapide

```bash
# Cloner le projet
git clone <repo-url>
cd rgaa-section2-tester

# Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou: venv\Scripts\activate  # Windows

# Installer les dépendances
pip install -r requirements.txt
```

## Utilisation

### Mode graphique (par défaut)

```bash
python main.py
```

L'interface graphique permet de :
1. Saisir l'URL à analyser
2. Choisir entre analyse de page unique ou crawler multi-pages
3. Lancer l'analyse et suivre la progression
4. Consulter les résultats en temps réel
5. Générer un rapport Markdown détaillé

### Mode ligne de commande

```bash
# Analyse d'une page unique
python main.py --cli https://exemple.fr

# Crawler multi-pages
python main.py --cli https://exemple.fr --max-pages 20

# Spécifier le fichier de sortie
python main.py --cli https://exemple.fr --output rapport.md
```

### Options disponibles

| Option | Description |
|--------|-------------|
| `--cli URL` | Mode ligne de commande avec l'URL spécifiée |
| `--max-pages N` | Nombre maximum de pages à crawler (défaut: 1) |
| `--output FILE` | Chemin du fichier de rapport |
| `--version` | Affiche la version |
| `--help` | Affiche l'aide |

## Configuration

Le fichier `config.json` permet de personnaliser :

- Paramètres du crawler (timeout, délai, user-agent)
- Titres génériques à détecter
- Options de rapport
- Paramètres d'interface

Exemple de configuration :

```json
{
    "crawler": {
        "max_pages": 50,
        "timeout": 30,
        "delai_entre_requetes": 1.0
    },
    "titres_generiques": [
        "frame", "iframe", "widget", "contenu"
    ],
    "rapport": {
        "dossier_sortie": "reports",
        "inclure_code_html": true
    }
}
```

## Structure du projet

```
rgaa-section2-tester/
├── main.py                    # Point d'entrée
├── requirements.txt           # Dépendances
├── config.json               # Configuration
├── README.md                 # Documentation
├── INSTALLATION.md           # Guide d'installation
├── rgaa_tester/              # Package principal
│   ├── __init__.py
│   ├── config.py             # Gestion de la configuration
│   ├── utils.py              # Fonctions utilitaires
│   ├── analyzer.py           # Analyseur RGAA
│   ├── crawler.py            # Crawler web
│   ├── report_generator.py   # Générateur de rapports
│   └── gui.py                # Interface graphique
└── reports/                  # Rapports générés
```

## Rapports générés

Les rapports Markdown incluent :

1. **Résumé exécutif** : Statut global et chiffres clés
2. **Synthèse de conformité** : Résultats par critère
3. **Détail du Critère 2.1** : Liste des cadres non conformes
4. **Détail du Critère 2.2** : Cadres à vérifier manuellement
5. **Détail par page** : Tableau récapitulatif
6. **Recommandations** : Actions correctives par priorité
7. **Annexes** : Méthodologie et références

## Référentiel

Ce projet implémente les tests de la **Section 2 - Cadres (Frames)** du RGAA 4.1.2 :

- [RGAA 4.1.2 officiel](https://www.numerique.gouv.fr/publications/rgaa-accessibilite/)
- [Critères Section 2](https://accessibilite.numerique.gouv.fr/methode/criteres-et-tests/#topic2)

## Licence

MIT License
