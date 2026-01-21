# src/pii_report.py
from typing import List
from .pii_finding import PiiFinding

class PiiReport:
    """A report class to hold structured findings from the PiiScanner."""

    def __init__(self):
        self._findings: List[PiiFinding] = []

    def add(self, finding: PiiFinding):
        """Adds a new PiiFinding object to the report."""
        self._findings.append(finding)

    def has_findings(self) -> bool:
        """Returns True if there are any findings, False otherwise."""
        return bool(self._findings)

    def get_findings(self) -> List[PiiFinding]:
        """Returns the list of all PiiFinding objects."""
        return self._findings

    def to_text(self) -> str:
        """Generates a formatted text summary of the report."""
        if not self.has_findings():
            return "No PII detected"

        # The __str__ method of PiiFinding is used implicitly here
        header = "PII DETECTED:\n"
        findings_list = "\n".join(f"- {f}" for f in self._findings)
        return header + findings_list + "\n"

    def __str__(self):
        return self.to_text()
