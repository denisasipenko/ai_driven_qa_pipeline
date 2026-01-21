# src/pii_finding.py
from dataclasses import dataclass

@dataclass(frozen=True)
class PiiFinding:
    """
    A structured class to hold information about a single PII finding.
    'frozen=True' makes instances of this class immutable, which is good practice for data containers.
    """
    pii_type: str
    value: str
    start: int
    end: int

    def __str__(self) -> str:
        return f"{self.pii_type}: {self.value}"
