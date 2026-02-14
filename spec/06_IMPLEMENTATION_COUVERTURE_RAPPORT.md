# Instructions d'implémentation - Couverture et limites de l'audit

## Objectif

Implémenter dans le générateur de rapports les sections indiquant :
- La couverture automatique de l'audit (98-100% pour 2.1, 30-40% pour 2.2)
- Les limites de l'outil automatique
- Les actions requises pour l'auditeur humain
- Les avertissements sur la nécessité de vérification manuelle

---

## 1. Calcul des métriques de couverture

### Dans `analyzer.py` - Nouvelles méthodes

Ajouter une méthode pour calculer les statistiques de couverture :

```python
class RGAASection2Analyzer:
    
    def calculate_coverage_metrics(self, all_results):
        """
        Calcule les métriques de couverture de l'audit automatique.
        
        Args:
            all_results: Liste des résultats d'analyse de toutes les pages
            
        Returns:
            dict: Métriques de couverture
        """
        metrics = {
            # Compteurs critère 2.1
            'total_frames': 0,
            'frames_with_title': 0,
            'frames_without_title': 0,
            'frames_empty_title': 0,
            'frames_exempted': 0,  # Cachés, donc exemptés
            
            # Compteurs critère 2.2
            'frames_generic_title': 0,
            'frames_short_title': 0,
            'frames_to_verify': 0,
            
            # Métriques de couverture
            'criterion_2_1_coverage': 98,  # Pourcentage automatique
            'criterion_2_2_coverage': 35,  # Pourcentage automatique (flagging)
            'overall_coverage': 65,        # Pourcentage global automatique
            
            # Temps estimé
            'estimated_manual_time_minutes': 0
        }
        
        for page_result in all_results:
            for frame in page_result.get('frames', []):
                # Ne compter que les frames testées (non exemptées)
                if not frame.get('is_exempted', False):
                    metrics['total_frames'] += 1
                    
                    # Critère 2.1
                    if frame.get('has_title', False):
                        metrics['frames_with_title'] += 1
                    else:
                        metrics['frames_without_title'] += 1
                    
                    if frame.get('title', '').strip() == '':
                        metrics['frames_empty_title'] += 1
                    
                    # Critère 2.2 - Flags
                    if frame.get('is_generic_title', False):
                        metrics['frames_generic_title'] += 1
                    
                    if frame.get('is_short_title', False):
                        metrics['frames_short_title'] += 1
                else:
                    metrics['frames_exempted'] += 1
        
        # Tous les frames avec titre nécessitent vérification manuelle
        metrics['frames_to_verify'] = metrics['frames_with_title']
        
        # Estimation temps: 1.5 minute par frame à vérifier
        # Arrondi au multiple de 5 supérieur
        raw_time = metrics['frames_to_verify'] * 1.5
        metrics['estimated_manual_time_minutes'] = int((raw_time + 4) // 5 * 5)
        
        return metrics
```

### Structure de données frame enrichie

Chaque frame analysé doit avoir ces propriétés :

```python
frame_data = {
    # Identification
    'element_type': 'iframe',  # ou 'frame'
    'selector': 'iframe#video-player',
    'src': 'https://example.com/video.mp4',
    
    # Attributs de titre
    'has_title': True,
    'title': 'Vidéo de démonstration',
    'title_attribute': 'title',  # ou 'aria-label' ou 'aria-labelledby'
    
    # Tests 2.1
    'test_2_1_result': 'Conforme',  # 'Conforme' | 'Non conforme' | 'NA'
    'is_exempted': False,  # True si caché (display:none, aria-hidden, etc.)
    
    # Tests 2.2 - Flags automatiques
    'is_generic_title': False,  # Titre dans liste générique
    'is_short_title': False,    # Titre < 3 caractères
    'needs_manual_check': True, # Toujours True si has_title
    'auto_evaluation': 'Semble pertinent',  # 'Semble pertinent' | 'Suspect' | 'À vérifier'
    
    # Contexte
    'page_url': 'https://example.com/page.html',
    'html_code': '<iframe ...></iframe>'
}
```

