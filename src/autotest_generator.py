# src/autotest_generator.py
import json
import re
import codecs
import os
from typing import List
from pathlib import Path

from .test_case_models import TestSuite, TestCase
from .mistral_client import MistralClient
from .files_util import FilesUtil
from .test_case_parser import extract_json_from_response, extract_assistant_content, extract_code_from_response # Updated import

class AutotestGenerator:
    GENERATION_PROMPT_PATH = "prompts/03_autotest_from_testcase.txt"
    CODE_REVIEW_PROMPT_PATH = "prompts/04_code_review.txt" # Now for consolidated review
    OUTPUT_DIR = "tests"

    @staticmethod
    def _sanitize_test_name(title: str, test_id: str) -> str:
        """Sanitizes a title and ID to create a valid Python function name."""
        # Replace non-alphanumeric characters with underscores
        sanitized_title = re.sub(r'[^a-zA-Z0-9_]', '_', title)
        # Remove leading/trailing underscores and multiple underscores
        sanitized_title = re.sub(r'_+', '_', sanitized_title).strip('_')
        # Add ID at the end to ensure uniqueness and traceability
        return f"test_{sanitized_title.lower()}_{test_id.lower()}"

    @staticmethod
    def generate_for_test_suite(test_suite_json_path: str, page_object_code: str):
        """
        Generates autotest files for each test case, then performs a single consolidated
        code review for all generated tests.
        """
        try:
            test_suite_json = FilesUtil.read(test_suite_json_path)
            test_suite: TestSuite = TestSuite.model_validate_json(test_suite_json)
        except Exception as e:
            print(f"Error: Could not load or parse test suite from '{test_suite_json_path}': {e}")
            return

        if not test_suite.testcases:
            print("No test cases found in the test suite. Skipping autotest generation.")
            return

        # Ensure output directory for tests exists
        Path(AutotestGenerator.OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
        # Ensure 'generated' directory exists for the consolidated review file
        Path("generated").mkdir(parents=True, exist_ok=True)


        autotest_generation_prompt_template = FilesUtil.read(AutotestGenerator.GENERATION_PROMPT_PATH)
        code_review_prompt_template = FilesUtil.read(AutotestGenerator.CODE_REVIEW_PROMPT_PATH)

        all_generated_code_blocks = [] # To collect code for consolidated review

        print(f"\nStarting autotest generation for {len(test_suite.testcases)} test cases...")
        for test_case in test_suite.testcases:
            print(f"-> Generating code for Test Case ID: {test_case.id} - '{test_case.title}'")

            # Prepare the prompt for this specific test case
            test_case_json_str = test_case.model_dump_json(indent=2)
            prompt_for_llm = autotest_generation_prompt_template.replace("{{TEST_CASE_JSON}}", test_case_json_str)
            prompt_for_llm = prompt_for_llm.replace("{{PAGE_OBJECT_CODE}}", page_object_code)

            try:
                # Call LLM to generate code
                raw_llm_response_code = MistralClient.call(prompt_for_llm)
                
                # Extract the assistant's content from the raw API response JSON
                llm_response_content_for_code = extract_assistant_content(raw_llm_response_code)
                
                # Extract clean code from markdown fences within the content
                generated_code_str = extract_code_from_response(llm_response_content_for_code)
                
                # Decode escape sequences like \n and \t into real characters
                final_code = codecs.decode(generated_code_str, 'unicode_escape')

                # Sanitize test name for filename and function name
                file_name_base = AutotestGenerator._sanitize_test_name(test_case.title, test_case.id)
                test_file_name = file_name_base + ".py"
                output_test_file_path = Path(AutotestGenerator.OUTPUT_DIR) / test_file_name

                FilesUtil.write(str(output_test_file_path), final_code)
                print(f"   Generated: {output_test_file_path}")

                # Collect code for consolidated review
                all_generated_code_blocks.append(f"\n--- FILE: {test_file_name} ---\n\n{final_code}")


            except Exception as e:
                print(f"   Error generating code for {test_case.id}: {e}")
                print(f"   Raw LLM response (code generation): {raw_llm_response_code if 'raw_llm_response_code' in locals() else 'N/A'}")

        print("\nAutotest generation finished.")

        # --- Perform Consolidated Code Review for all tests ---
        if all_generated_code_blocks:
            print(f"\nPerforming consolidated code review for {len(test_suite.testcases)} tests...")
            full_code_for_review = "".join(all_generated_code_blocks)
            
            review_prompt_for_llm = code_review_prompt_template.replace("{{ALL_TEST_CODE}}", full_code_for_review)
            raw_llm_response_review = MistralClient.call(review_prompt_for_llm)
            
            review_content = extract_assistant_content(raw_llm_response_review)
            
            consolidated_review_path = "generated/all_code_reviews.txt"
            FilesUtil.write(consolidated_review_path, review_content)
            print(f"-> Consolidated code review report saved to '{consolidated_review_path}'")
        else:
            print("\nNo tests generated, skipping consolidated code review.")

