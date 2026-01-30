# Spécifications GUI - RGAA Section 2 Tester

## Vue d'ensemble de l'interface

Application desktop avec interface graphique tkinter en français.

### Dimensions fenêtre
- **Largeur** : 900 pixels
- **Hauteur** : 700 pixels
- **Redimensionnable** : Oui
- **Taille minimale** : 800x600

## Layout principal

```
┌─────────────────────────────────────────────────────────────────┐
│  RGAA 4.1.2 - Vérification d'accessibilité Section 2 (Cadres)  │ ← Titre
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─── Configuration de l'audit ───────────────────────────┐    │
│  │                                                          │    │
│  │  URL du site:  [________________________________] [📁]  │    │
│  │                                                          │    │
│  │  ○ URL unique    ○ Fichier d'URLs (sitemap/liste)      │    │
│  │                                                          │    │
│  └──────────────────────────────────────────────────────────┘    │
│                                                                 │
│  ┌─── Tests à effectuer ──────────────────────────────────┐    │
│  │                                                          │    │
│  │  ☑ Tester toute la section 2 (recommandé)              │    │
│  │  ☐ Critère 2.1 uniquement (Présence titre cadre)       │    │
│  │  ☐ Critère 2.2 uniquement (Pertinence titre cadre)     │    │
│  │                                                          │    │
│  │  Profondeur d'exploration: [2▼] niveaux                │    │
│  │                                                          │    │
│  └──────────────────────────────────────────────────────────┘    │
│                                                                 │
│  ┌─── Rapport ────────────────────────────────────────────┐    │
│  │                                                          │    │
│  │  Dossier de sauvegarde: [___________________] [📁]     │    │
│  │                                                          │    │
│  │  Nom du rapport: [audit_YYYYMMDD_HHMMSS.md           ]  │    │
│  │                                                          │    │
│  └──────────────────────────────────────────────────────────┘    │
│                                                                 │
│  [        🚀 Lancer l'audit        ] [⚙️ Configuration avancée]│
│                                                                 │
│  ┌─── Progression ────────────────────────────────────────┐    │
│  │                                                          │    │
│  │  État: En attente                                       │    │
│  │                                                          │    │
│  │  [████████████░░░░░░░░░░░░░░░] 52%                     │    │
│  │                                                          │    │
│  │  Page en cours: www.example.com/produits.html           │    │
│  │  Pages analysées: 7/13                                  │    │
│  │  Frames détectées: 24                                   │    │
│  │  Temps écoulé: 00:02:35                                 │    │
│  │                                                          │    │
│  └──────────────────────────────────────────────────────────┘    │
│                                                                 │
│  ┌─── Journal d'activité ────────────────────────────────┐    │
│  │ ✓ [14:23:15] Démarrage de l'audit                      │    │
│  │ ℹ [14:23:16] Crawling du site www.example.com...       │    │
│  │ ✓ [14:23:18] Page d'accueil analysée - 2 iframes       │    │
│  │ ⚠ [14:23:22] Page /produits - iframe sans titre        │    │
│  │ ✓ [14:23:25] Page /contact analysée - 1 iframe         │    │
│  │ ✗ [14:23:30] Erreur réseau /ancienne-page (404)        │    │
│  │ ✓ [14:23:45] Analyse terminée - 13 pages traitées      │    │
│  │ ✓ [14:23:46] Rapport généré: audit_20260130_142346.md  │    │
│  │                                                          │    │
│  │                             ↕ [scroll vertical]         │    │
│  └──────────────────────────────────────────────────────────┘    │
│                                                                 │
│  [📄 Ouvrir le rapport] [🔄 Nouvelle analyse] [❌ Quitter]     │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│ Prêt                                            RGAA Tester v1.0 │ ← Barre d'état
└─────────────────────────────────────────────────────────────────┘
```

## Composants détaillés

### 1. Section Configuration de l'audit

