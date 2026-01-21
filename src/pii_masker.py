# src/pii_masker.py
import re
from typing import List, Dict, Any
from .config_loader import config_loader
from .pii_finding import PiiFinding

class PiiMasker:
    """Masks PII in a given text based on specific findings."""

    _rules_map: Dict[str, Dict[str, Any]] = {}

    @staticmethod
    def _get_rules_map() -> Dict[str, Dict[str, Any]]:
        """Builds a map of pii_type to its rule for quick lookup."""
        if not PiiMasker._rules_map:
            rules = config_loader.get_rules()
            # Assuming 'name' in rule is the pii_type
            PiiMasker._rules_map = {rule["name"]: rule for rule in rules}
        return PiiMasker._rules_map

    @staticmethod
    def mask(text: str, findings: List[PiiFinding]) -> str:
        """
        Masks PII in the input text based on a list of PiiFinding objects.
        
        Args:
            text: The original text.
            findings: A list of PiiFinding objects.
            
        Returns:
            The text with PII masked.
        """
        # Convert text to a list of characters for efficient in-place replacement
        masked_text_chars = list(text) 
        rules_map = PiiMasker._get_rules_map()

        # Iterate through findings in reverse order to avoid altering indices of subsequent findings
        for finding in sorted(findings, key=lambda f: f.start, reverse=True):
            rule = rules_map.get(finding.pii_type)
            if not rule:
                # If no rule is found for this PII type, skip masking it
                continue

            strategy = rule.get("strategy", "replace") # Default to 'replace'
            
            replacement_str = ""
            if strategy == "redact":
                replacement_str = '*' * len(finding.value)
            elif strategy == "replace":
                # For 'replace' strategy, we use the mask_replacement from the rule.
                # Special handling for PASSWORD where the replacement might contain backreferences like \1
                # We need to re-evaluate the replacement string with actual group values if needed.
                # However, since we are replacing a slice, simple string replacement is used.
                # The regex-based masking with \1 was handled by re.sub in the previous version.
                # Here, we need to apply the replacement to the *found value* if it has groups.
                # For simplicity, if it's 'replace', we use the static mask_replacement defined.
                # If the user wants dynamic \1 style replacement with finding.value,
                # they need to specify the exact replacement logic in config.
                replacement_str = rule["mask_replacement"]
                
                # A hack to handle the \1 in password replacement for now, as simple slicing doesn't support it.
                # This assumes the original mask_replacement has \1 and we need to apply it to finding.value
                # This part might need further refinement based on specific complex masking requirements.
                # For this specific case (password: \1[SECRET]), it's better to make mask_replacement explicit
                # like "password: [SECRET]" rather than using \1 if we replace by slice.
                # Let's assume for 'replace' strategy, mask_replacement is already the final string.
                # The current config.yaml has '\1[SECRET]' for password.
                # This needs to be applied by finding the first group again in the exact match.
                
                # Re-applying a small regex to the exact finding.value to handle \1 if needed.
                if '\\1' in replacement_str:
                    # This is specifically for password, assuming it's the only one using \1
                    original_mask_pattern = re.compile(rule["mask_pattern"])
                    match_in_finding_value = original_mask_pattern.match(finding.value) # Use match to check from start
                    if match_in_finding_value:
                        # Reconstruct replacement using matched groups
                        replacement_str = original_mask_pattern.sub(replacement_str, finding.value, count=1)
                    else:
                        # Fallback if pattern doesn't match finding.value itself, though it should.
                        replacement_str = '*' * len(finding.value) # Fallback to redact
                
            else:
                # Handle unknown strategy, default to redaction or raise an error
                replacement_str = '*' * len(finding.value) # Fallback to redact

            # Replace the characters in the list slice
            masked_text_chars[finding.start:finding.end] = list(replacement_str)
        
        return "".join(masked_text_chars)
