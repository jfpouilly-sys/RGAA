# Instructions for Claude Code: RGAA 4.1.2 Section 2 Accessibility Testing Tool

## Project Overview
Create a Python application with GUI to test websites against RGAA 4.1.2 Section 2 (Cadres/Frames) compliance and generate exhaustive Markdown reports.

## Core Requirements

### 1. RGAA 4.1.2 Section 2 Implementation
Implement all testable criteria from RGAA 4.1.2 Section 2 - Cadres (Frames):

**Criteria to implement:**
- **Critère 2.1**: Chaque cadre a-t-il un titre de cadre ?
- **Critère 2.2**: Pour chaque cadre ayant un titre de cadre, ce titre de cadre est-il pertinent ?

**Test Methods:**
- Automated detection: Check for `<frame>` and `<iframe>` elements
- Automated validation: Verify presence of `title` attribute
- Flag for manual review: Title pertinence (requires human judgment)
- Check for `aria-label`, `aria-labelledby` as alternatives
- Detect hidden/decorative frames
- Identify frames without accessible names

### 2. Technical Stack
- **GUI Framework**: tkinter (Python standard library)
- **Web Automation**: Selenium with ChromeDriver (or Playwright as alternative)
- **HTML Parsing**: BeautifulSoup4
- **Report Generation**: Markdown format
- **Configuration**: JSON file for settings persistence

### 3. GUI Specifications

**Main Window Layout:**
```
┌─────────────────────────────────────────────────┐
│  RGAA 4.1.2 - Vérification Section 2 (Cadres)  │
├─────────────────────────────────────────────────┤
│ URL du site: [_____________________________] [Parcourir] │
│                                                 │
│ Configuration:                                  │
│ ☐ Tester toute la section 2                   │
│ ☐ Critère 2.1 uniquement                       │
│ ☐ Critère 2.2 uniquement                       │
│                                                 │
│ Dossier de rapport: [___________________] [...]│
│                                                 │
│ [        Lancer l'audit        ]               │
│                                                 │
│ Progression:                                    │
│ [████████░░░░░░░░░░░░] 45% - Analyse page 3/7  │
│                                                 │
│ ┌─────────────────────────────────────────┐   │
│ │ Log en temps réel:                      │   │
│ │ ✓ Page d'accueil analysée - 2 iframes  │   │
│ │ ⚠ Page produit - Titre manquant iframe  │   │
│ │ ...                                      │   │
│ └─────────────────────────────────────────┘   │
│                                                 │
│ [Ouvrir le rapport] [Nouvelle analyse] [Quitter]│
└─────────────────────────────────────────────────┘
```

**Features Required:**
- URL input field with validation
- Browse button for sitemap/URL list file
- Checkboxes for test selection
- Directory picker for report storage
- Real-time progress bar
- Scrollable log window with color-coded messages
- Buttons: Launch, Open Report, New Analysis, Quit
- Status bar showing current operation

### 4. Markdown Report Format

**Must match ISIT-RGAA.pdf structure:**

