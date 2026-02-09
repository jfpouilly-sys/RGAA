#!/usr/bin/env python3
"""
RGAA Audit Log to CSV Converter
Converts RGAA accessibility audit log files (P*.log) to CSV format.
Supports single file or batch processing of multiple log files.
"""

import re
import csv
import argparse
from pathlib import Path
from typing import List, Dict, Tuple, Optional


class RGAALogParser:
    """Parser for RGAA audit log files"""
    
    # Status symbols mapping
    STATUS_MAPPING = {
        '✓ C': 'C',
        '✗ NC': 'NC',
        '⊘ NA': 'NA',
        '? NT': 'NT'
    }
    
    def __init__(self, log_file: Path):
        self.log_file = log_file
        self.page_name = ""
        self.url = ""
        self.criteria_data = []
        
    def parse(self) -> Tuple[str, str, List[Dict]]:
        """Parse the log file and extract data"""
        with open(self.log_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract page name
        page_match = re.search(r'Analyse de (P\d+):\s*(.+)', content)
        if page_match:
            self.page_name = f"{page_match.group(1)} - {page_match.group(2).strip()}"
        
        # Extract URL
        url_match = re.search(r'🔗 (https?://[^\s]+)', content)
        if url_match:
            self.url = url_match.group(1)
        
        # Extract criteria table
        self._parse_criteria_table(content)
        
        return self.page_name, self.url, self.criteria_data
    
    def _parse_criteria_table(self, content: str):
        """Parse the criteria table from the log content"""
        # Find the table section
        table_start = content.find('Critère | Description | Statut')
        if table_start == -1:
            return
        
        # Get lines after the separator
        lines = content[table_start:].split('\n')[2:]  # Skip header and separator
        
        for line in lines:
            if not line.strip() or line.startswith('💾'):
                continue
                
            # Parse criterion line
            criterion = self._parse_criterion_line(line)
            if criterion:
                self.criteria_data.append(criterion)
    
    def _parse_criterion_line(self, line: str) -> Optional[Dict]:
        """Parse a single criterion line"""
        # Split by | and clean up
        parts = [part.strip() for part in line.split('|')]
        
        if len(parts) < 3:
            return None
        
        criterion_id = parts[0].strip()
        description = parts[1].strip() if len(parts) > 1 else ""
        status_raw = parts[2].strip() if len(parts) > 2 else ""
        
        # Skip if no criterion ID
        if not criterion_id:
            return None
        
        # Parse status and notes
        status, note = self._parse_status(status_raw)
        
        return {
            'criterion': criterion_id,
            'description': description,
            'status': status,
            'note': note
        }
    
    def _parse_status(self, status_raw: str) -> Tuple[str, str]:
        """Parse status field to extract status code and optional note"""
        # Check for simple status symbols
        for symbol, code in self.STATUS_MAPPING.items():
            if status_raw.startswith(symbol):
                # Check for additional note in parentheses
                note_match = re.search(r'\(([^)]+)\)', status_raw)
                note = note_match.group(1) if note_match else ""
                return code, note
        
        # If no symbol match, return as-is
        return status_raw, ""


class CSVWriter:
    """Writer for converting parsed data to CSV"""
    
    HEADERS = ['Page', 'URL', 'Critère', 'Description', 'Statut', 'Note']
    
    def __init__(self, output_file: Path, delimiter: str = ';'):
        self.output_file = output_file
        self.delimiter = delimiter
    
    def write(self, page_name: str, url: str, criteria_data: List[Dict]):
        """Write data to CSV file"""
        with open(self.output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter=self.delimiter)
            
            # Write header
            writer.writerow(self.HEADERS)
            
            # Write data rows
            for criterion in criteria_data:
                writer.writerow([
                    page_name,
                    url,
                    criterion['criterion'],
                    criterion['description'],
                    criterion['status'],
                    criterion['note']
                ])


def convert_log_to_csv(log_file: Path, output_dir: Optional[Path] = None, 
                       delimiter: str = ';') -> Path:
    """
    Convert a single RGAA log file to CSV
    
    Args:
        log_file: Path to the .log file
        output_dir: Directory for output CSV (default: same as log file)
        delimiter: CSV delimiter (default: ';')
    
    Returns:
        Path to the created CSV file
    """
    # Parse log file
    parser = RGAALogParser(log_file)
    page_name, url, criteria_data = parser.parse()
    
    # Determine output path
    if output_dir is None:
        output_dir = log_file.parent
    else:
        output_dir.mkdir(parents=True, exist_ok=True)
    
    csv_file = output_dir / log_file.name.replace('.log', '.csv')
    
    # Write CSV
    writer = CSVWriter(csv_file, delimiter=delimiter)
    writer.write(page_name, url, criteria_data)
    
    return csv_file


def batch_convert(input_pattern: str, output_dir: Optional[Path] = None,
                 delimiter: str = ';') -> List[Path]:
    """
    Batch convert multiple RGAA log files to CSV
    
    Args:
        input_pattern: Glob pattern for log files (e.g., 'P*.log' or '*.log')
        output_dir: Directory for output CSVs
        delimiter: CSV delimiter
    
    Returns:
        List of created CSV file paths
    """
    # Find all matching log files
    current_dir = Path('.')
    log_files = sorted(current_dir.glob(input_pattern))
    
    if not log_files:
        print(f"No log files found matching pattern: {input_pattern}")
        return []
    
    print(f"Found {len(log_files)} log file(s) to convert:")
    
    converted_files = []
    for log_file in log_files:
        print(f"  Processing: {log_file.name}...", end=' ')
        try:
            csv_file = convert_log_to_csv(log_file, output_dir, delimiter)
            converted_files.append(csv_file)
            print(f"✓ → {csv_file.name}")
        except Exception as e:
            print(f"✗ Error: {e}")
    
    return converted_files


def main():
    """Main entry point for command-line usage"""
    parser = argparse.ArgumentParser(
        description='Convert RGAA audit log files to CSV format',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Convert a single file
  python convert_rgaa_logs.py P01.log
  
  # Convert all P*.log files
  python convert_rgaa_logs.py "P*.log"
  
  # Convert to specific output directory
  python convert_rgaa_logs.py "P*.log" -o ./csv_output
  
  # Use comma delimiter instead of semicolon
  python convert_rgaa_logs.py "P*.log" -d ","
        """
    )
    
    parser.add_argument(
        'input',
        help='Input log file or glob pattern (e.g., P01.log or "P*.log")'
    )
    parser.add_argument(
        '-o', '--output',
        type=Path,
        help='Output directory for CSV files (default: same as input files)'
    )
    parser.add_argument(
        '-d', '--delimiter',
        default=';',
        help='CSV delimiter (default: semicolon ";")'
    )
    
    args = parser.parse_args()
    
    # Check if input is a pattern or single file
    input_path = Path(args.input)
    
    if '*' in args.input or '?' in args.input:
        # Batch mode
        print(f"Batch conversion mode: {args.input}")
        print("-" * 60)
        converted = batch_convert(args.input, args.output, args.delimiter)
        print("-" * 60)
        print(f"Conversion complete: {len(converted)} file(s) converted")
    else:
        # Single file mode
        if not input_path.exists():
            print(f"Error: File not found: {args.input}")
            return 1
        
        print(f"Converting: {input_path.name}...", end=' ')
        try:
            csv_file = convert_log_to_csv(input_path, args.output, args.delimiter)
            print(f"✓")
            print(f"Output: {csv_file}")
        except Exception as e:
            print(f"✗ Error: {e}")
            return 1
    
    return 0


if __name__ == '__main__':
    exit(main())
