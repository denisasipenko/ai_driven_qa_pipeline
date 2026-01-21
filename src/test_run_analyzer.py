# src/test_run_analyzer.py
from pathlib import Path
from typing import List

from .files_util import FilesUtil
from .mistral_client import MistralClient
from .test_case_parser import extract_json_from_response, extract_assistant_content
from .test_case_models import TestRunAnalysisOutput

class TestRunAnalyzer:
    ANALYSIS_PROMPT_PATH = "prompts/06_test_run_analysis_and_bug_report.txt"
    OUTPUT_FILE_NAME = "test_run_analysis.json"

    @staticmethod
    def analyze_test_run(pytest_output_path: str) -> Path:
        """
        Analyzes raw pytest output using LLM to generate a QA summary and detect bugs.

        Args:
            pytest_output_path: Path to the raw pytest output file.

        Returns:
            Path to the generated JSON file with analysis output.
        """
        try:
            pytest_output_content = FilesUtil.read(pytest_output_path)
        except Exception as e:
            print(f"Error: Could not read pytest output from '{pytest_output_path}': {e}")
            raise

        analysis_prompt_template = FilesUtil.read(TestRunAnalyzer.ANALYSIS_PROMPT_PATH)

        # Prepare the prompt for the LLM
        prompt_for_llm = analysis_prompt_template.replace("{{PYTEST_OUTPUT}}", pytest_output_content)

        print("\nAnalyzing test run results with AI...")
        try:
            raw_llm_response = MistralClient.call(prompt_for_llm)
            
            # Extract clean JSON from markdown fences
            llm_content = extract_assistant_content(raw_llm_response)
            json_str = extract_json_from_response(llm_content)
            
            # Parse the JSON into the TestRunAnalysisOutput Pydantic model
            analysis_output = TestRunAnalysisOutput.model_validate_json(json_str)
            
            # Ensure output directory exists
            Path("generated").mkdir(parents=True, exist_ok=True)
            
            output_file_path = Path("generated") / TestRunAnalyzer.OUTPUT_FILE_NAME
            FilesUtil.write(str(output_file_path), analysis_output.model_dump_json(indent=2))
            
            print(f"-> Test run analysis saved to '{output_file_path}'")
            return output_file_path

        except Exception as e:
            print(f"Error analyzing test run or parsing LLM response: {e}")
            print(f"Raw LLM response (for debugging): {raw_llm_response}")
            raise
