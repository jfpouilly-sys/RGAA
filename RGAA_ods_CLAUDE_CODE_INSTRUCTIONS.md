# Claude Code Instructions: RGAA Audit ODS File Analysis Feature

## 🎯 Objective

Update the existing RGAA accessibility auditing software to support analysis based on `.ods` files (OpenDocument Spreadsheet format), using the official RGAA audit template `grilleAudit.ods`. The application must read the template, process audit data, and output an updated `.ods` file with analysis results.

---

## 📁 Understanding the grilleAudit.ods Structure

### Sheet Overview

The template contains the following sheets:

| Sheet Name | Purpose | Read/Write |
|------------|---------|------------|
| `Mode_d'emploi` | Instructions for auditors | Read-only |
| `Échantillon` | Sample pages to evaluate (URLs, titles) | Read |
| `Critères` | Reference list of all 106 RGAA 4.1.2 criteria | Read-only |
| `P01` to `P20` | Individual page audit sheets (one per page) | **Read/Write** |
| `BaseDeCalcul` | Aggregated data matrix (criteria × pages) | Auto-calculated |
| `Synthèse` | Summary statistics by theme | Auto-calculated |

### Échantillon (Sample) Sheet Structure

```
Row 3: Date: jj/mm/aaaa
Row 4: Auditeur: Nom Prénom
Row 5: Contexte: Visite initiale
Row 6: Site: [URL]
Row 8: N° page | Titre de la page | URL
Row 9-28: P01-P20 | [Page Title] | [Page URL]
```

### Page Assessment Sheets (P01-P20) Structure

```
Row 2: [Page Title] : [URL]
Row 3 (Header): Thématique | Critère | Recommandation | Statut | Dérogation | Modifications à apporter | Commentaires
Row 4+: [Data rows with 106 criteria]
```

#### Column Definitions:
- **A - Thématique**: Topic category (IMAGES, CADRES, COULEURS, MULTIMÉDIA, etc.)
- **B - Critère**: Criterion number (1.1, 1.2, ..., 13.12)
- **C - Recommandation**: Full criterion description text
- **D - Statut**: Assessment status (see values below)
- **E - Dérogation**: Derogation flag (see values below)
- **F - Modifications à apporter**: Required fixes/modifications
- **G - Commentaires en cas de dérogations**: Comments for derogations

#### Valid Status Values (Column D):
| Value | Meaning | French |
|-------|---------|--------|
| `C` | Compliant | Conforme |
| `NC` | Non-Compliant | Non Conforme |
| `NA` | Not Applicable | Non Applicable |
| `NT` | Not Tested | Non Testé |

#### Valid Derogation Values (Column E):
| Value | Meaning |
|-------|---------|
| `D` | Derogation applies |
| `N` | No derogation (Normal) |

### RGAA Thematic Categories (13 themes, 106 criteria)

```
1. IMAGES (Critères 1.1 - 1.9)
2. CADRES (Critères 2.1 - 2.2)
3. COULEURS (Critères 3.1 - 3.3)
4. MULTIMÉDIA (Critères 4.1 - 4.13)
5. TABLEAUX (Critères 5.1 - 5.8)
6. LIENS (Critères 6.1 - 6.2)
7. SCRIPTS (Critères 7.1 - 7.5)
8. ÉLÉMENTS OBLIGATOIRES (Critères 8.1 - 8.10)
9. STRUCTURATION DE L'INFORMATION (Critères 9.1 - 9.4)
10. PRÉSENTATION DE L'INFORMATION (Critères 10.1 - 10.14)
11. FORMULAIRES (Critères 11.1 - 11.13)
12. NAVIGATION (Critères 12.1 - 12.11)
13. CONSULTATION (Critères 13.1 - 13.12)
```

---

## 🔧 Implementation Requirements

### 1. Python Dependencies

```python
# Required packages
pip install odfpy          # For reading/writing .ods files
pip install pandas         # For data manipulation (optional but recommended)
pip install requests       # For fetching webpages (if automated testing)
pip install beautifulsoup4 # For HTML parsing (if automated testing)
pip install lxml           # For XML/HTML parsing
```

### 2. Core Module: ODS File Handler

Create a module `ods_handler.py` with the following capabilities:

