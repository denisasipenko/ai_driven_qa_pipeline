# src/test_case_parser.py
from .test_case_models import TestSuite
import json
import re

def extract_json_from_response(text: str) -> str:
    """
    Cleans the raw text response from an LLM to extract a JSON object string.
    Removes markdown fences and trims whitespace.
    """
    if not text:
        raise ValueError("LLM returned empty response")

    # Remove markdown fences and trim whitespace
    cleaned_text = text.replace("```json", "").replace("```", "").strip()

    # Find the start and end of the main JSON object
    start_index = cleaned_text.find("{")
    end_index = cleaned_text.rfind("}")

    if start_index == -1 or end_index == -1:
        raise ValueError("No JSON object found in LLM output")

    return cleaned_text[start_index : end_index + 1]


def parse_test_suite(json_string: str) -> TestSuite:
    """
    Parses a JSON string into a TestSuite Pydantic object.
    """
    try:
        # Pydantic's model_validate_json handles the parsing and validation
        return TestSuite.model_validate_json(json_string)
    except Exception as e:
        raise ValueError(f"Failed to parse test suite from JSON: {e}") from e

def extract_assistant_content(raw_json: str) -> str:
    """
    Extracts the assistant's message content from a raw JSON response from an LLM.
    """
    try:
        data = json.loads(raw_json)
        return data["choices"][0]["message"]["content"]
    except (json.JSONDecodeError, KeyError, IndexError) as e:
        raise RuntimeError("Failed to extract assistant content from LLM response") from e

def extract_code_from_response(text: str) -> str:
    """
    Extracts Python code from a string that is wrapped in markdown fences (```python).
    """
    if not text:
        raise ValueError("LLM response for code generation is empty.")

    # Regex to find content between ```python and ```
    match = re.search(r"```python\n(.*?)```", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    else:
        # If no markdown fences are found, return the original text, but log a warning.
        # This can happen if the LLM doesn't follow instructions perfectly.
        # For now, let's assume it should always be wrapped.
        # raise ValueError("No Python code block found in LLM output (expected ```python\\n...```).")
        print("Warning: No ```python code block found in LLM output. Returning raw text.")
        return text.strip()
