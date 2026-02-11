# Changelog

Toutes les modifications notables de ce projet sont documentées dans ce fichier.

Le format est basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/).

## [2.0.0] - 2026-02-09

### Ajouté

#### Mode RGAA Complet (106 critères)
- Support complet des 106 critères RGAA 4.1.2 (toutes les 13 thématiques)
- Détection automatique des critères NA (Non Applicable) basée sur le contenu de la page
- `ContentDetector` pour analyser la présence d'éléments (images, formulaires, tableaux, etc.)

#### Interface graphique ODS/XLSX
- Nouvelle interface pour travailler avec les fichiers `grilleAudit.ods` ou `.xlsx`
- Support des fichiers ODS (LibreOffice) avec odfpy
- Support des fichiers XLSX (Excel) avec openpyxl
- Affichage des informations d'audit (date, auditeur, contexte, site)
- Liste des pages à auditer avec statut visuel (bleu = testé)
- Boutons d'action : analyser page sélectionnée, analyser toutes les pages

#### Répertoire de sortie configurable
- Nouveau champ "Répertoire de sortie" dans l'interface
- Bouton "Parcourir..." pour sélectionner le répertoire
- Bouton "Réinitialiser" pour revenir au répertoire par défaut (même que le fichier ODS)
- Tous les fichiers de sortie utilisent ce répertoire : logs, CSV, statistiques

#### Fichiers de log
- `audit_journal.log` : Journal général de toutes les opérations (mode append)
- `Pxx.log` : Un fichier log par page analysée (P01.log, P02.log, etc.)
- Sauvegarde automatique en temps réel (flush après chaque message)
- En-tête de session avec date/heure et fichier source

#### Export CSV par page
- Génération automatique de `Pxx.csv` après chaque analyse de page
- Colonnes : Thématique, Critère, Description, Statut, Dérogation, Modifications, Commentaires, Date
- Utilise les données en mémoire pour garantir la cohérence

#### Analyse parallèle
- Option "Analyse parallèle" avec nombre de threads configurable (2-16)
- Chaque thread a son propre Crawler pour les requêtes HTTP
- Accès concurrent sécurisé au handler ODS avec RLock

#### Logs détaillés pendant l'analyse
- Affichage de chaque critère testé avec format : `Critère | Description | Statut`
- Symboles de statut : ✓ C, ✗ NC, ⊘ NA, ? NT
- Diagnostic des URLs : affichage de l'URL réellement analysée

### Corrigé

#### Parsing ODS
- Correction du parsing des cellules avec `numbercolumnsrepeated` (expansion correcte)
- Méthode `_expand_row_cells` réécrite pour reconstruire complètement les lignes
- Utilisation de `expand_row` (lecture seule) pour la recherche de critères

#### Parsing des URLs
- Correction du parsing des URLs dans les onglets Pxx
- Gestion correcte du format "Titre : https://..." (ne coupe plus l'URL)
- Détection des cellules contenant uniquement une URL (sans titre)

#### Pages absentes
- Optimisation du traitement des pages "Absente" (marquage NA en mémoire uniquement)
- Performance améliorée : de plusieurs secondes à quelques millisecondes par page absente

#### Création automatique des critères
- Auto-création des critères manquants dans `PageAudit.update_criterion()`
- Insertion triée par numéro de critère
- Utilisation de `CRITERIA_THEMES` pour le nom de la thématique

#### Détection des URLs dupliquées
- Avertissement au chargement si plusieurs pages utilisent la même URL
- Affichage de la liste des URLs de toutes les pages pour vérification

### Modifié

#### Architecture
- Séparation du code en modules : `ods_handler.py`, `ods_analyzer.py`, `ods_models.py`, `ods_gui.py`
- Thread-safety avec `threading.RLock()` pour les opérations ODS
- Support des callbacks de log pour le crawler

## [1.0.0] - Version initiale

### Ajouté
- Test automatisé du Critère 2.1 (cadres avec titre)
- Signalement pour le Critère 2.2 (pertinence des titres)
- Interface graphique tkinter
- Mode ligne de commande
- Crawler multi-pages
- Rapports Markdown détaillés
