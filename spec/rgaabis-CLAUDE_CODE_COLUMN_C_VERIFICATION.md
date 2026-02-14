# Supplementary Instructions: Column C Recommendation Verification

## 🚨 CRITICAL GAP IDENTIFICATION

**Issue**: The current implementation does NOT verify the actual recommendation text in Column C of P## sheets against webpage content.

**Column C ("Recommandation")** contains the actual criterion description from RGAA 4.1.2 that must be tested. Simply having a criterion ID (like "2.1") is NOT sufficient - the automated tests MUST verify what the recommendation actually asks.

---

## 🔍 SELF-VERIFICATION CHECKLIST

Claude Code must first audit its own code:

### Step 1: Verify Current Implementation
```python
# Check if your code does ANY of the following:
# ❌ BAD: Only stores criterion ID without reading column C
# ❌ BAD: Tests are hard-coded without referencing column C text
# ❌ BAD: No function extracts column C text from ODS
# ❌ BAD: No mapping between column C text and test logic

# Run this audit on your codebase:
def audit_column_c_implementation():
    """Check if column C is being used in testing"""
    issues = []
    
    # Check 1: Is column C being read?
    if not code_reads_column_c():
        issues.append("Column C (Recommandation) is not being extracted from ODS")
    
    # Check 2: Is column C content used in test logic?
    if not code_uses_column_c_content():
        issues.append("Column C content is not used to determine test criteria")
    
    # Check 3: Are test results linked to specific column C requirements?
    if not results_reference_column_c():
        issues.append("Test results don't reference the actual recommendation text")
    
    return issues
```

### Step 2: Required Code Updates

If gaps are found, update the code to include:

```python
@dataclass
class AuditCriterion:
    """UPDATED: Now includes full recommendation text from Column C"""
    theme: str                    # Column A
    criterion_id: str             # Column B
    recommendation: str           # Column C ← THIS MUST BE EXTRACTED AND USED
    status: Status                # Column D
    derogation: Derogation        # Column E
    modifications: str            # Column F
    comments: str                 # Column G
```

---

## 📋 Column C Extraction Implementation

### Reading Column C from ODS

```python
def extract_criterion_data(sheet, row_index: int) -> Dict:
    """Extract ALL columns including Column C recommendation text"""
    row = sheet.getElementsByType(TableRow)[row_index]
    cells = expand_row_with_values(row)
    
    return {
        'theme': cells[0] if len(cells) > 0 else '',           # Column A
        'criterion_id': cells[1] if len(cells) > 1 else '',    # Column B
        'recommendation': cells[2] if len(cells) > 2 else '',  # Column C ← CRITICAL
        'status': cells[3] if len(cells) > 3 else 'NT',        # Column D
        'derogation': cells[4] if len(cells) > 4 else 'N',     # Column E
        'modifications': cells[5] if len(cells) > 5 else '',   # Column F
        'comments': cells[6] if len(cells) > 6 else ''         # Column G
    }

def get_all_recommendations(ods_doc) -> Dict[str, str]:
    """Build dictionary mapping criterion IDs to their full recommendation text"""
    recommendations = {}
    
    for sheet in ods_doc.spreadsheet.getElementsByType(Table):
        sheet_name = sheet.getAttribute("name")
        if sheet_name.startswith("P") and sheet_name[1:].isdigit():
            rows = sheet.getElementsByType(TableRow)
            for i, row in enumerate(rows[3:], start=4):  # Data starts row 4
                data = extract_criterion_data(sheet, i-1)
                if data['criterion_id']:
                    recommendations[data['criterion_id']] = data['recommendation']
    
    return recommendations
```

---

## 🎯 Recommendation-Based Test Mapping

The key insight: **Column C text determines WHAT to test, not the criterion ID alone.**

### Master Recommendation Test Registry

