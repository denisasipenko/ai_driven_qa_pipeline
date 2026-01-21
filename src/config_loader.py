# src/config_loader.py
import re
import yaml
from typing import List, Dict, Any

class ConfigLoader:
    """A singleton class to load and cache configuration from config.yaml."""
    _instance = None
    _rules: List[Dict[str, Any]] = []

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigLoader, cls).__new__(cls)
            cls._instance._load_config()
        return cls._instance

    def _load_config(self):
        """Loads and compiles PII rules from config.yaml."""
        try:
            with open("config.yaml", "r") as f:
                config = yaml.safe_load(f)
            
            loaded_rules = config.get("pii_rules", [])
            
            # Compile regex patterns for efficiency
            for rule in loaded_rules:
                # Use mask_pattern if it exists, otherwise fall back to the main pattern
                mask_pattern_str = rule.get("mask_pattern", rule["pattern"])
                rule["compiled_mask_pattern"] = re.compile(mask_pattern_str)
            
            self._rules = loaded_rules
        except FileNotFoundError:
            self._rules = []
        except Exception as e:
            print(f"Error loading or parsing config.yaml: {e}")
            self._rules = []

    def get_rules(self) -> List[Dict[str, Any]]:
        """Returns the cached PII rules."""
        return self._rules

    def get_configured_entity_names(self) -> List[str]:
        """Returns a list of entity names configured in the PII rules."""
        return [rule["name"] for rule in self._rules]


# Create a single instance of the loader to be imported by other modules
config_loader = ConfigLoader()