#### Champ URL
- **Widget** : `Entry` avec largeur 50 caractères
- **Placeholder** : "https://www.example.com"
- **Validation** : Format URL valide (http/https)
- **Bouton Parcourir** : Ouvre dialogue fichier (.txt, .xml pour sitemap)

#### Radio buttons mode
- **URL unique** : Analyse une seule URL
- **Fichier d'URLs** : Charge liste d'URLs depuis fichier texte

### 2. Section Tests à effectuer

#### Checkbuttons
- **Toute la section 2** : Active critères 2.1 ET 2.2 (coché par défaut)
- **Critère 2.1 uniquement** : Désactive les autres
- **Critère 2.2 uniquement** : Désactive les autres

**Logique** :
- Si "Toute la section 2" coché → grise les deux autres
- Si un critère individuel coché → décoche "Toute la section 2"

#### Profondeur d'exploration
- **Widget** : `Spinbox` ou `Combobox`
- **Valeurs** : 1, 2, 3, 4, 5 niveaux
- **Défaut** : 2 niveaux
- **Tooltip** : "Nombre de niveaux de liens à suivre depuis la page d'accueil"

### 3. Section Rapport

#### Dossier de sauvegarde
- **Widget** : `Entry` + Button
- **Défaut** : `./reports/`
- **Bouton** : Ouvre `askdirectory()`

#### Nom du rapport
- **Format** : `audit_YYYYMMDD_HHMMSS.md`
- **Auto-généré** : Basé sur date/heure lancement
- **Éditable** : Oui

### 4. Boutons d'action principaux

#### Lancer l'audit
- **État initial** : Activé si URL valide
- **Pendant audit** : Désactivé, texte → "⏸ Pause" ou "⏹ Arrêter"
- **Après audit** : Texte → "🔄 Relancer l'audit"
- **Raccourci clavier** : F5

#### Configuration avancée
- **Action** : Ouvre fenêtre modale de configuration
- **Contenu** : Timeouts, User-Agent, options de crawling

### 5. Section Progression

#### Labels d'information
- **État** : "En attente" / "En cours" / "Terminé" / "Erreur"
- **Page en cours** : URL courante analysée
- **Pages analysées** : Compteur "X/Y"
- **Frames détectées** : Total trouvé
- **Temps écoulé** : Format HH:MM:SS

#### Barre de progression
- **Widget** : `ttk.Progressbar`
- **Mode** : Determinate
- **Plage** : 0-100%
- **Mise à jour** : Toutes les 2 secondes minimum

### 6. Journal d'activité

#### Widget Text
- **Dimensions** : Hauteur 12 lignes
- **Scrollbar** : Verticale uniquement
- **Auto-scroll** : Vers le bas lors de nouveaux messages
- **Read-only** : Oui

#### Code couleur des messages
```python
COLORS = {
    '✓': 'green',    # Succès
    'ℹ': 'blue',     # Information
    '⚠': 'orange',   # Avertissement
    '✗': 'red'       # Erreur
}
```

#### Format des messages
```
[HH:MM:SS] Icône Message descriptif
```

### 7. Boutons d'action finaux

#### Ouvrir le rapport
- **État** : Désactivé jusqu'à rapport généré
- **Action** : Ouvre fichier .md avec éditeur par défaut du système
- **Raccourci** : Ctrl+O

#### Nouvelle analyse
- **Action** : Réinitialise formulaire, garde config
- **Raccourci** : Ctrl+N

#### Quitter
- **Action** : Ferme application
- **Confirmation** : Si audit en cours
- **Raccourci** : Alt+F4 / Cmd+Q

### 8. Barre d'état (Status bar)

#### Contenu
- **Gauche** : Message d'état ("Prêt", "En cours...", "Erreur")
- **Droite** : Version application

## Fenêtre modale - Configuration avancée