---

## 2. Génération des sections du rapport

### Dans `report_generator.py` - Nouvelles méthodes

#### 2.1 Section "Couverture de l'audit automatique"

```python
class ReportGenerator:
    
    def generate_coverage_section(self, metrics):
        """
        Génère la section sur la couverture de l'audit automatique.
        
        Args:
            metrics: dict retourné par calculate_coverage_metrics()
            
        Returns:
            str: Section Markdown complète
        """
        
        section = """### Couverture de l'audit automatique

#### Tests automatisés réalisés

| Critère | Type de test | Couverture automatique | Fiabilité | Vérification manuelle requise |
|---------|--------------|----------------------|-----------|------------------------------|
| **2.1** - Présence titre cadre | ✅ Automatique complet | **98-100%** | Très élevée | ❌ Non |
| **2.2** - Pertinence titre cadre | ⚠️ Détection partielle (flagging) | **30-40%** | Indicative | ✅ **OUI - OBLIGATOIRE** |

#### Détails par critère

**Critère 2.1 - Présence d'un titre de cadre** :
- ✅ Détection exhaustive de tous les éléments `<frame>` et `<iframe>`
- ✅ Vérification présence attribut `title` non vide
- ✅ Vérification présence alternatives (`aria-label`, `aria-labelledby`)
- ✅ Détection et exemption des cadres cachés
- ✅ **Décision automatique fiable : CONFORME / NON CONFORME**

**Critère 2.2 - Pertinence du titre de cadre** :
- ⚠️ Détection titres génériques ("frame", "iframe", "widget", "content")
- ⚠️ Détection titres très courts (< 3 caractères)
- ⚠️ Signalement titres suspects nécessitant vérification
- ❌ **Validation finale de la pertinence : IMPOSSIBLE automatiquement**
- ✅ **Vérification manuelle obligatoire selon RGAA 4.1.2**

#### Avertissement important

> ⚠️ **LIMITE DE L'AUDIT AUTOMATIQUE**
>
> Le critère 2.2 (pertinence des titres de cadres) **ne peut pas être validé automatiquement** car la notion de "pertinence" requiert un jugement humain contextuel. L'outil a signalé les titres suspects, mais **une vérification manuelle est obligatoire** pour tous les cadres afin de valider la conformité complète à la Section 2 du RGAA 4.1.2.
>
> **Les résultats du critère 2.2 dans ce rapport sont des indicateurs uniquement** et nécessitent une validation par un auditeur humain qualifié.

#### Taux de couverture global de cet audit

- **Tests automatiques réalisés** : ~65% de la Section 2
- **Validation manuelle requise** : ~35% de la Section 2 (critère 2.2)
- **Gain de temps estimé** : ~75% par rapport à un audit 100% manuel

---
"""
        return section
```

#### 2.2 Section "Actions requises"

```python
    def generate_required_actions_section(self, metrics):
        """
        Génère la section sur les actions requises pour finaliser l'audit.
        
        Args:
            metrics: dict avec les métriques
            
        Returns:
            str: Section Markdown
        """
        
        frames_to_check = metrics['frames_to_verify']
        estimated_time = metrics['estimated_manual_time_minutes']
        
        section = f"""### 📋 Actions requises pour finaliser l'audit

> 🔴 **VÉRIFICATION MANUELLE OBLIGATOIRE**
>
> Pour compléter cet audit et valider la conformité RGAA 4.1.2 Section 2, les actions suivantes sont **obligatoires** :
>
> 1. ✅ **Critère 2.1** : Résultats validés automatiquement - aucune action requise
> 2. ⚠️ **Critère 2.2** : **Vérification manuelle requise** pour {frames_to_check} cadre(s)
>    - Ouvrir chaque page concernée dans un navigateur
>    - Vérifier que chaque titre de cadre décrit précisément son contenu ou sa fonction
>    - Valider ou invalider chaque titre selon le contexte
>    - Compléter la section "Critère 2.2" de ce rapport avec vos conclusions
>
> **Temps estimé pour la vérification manuelle** : ~{estimated_time} minutes
>
> **Compétences requises** : Auditeur accessibilité familier avec RGAA 4.1.2 et l'utilisation de lecteurs d'écran

---
"""
        return section
```

