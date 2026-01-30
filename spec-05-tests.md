# Tests et critères de qualité - RGAA Section 2 Tester

## Stratégie de test

### Niveaux de test

1. **Tests unitaires** : Fonctions individuelles
2. **Tests d'intégration** : Modules combinés
3. **Tests fonctionnels** : Scénarios utilisateur complets
4. **Tests de validation** : Conformité RGAA 4.1.2

---

## Tests unitaires

### Module `analyzer.py`

#### Test de détection de frames

```python
def test_detect_frames_iframe():
    """Doit détecter tous les iframes dans une page"""
    html = """
    <html>
        <body>
            <iframe src="video.html" title="Vidéo"></iframe>
            <iframe src="ad.html"></iframe>
        </body>
    </html>
    """
    analyzer = RGAASection2Analyzer()
    frames = analyzer.detect_frames(BeautifulSoup(html, 'html.parser'))
    
    assert len(frames) == 2
    assert frames[0]['element'] == 'iframe'
    assert frames[0]['title'] == 'Vidéo'
    assert frames[1]['title'] is None
```

#### Test critère 2.1 - Avec titre

```python
def test_criterion_2_1_with_title():
    """Frame avec titre doit être conforme"""
    frame = {
        'element': 'iframe',
        'title': 'Vidéo de démonstration',
        'aria_label': None,
        'aria_labelledby': None
    }
    
    result = analyzer.test_criterion_2_1(frame)
    assert result == 'Conforme'
```

#### Test critère 2.1 - Sans titre

```python
def test_criterion_2_1_without_title():
    """Frame sans titre doit être non conforme"""
    frame = {
        'element': 'iframe',
        'title': None,
        'aria_label': None,
        'aria_labelledby': None
    }
    
    result = analyzer.test_criterion_2_1(frame)
    assert result == 'Non conforme'
```

#### Test critère 2.1 - Titre vide

```python
def test_criterion_2_1_empty_title():
    """Frame avec titre vide doit être non conforme"""
    frame = {
        'element': 'iframe',
        'title': '',
        'aria_label': None,
        'aria_labelledby': None
    }
    
    result = analyzer.test_criterion_2_1(frame)
    assert result == 'Non conforme'
```

#### Test critère 2.1 - Aria-label

```python
def test_criterion_2_1_with_aria_label():
    """Frame avec aria-label doit être conforme"""
    frame = {
        'element': 'iframe',
        'title': None,
        'aria_label': 'Contenu publicitaire',
        'aria_labelledby': None
    }
    
    result = analyzer.test_criterion_2_1(frame)
    assert result == 'Conforme'
```

#### Test détection titre générique

```python
def test_detect_generic_title():
    """Doit détecter les titres génériques"""
    generic_titles = ['frame', 'iframe', 'content', 'widget']
    
    assert analyzer.detect_generic_title('frame') == True
    assert analyzer.detect_generic_title('IFRAME') == True  # Case insensitive
    assert analyzer.detect_generic_title('Vidéo produit') == False
```

#### Test frame cachée

```python
def test_is_frame_hidden():
    """Doit détecter les frames cachées"""
    html_hidden = '<iframe style="display:none" src="track.html"></iframe>'
    html_visible = '<iframe src="video.html"></iframe>'
    
    soup_hidden = BeautifulSoup(html_hidden, 'html.parser')
    soup_visible = BeautifulSoup(html_visible, 'html.parser')
    
    assert analyzer.is_frame_hidden(soup_hidden.find('iframe')) == True
    assert analyzer.is_frame_hidden(soup_visible.find('iframe')) == False
```

### Module `crawler.py`

#### Test validation URL

```python
def test_validate_url_valid():
    """URLs valides doivent être acceptées"""
    assert validate_url('https://www.example.com') == True
    assert validate_url('http://example.com/page') == True
```

#### Test validation URL invalide

```python
def test_validate_url_invalid():
    """URLs invalides doivent être rejetées"""
    assert validate_url('not-a-url') == False
    assert validate_url('ftp://example.com') == False
    assert validate_url('') == False
```

### Module `report_generator.py`

#### Test génération tableau synthèse

