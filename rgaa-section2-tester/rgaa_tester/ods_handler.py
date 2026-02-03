# -*- coding: utf-8 -*-
"""
ODS File Handler for RGAA Audit Analysis.

Handles reading and writing grilleAudit.ods format files.
"""

import os
import shutil
from datetime import datetime
from typing import List, Dict, Optional
from odf.opendocument import load, OpenDocumentSpreadsheet
from odf.table import Table, TableRow, TableCell
from odf.text import P

from .ods_models import (
    Status,
    Derogation,
    AuditCriterion,
    PageAudit,
    AuditFile,
    CRITERIA_THEMES,
    get_all_criterion_ids
)


def get_cell_value(cell: TableCell) -> str:
    """
    Extract text value from an ODS cell.

    Args:
        cell: TableCell object

    Returns:
        String value of the cell
    """
    paragraphs = cell.getElementsByType(P)
    if not paragraphs:
        return ""
    return " ".join([str(p.firstChild) if p.firstChild else "" for p in paragraphs]).strip()


def set_cell_value(cell: TableCell, value: str):
    """
    Set text value in an ODS cell.

    Args:
        cell: TableCell object
        value: String value to set
    """
    # Clear existing content
    for child in list(cell.childNodes):
        cell.removeChild(child)

    # Add new paragraph with value
    if value:
        p = P(text=value)
        cell.addElement(p)


def expand_row(row: TableRow) -> List[str]:
    """
    Expand a row considering repeated cells.

    ODS files use table:number-columns-repeated attribute for empty cells.

    Args:
        row: TableRow object

    Returns:
        List of cell values
    """
    values = []
    for cell in row.getElementsByType(TableCell):
        repeat = cell.getAttribute("numbercolumnsrepeated")
        repeat = int(repeat) if repeat else 1
        value = get_cell_value(cell)
        values.extend([value] * repeat)
    return values