#### 2.3 Avertissement pour le critère 2.2

```python
    def generate_criterion_2_2_warning(self):
        """
        Génère l'avertissement pour le critère 2.2.
        
        Returns:
            str: Avertissement Markdown
        """
        
        warning = """
> ⚠️ **AVERTISSEMENT IMPORTANT**
> 
> La pertinence d'un titre de cadre **ne peut être évaluée que par un auditeur humain**.
> Les résultats ci-dessous sont des **indicateurs automatiques** qui signalent les titres 
> suspects nécessitant une attention particulière. 
>
> **Ce rapport ne constitue PAS une validation du critère 2.2.**
> Une vérification manuelle de tous les titres de cadres est obligatoire pour 
> confirmer la conformité à ce critère.
"""
        return warning
```

#### 2.4 Annexe B enrichie

```python
    def generate_methodology_annex(self, metrics, config):
        """
        Génère l'annexe méthodologie avec détails sur la couverture.
        
        Args:
            metrics: dict avec métriques
            config: dict avec configuration de l'audit
            
        Returns:
            str: Annexe complète
        """
        
        frames_to_verify = metrics['frames_to_verify']
        estimated_time = metrics['estimated_manual_time_minutes']
        
        annex = f"""### Annexe B : Méthodologie de test détaillée

#### Environnement technique

L'audit a été réalisé avec les outils suivants :
- **Outil principal** : RGAA Section 2 Tester v{config['app_version']}
- **Technologie** : Python {config['python_version']} avec Selenium {config['selenium_version']}
- **Navigateur** : {config['browser_name']} {config['browser_version']}
- **Système** : {config['os_full_info']}

#### Processus d'audit

1. **Crawling** : Exploration du site jusqu'à {config['crawl_depth']} niveaux de profondeur
2. **Détection** : Identification de tous les éléments `<frame>` et `<iframe>`
3. **Analyse automatique** :
   - Vérification présence attributs title/aria-label/aria-labelledby
   - Détection titres vides ou génériques
   - Identification frames cachées (exclusion du test)
4. **Flagging manuel** : Marquage titres nécessitant vérification humaine
5. **Génération rapport** : Compilation résultats au format Markdown

#### Critères de conformité

**Critère 2.1 - Présence d'un titre de cadre** :
- ✅ Conforme : Titre présent via title, aria-label ou aria-labelledby
- ❌ Non conforme : Aucun titre fourni ou titre vide
- ⚪ NA : Cadre décoratif caché (aria-hidden="true" ou display:none)

**Résultats automatiques fiables** : L'outil peut déterminer automatiquement et de manière fiable la conformité ou non-conformité pour ce critère.

**Critère 2.2 - Pertinence du titre de cadre** :
- ✅ Pertinent : Titre descriptif du contenu (**validation manuelle obligatoire**)
- ⚠️ Suspect : Titre générique ("frame", "iframe", "widget"...) - **flaggé automatiquement**
- ❓ À vérifier : Titre présent mais pertinence incertaine - **nécessite vérification manuelle**

**Résultats automatiques indicatifs uniquement** : L'outil peut uniquement signaler des problèmes probables. La validation finale nécessite un jugement humain.

#### Ce qui a été testé automatiquement

| Aspect testé | Méthode | Fiabilité | Décision automatique possible |
|--------------|---------|-----------|------------------------------|
| Détection des cadres | Parsing DOM complet | 100% | ✅ Oui |
| Présence attribut `title` | Vérification attribut | 100% | ✅ Oui |
| Titre non vide | Vérification contenu | 100% | ✅ Oui |
| Présence `aria-label` | Vérification attribut | 100% | ✅ Oui |
| Présence `aria-labelledby` | Vérification attribut | 100% | ✅ Oui |
| Cadres cachés (exemptés) | Analyse CSS/attributs | 95% | ✅ Oui |
| Titres génériques | Liste mots-clés | 80% | ⚠️ Indicatif uniquement |
| Titres courts | Comptage caractères | 90% | ⚠️ Indicatif uniquement |
| **Pertinence réelle du titre** | **Impossible** | **0%** | **❌ NON - Humain requis** |

#### Ce qui nécessite une vérification manuelle

**Obligatoire pour le critère 2.2** :
1. Ouvrir chaque page contenant des cadres dans un navigateur
2. Pour chaque cadre, vérifier que le titre :
   - Décrit précisément le contenu OU la fonction du cadre
   - Permet à un utilisateur de lecteur d'écran d'identifier le cadre
   - Est suffisamment distinctif s'il y a plusieurs cadres
3. Contexte important :
   - Un titre "Vidéo" peut être OK s'il n'y a qu'une vidéo
   - Un titre "Vidéo" est insuffisant s'il y a plusieurs vidéos
   - Un titre "Menu principal" est meilleur que juste "Menu"

**Pourquoi c'est impossible automatiquement** :
- La pertinence dépend du contexte de la page
- Nécessite de comprendre le contenu du cadre
- Requiert un jugement sur la qualité descriptive
- Varie selon le nombre d'éléments similaires sur la page

#### Taux de couverture de cet audit

- **Couverture automatique** : ~65% de la Section 2
  - Critère 2.1 : 100% automatisé
  - Critère 2.2 : 30-40% automatisé (flagging uniquement)

- **Vérification manuelle requise** : ~35% de la Section 2
  - Critère 2.2 : Validation de la pertinence de {frames_to_verify} titre(s)

#### Gain de temps estimé

Par rapport à un audit 100% manuel :
- **Temps économisé** : ~75%
- **Temps manuel restant** : ~{estimated_time} minutes pour validation critère 2.2
- **Bénéfice** : Focus de l'auditeur sur la validation qualitative, pas sur la détection

---
"""
        return annex
```

