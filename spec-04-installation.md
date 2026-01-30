# Manuel d'installation - RGAA Section 2 Tester

## Table des matières

1. [Prérequis système](#prérequis-système)
2. [Installation de Python](#installation-de-python)
3. [Téléchargement de l'application](#téléchargement-de-lapplication)
4. [Installation des dépendances](#installation-des-dépendances)
5. [Installation du WebDriver](#installation-du-webdriver)
6. [Configuration initiale](#configuration-initiale)
7. [Test de l'installation](#test-de-linstallation)
8. [Résolution des problèmes](#résolution-des-problèmes)
9. [Mise à jour](#mise-à-jour)
10. [Désinstallation](#désinstallation)

---

## Prérequis système

### Configuration minimale requise

- **Système d'exploitation** :
  - Windows 10/11 (64-bit)
  - macOS 10.14 Mojave ou supérieur
  - Linux : Ubuntu 20.04+, Debian 10+, Fedora 35+
  
- **Matériel** :
  - Processeur : 2 GHz ou supérieur
  - RAM : 4 GB minimum (8 GB recommandé)
  - Espace disque : 500 MB libres
  - Résolution d'écran : 1280x720 minimum
  
- **Logiciels** :
  - Python 3.8 ou supérieur
  - Navigateur web : Google Chrome 90+ ou Firefox 88+
  - Connexion Internet (pour installation et audits)

---

## Installation de Python

### Windows

#### Option 1 : Installateur officiel (recommandé)

1. Téléchargez Python depuis : https://www.python.org/downloads/
2. Exécutez l'installateur téléchargé
3. **IMPORTANT** : Cochez "Add Python to PATH"
4. Cliquez sur "Install Now"
5. Attendez la fin de l'installation
6. Vérifiez l'installation :
   ```cmd
   python --version
   ```
   Résultat attendu : `Python 3.10.x` (ou supérieur)

#### Option 2 : Microsoft Store

1. Ouvrez le Microsoft Store
2. Recherchez "Python 3.10" (ou version supérieure)
3. Cliquez sur "Obtenir"
4. Vérifiez l'installation dans PowerShell :
   ```powershell
   python --version
   ```

### macOS

#### Option 1 : Homebrew (recommandé)

1. Installez Homebrew si nécessaire :
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```

2. Installez Python :
   ```bash
   brew install python@3.10
   ```

3. Vérifiez l'installation :
   ```bash
   python3 --version
   ```

#### Option 2 : Installateur officiel

1. Téléchargez depuis : https://www.python.org/downloads/macos/
2. Ouvrez le fichier `.pkg` téléchargé
3. Suivez les instructions d'installation
4. Vérifiez dans Terminal :
   ```bash
   python3 --version
   ```

### Linux

#### Ubuntu/Debian

```bash
# Mise à jour des paquets
sudo apt update

# Installation Python 3.10
sudo apt install python3.10 python3.10-venv python3-pip

# Vérification
python3 --version
```

#### Fedora

```bash
# Installation Python
sudo dnf install python3 python3-pip

# Vérification
python3 --version
```

---

## Téléchargement de l'application

### Option 1 : Git (recommandé)

```bash
# Cloner le dépôt
git clone https://github.com/votre-organisation/rgaa-section2-tester.git

# Accéder au dossier
cd rgaa-section2-tester
```

### Option 2 : Archive ZIP

1. Téléchargez l'archive depuis : [URL_RELEASE]
2. Extrayez le fichier ZIP dans un dossier de votre choix
3. Ouvrez un terminal/invite de commandes dans ce dossier

---

## Installation des dépendances

### Création d'un environnement virtuel (recommandé)

#### Windows

```cmd
# Créer l'environnement virtuel
python -m venv venv

# Activer l'environnement
venv\Scripts\activate

# Vous devriez voir (venv) dans votre prompt
```

#### macOS / Linux

```bash
# Créer l'environnement virtuel
python3 -m venv venv

# Activer l'environnement
source venv/bin/activate

# Vous devriez voir (venv) dans votre prompt
```

### Installation des packages Python

```bash
# Mise à jour de pip
pip install --upgrade pip

# Installation des dépendances
pip install -r requirements.txt
```

**Contenu du fichier `requirements.txt`** :
```
selenium>=4.0.0
beautifulsoup4>=4.11.0
requests>=2.28.0
lxml>=4.9.0
webdriver-manager>=3.8.0
```

---

## Installation du WebDriver

### Option 1 : Installation automatique (recommandé)

L'application utilise `webdriver-manager` qui télécharge automatiquement le WebDriver approprié au premier lancement.

**Aucune action manuelle requise.**

### Option 2 : Installation manuelle de ChromeDriver

Si l'installation automatique échoue :

#### Windows

1. Vérifiez votre version de Chrome :
   - Ouvrez Chrome → Menu (⋮) → Aide → À propos de Google Chrome
   - Notez le numéro de version (ex: 120.0.6099.109)

2. Téléchargez ChromeDriver correspondant :
   - https://chromedriver.chromium.org/downloads
   - Choisissez la version correspondant à votre Chrome

3. Extrayez `chromedriver.exe`

4. Placez-le dans l'un de ces emplacements :
   - Dans le dossier de l'application
   - Dans `C:\Windows\System32\`
   - Ou ajoutez son dossier au PATH

#### macOS

```bash
# Avec Homebrew
brew install --cask chromedriver

# Autoriser l'exécution
xattr -d com.apple.quarantine /usr/local/bin/chromedriver
```

#### Linux

```bash
# Ubuntu/Debian
sudo apt install chromium-chromedriver

# Fedora
sudo dnf install chromium-chromedriver
```

---

## Configuration initiale

### 1. Créer les dossiers nécessaires

```bash
# Créer le dossier pour les rapports
mkdir reports

# Créer le dossier pour les docs de référence
mkdir docs
```

### 2. Ajouter les documents de référence

Placez les documents suivants dans le dossier `docs/` :

- **RGAA_4.1.2_Section2.pdf** - Référentiel technique officiel
- **ISIT-RGAA.pdf** - Modèle de rapport (si disponible)
- **RGAA_glossaire.pdf** - Glossaire (optionnel)

### 3. Configuration de l'application

Le fichier `config.json` est créé automatiquement au premier lancement avec les valeurs par défaut :

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
        "format": "markdown"
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

Vous pouvez modifier ces valeurs selon vos besoins.

---

## Test de l'installation

### 1. Test de Python et dépendances

```bash
# Vérifier Python
python --version  # ou python3 --version

# Vérifier les packages installés
pip list | grep selenium
pip list | grep beautifulsoup4
```

### 2. Lancer l'application

```bash
# Windows
python main.py

# macOS / Linux
python3 main.py
```

**Résultat attendu** : La fenêtre GUI doit s'ouvrir sans erreur.

### 3. Test d'audit basique

1. Dans l'interface, entrez l'URL : `https://www.w3.org/WAI/demos/bad/`
2. Sélectionnez "Tester toute la section 2"
3. Cliquez sur "Lancer l'audit"
4. Vérifiez que :
   - La barre de progression s'affiche
   - Les logs apparaissent
   - Un rapport est généré dans `reports/`

### 4. Vérifier le rapport généré

```bash
# Lister les rapports
ls reports/

# Ouvrir le dernier rapport (adapté selon votre OS)
# Windows
notepad reports\audit_*.md

# macOS
open reports/audit_*.md

# Linux
xdg-open reports/audit_*.md
```

---

## Résolution des problèmes

### Problème 1 : "Python n'est pas reconnu..."

**Symptôme** : `'python' n'est pas reconnu en tant que commande interne...`

**Solution Windows** :
1. Ouvrez "Variables d'environnement système"
2. Dans "Variables système", trouvez "Path"
3. Ajoutez : `C:\Users\VotreNom\AppData\Local\Programs\Python\Python310`
4. Redémarrez le terminal

**Solution macOS/Linux** :
Utilisez `python3` au lieu de `python`

### Problème 2 : Erreur lors de l'installation des packages

**Symptôme** : Erreur lors de `pip install -r requirements.txt`

**Solution** :
```bash
# Mise à jour pip
pip install --upgrade pip setuptools wheel

# Réessayer
pip install -r requirements.txt
```

### Problème 3 : ChromeDriver non compatible

**Symptôme** : `SessionNotCreatedException: Message: session not created: This version of ChromeDriver only supports Chrome version XXX`

**Solution** :
1. Mettez à jour Google Chrome vers la dernière version
2. Supprimez le cache de webdriver-manager :
   ```bash
   # Windows
   rd /s /q %USERPROFILE%\.wdm

   # macOS/Linux
   rm -rf ~/.wdm
   ```
3. Relancez l'application

### Problème 4 : L'interface ne s'affiche pas

**Symptôme** : Erreur `ModuleNotFoundError: No module named 'tkinter'`

**Solution Linux** :
```bash
# Ubuntu/Debian
sudo apt install python3-tk

# Fedora
sudo dnf install python3-tkinter
```

### Problème 5 : Erreur de certificat SSL

**Symptôme** : `SSLError` lors du crawling

**Solution** :
```bash
# Windows
pip install --upgrade certifi

# macOS
/Applications/Python\ 3.10/Install\ Certificates.command
```

### Problème 6 : Permission refusée (macOS)

**Symptôme** : `PermissionError` lors de l'exécution

**Solution** :
```bash
chmod +x main.py
python3 main.py
```

### Problème 7 : Timeout lors du crawling

**Symptôme** : Pages qui ne se chargent pas

**Solution** :
Modifiez `config.json` :
```json
{
    "crawler": {
        "timeout": 60
    }
}
```

---

## Mise à jour de l'application

### Mise à jour depuis Git

```bash
# Sauvegarder votre config personnalisée
cp config.json config.json.bak

# Mettre à jour
git pull origin main

# Restaurer votre config si nécessaire
cp config.json.bak config.json

# Mettre à jour les dépendances
pip install -r requirements.txt --upgrade
```

### Mise à jour manuelle

1. Téléchargez la nouvelle version
2. Sauvegardez votre `config.json` et dossier `reports/`
3. Extrayez la nouvelle version
4. Restaurez `config.json` et `reports/`
5. Mettez à jour les dépendances :
   ```bash
   pip install -r requirements.txt --upgrade
   ```

---

## Désinstallation

### Désinstallation complète

#### Windows

```cmd
# Désactiver l'environnement virtuel (si actif)
deactivate

# Supprimer le dossier de l'application
rd /s /q C:\chemin\vers\rgaa-section2-tester
```

#### macOS / Linux

```bash
# Désactiver l'environnement virtuel (si actif)
deactivate

# Supprimer le dossier de l'application
rm -rf ~/chemin/vers/rgaa-section2-tester
```

### Conservation des rapports

Avant de désinstaller, sauvegardez vos rapports :

```bash
# Créer une archive des rapports
tar -czf rapports_rgaa_backup.tar.gz reports/

# Ou copier dans un autre dossier
cp -r reports/ ~/Documents/Rapports_RGAA/
```

---

## Utilisation en ligne de commande (avancé)

### Lancement direct

```bash
# Windows
python main.py

# macOS/Linux
python3 main.py
```

### Options de ligne de commande (si implémentées)

```bash
# Audit d'une URL sans GUI
python main.py --url https://example.com --headless

# Spécifier profondeur de crawl
python main.py --url https://example.com --depth 3

# Générer rapport dans dossier spécifique
python main.py --url https://example.com --output /chemin/vers/rapport
```

---

## Support et aide

### Documentation

- **README.md** : Guide d'utilisation
- **docs/** : Documentation de référence RGAA
- **specifications/** : Spécifications techniques

### Logs

En cas de problème, consultez :
- **rgaa_tester.log** : Journal de l'application
- Console/Terminal : Messages d'erreur en temps réel

### Signaler un bug

1. Vérifiez que le problème persiste après redémarrage
2. Consultez `rgaa_tester.log`
3. Créez un ticket avec :
   - Description du problème
   - Extrait du log
   - Système d'exploitation et version Python
   - Étapes pour reproduire

---

**Version du manuel** : 1.0.0
**Dernière mise à jour** : Janvier 2026