```python
RECOMMENDATION_TESTS = {
    # Pattern: criterion_id -> (recommendation_keywords, test_function, automated_coverage)
    
    # ============ THEME 2: CADRES (FRAMES) ============
    "2.1": {
        "recommendation_pattern": r"Chaque cadre.*a-t-il un titre de cadre",
        "test_function": "test_frame_title_presence",
        "automated_coverage": 0.98,  # 98% - Automated can check iframe/frame title attr
        "test_logic": """
            1. Find all <iframe> and <frame> elements
            2. For each frame, check if title attribute exists
            3. Check if title attribute is non-empty
        """,
        "what_automated_checks": [
            "Presence of title attribute on iframe/frame",
            "Non-empty title value"
        ],
        "requires_human_verification": [
            "None for presence check"
        ]
    },
    
    "2.2": {
        "recommendation_pattern": r".*titre de cadre.*est-il pertinent",
        "test_function": "test_frame_title_relevance",
        "automated_coverage": 0.35,  # Only 35% - Relevance requires human judgment
        "test_logic": """
            1. Get frame titles from 2.1
            2. Fetch frame content when possible
            3. Check if title describes frame content
            4. Flag generic titles like "frame", "iframe", "content"
        """,
        "what_automated_checks": [
            "Detect generic/meaningless titles (e.g., 'frame1', 'iframe')",
            "Check if title matches frame src filename",
            "Detect placeholder titles"
        ],
        "requires_human_verification": [
            "Semantic relevance of title to actual frame content",
            "Appropriateness in context of page purpose"
        ]
    },
    
    # ============ THEME 1: IMAGES ============
    "1.1": {
        "recommendation_pattern": r"Chaque image porteuse d'information a-t-elle une alternative textuelle",
        "test_function": "test_informative_images_have_alt",
        "automated_coverage": 0.75,
        "test_logic": """
            1. Find all img, svg, canvas, object elements
            2. Check for alt, aria-label, aria-labelledby, title
            3. Cannot determine if image is "porteuse d'information" automatically
        """,
        "what_automated_checks": [
            "Presence of alt attribute",
            "Presence of aria-label/aria-labelledby",
            "Non-empty alternative text"
        ],
        "requires_human_verification": [
            "Whether image is informative or decorative",
            "Whether alternative accurately describes information"
        ]
    },
    
    "1.2": {
        "recommendation_pattern": r"image de décoration.*correctement ignorée",
        "test_function": "test_decorative_images_hidden",
        "automated_coverage": 0.40,
        "test_logic": """
            1. Find images with empty alt=""
            2. Find images with aria-hidden="true"
            3. Find images with role="presentation"
        """,
        "what_automated_checks": [
            "Empty alt attribute presence",
            "aria-hidden='true' presence",
            "role='presentation' usage"
        ],
        "requires_human_verification": [
            "Whether image is truly decorative",
            "Context in which image appears"
        ]
    },
    
    # ============ THEME 8: ÉLÉMENTS OBLIGATOIRES ============
    "8.1": {
        "recommendation_pattern": r"page web.*définie par un type de document",
        "test_function": "test_doctype_presence",
        "automated_coverage": 1.0,  # 100% automated
        "test_logic": """
            1. Check if <!DOCTYPE> is present
            2. Check if DOCTYPE is valid HTML5
            3. Check DOCTYPE position (before <html>)
        """,
        "what_automated_checks": [
            "DOCTYPE declaration presence",
            "DOCTYPE validity",
            "DOCTYPE position in document"
        ],
        "requires_human_verification": []
    },
    
    "8.2": {
        "recommendation_pattern": r"code source généré est-il valide",
        "test_function": "test_html_validity",
        "automated_coverage": 0.95,
        "test_logic": """
            1. Run HTML validator (W3C Nu HTML Checker)
            2. Check for unique IDs
            3. Check tag nesting
            4. Check attribute validity
        """,
        "what_automated_checks": [
            "HTML5 validation errors",
            "Duplicate ID detection",
            "Tag nesting errors",
            "Invalid attributes"
        ],
        "requires_human_verification": [
            "Contextual validity of certain markup patterns"
        ]
    },
    
    "8.3": {
        "recommendation_pattern": r"langue par défaut est-elle présente",
        "test_function": "test_default_language",
        "automated_coverage": 1.0,
        "test_logic": """
            1. Check <html> for lang attribute
            2. Verify lang value is valid ISO 639-1
        """,
        "what_automated_checks": [
            "Presence of lang attribute on <html>",
            "Valid ISO language code"
        ],
        "requires_human_verification": []
    },
    
    "8.4": {
        "recommendation_pattern": r"code de langue est-il pertinent",
        "test_function": "test_language_relevance",
        "automated_coverage": 0.60,
        "test_logic": """
            1. Get declared lang
            2. Detect actual page content language (heuristic)
            3. Compare declared vs detected
        """,
        "what_automated_checks": [
            "Language detection heuristics",
            "Mismatch between declared and detected language"
        ],
        "requires_human_verification": [
            "Actual primary language of page content",
            "Edge cases with multilingual content"
        ]
    },
    
    "8.5": {
        "recommendation_pattern": r"page web a-t-elle un titre de page",
        "test_function": "test_page_title_presence",
        "automated_coverage": 1.0,
        "test_logic": """
            1. Check for <title> element in <head>
            2. Verify <title> has non-empty text content
        """,
        "what_automated_checks": [
            "Presence of <title> element",
            "Non-empty title content"
        ],
        "requires_human_verification": []
    },
    
    "8.6": {
        "recommendation_pattern": r"titre.*est-il pertinent",
        "test_function": "test_page_title_relevance",
        "automated_coverage": 0.40,
        "test_logic": """
            1. Get title text
            2. Check against URL path
            3. Check against h1 content
            4. Detect generic titles
        """,
        "what_automated_checks": [
            "Generic title detection",
            "Title-URL consistency",
            "Title-H1 consistency"
        ],
        "requires_human_verification": [
            "Semantic relevance to page content",
            "Uniqueness within site"
        ]
    },
    
    # Add more criteria following this pattern...
}
```

