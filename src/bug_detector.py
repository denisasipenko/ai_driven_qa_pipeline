# src/bug_detector.py
from pathlib import Path
import json
from typing import Union

from .files_util import FilesUtil
from .mistral_client import MistralClient
from .test_case_parser import extract_json_from_response
from .test_case_models import BugDetectionReport, NoBugsFoundStatus, BugDetectionOutput

class BugDetector:
    BUG_DETECTION_PROMPT_PATH = "prompts/05_bug_report_from_failure.txt"
    OUTPUT_FILE_NAME = "detected_bugs.json"

    @staticmethod
    def detect_bugs_from_artifacts(
        original_checklist: str,
        generated_test_cases_json: str,
        generated_autotests_code: str,
        ai_code_review: str
    ) -> Path:
        """
        Analyzes all generated artifacts to detect potential defects and
        generates a structured bug report or a 'no bugs found' status.

        Args:
            original_checklist: Content of the original checklist.
            generated_test_cases_json: JSON string of the generated test cases.
            generated_autotests_code: Consolidated code of all generated autotests.
            ai_code_review: Consolidated AI code review for all autotests.

        Returns:
            Path to the generated JSON file (either a bug report or status).
        """
        bug_detection_prompt_template = FilesUtil.read(BugDetector.BUG_DETECTION_PROMPT_PATH)

        # Prepare the prompt for the LLM
        prompt_for_llm = bug_detection_prompt_template.replace("{{CHECKLIST}}", original_checklist)
        prompt_for_llm = prompt_for_llm.replace("{{TESTCASES}}", generated_test_cases_json)
        prompt_for_llm = prompt_for_llm.replace("{{REVIEW}}", ai_code_review)
        prompt_for_llm = prompt_for_llm.replace("{{TESTS}}", generated_autotests_code)

        print("\nDetecting potential bugs from generated artifacts...")
        try:
            raw_llm_response = MistralClient.call(prompt_for_llm)
            
            # Extract clean JSON from markdown fences
            json_str = extract_json_from_response(raw_llm_response)
            
            # Parse the JSON into the appropriate Pydantic model
            # This handles both BugDetectionReport and NoBugsFoundStatus
            try:
                bug_detection_output: BugDetectionOutput = BugDetectionReport.model_validate_json(json_str)
            except Exception:
                # If it's not a full bug report, try to parse as NoBugsFoundStatus
                bug_detection_output: BugDetectionOutput = NoBugsFoundStatus.model_validate_json(json_str)
            
            # Ensure output directory exists
            Path("generated").mkdir(parents=True, exist_ok=True)
            
            output_file_path = Path("generated") / BugDetector.OUTPUT_FILE_NAME
            FilesUtil.write(str(output_file_path), bug_detection_output.model_dump_json(indent=2))
            
            print(f"-> Bug detection report saved to '{output_file_path}'")
            return output_file_path

        except Exception as e:
            print(f"Error detecting bugs: {e}")
            print(f"Raw LLM response (for debugging): {raw_llm_response}")
            raise