```
┌─── Configuration avancée ──────────────────────┐
│                                                 │
│  Crawling:                                      │
│  Timeout (secondes): [30]                       │
│  Délai entre pages (ms): [1000]                 │
│  ☑ Respecter robots.txt                         │
│  ☐ Suivre les redirections                      │
│                                                 │
│  Détection:                                     │
│  ☑ Détecter frames cachées                      │
│  ☑ Détecter frames dans shadowDOM               │
│                                                 │
│  User-Agent:                                    │
│  [RGAA-Tester/1.0 (Accessibility Audit)____]    │
│                                                 │
│  Titres génériques à détecter:                  │
│  [frame, iframe, content, widget, embed___]     │
│                                                 │
│         [Enregistrer]  [Annuler]  [Par défaut] │
└─────────────────────────────────────────────────┘
```

## Comportements et interactions

### Validation en temps réel
- URL invalide → Bordure rouge sur Entry
- Aucun test sélectionné → Désactiver bouton "Lancer"
- Dossier rapport inexistant → Créer automatiquement

### Gestion d'état
```python
STATES = {
    'IDLE': 'En attente',
    'CRAWLING': 'Exploration du site...',
    'ANALYZING': 'Analyse des frames...',
    'GENERATING': 'Génération du rapport...',
    'COMPLETED': 'Audit terminé',
    'ERROR': 'Erreur'
}
```

### Thread management
- **Thread principal** : Tkinter GUI (obligatoire)
- **Thread worker** : Audit (crawling + analyse)
- **Communication** : `queue.Queue` pour updates

```python
def update_gui_from_queue(self):
    """Vérifie queue toutes les 100ms"""
    try:
        message = self.progress_queue.get_nowait()
        self.process_message(message)
    except queue.Empty:
        pass
    finally:
        self.root.after(100, self.update_gui_from_queue)
```

### Messages de progression
```python
{
    'type': 'progress',
    'percentage': 45,
    'current_page': 'https://...',
    'pages_done': 7,
    'pages_total': 13,
    'frames_found': 24
}
```

## Raccourcis clavier

| Raccourci | Action |
|-----------|--------|
| F5 | Lancer/Relancer audit |
| Ctrl+O | Ouvrir rapport |
| Ctrl+N | Nouvelle analyse |
| Ctrl+S | Enregistrer configuration |
| Ctrl+Q | Quitter |
| Ctrl+L | Focus sur champ URL |
| F1 | Aide (ouvre README.md) |

## Gestion des erreurs GUI

### Messages d'erreur
Utiliser `messagebox` de tkinter :

```python
from tkinter import messagebox

# Erreur critique
messagebox.showerror(
    "Erreur critique",
    "Impossible de démarrer le WebDriver.\nVeuillez vérifier Chrome/ChromeDriver."
)

# Avertissement
messagebox.showwarning(
    "Avertissement",
    "Certaines pages n'ont pas pu être analysées (404).\nLe rapport sera partiel."
)

# Information
messagebox.showinfo(
    "Audit terminé",
    "L'audit est terminé avec succès!\n13 pages analysées, 24 frames détectées."
)

# Confirmation
result = messagebox.askyesno(
    "Confirmer",
    "Un audit est en cours. Voulez-vous vraiment quitter?"
)
```

## Accessibilité de l'interface

### Contraste
- Texte noir (#000000) sur fond blanc (#FFFFFF)
- Liens/succès : Vert foncé (#006400)
- Erreurs : Rouge foncé (#8B0000)
- Avertissements : Orange foncé (#FF8C00)

### Navigation clavier
- Tous les contrôles accessibles via Tab
- Ordre de tabulation logique
- Focus visible sur tous les éléments

### Labels
- Tous les Entry ont des Label associés
- Instructions claires pour chaque section

---

**Notes d'implémentation** :
- Utiliser `ttk` (themed widgets) pour apparence moderne
- Icônes Unicode pour compatibilité multi-plateforme
- Tester sur Windows, macOS et Linux
- Prévoir mode haute résolution (DPI scaling)