#### 2.5 Mentions légales complètes

```python
    def generate_legal_mentions(self, config):
        """
        Génère la section mentions légales avec limites de responsabilité.
        
        Args:
            config: dict avec info application
            
        Returns:
            str: Mentions légales complètes
        """
        
        mentions = f"""## Mentions légales

### Portée et limites de l'audit automatique

Ce rapport d'audit a été généré automatiquement par l'outil RGAA Section 2 Tester.

#### Couverture des tests automatiques

**Tests réalisés automatiquement (fiabilité élevée)** :
- ✅ Critère 2.1 : Détection exhaustive de la présence ou absence de titres de cadres
- ✅ Identification des cadres exemptés (cachés)
- ✅ Calcul des taux de conformité pour le critère 2.1

**Tests partiels (indicateurs uniquement)** :
- ⚠️ Critère 2.2 : Détection de titres suspects (génériques, trop courts)
- ⚠️ Signalement des cadres nécessitant une vérification manuelle prioritaire

**Tests NON réalisés (vérification manuelle obligatoire)** :
- ❌ Validation de la pertinence réelle des titres de cadres (critère 2.2)
- ❌ Évaluation contextuelle de l'adéquation titre/contenu
- ❌ Jugement sur la qualité descriptive des titres

#### Responsabilités

**L'outil automatique** :
- Fournit une détection exhaustive et fiable du critère 2.1
- Signale les problèmes probables du critère 2.2
- Génère un rapport structuré conforme au format RGAA
- Fait gagner ~75% du temps d'audit

**L'auditeur humain** :
- DOIT vérifier manuellement la pertinence de tous les titres de cadres (critère 2.2)
- DOIT valider les signalements automatiques dans leur contexte
- DOIT compléter le rapport avec ses conclusions sur le critère 2.2
- Est responsable de la validation finale de conformité

#### Conformité réglementaire

Ce rapport d'audit automatique **ne constitue PAS à lui seul** :
- ❌ Une certification de conformité RGAA complète
- ❌ Une validation réglementaire sans intervention humaine
- ❌ Un audit RGAA complet de la Section 2

Ce rapport **constitue** :
- ✅ Un pré-audit automatique fiable pour le critère 2.1
- ✅ Un support d'aide à l'audit pour le critère 2.2
- ✅ Une base de travail pour l'auditeur accessibilité
- ✅ Un outil de suivi de conformité dans le temps

### Méthodologie conforme RGAA 4.1.2

Les tests automatisés suivent strictement la méthodologie du RGAA 4.1.2 publiée par la DINUM (Direction Interministérielle du Numérique).

**Référence** : https://accessibilite.numerique.gouv.fr/methode/criteres-et-tests/#topic2

L'outil respecte les cas particuliers et exemptions définis dans le référentiel, notamment :
- Exemption des cadres cachés (aria-hidden, display:none, visibility:hidden)
- Prise en compte des alternatives au title (aria-label, aria-labelledby)
- Signalement obligatoire de la nécessité de vérification manuelle pour le critère 2.2

### Limitation de responsabilité

L'outil RGAA Section 2 Tester est fourni comme aide à l'audit d'accessibilité.
Les résultats automatiques, bien que fiables pour le critère 2.1, ne remplacent pas 
le jugement professionnel d'un auditeur qualifié.

La validation finale de la conformité RGAA Section 2 nécessite obligatoirement 
une vérification manuelle, en particulier pour le critère 2.2 (pertinence des titres).

---

**Rapport généré le** : {{date_generation}}
**Outil** : RGAA Section 2 Tester v{config['app_version']}
**Licence** : Audit réalisé conformément au RGAA 4.1.2
**Validation manuelle requise** : OUI - Critère 2.2 à compléter par auditeur humain
"""
        return mentions
```

