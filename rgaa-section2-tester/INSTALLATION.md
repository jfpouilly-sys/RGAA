# Guide d'Installation - RGAA Section 2 Tester

Ce guide détaille les étapes d'installation de l'application RGAA Section 2 Tester sur différents systèmes d'exploitation.

## Prérequis

### Python

- **Version requise** : Python 3.8 ou supérieur
- **Vérification** : `python --version` ou `python3 --version`

### tkinter (pour l'interface graphique)

tkinter est généralement inclus avec Python, mais peut nécessiter une installation séparée sur certains systèmes.

## Installation par système d'exploitation

### Linux (Ubuntu/Debian)

```bash
# 1. Installer Python et tkinter si nécessaire
sudo apt update
sudo apt install python3 python3-pip python3-tk python3-venv

# 2. Cloner le projet
git clone <repo-url>
cd rgaa-section2-tester

# 3. Créer un environnement virtuel
python3 -m venv venv
source venv/bin/activate

# 4. Installer les dépendances
pip install -r requirements.txt

# 5. Lancer l'application
python main.py
```

### Linux (Fedora/RHEL)

```bash
# 1. Installer Python et tkinter
sudo dnf install python3 python3-pip python3-tkinter

# 2. Suivre les étapes 2-5 ci-dessus
```

### macOS

```bash
# 1. Installer Python (si nécessaire, via Homebrew)
brew install python python-tk

# 2. Cloner le projet
git clone <repo-url>
cd rgaa-section2-tester

# 3. Créer un environnement virtuel
python3 -m venv venv
source venv/bin/activate

# 4. Installer les dépendances
pip install -r requirements.txt

# 5. Lancer l'application
python main.py
```

### Windows

```powershell
# 1. Télécharger Python depuis https://www.python.org/downloads/
#    Cocher "Add Python to PATH" lors de l'installation

# 2. Ouvrir PowerShell ou CMD

# 3. Cloner le projet (ou télécharger le ZIP)
git clone <repo-url>
cd rgaa-section2-tester

# 4. Créer un environnement virtuel
python -m venv venv
venv\Scripts\activate

# 5. Installer les dépendances
pip install -r requirements.txt

# 6. Lancer l'application
python main.py
```

## Vérification de l'installation

### Test rapide

```bash
# Vérifier que l'import fonctionne
python -c "from rgaa_tester import analyzer; print('OK')"

# Afficher la version
python main.py --version
```

### Test de l'interface graphique

```bash
# Lancer l'interface
python main.py

# Si une erreur tkinter apparaît, installer tkinter selon votre OS
```

### Test en mode CLI

```bash
# Tester sur une URL
python main.py --cli https://www.google.fr

# Le rapport devrait être généré dans le dossier reports/
```

## Dépendances

Le fichier `requirements.txt` contient les dépendances suivantes :

| Package | Version | Description |
|---------|---------|-------------|
| beautifulsoup4 | >= 4.12.0 | Parsing HTML |
| lxml | >= 4.9.0 | Parser HTML performant |
| requests | >= 2.31.0 | Requêtes HTTP |
| urllib3 | >= 2.0.0 | Utilitaires URL |

### Installation manuelle des dépendances

```bash
pip install beautifulsoup4>=4.12.0
pip install lxml>=4.9.0
pip install requests>=2.31.0
pip install urllib3>=2.0.0
```

## Configuration initiale

### Fichier config.json

Un fichier `config.json` par défaut est fourni. Vous pouvez le modifier selon vos besoins :

```json
{
    "crawler": {
        "max_pages": 50,
        "timeout": 30,
        "user_agent": "RGAA-Tester/1.0 (Accessibility Checker)",
        "delai_entre_requetes": 1.0
    },
    "analyse": {
        "longueur_titre_minimum": 3,
        "detecter_titres_generiques": true
    },
    "rapport": {
        "dossier_sortie": "reports",
        "inclure_code_html": true
    }
}
```

### Dossier des rapports

Créer le dossier des rapports si nécessaire :

```bash
mkdir -p reports
```

## Résolution des problèmes courants

### Erreur : "No module named 'tkinter'"

**Solution Linux :**
```bash
sudo apt install python3-tk  # Debian/Ubuntu
sudo dnf install python3-tkinter  # Fedora
```

**Solution macOS :**
```bash
brew install python-tk
```

### Erreur : "ModuleNotFoundError: No module named 'lxml'"

```bash
pip install lxml

# Si erreur de compilation sur Linux :
sudo apt install libxml2-dev libxslt-dev python3-dev
pip install lxml
```

### Erreur SSL/Certificat

```bash
# Mettre à jour les certificats
pip install --upgrade certifi
```

### L'interface graphique ne s'affiche pas (serveur distant)

L'interface graphique nécessite un environnement de bureau. Sur un serveur distant, utilisez le mode CLI :

```bash
python main.py --cli https://exemple.fr
```

Ou configurez X11 forwarding :
```bash
ssh -X user@serveur
python main.py
```

## Mise à jour

```bash
# Mettre à jour les dépendances
pip install --upgrade -r requirements.txt

# Mettre à jour le projet (si git)
git pull origin main
```

## Désinstallation

```bash
# Supprimer l'environnement virtuel
deactivate
rm -rf venv

# Supprimer le dossier du projet
cd ..
rm -rf rgaa-section2-tester
```

## Support

En cas de problème :

1. Vérifier les prérequis (Python 3.8+, tkinter)
2. Consulter les logs d'erreur
3. Vérifier la connectivité réseau pour les tests

## Ressources

- [Documentation Python](https://docs.python.org/3/)
- [RGAA 4.1.2](https://www.numerique.gouv.fr/publications/rgaa-accessibilite/)
- [BeautifulSoup Documentation](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