```python
"""
ODS File Handler for RGAA Audit Analysis
"""

from odf.opendocument import load, OpenDocumentSpreadsheet
from odf.table import Table, TableRow, TableCell
from odf.text import P
from dataclasses import dataclass
from typing import List, Dict, Optional
from enum import Enum

class Status(Enum):
    COMPLIANT = "C"
    NON_COMPLIANT = "NC"
    NOT_APPLICABLE = "NA"
    NOT_TESTED = "NT"

class Derogation(Enum):
    YES = "D"
    NO = "N"

@dataclass
class AuditCriterion:
    """Represents a single criterion evaluation"""
    theme: str
    criterion_id: str
    description: str
    status: Status
    derogation: Derogation
    modifications: str
    comments: str

@dataclass
class PageAudit:
    """Represents audit results for a single page"""
    page_id: str  # P01, P02, etc.
    title: str
    url: str
    criteria: List[AuditCriterion]

@dataclass
class AuditFile:
    """Represents the complete audit file"""
    date: str
    auditor: str
    context: str
    site_url: str
    pages: List[PageAudit]

class RGAAAuditODSHandler:
    """Handler for reading and writing RGAA audit .ods files"""
    
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.doc = None
        
    def load(self) -> AuditFile:
        """Load and parse the .ods audit file"""
        self.doc = load(self.filepath)
        # Implementation: Parse all sheets
        pass
    
    def get_sample_pages(self) -> List[Dict]:
        """Extract page list from Échantillon sheet"""
        pass
    
    def get_page_audit(self, page_id: str) -> PageAudit:
        """Get audit data for a specific page"""
        pass
    
    def update_criterion(self, page_id: str, criterion_id: str, 
                        status: Status, derogation: Derogation = Derogation.NO,
                        modifications: str = "", comments: str = ""):
        """Update a single criterion evaluation"""
        pass
    
    def update_page_audit(self, page_audit: PageAudit):
        """Update all criteria for a page"""
        pass
    
    def calculate_synthesis(self) -> Dict:
        """Calculate summary statistics"""
        pass
    
    def save(self, output_path: Optional[str] = None):
        """Save the modified .ods file"""
        pass
```

### 3. Data Structures