class RGAAAuditODSHandler:
    """Handler for reading and writing RGAA audit .ods files."""

    def __init__(self, filepath: str):
        """
        Initialize the ODS handler.

        Args:
            filepath: Path to the .ods file
        """
        self.filepath = filepath
        self.doc = None
        self.audit_data = None
        self._sheets_cache = {}

    def load(self) -> AuditFile:
        """
        Load and parse the .ods audit file.

        Returns:
            AuditFile object with parsed data
        """
        if not os.path.exists(self.filepath):
            raise FileNotFoundError(f"File not found: {self.filepath}")

        self.doc = load(self.filepath)
        self.audit_data = AuditFile()

        # Parse Échantillon sheet for metadata
        self._parse_echantillon_sheet()

        # Parse page audit sheets (P01-P20)
        for i in range(1, 21):
            page_id = f"P{i:02d}"
            try:
                page_audit = self._parse_page_sheet(page_id)
                if page_audit:
                    self.audit_data.pages.append(page_audit)
            except Exception as e:
                print(f"Warning: Could not parse sheet {page_id}: {e}")

        return self.audit_data

    def _get_sheet_by_name(self, sheet_name: str) -> Optional[Table]:
        """
        Get a sheet by name.

        Args:
            sheet_name: Name of the sheet

        Returns:
            Table object or None if not found
        """
        if sheet_name in self._sheets_cache:
            return self._sheets_cache[sheet_name]

        tables = self.doc.spreadsheet.getElementsByType(Table)
        for table in tables:
            name = table.getAttribute("name")
            if name == sheet_name:
                self._sheets_cache[sheet_name] = table
                return table
        return None

    def _parse_echantillon_sheet(self):
        """Parse the Échantillon (Sample) sheet for audit metadata."""
        sheet = self._get_sheet_by_name("Échantillon")
        if not sheet:
            return

        rows = sheet.getElementsByType(TableRow)
        if len(rows) < 7:
            return

        # Row 3: Date
        row_3 = expand_row(rows[2])
        if len(row_3) > 1:
            self.audit_data.date = row_3[1]

        # Row 4: Auditeur
        row_4 = expand_row(rows[3])
        if len(row_4) > 1:
            self.audit_data.auditor = row_4[1]

        # Row 5: Contexte
        row_5 = expand_row(rows[4])
        if len(row_5) > 1:
            self.audit_data.context = row_5[1]

        # Row 6: Site
        row_6 = expand_row(rows[5])
        if len(row_6) > 1:
            self.audit_data.site_url = row_6[1]

    def _parse_page_sheet(self, page_id: str) -> Optional[PageAudit]:
        """
        Parse a page audit sheet (P01-P20).

        Args:
            page_id: Page identifier (P01, P02, etc.)

        Returns:
            PageAudit object or None if sheet not found
        """
        sheet = self._get_sheet_by_name(page_id)
        if not sheet:
            return None

        rows = sheet.getElementsByType(TableRow)
        if len(rows) < 4:
            return None

        # Row 2: [Page Title] : [URL]
        row_2 = expand_row(rows[1])
        page_title = ""
        page_url = ""
        if len(row_2) > 0 and row_2[0]:
            # Parse format "Title : URL"
            parts = row_2[0].split(':', 1)
            if len(parts) == 2:
                page_title = parts[0].strip()
                page_url = parts[1].strip()
            else:
                page_title = row_2[0].strip()

        page_audit = PageAudit(
            page_id=page_id,
            title=page_title,
            url=page_url
        )

        # Parse criterion rows (starting from row 4, index 3)
        for i in range(3, len(rows)):
            row_values = expand_row(rows[i])
            if len(row_values) < 4:
                continue

            # Column A: Thématique
            # Column B: Critère
            # Column C: Recommandation
            # Column D: Statut
            # Column E: Dérogation
            # Column F: Modifications
            # Column G: Commentaires
            # Column H: Date de modification

            theme = row_values[0] if len(row_values) > 0 else ""
            criterion_id = row_values[1] if len(row_values) > 1 else ""
            description = row_values[2] if len(row_values) > 2 else ""
            status_str = row_values[3] if len(row_values) > 3 else "NT"
            derogation_str = row_values[4] if len(row_values) > 4 else "N"
            modifications = row_values[5] if len(row_values) > 5 else ""
            comments = row_values[6] if len(row_values) > 6 else ""
            modification_date = row_values[7] if len(row_values) > 7 else ""

            # Skip if no criterion ID
            if not criterion_id or not criterion_id[0].isdigit():
                continue

            criterion = AuditCriterion(
                theme=theme,
                criterion_id=criterion_id,
                description=description,
                status=Status.from_string(status_str),
                derogation=Derogation.from_string(derogation_str),
                modifications=modifications,
                comments=comments,
                modification_date=modification_date
            )

            page_audit.criteria.append(criterion)

        return page_audit

    def get_sample_pages(self) -> List[Dict]:
        """
        Extract page list from Échantillon sheet.

        Returns:
            List of dictionaries with page info
        """
        if not self.audit_data:
            self.load()

        pages = []
        for page in self.audit_data.pages:
            pages.append({
                'page_id': page.page_id,
                'title': page.title,
                'url': page.url
            })
        return pages

    def get_page_audit(self, page_id: str) -> Optional[PageAudit]:
        """
        Get audit data for a specific page.

        Args:
            page_id: Page identifier (P01, P02, etc.)

        Returns:
            PageAudit object or None if not found
        """
        if not self.audit_data:
            self.load()

        return self.audit_data.get_page(page_id)

    def update_criterion(self, page_id: str, criterion_id: str,
                        status: Status, derogation: Derogation = Derogation.NO,
                        modifications: str = "", comments: str = ""):
        """
        Update a single criterion evaluation.

        Args:
            page_id: Page identifier (P01, P02, etc.)
            criterion_id: Criterion ID (e.g., "2.1")
            status: Criterion status
            derogation: Derogation flag
            modifications: Required modifications
            comments: Comments
        """
        # Generate timestamp
        timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        # Update in-memory data
        page = self.audit_data.get_page(page_id)
        if page:
            page.update_criterion(criterion_id, status, derogation, modifications, comments, timestamp)

        # Update in ODS file
        sheet = self._get_sheet_by_name(page_id)
        if not sheet:
            return

        rows = sheet.getElementsByType(TableRow)

        # Find the row for this criterion (starting from row 4, index 3)
        for i in range(3, len(rows)):
            cells = rows[i].getElementsByType(TableCell)
            if len(cells) < 2:
                continue

            # Check criterion ID in column B (index 1)
            criterion_cell_value = get_cell_value(cells[1])
            if criterion_cell_value == criterion_id:
                # Update column D (Status) - index 3
                if len(cells) > 3:
                    set_cell_value(cells[3], status.value)

                # Update column E (Derogation) - index 4
                if len(cells) > 4:
                    set_cell_value(cells[4], derogation.value)

                # Update column F (Modifications) - index 5
                if len(cells) > 5:
                    set_cell_value(cells[5], modifications)

                # Update column G (Comments) - index 6
                if len(cells) > 6:
                    set_cell_value(cells[6], comments)

                # Update column H (Modification Date) - index 7
                if len(cells) > 7:
                    timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                    set_cell_value(cells[7], timestamp)

                break

    def update_page_audit(self, page_audit: PageAudit):
        """
        Update all criteria for a page.

        Args:
            page_audit: PageAudit object with updated data
        """
        for criterion in page_audit.criteria:
            self.update_criterion(
                page_id=page_audit.page_id,
                criterion_id=criterion.criterion_id,
                status=criterion.status,
                derogation=criterion.derogation,
                modifications=criterion.modifications,
                comments=criterion.comments
            )

    def save(self, output_path: Optional[str] = None):
        """
        Save the modified .ods file.

        Args:
            output_path: Output file path (defaults to original path)
        """
        if not self.doc:
            raise ValueError("No document loaded")

        output_path = output_path or self.filepath

        # Create backup if overwriting original
        if output_path == self.filepath:
            backup_path = self.filepath + ".backup"
            shutil.copy2(self.filepath, backup_path)

        # Save the document
        self.doc.save(output_path)

    def calculate_synthesis(self) -> Dict:
        """
        Calculate summary statistics.

        Returns:
            Dictionary with synthesis data
        """
        if not self.audit_data:
            self.load()

        return self.audit_data.get_global_statistics()
