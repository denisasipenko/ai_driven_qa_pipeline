# src/presidio_pii_scanner.py
from presidio_analyzer import AnalyzerEngine
from presidio_analyzer.pattern import Pattern
from presidio_analyzer.pattern_recognizer import PatternRecognizer
from presidio_analyzer.recognizer_registry import RecognizerRegistry # New import
from .pii_report import PiiReport
from .pii_finding import PiiFinding
from .config_loader import config_loader

class PresidioPiiScanner:
    """
    A PII scanner that uses the Presidio NLP library for detection,
    configured with custom regex rules from config.yaml only.
    """
    _analyzer = None

    @staticmethod
    def _get_analyzer() -> AnalyzerEngine:
        """Initializes and returns a singleton instance of the AnalyzerEngine,
        registering custom regex recognizers from config.yaml."""
        if PresidioPiiScanner._analyzer is None:
            custom_registry = RecognizerRegistry() # Create a new, empty registry

            # Register custom regex recognizers from config.yaml
            rules = config_loader.get_rules()
            for rule in rules:
                if "pattern" in rule and rule["pattern"]:
                    pattern = Pattern(name=f"pattern_for_{rule['name']}", regex=rule["pattern"], score=1.0)
                    
                    custom_recognizer = PatternRecognizer(
                        supported_entity=rule["name"],
                        name=f"recognizer_for_{rule['name']}",
                        patterns=[pattern]
                    )
                    custom_registry.add_recognizer(custom_recognizer)
            
            # Initialize AnalyzerEngine with our custom registry, effectively disabling built-in NLP recognizers
            PresidioPiiScanner._analyzer = AnalyzerEngine(registry=custom_registry)
        return PresidioPiiScanner._analyzer

    @staticmethod
    def scan(text: str) -> PiiReport:
        """
        Scans the input text for PII using Presidio (including custom regex rules)
        and returns a report.
        
        Args:
            text: The text to scan.
            
        Returns:
            A PiiReport object containing the findings.
        """
        analyzer = PresidioPiiScanner._get_analyzer()
        report = PiiReport()

        try:
            # Presidio's analyze method will now use only the recognizers in our custom registry.
            # We still pass entities from config to ensure a clear list of what to look for.
            analyzer_results = analyzer.analyze(text=text, language="en", 
                                                entities=config_loader.get_configured_entity_names())

            for result in analyzer_results:
                finding = PiiFinding(
                    pii_type=result.entity_type,
                    value=text[result.start:result.end],
                    start=result.start,
                    end=result.end
                )
                report.add(finding)
                
        except Exception as e:
            # This can happen if the required spaCy model is not downloaded.
            print(f"An error occurred during Presidio analysis: {e}")
            print("Please ensure you have downloaded the required spaCy model, for example: ")
            print("python -m spacy download en_core_web_lg")

        return report