---

## 🔧 Implementing Recommendation-Aware Testing

### Core Test Dispatcher

```python
class RecommendationBasedTester:
    """Tests criteria based on their Column C recommendation text"""
    
    def __init__(self, ods_handler):
        self.handler = ods_handler
        self.recommendations = self.handler.get_all_recommendations()
        
    def test_criterion(self, criterion_id: str, page_url: str) -> Dict:
        """
        Test a criterion by reading its recommendation text and applying
        appropriate test logic.
        """
        recommendation = self.recommendations.get(criterion_id, "")
        
        if not recommendation:
            return {
                'status': 'NT',
                'reason': 'Recommendation text not found in Column C',
                'automated_coverage': 0
            }
        
        # Get test configuration from registry
        test_config = RECOMMENDATION_TESTS.get(criterion_id)
        
        if not test_config:
            return {
                'status': 'NT',
                'reason': f'No automated test defined for criterion {criterion_id}',
                'automated_coverage': 0,
                'recommendation_text': recommendation
            }
        
        # Verify recommendation matches expected pattern
        import re
        if not re.search(test_config['recommendation_pattern'], recommendation, re.IGNORECASE):
            return {
                'status': 'NT',
                'reason': 'Recommendation text does not match expected pattern',
                'expected_pattern': test_config['recommendation_pattern'],
                'actual_recommendation': recommendation,
                'automated_coverage': 0
            }
        
        # Run the appropriate test function
        test_func = getattr(self, test_config['test_function'], None)
        if test_func:
            result = test_func(page_url, recommendation)
            result['automated_coverage'] = test_config['automated_coverage']
            result['human_verification_needed'] = test_config['requires_human_verification']
            return result
        
        return {
            'status': 'NT',
            'reason': f'Test function {test_config["test_function"]} not implemented',
            'automated_coverage': 0
        }
    
    # ============ TEST IMPLEMENTATIONS ============
    
    def test_frame_title_presence(self, url: str, recommendation: str) -> Dict:
        """
        Criterion 2.1: Chaque cadre a-t-il un titre de cadre ?
        Verifies: <iframe> and <frame> elements have title attribute
        """
        from bs4 import BeautifulSoup
        import requests
        
        try:
            response = requests.get(url, timeout=30)
            soup = BeautifulSoup(response.text, 'lxml')
            
            frames = soup.find_all(['iframe', 'frame'])
            
            if not frames:
                return {
                    'status': 'NA',
                    'reason': 'No frames found on page',
                    'details': {'frame_count': 0}
                }
            
            issues = []
            compliant_frames = 0
            
            for i, frame in enumerate(frames):
                frame_info = {
                    'index': i,
                    'tag': frame.name,
                    'src': frame.get('src', 'no-src'),
                    'title': frame.get('title', None)
                }
                
                if not frame.get('title'):
                    issues.append(f"Frame {i} ({frame.get('src', 'no src')}) missing title attribute")
                elif frame.get('title', '').strip() == '':
                    issues.append(f"Frame {i} has empty title")
                else:
                    compliant_frames += 1
            
            status = 'C' if not issues else 'NC'
            
            return {
                'status': status,
                'total_frames': len(frames),
                'compliant_frames': compliant_frames,
                'issues': issues,
                'recommendation_verified': recommendation,
                'modifications': '\n'.join(issues) if issues else ''
            }
            
        except Exception as e:
            return {
                'status': 'NT',
                'reason': f'Error testing page: {str(e)}'
            }
    
    def test_frame_title_relevance(self, url: str, recommendation: str) -> Dict:
        """
        Criterion 2.2: Le titre de cadre est-il pertinent ?
        Note: Limited automated capability - flags obvious issues only
        """
        from bs4 import BeautifulSoup
        import requests
        
        GENERIC_TITLES = [
            'frame', 'iframe', 'content', 'main', 'untitled',
            'cadre', 'contenu', 'frame1', 'frame2', 'f1', 'f2'
        ]
        
        try:
            response = requests.get(url, timeout=30)
            soup = BeautifulSoup(response.text, 'lxml')
            
            frames = soup.find_all(['iframe', 'frame'])
            frames_with_title = [f for f in frames if f.get('title')]
            
            if not frames_with_title:
                return {
                    'status': 'NA',
                    'reason': 'No frames with titles to evaluate'
                }
            
            issues = []
            possibly_ok = []
            
            for i, frame in enumerate(frames_with_title):
                title = frame.get('title', '').lower().strip()
                
                if title in GENERIC_TITLES:
                    issues.append(f"Frame {i}: Generic title '{title}' - likely not relevant")
                elif len(title) < 3:
                    issues.append(f"Frame {i}: Title too short '{title}'")
                else:
                    possibly_ok.append(f"Frame {i}: Title '{title}' - requires human verification")
            
            # Cannot be fully compliant via automation due to semantic verification
            if issues:
                status = 'NC'
                modifications = '\n'.join(issues)
            else:
                status = 'NT'  # Needs human verification
                modifications = 'Automated check found no obvious issues, but human verification required for relevance'
            
            return {
                'status': status,
                'issues': issues,
                'requires_human_review': possibly_ok,
                'recommendation_verified': recommendation,
                'modifications': modifications,
                'note': 'HUMAN VERIFICATION REQUIRED: Automated tests can only detect obviously irrelevant titles'
            }
            
        except Exception as e:
            return {
                'status': 'NT',
                'reason': f'Error testing page: {str(e)}'
            }
    
    def test_doctype_presence(self, url: str, recommendation: str) -> Dict:
        """Criterion 8.1: DOCTYPE presence and validity"""
        import requests
        
        try:
            response = requests.get(url, timeout=30)
            html = response.text.strip()
            
            # Check for DOCTYPE
            has_doctype = html.lower().startswith('<!doctype')
            
            if not has_doctype:
                return {
                    'status': 'NC',
                    'reason': 'No DOCTYPE declaration found',
                    'modifications': 'Add <!DOCTYPE html> at the beginning of the document'
                }
            
            # Check DOCTYPE is valid HTML5
            is_html5 = 'html>' in html[:50].lower() and 'html ' not in html[:50].lower()
            
            return {
                'status': 'C' if has_doctype else 'NC',
                'has_doctype': has_doctype,
                'is_html5': is_html5,
                'recommendation_verified': recommendation
            }
            
        except Exception as e:
            return {'status': 'NT', 'reason': str(e)}
    
    def test_default_language(self, url: str, recommendation: str) -> Dict:
        """Criterion 8.3: Default language presence"""
        from bs4 import BeautifulSoup
        import requests
        
        try:
            response = requests.get(url, timeout=30)
            soup = BeautifulSoup(response.text, 'lxml')
            
            html_tag = soup.find('html')
            if not html_tag:
                return {'status': 'NC', 'reason': 'No <html> element found'}
            
            lang = html_tag.get('lang') or html_tag.get('xml:lang')
            
            if not lang:
                return {
                    'status': 'NC',
                    'reason': 'No lang attribute on <html> element',
                    'modifications': 'Add lang="fr" (or appropriate language code) to <html> element'
                }
            
            return {
                'status': 'C',
                'lang_value': lang,
                'recommendation_verified': recommendation
            }
            
        except Exception as e:
            return {'status': 'NT', 'reason': str(e)}
    
    def test_page_title_presence(self, url: str, recommendation: str) -> Dict:
        """Criterion 8.5: Page title presence"""
        from bs4 import BeautifulSoup
        import requests
        
        try:
            response = requests.get(url, timeout=30)
            soup = BeautifulSoup(response.text, 'lxml')
            
            title_tag = soup.find('title')
            
            if not title_tag:
                return {
                    'status': 'NC',
                    'reason': 'No <title> element found',
                    'modifications': 'Add <title>Page Title</title> in <head>'
                }
            
            title_text = title_tag.get_text(strip=True)
            
            if not title_text:
                return {
                    'status': 'NC',
                    'reason': 'Title element is empty',
                    'modifications': 'Add descriptive text to <title> element'
                }
            
            return {
                'status': 'C',
                'title_value': title_text,
                'recommendation_verified': recommendation
            }
            
        except Exception as e:
            return {'status': 'NT', 'reason': str(e)}
```