```markdown
# Rapport d'audit d'accessibilité RGAA 4.1.2
## Section 2 : Cadres (Frames)

### Informations sur l'audit

**Site audité** : [URL]
**Date de l'audit** : [Date]
**Version RGAA** : 4.1.2
**Section testée** : Section 2 - Cadres
**Nombre de pages testées** : [N]

### Environnement de test

- **Système d'exploitation** : [OS]
- **Navigateur** : [Browser + Version]
- **Outil d'audit** : RGAA Section 2 Tester v[version]

---

## Synthèse des résultats

### Taux de conformité - Section 2

| Critère | Statut | Taux de conformité | Pages impactées |
|---------|--------|-------------------|-----------------|
| 2.1     | [C/NC/NA] | [%] | [N/N] |
| 2.2     | [C/NC/NA] | [%] | [N/N] |
| **Total Section 2** | **[C/NC]** | **[%]** | **[N/N]** |

**Légende** : C = Conforme | NC = Non conforme | NA = Non applicable

---

## Détails des tests

### Critère 2.1 : Chaque cadre a-t-il un titre de cadre ?

**Niveau** : A
**Test automatisé** : Oui (partiel)
**Vérification manuelle requise** : Non

#### Résultats par page

##### Page : [URL/Nom de page]

**Cadres détectés** : [N]

| Élément | Type | Titre présent | Attribut utilisé | Statut | Recommandation |
|---------|------|---------------|------------------|--------|----------------|
| iframe#1 | iframe | ✓ | title="..." | Conforme | - |
| iframe#2 | iframe | ✗ | - | Non conforme | Ajouter attribut title |
| frame#1 | frame | ✓ | aria-label="..." | Conforme | - |

**Problèmes identifiés** :
- [Description du problème]
- [Impact utilisateur]

**Code concerné** :
```html
[Code HTML de l'élément non conforme]
```

**Recommandation de correction** :
```html
[Code HTML corrigé]
```

---

### Critère 2.2 : Pour chaque cadre ayant un titre de cadre, ce titre de cadre est-il pertinent ?

**Niveau** : A
**Test automatisé** : Non
**Vérification manuelle requise** : Oui

#### Résultats par page

##### Page : [URL/Nom de page]

| Élément | Titre actuel | À vérifier manuellement | Notes |
|---------|--------------|-------------------------|-------|
| iframe#1 | "Publicité" | ⚠ Vérifier pertinence | Titre générique |
| iframe#2 | "Contenu externe - Vidéo démonstration produit" | ✓ Semble pertinent | Descriptif |

**Éléments nécessitant une vérification manuelle** :
- [Liste des éléments avec explications]

---

## Recommandations prioritaires

### Priorité 1 - Critique
- [ ] [Problème critique identifié]
- [ ] [Impact et solution]

### Priorité 2 - Important
- [ ] [Problème important]
- [ ] [Impact et solution]

### Priorité 3 - Amélioration
- [ ] [Amélioration suggérée]

---

## Plan de remédiation

### Phase 1 : Corrections critiques (Semaine 1-2)
- [Actions à entreprendre]

### Phase 2 : Corrections importantes (Semaine 3-4)
- [Actions à entreprendre]

### Phase 3 : Vérifications manuelles (Semaine 5)
- [Actions à entreprendre]

---

## Annexes

### Liste complète des pages testées
1. [URL 1] - [Titre]
2. [URL 2] - [Titre]
...

### Méthodologie de test
[Description de la méthodologie utilisée]

### Glossaire RGAA Section 2
**Cadre** : Élément HTML `<frame>` ou `<iframe>` permettant d'inclure un document dans un autre.
**Titre de cadre** : Texte fourni via attribut `title`, `aria-label` ou `aria-labelledby`.
...

---

**Rapport généré le** : [Date et heure]
**Outil** : RGAA Section 2 Tester v[version]
```

### 5. Application Features

**Core Functions:**

1. **URL Crawler**: 
   - Accept single URL or sitemap
   - Crawl up to configurable depth (default: 2 levels)
   - Respect robots.txt
   - Handle JavaScript-rendered content

2. **Frame Detection**:
   - Detect all `<iframe>` elements
   - Detect all `<frame>` elements (legacy)
   - Extract frame attributes (src, title, aria-label, aria-labelledby, id, class)
   - Identify hidden frames (display:none, visibility:hidden, aria-hidden)
   - Check for decorative frames

3. **Automated Tests**:
   - **Test 2.1**: Verify presence of title/aria-label/aria-labelledby
   - Check for empty titles
   - Validate title attribute is not empty string
   - Score: Conforme/Non conforme/Non applicable

4. **Manual Review Flags**:
   - **Test 2.2**: Flag all frames for manual title pertinence review
   - Detect generic titles ("frame", "iframe", "content", etc.)
   - Flag suspiciously short titles (< 3 characters)

5. **Report Generation**:
   - Generate complete Markdown report matching ISIT format
   - Include statistics and compliance rates
   - Provide code examples for issues
   - Include corrected code samples
   - Add screenshots (optional)

6. **Configuration Management**:
   - Save/load settings to JSON
   - Configurable crawl depth
   - Configurable timeout values
   - Report output directory preference
   - Test selection memory

### 6. Installation Manual Requirements

**Create comprehensive `INSTALLATION.md` including:**

```markdown
# Manuel d'installation - RGAA Section 2 Tester

## Prérequis système
- Python 3.8 ou supérieur
- Système d'exploitation : Windows 10/11, macOS 10.14+, ou Linux
- 4 GB RAM minimum
- Connexion Internet pour l'installation initiale

## Installation étape par étape

### Étape 1 : Installation de Python
[Instructions détaillées par OS]

### Étape 2 : Téléchargement de l'application
[Instructions]

### Étape 3 : Installation des dépendances
```bash
pip install -r requirements.txt
```

### Étape 4 : Installation du WebDriver
[Instructions ChromeDriver/geckodriver]

### Étape 5 : Configuration initiale
[Premier lancement, configuration]

### Étape 6 : Test de l'installation
[Procédure de test]

## Résolution des problèmes courants
[FAQ et solutions]

## Mise à jour de l'application
[Procédure de mise à jour]

## Désinstallation
[Procédure complète]
```

### 7. File Structure

```
rgaa-section2-tester/
├── main.py                 # Point d'entrée GUI
├── rgaa_tester/
│   ├── __init__.py
│   ├── gui.py             # Interface tkinter
│   ├── crawler.py         # Web crawler
│   ├── analyzer.py        # RGAA Section 2 tests
│   ├── report_generator.py # Markdown generation
│   ├── config.py          # Configuration management
│   └── utils.py           # Utilitaires
├── requirements.txt
├── INSTALLATION.md
├── README.md
├── config.json            # Configuration par défaut
└── reports/               # Dossier rapports générés
```

### 8. Additional Requirements

- **Error Handling**: Comprehensive try-catch for network errors, invalid URLs, timeout
- **Logging**: Log all operations to `rgaa_tester.log`
- **Internationalization**: All UI and reports in French
- **Performance**: Progress updates every 2 seconds minimum
- **Validation**: URL validation before testing
- **Export Options**: Markdown (primary), optional HTML/PDF conversion

### 9. Testing & Quality

- Include sample test URLs
- Validate against RGAA 4.1.2 official documentation
- Test with sites containing: no frames, single frame, multiple frames, nested frames
- Ensure report formatting matches ISIT-RGAA.pdf exactly

## Deliverables Expected

1. Complete Python application with GUI
2. `requirements.txt` with all dependencies
3. `INSTALLATION.md` with step-by-step setup
4. `README.md` with usage instructions
5. Sample configuration file
6. Example reports in `reports/` directory
7. Comments in French within code

## Development Priority

1. Core frame detection and analysis
2. Basic GUI with URL input
3. Markdown report generation (ISIT format)
4. Progress tracking and logging
5. Configuration management
6. Installation documentation
7. Advanced features (crawling, filtering)

---

**Implementation Notes:**
- Follow RGAA 4.1.2 guidelines strictly
- Ensure report format exactly matches ISIT-RGAA.pdf reference structure
- All user-facing text must be in French
- Code comments should be in French
- Prioritize accuracy and compliance over speed
- Include comprehensive error messages in French

## References

- RGAA 4.1.2 Official Documentation: https://www.numerique.gouv.fr/publications/rgaa-accessibilite/
- RGAA Section 2 Criteria: https://accessibilite.numerique.gouv.fr/methode/criteres-et-tests/#topic2
- WCAG 2.1 Frame Guidelines: https://www.w3.org/WAI/WCAG21/Understanding/