```python
def test_generate_summary_table():
    """Doit générer un tableau Markdown correct"""
    data = {
        'criterion_2_1': {'conforme': 5, 'non_conforme': 2, 'na': 1},
        'criterion_2_2': {'conforme': 4, 'non_conforme': 3, 'na': 1},
        'total_pages': 8
    }
    
    table = report_generator.generate_summary_table(data)
    
    assert '| 2.1' in table
    assert '| 2.2' in table
    assert '62.5%' in table  # (5/8)*100 pour 2.1
```

---

## Tests d'intégration

### Test workflow complet

```python
def test_full_audit_workflow():
    """Test du workflow complet d'audit"""
    # 1. Crawler récupère pages
    crawler = WebCrawler('https://example.com', max_depth=1)
    pages = crawler.crawl()
    assert len(pages) > 0
    
    # 2. Analyzer teste chaque page
    analyzer = RGAASection2Analyzer()
    results = []
    for page in pages:
        result = analyzer.analyze_page(page['url'], page['html'])
        results.append(result)
    
    # 3. Report generator crée le rapport
    report_gen = ReportGenerator(results)
    markdown = report_gen.generate_markdown()
    
    assert '# Rapport d\'audit' in markdown
    assert 'Section 2' in markdown
```

### Test gestion erreurs réseau

```python
def test_network_error_handling():
    """Doit gérer correctement les erreurs réseau"""
    crawler = WebCrawler('https://nonexistent-domain-xyz123.com')
    
    try:
        pages = crawler.crawl()
        # Doit retourner liste vide ou lever exception gérée
        assert pages == [] or isinstance(pages, list)
    except CrawlerError as e:
        # Exception attendue et gérée
        assert 'DNS' in str(e) or 'network' in str(e).lower()
```

---

## Tests fonctionnels

### Scénarios utilisateur

#### Scénario 1 : Audit site sans frames

**Étapes** :
1. Lancer l'application
2. Entrer URL : `https://example.com/no-frames`
3. Sélectionner "Tester toute la section 2"
4. Cliquer "Lancer l'audit"

**Résultat attendu** :
- Audit se termine sans erreur
- Rapport généré indique "NA - Aucun cadre détecté"
- Taux de conformité : NA

#### Scénario 2 : Audit site avec frames conformes

**Étapes** :
1. Lancer l'application
2. Entrer URL : `https://www.w3.org/WAI/`
3. Sélectionner "Tester toute la section 2"
4. Cliquer "Lancer l'audit"

**Résultat attendu** :
- Frames détectées et analysées
- Rapport indique "Conforme" si tous les frames ont des titres
- Détails par page présents

#### Scénario 3 : Audit avec erreur 404

**Étapes** :
1. Créer fichier URLs avec une URL 404
2. Charger ce fichier dans l'application
3. Lancer l'audit

**Résultat attendu** :
- Warning dans les logs pour page 404
- Autres pages traitées normalement
- Rapport généré malgré l'erreur

#### Scénario 4 : Sauvegarde et reprise

**Étapes** :
1. Modifier configuration (profondeur=3, dossier rapport personnalisé)
2. Fermer l'application
3. Rouvrir l'application

**Résultat attendu** :
- Configuration sauvegardée et restaurée
- Dossier rapport personnalisé toujours configuré

---

## Tests de validation RGAA

### Sites de test

#### Site test 1 : Frames basiques

**HTML de test** :
```html
<!DOCTYPE html>
<html lang="fr">
<head>
    <title>Test Frames RGAA</title>
</head>
<body>
    <!-- Conforme : title présent -->
    <iframe src="video.html" title="Vidéo de démonstration produit"></iframe>
    
    <!-- Non conforme : pas de title -->
    <iframe src="ad.html"></iframe>
    
    <!-- Conforme : aria-label -->
    <iframe src="map.html" aria-label="Carte interactive du site"></iframe>
    
    <!-- Non conforme : title vide -->
    <iframe src="widget.html" title=""></iframe>
    
    <!-- Conforme mais suspect : titre générique -->
    <iframe src="external.html" title="frame"></iframe>
</body>
</html>
```

**Résultats attendus** :
- Total frames : 5
- Critère 2.1 Conformes : 3 (title, aria-label, aria-labelledby)
- Critère 2.1 Non conformes : 2 (pas de title, title vide)
- Critère 2.2 Suspects : 1 (titre "frame" générique)