---

## 3. Modification de la synthèse globale

### Enrichir la synthèse avec distinction auto/manuel

```python
    def generate_summary_with_coverage(self, metrics, results):
        """
        Génère la synthèse globale avec distinction auto/manuel.
        
        Args:
            metrics: dict métriques de couverture
            results: dict résultats globaux
            
        Returns:
            str: Synthèse enrichie
        """
        
        status = results['global_status']
        
        if status == 'C':
            summary = """✅ **Le site est conforme** à la section 2 du RGAA 4.1.2.
Tous les cadres présents possèdent un titre pertinent et accessible.

> ⚠️ **Note** : Le critère 2.2 (pertinence des titres) a été évalué automatiquement avec des indicateurs. Une validation manuelle finale est recommandée pour confirmer la conformité complète.
"""
        elif status == 'NC':
            summary = f"""❌ **Le site n'est pas conforme** à la section 2 du RGAA 4.1.2.
Des non-conformités ont été identifiées concernant les titres de cadres.

**Résumé des problèmes** :
- {metrics['frames_without_title']} cadre(s) sans titre (Critère 2.1 - **validé automatiquement**)
- {metrics['frames_empty_title']} cadre(s) avec titre vide (Critère 2.1 - **validé automatiquement**)
- {metrics['frames_generic_title']} cadre(s) avec titre générique (Critère 2.2 - **à vérifier manuellement**)
- {metrics['frames_to_verify']} cadre(s) à vérifier manuellement (Critère 2.2 - **validation requise**)

> ⚠️ **Action requise** : Les problèmes du critère 2.1 sont confirmés. Les signalements du critère 2.2 nécessitent une vérification manuelle obligatoire pour validation finale.
"""
        else:  # NA
            summary = """ℹ️ **La section 2 n'est pas applicable** à ce site.
Aucun cadre (frame ou iframe) n'a été détecté sur les pages testées.
"""
        
        return summary
```