```python
# Mapping of criterion IDs to themes
CRITERIA_THEMES = {
    "1.1": "IMAGES", "1.2": "IMAGES", "1.3": "IMAGES", "1.4": "IMAGES",
    "1.5": "IMAGES", "1.6": "IMAGES", "1.7": "IMAGES", "1.8": "IMAGES", "1.9": "IMAGES",
    "2.1": "CADRES", "2.2": "CADRES",
    "3.1": "COULEURS", "3.2": "COULEURS", "3.3": "COULEURS",
    "4.1": "MULTIMÉDIA", "4.2": "MULTIMÉDIA", "4.3": "MULTIMÉDIA", "4.4": "MULTIMÉDIA",
    "4.5": "MULTIMÉDIA", "4.6": "MULTIMÉDIA", "4.7": "MULTIMÉDIA", "4.8": "MULTIMÉDIA",
    "4.9": "MULTIMÉDIA", "4.10": "MULTIMÉDIA", "4.11": "MULTIMÉDIA", "4.12": "MULTIMÉDIA",
    "4.13": "MULTIMÉDIA",
    "5.1": "TABLEAUX", "5.2": "TABLEAUX", "5.3": "TABLEAUX", "5.4": "TABLEAUX",
    "5.5": "TABLEAUX", "5.6": "TABLEAUX", "5.7": "TABLEAUX", "5.8": "TABLEAUX",
    "6.1": "LIENS", "6.2": "LIENS",
    "7.1": "SCRIPTS", "7.2": "SCRIPTS", "7.3": "SCRIPTS", "7.4": "SCRIPTS", "7.5": "SCRIPTS",
    "8.1": "ÉLÉMENTS OBLIGATOIRES", "8.2": "ÉLÉMENTS OBLIGATOIRES",
    "8.3": "ÉLÉMENTS OBLIGATOIRES", "8.4": "ÉLÉMENTS OBLIGATOIRES",
    "8.5": "ÉLÉMENTS OBLIGATOIRES", "8.6": "ÉLÉMENTS OBLIGATOIRES",
    "8.7": "ÉLÉMENTS OBLIGATOIRES", "8.8": "ÉLÉMENTS OBLIGATOIRES",
    "8.9": "ÉLÉMENTS OBLIGATOIRES", "8.10": "ÉLÉMENTS OBLIGATOIRES",
    "9.1": "STRUCTURATION DE L'INFORMATION", "9.2": "STRUCTURATION DE L'INFORMATION",
    "9.3": "STRUCTURATION DE L'INFORMATION", "9.4": "STRUCTURATION DE L'INFORMATION",
    "10.1": "PRÉSENTATION DE L'INFORMATION", "10.2": "PRÉSENTATION DE L'INFORMATION",
    "10.3": "PRÉSENTATION DE L'INFORMATION", "10.4": "PRÉSENTATION DE L'INFORMATION",
    "10.5": "PRÉSENTATION DE L'INFORMATION", "10.6": "PRÉSENTATION DE L'INFORMATION",
    "10.7": "PRÉSENTATION DE L'INFORMATION", "10.8": "PRÉSENTATION DE L'INFORMATION",
    "10.9": "PRÉSENTATION DE L'INFORMATION", "10.10": "PRÉSENTATION DE L'INFORMATION",
    "10.11": "PRÉSENTATION DE L'INFORMATION", "10.12": "PRÉSENTATION DE L'INFORMATION",
    "10.13": "PRÉSENTATION DE L'INFORMATION", "10.14": "PRÉSENTATION DE L'INFORMATION",
    "11.1": "FORMULAIRES", "11.2": "FORMULAIRES", "11.3": "FORMULAIRES",
    "11.4": "FORMULAIRES", "11.5": "FORMULAIRES", "11.6": "FORMULAIRES",
    "11.7": "FORMULAIRES", "11.8": "FORMULAIRES", "11.9": "FORMULAIRES",
    "11.10": "FORMULAIRES", "11.11": "FORMULAIRES", "11.12": "FORMULAIRES",
    "11.13": "FORMULAIRES",
    "12.1": "NAVIGATION", "12.2": "NAVIGATION", "12.3": "NAVIGATION",
    "12.4": "NAVIGATION", "12.5": "NAVIGATION", "12.6": "NAVIGATION",
    "12.7": "NAVIGATION", "12.8": "NAVIGATION", "12.9": "NAVIGATION",
    "12.10": "NAVIGATION", "12.11": "NAVIGATION",
    "13.1": "CONSULTATION", "13.2": "CONSULTATION", "13.3": "CONSULTATION",
    "13.4": "CONSULTATION", "13.5": "CONSULTATION", "13.6": "CONSULTATION",
    "13.7": "CONSULTATION", "13.8": "CONSULTATION", "13.9": "CONSULTATION",
    "13.10": "CONSULTATION", "13.11": "CONSULTATION", "13.12": "CONSULTATION"
}

# Total: 106 criteria
```

### 4. GUI Integration (Tkinter)

Add a new tab or section to the existing application:

