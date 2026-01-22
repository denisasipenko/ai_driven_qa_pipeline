# src/bug_report_generator.py
import json
from pathlib import Path
from typing import List

from .files_util import FilesUtil
from .mistral_client import MistralClient
from .test_case_models import BugReport
from .test_case_parser import extract_json_from_response, parse_test_suite # Re-using extract_json for code, but here for JSON

class BugReportGenerator:
    BUG_REPORT_PROMPT_PATH = "prompts/05_bug_report_from_failure.txt"
    OUTPUT_DIR = "generated"

    @staticmethod
    def generate_bug_report(failure_facts: str) -> Path:
        """
        Generates a structured bug report based on provided failure facts.

        Args:
            failure_facts: A string containing details about the test failure
                           (steps, input data, expected/actual results, errors, stack traces).

        Returns:
            Path to the generated bug report JSON file.
        """
        bug_report_prompt_template = FilesUtil.read(BugReportGenerator.BUG_REPORT_PROMPT_PATH)
        
        # Prepare the prompt for the LLM
        prompt_for_llm = bug_report_prompt_template.replace("{{FAILURE_FACTS}}", failure_facts)

        print("\nGenerating bug report...")
        try:
            raw_llm_response = MistralClient.call(prompt_for_llm)
            
            # Extract clean JSON from markdown fences
            json_str = extract_json_from_response(raw_llm_response)
            
            # Parse the JSON into the BugReport Pydantic model
            bug_report_data = BugReport.model_validate_json(json_str)
            
            # Ensure output directory exists
            Path(BugReportGenerator.OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
            
            output_file_path = Path(BugReportGenerator.OUTPUT_DIR) / "bug_report.json"
            FilesUtil.write(str(output_file_path), bug_report_data.model_dump_json(indent=2))
            
            print(f"-> Structured bug report saved to '{output_file_path}'")
            return output_file_path

        except Exception as e:
            print(f"Error generating bug report: {e}")
            print(f"Raw LLM response (for debugging): {raw_llm_response}")
            raise
