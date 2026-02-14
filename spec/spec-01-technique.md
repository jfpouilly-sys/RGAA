# Spécifications techniques - RGAA Section 2 Tester

## Stack technique

### Langage et version
- **Python** : 3.8 minimum (recommandé : 3.10+)
- **Encodage** : UTF-8 pour tous les fichiers

### Frameworks et bibliothèques principales

#### Interface graphique
- **tkinter** : Interface graphique (bibliothèque standard Python)
- Widgets requis : Frame, Label, Entry, Button, Checkbutton, Progressbar, Text, Scrollbar

#### Web scraping et automatisation
- **Selenium** : 4.x avec ChromeDriver (ou geckodriver pour Firefox)
  - Alternative acceptable : Playwright
- **BeautifulSoup4** : Parsing HTML
- **requests** : Requêtes HTTP basiques

#### Génération de rapports
- **Markdown** : Format natif des rapports
- **datetime** : Timestamps et dates
- **platform** : Détection OS et environnement

#### Configuration et données
- **json** : Gestion configuration persistante
- **logging** : Journalisation des opérations

### Dépendances complètes (requirements.txt)

```txt
selenium>=4.0.0
beautifulsoup4>=4.11.0
requests>=2.28.0
lxml>=4.9.0
webdriver-manager>=3.8.0
```

## Architecture de l'application

### Structure modulaire

```
rgaa_tester/
├── __init__.py              # Package initialization
├── gui.py                   # Interface graphique tkinter
├── crawler.py               # Exploration de sites web
├── analyzer.py              # Tests RGAA Section 2
├── report_generator.py      # Génération rapports Markdown
├── config.py                # Gestion configuration
└── utils.py                 # Fonctions utilitaires
```

### Responsabilités des modules

#### `gui.py` - Interface graphique
**Classe principale** : `RGAAApp`

Méthodes clés :
- `__init__()` : Initialisation fenêtre et widgets
- `create_widgets()` : Création interface
- `browse_url_file()` : Sélection fichier URLs
- `browse_report_dir()` : Sélection dossier rapports
- `start_audit()` : Lancement audit
- `update_progress(percentage, message)` : Mise à jour progression
- `log_message(message, level)` : Affichage logs
- `open_report()` : Ouverture rapport généré

#### `crawler.py` - Exploration web
**Classe principale** : `WebCrawler`

Méthodes clés :
- `__init__(url, max_depth=2)` : Initialisation crawler
- `crawl()` : Exploration site
- `get_all_pages()` : Récupération liste pages
- `fetch_page(url)` : Récupération contenu page
- `extract_links(html, base_url)` : Extraction liens
- `respect_robots_txt(url)` : Vérification robots.txt

#### `analyzer.py` - Tests RGAA
**Classe principale** : `RGAASection2Analyzer`

Méthodes clés :
- `analyze_page(url, html)` : Analyse page complète
- `detect_frames(soup)` : Détection frames et iframes
- `test_criterion_2_1(frame)` : Test présence titre
- `test_criterion_2_2(frame)` : Flagging pertinence titre
- `check_frame_title(frame)` : Vérification attributs titre
- `is_frame_hidden(frame)` : Détection frames cachées
- `detect_generic_title(title)` : Détection titres génériques
- `calculate_compliance()` : Calcul taux conformité

**Structure de données - Frame** :
```python
{
    'element': 'iframe',  # ou 'frame'
    'id': 'video-player',
    'class': 'embed-responsive',
    'src': 'https://...',
    'title': 'Vidéo de démonstration',
    'aria_label': None,
    'aria_labelledby': None,
    'is_hidden': False,
    'test_2_1': 'Conforme',  # Conforme / Non conforme / NA
    'test_2_2': 'À vérifier',  # À vérifier / OK / Suspect
    'issues': [],
    'recommendations': []
}
```

#### `report_generator.py` - Génération rapports
**Classe principale** : `ReportGenerator`

Méthodes clés :
- `__init__(audit_data)` : Initialisation avec données audit
- `generate_markdown()` : Génération rapport complet
- `generate_summary_table()` : Tableau synthèse
- `generate_criterion_details(criterion_number)` : Détails critère
- `generate_page_results(page_data)` : Résultats par page
- `generate_recommendations()` : Recommandations prioritaires
- `generate_remediation_plan()` : Plan de remédiation
- `save_report(filepath)` : Sauvegarde fichier

