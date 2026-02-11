# -*- coding: utf-8 -*-
"""
Data models for RGAA ODS audit files.

Defines data structures for working with grilleAudit.ods format.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Optional


class Status(Enum):
    """Audit criterion status values."""
    COMPLIANT = "C"  # Conforme
    NON_COMPLIANT = "NC"  # Non Conforme
    NOT_APPLICABLE = "NA"  # Non Applicable
    NOT_TESTED = "NT"  # Non Testé

    @classmethod
    def from_string(cls, value: str) -> 'Status':
        """Convert string value to Status enum."""
        value = value.strip().upper()
        for status in cls:
            if status.value == value:
                return status
        return cls.NOT_TESTED  # Default if unknown


class Derogation(Enum):
    """Derogation flag values."""
    YES = "D"  # Derogation applies
    NO = "N"  # No derogation (Normal)

    @classmethod
    def from_string(cls, value: str) -> 'Derogation':
        """Convert string value to Derogation enum."""
        value = value.strip().upper()
        for derog in cls:
            if derog.value == value:
                return derog
        return cls.NO  # Default if unknown


@dataclass
class AuditCriterion:
    """Represents a single criterion evaluation."""
    theme: str
    criterion_id: str
    description: str
    status: Status = Status.NOT_TESTED
    derogation: Derogation = Derogation.NO
    modifications: str = ""
    comments: str = ""
    modification_date: str = ""  # Date/time of last status modification

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'theme': self.theme,
            'criterion_id': self.criterion_id,
            'description': self.description,
            'status': self.status.value,
            'derogation': self.derogation.value,
            'modifications': self.modifications,
            'comments': self.comments,
            'modification_date': self.modification_date
        }


@dataclass
class PageAudit:
    """Represents audit results for a single page."""
    page_id: str  # P01, P02, etc.
    title: str
    url: str
    criteria: List[AuditCriterion] = field(default_factory=list)

    def get_criterion(self, criterion_id: str) -> Optional[AuditCriterion]:
        """Get a specific criterion by ID."""
        for criterion in self.criteria:
            if criterion.criterion_id == criterion_id:
                return criterion
        return None

    def update_criterion(self, criterion_id: str, status: Status,
                        derogation: Derogation = Derogation.NO,
                        modifications: str = "", comments: str = "",
                        modification_date: str = "") -> bool:
        """Update a criterion's values. Creates it if it doesn't exist."""
        criterion = self.get_criterion(criterion_id)
        if not criterion:
            # Create the criterion if it doesn't exist
            theme = CRITERIA_THEMES.get(criterion_id, "")
            criterion = AuditCriterion(
                theme=theme,
                criterion_id=criterion_id,
                description=""
            )
            # Insert in sorted position
            insert_idx = len(self.criteria)
            parts = criterion_id.split('.')
            crit_key = (int(parts[0]), int(parts[1]))
            for i, c in enumerate(self.criteria):
                c_parts = c.criterion_id.split('.')
                try:
                    c_key = (int(c_parts[0]), int(c_parts[1]))
                    if crit_key < c_key:
                        insert_idx = i
                        break
                except (ValueError, IndexError):
                    continue
            self.criteria.insert(insert_idx, criterion)

        criterion.status = status
        criterion.derogation = derogation
        criterion.modifications = modifications
        criterion.comments = comments
        criterion.modification_date = modification_date
        return True

    def get_statistics(self) -> Dict:
        """Calculate statistics for this page."""
        stats = {
            'total': len(self.criteria),
            'compliant': 0,
            'non_compliant': 0,
            'not_applicable': 0,
            'not_tested': 0,
            'derogations': 0
        }

        for criterion in self.criteria:
            if criterion.status == Status.COMPLIANT:
                stats['compliant'] += 1
            elif criterion.status == Status.NON_COMPLIANT:
                stats['non_compliant'] += 1
            elif criterion.status == Status.NOT_APPLICABLE:
                stats['not_applicable'] += 1
            else:
                stats['not_tested'] += 1

            if criterion.derogation == Derogation.YES:
                stats['derogations'] += 1

        # Calculate compliance rate
        applicable = stats['compliant'] + stats['non_compliant']
        if applicable > 0:
            stats['compliance_rate'] = (stats['compliant'] / applicable) * 100
        else:
            stats['compliance_rate'] = None

        return stats


@dataclass
class AuditFile:
    """Represents the complete audit file."""
    date: str = ""
    auditor: str = ""
    context: str = ""
    site_url: str = ""
    pages: List[PageAudit] = field(default_factory=list)

    def get_page(self, page_id: str) -> Optional[PageAudit]:
        """Get a specific page by ID."""
        for page in self.pages:
            if page.page_id == page_id:
                return page
        return None

    def get_global_statistics(self) -> Dict:
        """Calculate global statistics across all pages."""
        global_stats = {
            'total_pages': len(self.pages),
            'total_criteria': 0,
            'compliant': 0,
            'non_compliant': 0,
            'not_applicable': 0,
            'not_tested': 0,
            'derogations': 0,
            'by_theme': {}
        }

        for page in self.pages:
            stats = page.get_statistics()
            global_stats['total_criteria'] += stats['total']
            global_stats['compliant'] += stats['compliant']
            global_stats['non_compliant'] += stats['non_compliant']
            global_stats['not_applicable'] += stats['not_applicable']
            global_stats['not_tested'] += stats['not_tested']
            global_stats['derogations'] += stats['derogations']

        # Calculate global compliance rate
        applicable = global_stats['compliant'] + global_stats['non_compliant']
        if applicable > 0:
            global_stats['compliance_rate'] = (global_stats['compliant'] / applicable) * 100
        else:
            global_stats['compliance_rate'] = None

        return global_stats


# Mapping of criterion IDs to themes
CRITERIA_THEMES = {
    # IMAGES (9 criteria)
    "1.1": "IMAGES", "1.2": "IMAGES", "1.3": "IMAGES", "1.4": "IMAGES",
    "1.5": "IMAGES", "1.6": "IMAGES", "1.7": "IMAGES", "1.8": "IMAGES", "1.9": "IMAGES",

    # CADRES (2 criteria)
    "2.1": "CADRES", "2.2": "CADRES",

    # COULEURS (3 criteria)
    "3.1": "COULEURS", "3.2": "COULEURS", "3.3": "COULEURS",

    # MULTIMÉDIA (13 criteria)
    "4.1": "MULTIMÉDIA", "4.2": "MULTIMÉDIA", "4.3": "MULTIMÉDIA", "4.4": "MULTIMÉDIA",
    "4.5": "MULTIMÉDIA", "4.6": "MULTIMÉDIA", "4.7": "MULTIMÉDIA", "4.8": "MULTIMÉDIA",
    "4.9": "MULTIMÉDIA", "4.10": "MULTIMÉDIA", "4.11": "MULTIMÉDIA", "4.12": "MULTIMÉDIA",
    "4.13": "MULTIMÉDIA",

    # TABLEAUX (8 criteria)
    "5.1": "TABLEAUX", "5.2": "TABLEAUX", "5.3": "TABLEAUX", "5.4": "TABLEAUX",
    "5.5": "TABLEAUX", "5.6": "TABLEAUX", "5.7": "TABLEAUX", "5.8": "TABLEAUX",

    # LIENS (2 criteria)
    "6.1": "LIENS", "6.2": "LIENS",

    # SCRIPTS (5 criteria)
    "7.1": "SCRIPTS", "7.2": "SCRIPTS", "7.3": "SCRIPTS", "7.4": "SCRIPTS", "7.5": "SCRIPTS",

    # ÉLÉMENTS OBLIGATOIRES (10 criteria)
    "8.1": "ÉLÉMENTS OBLIGATOIRES", "8.2": "ÉLÉMENTS OBLIGATOIRES",
    "8.3": "ÉLÉMENTS OBLIGATOIRES", "8.4": "ÉLÉMENTS OBLIGATOIRES",
    "8.5": "ÉLÉMENTS OBLIGATOIRES", "8.6": "ÉLÉMENTS OBLIGATOIRES",
    "8.7": "ÉLÉMENTS OBLIGATOIRES", "8.8": "ÉLÉMENTS OBLIGATOIRES",
    "8.9": "ÉLÉMENTS OBLIGATOIRES", "8.10": "ÉLÉMENTS OBLIGATOIRES",

    # STRUCTURATION DE L'INFORMATION (4 criteria)
    "9.1": "STRUCTURATION DE L'INFORMATION", "9.2": "STRUCTURATION DE L'INFORMATION",
    "9.3": "STRUCTURATION DE L'INFORMATION", "9.4": "STRUCTURATION DE L'INFORMATION",

    # PRÉSENTATION DE L'INFORMATION (14 criteria)
    "10.1": "PRÉSENTATION DE L'INFORMATION", "10.2": "PRÉSENTATION DE L'INFORMATION",
    "10.3": "PRÉSENTATION DE L'INFORMATION", "10.4": "PRÉSENTATION DE L'INFORMATION",
    "10.5": "PRÉSENTATION DE L'INFORMATION", "10.6": "PRÉSENTATION DE L'INFORMATION",
    "10.7": "PRÉSENTATION DE L'INFORMATION", "10.8": "PRÉSENTATION DE L'INFORMATION",
    "10.9": "PRÉSENTATION DE L'INFORMATION", "10.10": "PRÉSENTATION DE L'INFORMATION",
    "10.11": "PRÉSENTATION DE L'INFORMATION", "10.12": "PRÉSENTATION DE L'INFORMATION",
    "10.13": "PRÉSENTATION DE L'INFORMATION", "10.14": "PRÉSENTATION DE L'INFORMATION",

    # FORMULAIRES (13 criteria)
    "11.1": "FORMULAIRES", "11.2": "FORMULAIRES", "11.3": "FORMULAIRES",
    "11.4": "FORMULAIRES", "11.5": "FORMULAIRES", "11.6": "FORMULAIRES",
    "11.7": "FORMULAIRES", "11.8": "FORMULAIRES", "11.9": "FORMULAIRES",
    "11.10": "FORMULAIRES", "11.11": "FORMULAIRES", "11.12": "FORMULAIRES",
    "11.13": "FORMULAIRES",

    # NAVIGATION (11 criteria)
    "12.1": "NAVIGATION", "12.2": "NAVIGATION", "12.3": "NAVIGATION",
    "12.4": "NAVIGATION", "12.5": "NAVIGATION", "12.6": "NAVIGATION",
    "12.7": "NAVIGATION", "12.8": "NAVIGATION", "12.9": "NAVIGATION",
    "12.10": "NAVIGATION", "12.11": "NAVIGATION",

    # CONSULTATION (12 criteria)
    "13.1": "CONSULTATION", "13.2": "CONSULTATION", "13.3": "CONSULTATION",
    "13.4": "CONSULTATION", "13.5": "CONSULTATION", "13.6": "CONSULTATION",
    "13.7": "CONSULTATION", "13.8": "CONSULTATION", "13.9": "CONSULTATION",
    "13.10": "CONSULTATION", "13.11": "CONSULTATION", "13.12": "CONSULTATION"
}

# Total: 106 criteria across 13 themes


def get_theme_for_criterion(criterion_id: str) -> str:
    """Get the theme for a given criterion ID."""
    return CRITERIA_THEMES.get(criterion_id, "UNKNOWN")


def get_all_criterion_ids() -> List[str]:
    """Get list of all 106 criterion IDs in order."""
    return sorted(CRITERIA_THEMES.keys(), key=lambda x: (int(x.split('.')[0]), int(x.split('.')[1])))