---

## 4. Intégration dans le workflow principal

### Méthode principale `generate_markdown()`

```python
class ReportGenerator:
    
    def __init__(self, audit_results, config):
        """
        Args:
            audit_results: Résultats complets de l'audit
            config: Configuration de l'application
        """
        self.results = audit_results
        self.config = config
        self.metrics = None  # Sera calculé
    
    def generate_markdown(self):
        """
        Génère le rapport Markdown complet.
        
        Returns:
            str: Rapport complet au format Markdown
        """
        
        # 1. Calculer les métriques de couverture
        self.metrics = self.calculate_coverage_metrics_from_results()
        
        # 2. Construire le rapport section par section
        report = []
        
        # En-tête et infos de base
        report.append(self.generate_header())
        report.append(self.generate_audit_info())
        report.append(self.generate_test_environment())
        
        # NOUVEAU: Section couverture
        report.append(self.generate_coverage_section(self.metrics))
        
        # Synthèse des résultats
        report.append(self.generate_summary_table())
        report.append(self.generate_summary_with_coverage(self.metrics, self.results))
        
        # NOUVEAU: Actions requises
        report.append(self.generate_required_actions_section(self.metrics))
        
        # Détails des tests
        report.append(self.generate_criterion_2_1_details())
        
        # NOUVEAU: Avertissement 2.2
        report.append(self.generate_criterion_2_2_warning())
        report.append(self.generate_criterion_2_2_details())
        
        # Recommandations et plan
        report.append(self.generate_recommendations())
        report.append(self.generate_remediation_plan())
        
        # Annexes
        report.append(self.generate_pages_list())
        
        # NOUVEAU: Annexe B enrichie
        report.append(self.generate_methodology_annex(self.metrics, self.config))
        
        report.append(self.generate_glossary())
        report.append(self.generate_references())
        
        # NOUVEAU: Mentions légales complètes
        report.append(self.generate_legal_mentions(self.config))
        
        return '\n\n'.join(report)
    
    def calculate_coverage_metrics_from_results(self):
        """
        Wrapper pour calculer les métriques à partir des résultats stockés.
        
        Returns:
            dict: Métriques de couverture
        """
        analyzer = RGAASection2Analyzer()
        return analyzer.calculate_coverage_metrics(self.results['all_pages'])
```

---

## 5. Variables de configuration nécessaires

### Dans `config.json` - Ajouter

```json
{
    "app_version": "1.0.0",
    "report": {
        "show_coverage_section": true,
        "show_legal_mentions": true,
        "show_required_actions": true,
        "manual_time_per_frame_minutes": 1.5,
        "round_time_to_multiple_of": 5
    }
}
```

### Dans le code - Récupérer les infos système

```python
import platform
import sys
from selenium import __version__ as selenium_version

def get_system_info():
    """
    Récupère les informations sur l'environnement d'exécution.
    
    Returns:
        dict: Informations système
    """
    return {
        'os_name': platform.system(),
        'os_version': platform.version(),
        'os_full_info': f"{platform.system()} {platform.release()}",
        'python_version': f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        'selenium_version': selenium_version,
        'browser_name': 'Google Chrome',  # À détecter dynamiquement
        'browser_version': '120.0.6099.129',  # À détecter dynamiquement
        'app_version': '1.0.0'
    }
```

---

## 6. Tests d'intégration

### Test de génération complète