---

## 📊 Reporting Test Coverage

### Generate Coverage Report

```python
def generate_coverage_report(test_results: Dict) -> str:
    """Generate report showing what was tested and how"""
    
    report = []
    report.append("=" * 60)
    report.append("RGAA AUDIT AUTOMATED TEST COVERAGE REPORT")
    report.append("=" * 60)
    report.append("")
    
    fully_automated = []
    partially_automated = []
    human_only = []
    not_tested = []
    
    for criterion_id, result in test_results.items():
        coverage = result.get('automated_coverage', 0)
        
        if coverage >= 0.95:
            fully_automated.append((criterion_id, result))
        elif coverage >= 0.30:
            partially_automated.append((criterion_id, result))
        elif coverage > 0:
            human_only.append((criterion_id, result))
        else:
            not_tested.append((criterion_id, result))
    
    report.append(f"FULLY AUTOMATED (≥95% coverage): {len(fully_automated)} criteria")
    for cid, res in fully_automated:
        report.append(f"  ✓ {cid}: {res.get('status', 'NT')} - {res.get('recommendation_verified', '')[:50]}...")
    
    report.append("")
    report.append(f"PARTIALLY AUTOMATED (30-94% coverage): {len(partially_automated)} criteria")
    for cid, res in partially_automated:
        human_items = res.get('human_verification_needed', [])
        report.append(f"  ◐ {cid}: {res.get('status', 'NT')} - Needs human check: {', '.join(human_items)[:50]}")
    
    report.append("")
    report.append(f"REQUIRES HUMAN VERIFICATION: {len(human_only)} criteria")
    for cid, res in human_only:
        report.append(f"  ○ {cid}: Automated coverage too low for reliable results")
    
    report.append("")
    report.append(f"NOT TESTED: {len(not_tested)} criteria")
    for cid, res in not_tested:
        report.append(f"  ✗ {cid}: {res.get('reason', 'No test available')}")
    
    report.append("")
    report.append("=" * 60)
    report.append("LEGAL DISCLAIMER")
    report.append("=" * 60)
    report.append("This automated audit does NOT replace human expert evaluation.")
    report.append("Criteria marked as 'Partially Automated' or 'Human Verification'")
    report.append("MUST be verified by a qualified accessibility auditor.")
    report.append("")
    
    return '\n'.join(report)
```

