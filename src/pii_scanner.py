# src/pii_scanner.py
import re
from typing import Pattern
from .pii_report import PiiReport
from .pii_finding import PiiFinding
from .config_loader import config_loader

class PiiScanner:
    """Scans text for PII based on rules defined in config.yaml."""

    @staticmethod
    def _find(text: str, pattern: Pattern, pii_type: str, report: PiiReport):
        """Helper method to find all matches for a given pattern and add them to the report."""
        for match in re.finditer(pattern, text):
            finding = PiiFinding(
                pii_type=pii_type,
                value=match.group(0),
                start=match.start(),
                end=match.end()
            )
            report.add(finding)

    @staticmethod
    def scan(text: str) -> PiiReport:
        """
        Scans the input text for various types of PII and returns a report.
        
        Args:
            text: The text to scan.
            
        Returns:
            A PiiReport object containing the findings.
        """
        rules = config_loader.get_rules()
        report = PiiReport()

        for rule in rules:
            pii_type = rule["name"]
            # Compile the scan pattern on the fly
            pattern = re.compile(rule["pattern"])
            PiiScanner._find(text, pattern, pii_type, report)

        return report