```python
def test_generate_report_with_coverage():
    """
    Test que le rapport contient toutes les sections de couverture.
    """
    # Préparer données de test
    test_results = {
        'all_pages': [
            {
                'url': 'https://example.com',
                'frames': [
                    {
                        'has_title': False,
                        'is_exempted': False,
                        'test_2_1_result': 'Non conforme'
                    },
                    {
                        'has_title': True,
                        'title': 'widget',
                        'is_exempted': False,
                        'is_generic_title': True,
                        'test_2_1_result': 'Conforme'
                    }
                ]
            }
        ]
    }
    
    config = get_system_info()
    config['crawl_depth'] = 2
    
    # Générer rapport
    generator = ReportGenerator(test_results, config)
    report = generator.generate_markdown()
    
    # Vérifications
    assert '### Couverture de l\'audit automatique' in report
    assert '98-100%' in report
    assert '30-40%' in report
    assert 'VÉRIFICATION MANUELLE OBLIGATOIRE' in report
    assert 'AVERTISSEMENT IMPORTANT' in report
    assert 'Portée et limites de l\'audit automatique' in report
    assert 'Temps estimé pour la vérification manuelle' in report
    
    print("✅ Test génération rapport avec couverture: PASSED")
```

---

## 7. Checklist d'implémentation

### Pour Claude Code - À implémenter

- [ ] **analyzer.py**
  - [ ] Méthode `calculate_coverage_metrics()`
  - [ ] Enrichir structure `frame_data` avec flags `is_generic_title`, `is_short_title`, etc.
  - [ ] Détecter frames exemptées (`is_exempted`)

- [ ] **report_generator.py**
  - [ ] Méthode `generate_coverage_section()`
  - [ ] Méthode `generate_required_actions_section()`
  - [ ] Méthode `generate_criterion_2_2_warning()`
  - [ ] Méthode `generate_methodology_annex()` enrichie
  - [ ] Méthode `generate_legal_mentions()`
  - [ ] Méthode `generate_summary_with_coverage()`
  - [ ] Modifier `generate_markdown()` pour intégrer nouvelles sections

- [ ] **utils.py**
  - [ ] Fonction `get_system_info()` pour détecter OS, Python, Selenium, navigateur

- [ ] **config.py**
  - [ ] Ajouter paramètres de couverture dans config.json

- [ ] **Tests**
  - [ ] Test `test_generate_report_with_coverage()`
  - [ ] Test calcul métriques
  - [ ] Test temps estimé

---

## 8. Ordre d'implémentation recommandé

1. **Étape 1** : Implémenter `get_system_info()` dans utils.py
2. **Étape 2** : Enrichir structure `frame_data` dans analyzer.py
3. **Étape 3** : Implémenter `calculate_coverage_metrics()` dans analyzer.py
4. **Étape 4** : Créer toutes les nouvelles méthodes `generate_*` dans report_generator.py
5. **Étape 5** : Modifier `generate_markdown()` pour intégrer les sections
6. **Étape 6** : Tester avec un site exemple
7. **Étape 7** : Ajuster formatage et messages

---

## 9. Exemple de sortie attendue

Après implémentation, le rapport doit contenir :

```markdown
# Rapport d'audit d'accessibilité RGAA 4.1.2
## Section 2 : Cadres (Frames)

### Informations sur l'audit
[...]

### Environnement de test
[...]

### Couverture de l'audit automatique    ← NOUVEAU
[Tableau + avertissements]

## Synthèse des résultats
[...]

### 📋 Actions requises pour finaliser     ← NOUVEAU
[Encadré avec actions obligatoires]

## Détails des tests

### Critère 2.1 : [...]

### Critère 2.2 : [...]
> ⚠️ AVERTISSEMENT IMPORTANT              ← NOUVEAU
[Avertissement sur limites]

[...]

### Annexe B : Méthodologie               ← ENRICHIE
[Tableau "Ce qui a été testé"]
[Section "Ce qui nécessite vérification manuelle"]

## Mentions légales                       ← NOUVELLE SECTION
[Portée et limites]
[Responsabilités]
[Conformité réglementaire]
```

---

**Ces instructions permettent à Claude Code d'implémenter complètement la fonctionnalité de couverture et limites dans les rapports générés.**