```python
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

class ODSAuditFrame(ttk.Frame):
    """Frame for ODS-based audit analysis"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.audit_handler = None
        self.create_widgets()
    
    def create_widgets(self):
        # File selection
        file_frame = ttk.LabelFrame(self, text="Fichier d'audit ODS")
        file_frame.pack(fill="x", padx=10, pady=5)
        
        self.file_path_var = tk.StringVar()
        ttk.Entry(file_frame, textvariable=self.file_path_var, width=60).pack(side="left", padx=5)
        ttk.Button(file_frame, text="Parcourir...", command=self.browse_file).pack(side="left")
        ttk.Button(file_frame, text="Charger", command=self.load_file).pack(side="left", padx=5)
        
        # Audit info display
        info_frame = ttk.LabelFrame(self, text="Informations de l'audit")
        info_frame.pack(fill="x", padx=10, pady=5)
        
        # Page selection
        pages_frame = ttk.LabelFrame(self, text="Pages à auditer")
        pages_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.pages_tree = ttk.Treeview(pages_frame, columns=("id", "title", "url", "status"))
        self.pages_tree.heading("id", text="N°")
        self.pages_tree.heading("title", text="Titre")
        self.pages_tree.heading("url", text="URL")
        self.pages_tree.heading("status", text="Statut")
        self.pages_tree.pack(fill="both", expand=True)
        
        # Action buttons
        action_frame = ttk.Frame(self)
        action_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Button(action_frame, text="Analyser page sélectionnée", 
                   command=self.analyze_selected).pack(side="left", padx=5)
        ttk.Button(action_frame, text="Exporter résultats", 
                   command=self.export_results).pack(side="left", padx=5)
    
    def browse_file(self):
        filepath = filedialog.askopenfilename(
            title="Sélectionner le fichier d'audit",
            filetypes=[("OpenDocument Spreadsheet", "*.ods"), ("All files", "*.*")]
        )
        if filepath:
            self.file_path_var.set(filepath)
    
    def load_file(self):
        """Load the ODS file and display audit information"""
        filepath = self.file_path_var.get()
        if not filepath:
            messagebox.showerror("Erreur", "Veuillez sélectionner un fichier")
            return
        
        try:
            self.audit_handler = RGAAAuditODSHandler(filepath)
            self.audit_data = self.audit_handler.load()
            self.populate_pages_list()
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de charger le fichier: {e}")
    
    def populate_pages_list(self):
        """Populate the pages treeview"""
        pass
    
    def analyze_selected(self):
        """Analyze the selected page"""
        pass
    
    def export_results(self):
        """Export updated ODS file"""
        pass
```

### 5. Analysis Engine Integration

Connect the ODS handler to your existing automated testing engine:

```python
class ODSAuditAnalyzer:
    """Integrates ODS handler with automated testing"""
    
    def __init__(self, ods_handler: RGAAAuditODSHandler):
        self.handler = ods_handler
        # Import your existing testing modules
        # from your_app.tests.frames import FrameTests
        # from your_app.tests.images import ImageTests
        # etc.
    
    def analyze_page(self, page_id: str) -> PageAudit:
        """Run automated tests on a page and update results"""
        page_data = self.handler.get_page_audit(page_id)
        url = page_data.url
        
        if url == "Absente" or not url.startswith("http"):
            # Mark all criteria as NA for absent pages
            for criterion in page_data.criteria:
                criterion.status = Status.NOT_APPLICABLE
            return page_data
        
        # Run automated tests
        results = self.run_automated_tests(url)
        
        # Update criteria based on test results
        for criterion_id, result in results.items():
            self.handler.update_criterion(
                page_id=page_id,
                criterion_id=criterion_id,
                status=result['status'],
                modifications=result.get('modifications', ''),
                comments=result.get('comments', '')
            )
        
        return self.handler.get_page_audit(page_id)
    
    def run_automated_tests(self, url: str) -> Dict:
        """Execute automated tests and return results"""
        results = {}
        
        # Example: Test criterion 2.1 (Frames have titles)
        # results["2.1"] = self.test_frame_titles(url)
        
        # Example: Test criterion 2.2 (Frame titles are relevant)
        # results["2.2"] = self.test_frame_title_relevance(url)
        
        # Add more automated tests...
        
        return results
```

### 6. Compliance Rate Calculation

```python
def calculate_compliance_rate(criteria: List[AuditCriterion]) -> Dict:
    """Calculate RGAA compliance statistics"""
    stats = {
        "total": len(criteria),
        "compliant": 0,
        "non_compliant": 0,
        "not_applicable": 0,
        "not_tested": 0,
        "derogations": 0,
        "by_theme": {}
    }
    
    for c in criteria:
        if c.status == Status.COMPLIANT:
            stats["compliant"] += 1
        elif c.status == Status.NON_COMPLIANT:
            stats["non_compliant"] += 1
        elif c.status == Status.NOT_APPLICABLE:
            stats["not_applicable"] += 1
        else:
            stats["not_tested"] += 1
        
        if c.derogation == Derogation.YES:
            stats["derogations"] += 1
    
    # Calculate compliance rate
    applicable = stats["compliant"] + stats["non_compliant"]
    if applicable > 0:
        stats["compliance_rate"] = (stats["compliant"] / applicable) * 100
    else:
        stats["compliance_rate"] = None  # Not calculable
    
    return stats
```

---

## 📝 Key Implementation Notes

### Reading ODS Cells