---

## ✅ Implementation Verification Steps

After updating your code, verify the implementation:

```python
def verify_column_c_implementation():
    """Verify that Column C is properly integrated"""
    
    checks = {
        'column_c_extracted': False,
        'recommendations_mapped': False,
        'tests_use_recommendations': False,
        'coverage_reported': False
    }
    
    # Test 1: Load ODS and check Column C extraction
    handler = RGAAAuditODSHandler("grilleAudit.ods")
    handler.load()
    
    recommendations = handler.get_all_recommendations()
    checks['column_c_extracted'] = len(recommendations) == 106
    
    # Test 2: Check recommendations are meaningful
    sample = recommendations.get("2.1", "")
    checks['recommendations_mapped'] = "cadre" in sample.lower()
    
    # Test 3: Run a test and verify it uses recommendation
    tester = RecommendationBasedTester(handler)
    result = tester.test_criterion("2.1", "https://example.com")
    checks['tests_use_recommendations'] = 'recommendation_verified' in result
    
    # Test 4: Check coverage reporting
    all_results = {cid: tester.test_criterion(cid, "https://example.com") 
                   for cid in recommendations.keys()}
    report = generate_coverage_report(all_results)
    checks['coverage_reported'] = "AUTOMATED TEST COVERAGE" in report
    
    # Output verification results
    print("\n=== COLUMN C IMPLEMENTATION VERIFICATION ===")
    for check, passed in checks.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {check}")
    
    all_passed = all(checks.values())
    print(f"\nOverall: {'IMPLEMENTATION COMPLETE' if all_passed else 'GAPS FOUND - UPDATE CODE'}")
    
    return all_passed
```

---

## 📝 Comments Format for ODS Output

When writing to Column G (Commentaires), include:

```
[AUTOMATED TEST - {date}]
Coverage: {percentage}%
Checks performed:
- {check1}
- {check2}
Requires human verification:
- {human_check1}
Tool: RGAA Audit Analyzer v{version}
```

---

## 🔗 Reference: RGAA 4.1.2 Criterion to Test Mapping

See `/mnt/project/RGAA-v4.1.2.pdf` for complete criterion definitions.

Key sections for Column C verification:
- Section 2.2.1: Images (Criteria 1.1-1.9)
- Section 2.2.2: Cadres (Criteria 2.1-2.2)
- Section 2.2.3: Couleurs (Criteria 3.1-3.3)
- [Continue for all 13 themes...]

---

## ⚠️ MANDATORY REQUIREMENTS

1. **Column C MUST be read** from ODS file for every criterion
2. **Recommendation text MUST be verified** against expected patterns
3. **Test results MUST indicate** what was actually checked
4. **Coverage percentage MUST be reported** for transparency
5. **Human verification requirements MUST be clearly stated**
6. **Legal disclaimer MUST be included** in all reports

---

**END OF SUPPLEMENTARY INSTRUCTIONS**