#### Site test 2 : Frames cachées

**HTML de test** :
```html
<body>
    <!-- Doit être ignoré : caché -->
    <iframe src="tracking.html" style="display:none"></iframe>
    
    <!-- Doit être testé : visible -->
    <iframe src="content.html" title="Contenu principal"></iframe>
    
    <!-- Doit être ignoré : aria-hidden -->
    <iframe src="analytics.html" aria-hidden="true"></iframe>
</body>
```

**Résultats attendus** :
- Frames détectées : 3
- Frames testées : 1 (celle visible)
- Frames exclues : 2 (cachées)

### Validation conformité référentiel

#### Checklist validation RGAA 4.1.2 Section 2

- [ ] **Critère 2.1** :
  - [ ] Détecte attribut `title`
  - [ ] Détecte attribut `aria-label`
  - [ ] Détecte attribut `aria-labelledby`
  - [ ] Rejette titre vide (`title=""`)
  - [ ] Accepte au moins un attribut présent
  
- [ ] **Critère 2.2** :
  - [ ] Flag titres génériques ("frame", "iframe", "content", "widget", "embed")
  - [ ] Flag titres très courts (< 3 caractères)
  - [ ] Indique vérification manuelle nécessaire
  
- [ ] **Frames spéciales** :
  - [ ] Ignore frames cachées (`display:none`)
  - [ ] Ignore frames avec `aria-hidden="true"`
  - [ ] Ignore frames avec `visibility:hidden`

---

## Critères de qualité du code

### Lisibilité

- **Commentaires** : En français, expliquant la logique RGAA
- **Nommage** : Variables explicites (français accepté pour termes métier)
- **Structure** : Fonctions < 50 lignes
- **Complexité** : Éviter imbrications > 3 niveaux

### Performance

- **Crawling** : Maximum 5 pages/seconde
- **Analyse** : < 1 seconde par page (hors chargement réseau)
- **Rapport** : < 2 secondes pour génération

### Robustesse

- **Gestion erreurs** : Try-catch pour toutes les opérations réseau
- **Validation** : Vérifier tous les inputs utilisateur
- **Logs** : Tracer toutes les erreurs et warnings

### Maintenabilité

- **Modularité** : Chaque module indépendant
- **Configuration** : Aucun hardcoding de valeurs
- **Documentation** : Docstrings pour toutes les fonctions publiques

---

## Critères d'acceptation

### Fonctionnalités obligatoires

- ✅ Détection frames et iframes
- ✅ Test critère 2.1 (présence titre)
- ✅ Flagging critère 2.2 (pertinence)
- ✅ GUI fonctionnelle
- ✅ Génération rapport Markdown format ISIT
- ✅ Configuration persistante
- ✅ Logs détaillés

### Qualité rapport

- ✅ Structure identique à ISIT-RGAA.pdf
- ✅ Tous les tableaux présents
- ✅ Calculs de taux corrects
- ✅ Recommandations prioritaires
- ✅ Plan de remédiation
- ✅ Annexes complètes

### Performance

- ✅ Audit de 10 pages < 2 minutes
- ✅ Rapport généré < 5 secondes
- ✅ GUI réactive (pas de freeze)

### Documentation

- ✅ INSTALLATION.md complet
- ✅ README.md avec guide utilisation
- ✅ Code commenté en français
- ✅ Exemples de rapports

---

## Plan de test final

### Avant release

1. **Tests automatisés** : Tous les tests unitaires passent
2. **Tests manuels** : Tous les scénarios utilisateur validés
3. **Tests multi-plateformes** :
   - Windows 10/11
   - macOS 11+
   - Ubuntu 20.04/22.04
4. **Validation RGAA** : Tests avec sites de référence
5. **Documentation** : Relecture complète
6. **Performance** : Benchmarks respectés

### Validation finale

- [ ] Tous les tests passent
- [ ] Aucun bug critique
- [ ] Documentation complète
- [ ] Installation testée sur 3 OS
- [ ] Rapports conformes format ISIT
- [ ] Conformité RGAA 4.1.2 validée

---

**Version** : 1.0.0
**Date** : Janvier 2026