```python
from odf.table import TableCell
from odf.text import P

def get_cell_value(cell: TableCell) -> str:
    """Extract text value from an ODS cell"""
    paragraphs = cell.getElementsByType(P)
    return " ".join([str(p) for p in paragraphs]).strip() if paragraphs else ""

def set_cell_value(cell: TableCell, value: str):
    """Set text value in an ODS cell"""
    # Clear existing content
    for child in list(cell.childNodes):
        cell.removeChild(child)
    # Add new paragraph with value
    p = P(text=value)
    cell.addElement(p)
```

### Handling Row Spans and Repeated Cells

ODS files use `table:number-columns-repeated` attribute for empty cells:

```python
def expand_row(row: TableRow) -> List[str]:
    """Expand a row considering repeated cells"""
    values = []
    for cell in row.getElementsByType(TableCell):
        repeat = int(cell.getAttribute("numbercolumnsrepeated") or 1)
        value = get_cell_value(cell)
        values.extend([value] * repeat)
    return values
```

### Preserving Formulas and Formatting

When updating cells, preserve existing formulas in calculation sheets:
- `BaseDeCalcul` and `Synthèse` sheets contain formulas
- Only update data cells in `P01-P20` sheets
- Do NOT modify cells with formulas (they auto-calculate)

---

## 🔄 Workflow Summary

```
1. User loads grilleAudit.ods template (or filled audit file)
   ↓
2. Application parses Échantillon sheet to get page list
   ↓
3. For each page (P01-P20):
   a. Read existing audit data
   b. User selects page for analysis
   c. Run automated tests (optional)
   d. Display results in GUI for review/modification
   e. User validates and edits results
   f. Update P## sheet with new values
   ↓
4. Recalculate synthesis (BaseDeCalcul formulas update automatically)
   ↓
5. Save updated .ods file with results
```

---

## ⚠️ Important Constraints

1. **Preserve ODS structure**: Do not modify sheet names, column order, or formula cells
2. **Valid status values only**: Only use C, NC, NA, NT for status
3. **Valid derogation values only**: Only use D, N for derogation
4. **UTF-8 encoding**: Handle French special characters properly
5. **Backup original file**: Always create a backup before modifying
6. **Report limitations**: Clearly indicate which criteria were tested automatically vs manually

---

## 📊 Expected Output

After analysis, the `.ods` file should have:

1. **Updated P01-P20 sheets** with:
   - Status values (C/NC/NA/NT) based on test results
   - Derogation flags where applicable
   - Modifications needed for NC criteria
   - Comments explaining results

2. **Auto-updated BaseDeCalcul** (via existing formulas):
   - Matrix showing status per criterion per page

3. **Auto-updated Synthèse** (via existing formulas):
   - Statistics by theme
   - Overall compliance rate
   - Derogation count

---

## 🧪 Testing the Implementation

```python
# Test script
def test_ods_handler():
    handler = RGAAAuditODSHandler("test_audit.ods")
    audit = handler.load()
    
    # Verify structure
    assert len(audit.pages) == 20
    assert audit.pages[0].page_id == "P01"
    
    # Test update
    handler.update_criterion("P01", "2.1", Status.COMPLIANT)
    
    # Verify update
    page = handler.get_page_audit("P01")
    criterion = next(c for c in page.criteria if c.criterion_id == "2.1")
    assert criterion.status == Status.COMPLIANT
    
    # Save and reload
    handler.save("test_output.ods")
    
    print("All tests passed!")

if __name__ == "__main__":
    test_ods_handler()
```

---

## 📚 Reference Documents

- RGAA 4.1.2 specification (provided in project)
- grilleAudit.ods template (provided in project)
- odfpy documentation: https://github.com/eea/odfpy
- OpenDocument Format specification: https://docs.oasis-open.org/office/v1.2/

---

## ✅ Deliverables Checklist

- [ ] `ods_handler.py` - Core ODS reading/writing module
- [ ] `ods_models.py` - Data classes for audit structures
- [ ] `ods_analyzer.py` - Integration with automated tests
- [ ] `ods_gui.py` - Tkinter GUI components
- [ ] Unit tests for ODS handling
- [ ] Integration tests with sample audit files
- [ ] User documentation (French)