#### `config.py` - Gestion configuration
**Classe principale** : `ConfigManager`

Méthodes clés :
- `load_config()` : Chargement configuration
- `save_config()` : Sauvegarde configuration
- `get(key, default=None)` : Récupération valeur
- `set(key, value)` : Modification valeur

**Structure config.json** :
```json
{
    "app_version": "1.0.0",
    "crawler": {
        "max_depth": 2,
        "timeout": 30,
        "user_agent": "RGAA-Tester/1.0",
        "respect_robots_txt": true
    },
    "tests": {
        "test_2_1": true,
        "test_2_2": true
    },
    "report": {
        "output_dir": "./reports",
        "format": "markdown",
        "include_screenshots": false
    },
    "gui": {
        "window_width": 800,
        "window_height": 600,
        "theme": "default"
    },
    "generic_titles": [
        "frame",
        "iframe",
        "content",
        "widget",
        "embed"
    ]
}
```

#### `utils.py` - Utilitaires
Fonctions utilitaires :
- `validate_url(url)` : Validation URL
- `sanitize_filename(name)` : Nettoyage nom fichier
- `get_timestamp()` : Génération timestamp
- `get_system_info()` : Info système et navigateur
- `format_date(date)` : Formatage date français
- `extract_domain(url)` : Extraction nom de domaine

## Gestion des erreurs

### Exceptions personnalisées

```python
class RGAATestError(Exception):
    """Exception de base pour les erreurs de test RGAA"""
    pass

class CrawlerError(RGAATestError):
    """Erreur lors du crawling"""
    pass

class AnalyzerError(RGAATestError):
    """Erreur lors de l'analyse"""
    pass

class ReportError(RGAATestError):
    """Erreur lors de la génération de rapport"""
    pass
```

### Gestion des erreurs réseau

- **Timeout** : 30 secondes par défaut
- **Retry** : 3 tentatives maximum
- **404/500** : Ignorer et logger, continuer avec les autres pages
- **DNS errors** : Logger et arrêter le crawling pour ce domaine

## Logging

### Configuration logging

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('rgaa_tester.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
```

### Niveaux de log

- **DEBUG** : Détails techniques (détection chaque frame)
- **INFO** : Progression normale (page analysée, rapport généré)
- **WARNING** : Problèmes non-bloquants (timeout, 404)
- **ERROR** : Erreurs bloquantes (crash parser, écriture rapport)
- **CRITICAL** : Erreurs critiques (WebDriver indisponible)

## Performance et optimisation

### Contraintes de performance

- **Crawling** : Maximum 5 pages/seconde (respect serveurs)
- **GUI** : Mise à jour progression toutes les 2 secondes minimum
- **Mémoire** : Libérer BeautifulSoup objects après analyse
- **Cache** : Pas de cache entre sessions (toujours analyser frais)

### Multi-threading

- Thread séparé pour le crawling/analyse (ne pas bloquer GUI)
- Thread principal pour tkinter (obligatoire)
- Queue pour communication entre threads

```python
from queue import Queue
from threading import Thread

def run_audit_thread(url, config, progress_queue):
    # Code d'audit dans thread séparé
    # Envoie progression via progress_queue
    pass
```

## Compatibilité

### Systèmes d'exploitation
- **Windows** : 10/11 (64-bit)
- **macOS** : 10.14+ (Mojave ou supérieur)
- **Linux** : Ubuntu 20.04+, Debian 10+, Fedora 35+

### Navigateurs supportés
- **Chrome/Chromium** : 90+ (recommandé)
- **Firefox** : 88+ (alternatif)

### Résolution d'écran minimale
- **1280x720** pixels minimum pour GUI

---

**Notes d'implémentation** :
- Utiliser `webdriver-manager` pour gestion automatique ChromeDriver
- Tous les chemins doivent être compatibles Windows/macOS/Linux (utiliser `pathlib`)
- Encoder tous les fichiers en UTF-8
- Préfixer les f-strings pour Python 3.8+ uniquement