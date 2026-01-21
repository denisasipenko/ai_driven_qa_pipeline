import json
import os # New import
from pathlib import Path # New import
from typing import List
from .prompt_engine import PromptEngine
from .files_util import FilesUtil
from .mistral_client import MistralClient
from .presidio_pii_scanner import PresidioPiiScanner
from .pii_masker import PiiMasker
from .pii_finding import PiiFinding
from .test_case_models import TestSuite, BugReport, BugDetectionReport, TestRunAnalysisOutput # Updated import
from .test_case_parser import extract_json_from_response, parse_test_suite, extract_assistant_content # Updated import
from .autotest_generator import AutotestGenerator
from .page_source_getter import PageSourceGetter
from .page_object_generator import PageObjectGenerator
from .bug_report_generator import BugReportGenerator
from .bug_detector import BugDetector # New import
from .test_runner import TestRunner # New import
from .test_run_analyzer import TestRunAnalyzer # New import


class PipelineMain:
    # Define the target URL for page object generation
    TARGET_URL = "https://www.saucedemo.com/" 
    # This will be updated by Stage 2 with the path to the generated page object
    GENERATED_PAGE_OBJECT_PATH = "" 

    @staticmethod
    def filter_overlapping_findings(findings: List[PiiFinding]) -> List[PiiFinding]:
        """
        Filters a list of PiiFinding objects to remove findings that overlap.
        If two findings overlap, the longer one is kept.
        """
        if not findings:
            return []

        # Sort by start index ascending, and by length descending to prioritize longer matches
        sorted_findings = sorted(findings, key=lambda f: (f.start, -(f.end - f.start)))
        
        filtered_list = []
        last_finding_end = -1

        for finding in sorted_findings:
            # Only add the finding if it does not overlap with the last one added.
            if finding.start >= last_finding_end:
                filtered_list.append(finding)
                last_finding_end = finding.end
        
        return filtered_list

    # extract_assistant_content is now moved to test_case_parser.py

    @staticmethod
    def run():
        """
        The main entry point for the AI QA Pipeline.
        """
        print("=== AI QA PIPELINE STARTED ===")

        # STAGE 1. GET PAGE SOURCE
        print("\nStage 1: Getting page source for URL...")
        page_html_path = "generated/page_source.html"
        try:
            page_html = PageSourceGetter.get_source(PipelineMain.TARGET_URL)
            FilesUtil.write(page_html_path, page_html)
            print(f"-> Page source saved to '{page_html_path}' for {PipelineMain.TARGET_URL}")
        except Exception as e:
            print(f"Error in Stage 1: Failed to get page source: {e}")
            return # Exit pipeline on failure

        # --- NEW STAGE 2: GENERATE PAGE OBJECT ---
        print("\nStage 2: Generating Page Object...")
        page_object_name = "login" # Or derive from TARGET_URL
        try:
            generated_po_path = PageObjectGenerator.generate_page_object(page_html_path, page_object_name)
            PipelineMain.GENERATED_PAGE_OBJECT_PATH = generated_po_path
            print(f"-> Page Object generated and saved to '{generated_po_path}'")
        except Exception as e:
            print(f"Error in Stage 2: Failed to generate Page Object: {e}")
            return # Exit pipeline on failure


        # --- STAGE 3 (was 1). BUILD PROMPT FROM CHECKLIST ---
        print("\nStage 3: Building prompt from checklist...")
        generated_page_object_code = FilesUtil.read(PipelineMain.GENERATED_PAGE_OBJECT_PATH)
        prompt = PromptEngine.build_prompt(
            "prompts/02_test_cases_from_checklist.txt",
            "checklist_login.txt",
            generated_page_object_code
        )
        FilesUtil.write("generated/final_prompt_test_cases.txt", prompt)
        print("-> Prompt for test cases successfully generated and saved to 'generated/final_prompt_test_cases.txt'")

        # --- STAGE 4 (was 2). PII CHECK ---
        print("\nStage 4: Scanning prompt for PII...")
        pii_report = PresidioPiiScanner.scan(prompt)
        
        if pii_report.has_findings():
            original_findings = pii_report.get_findings()
            filtered_findings = PipelineMain.filter_overlapping_findings(original_findings)
            
            pii_report._findings = filtered_findings

        prompt_to_send = prompt
        if pii_report.has_findings():
            pii_report_content = pii_report.to_text()
            print("PII Detected (after filtering overlaps):")
            print(pii_report_content)
            FilesUtil.write("generated/pii_report.txt", pii_report_content)
            print("-> PII report saved to 'generated/pii_report.txt'")
            
            prompt_to_send = PiiMasker.mask(prompt, pii_report.get_findings())
            FilesUtil.write("generated/masked_prompt.txt", prompt_to_send)
            print("-> PII found and masked. Masked prompt saved to 'generated/masked_prompt.txt'")
        else:
            print("-> No PII found in the prompt.")

        # --- STAGE 5 (was 3). CALL MISTRAL API (for Test Cases) ---
        print("\nStage 5: Calling Mistral API to generate Test Cases...")
        raw_response = MistralClient.call(prompt_to_send)
        FilesUtil.write("generated/raw_response_test_cases.json", raw_response)
        print("-> Raw response for test cases saved to 'generated/raw_response_test_cases.json'")

        # --- STAGE 6 (was 4). EXTRACT LLM RESPONSE CONTENT (for Test Cases) ---
        print("\nStage 6: Extracting content from LLM response (Test Cases)...")
        llm_response_content_test_cases = extract_assistant_content(raw_response)
        FilesUtil.write("generated/llm_response_content_test_cases.txt", llm_response_content_test_cases)
        print("-> Extracted LLM response content for test cases saved to 'generated/llm_response_content_test_cases.txt'")

        # --- STAGE 7 (was 5). PARSE AND SAVE TEST CASES ---
        print("\nStage 7: Parsing and saving test cases...")
        try:
            cleaned_json_string = extract_json_from_response(llm_response_content_test_cases)
            test_suite = parse_test_suite(cleaned_json_string)
            FilesUtil.write("generated/test_suite.json", test_suite.model_dump_json(indent=2))
            print("-> Structured test suite saved to 'generated/test_suite.json'")
        except Exception as e:
            print(f"Error in Stage 7: Failed to parse test cases: {e}")
            print("This usually means the LLM did not return a valid JSON format.")
            return

        # --- STAGE 8 (was 6). GENERATE AUTOTESTS ---
        print("\nStage 8: Generating autotests and performing consolidated code review...")
        generated_page_object_code_for_autotests = FilesUtil.read(PipelineMain.GENERATED_PAGE_OBJECT_PATH)
        AutotestGenerator.generate_for_test_suite(
            "generated/test_suite.json",
            generated_page_object_code_for_autotests
        )
        print("-> Autotest generation process initiated.")


        # --- NEW STAGE 9: RUN AUTOTESTS & COLLECT RESULTS ---
        print("\nStage 9: Running autotests and collecting results...")
        pytest_output_path, allure_results_path, allure_report_path = TestRunner.run_tests_and_collect_results()
        print("-> Autotests run, results collected.")

        # --- NEW STAGE 10: GENERATE ALLURE REPORT ---
        print("\nStage 10: Generating Allure report...")
        try:
            TestRunner.generate_allure_report(allure_results_path, allure_report_path)
            print("-> Allure report generated.")
        except Exception as e:
            print(f"Error in Stage 10: Failed to generate Allure report: {e}")
            # Decide if pipeline should continue without Allure report
            # For now, it will continue, but the report might be missing.


        # --- STAGE 11 (was 9). AI ANALYZE TEST RUN RESULTS ---
        print("\nStage 11: AI Analyzing test run results...")
        try:
            test_run_analysis_output_path = TestRunAnalyzer.analyze_test_run(pytest_output_path)
            # Store the analysis output for subsequent stages
            # If you need to access the content later:
            # test_run_analysis_content = FilesUtil.read(test_run_analysis_output_path)
            print("-> AI test run analysis completed.")
        except Exception as e:
            print(f"Error in Stage 11: Failed to analyze test run results: {e}")
            return # Exit pipeline on failure


        # --- STAGE 12 (was 10). DETECT POTENTIAL BUGS FROM ARTIFACTS ---
        print("\nStage 12: Detecting potential bugs from generated artifacts (design-time analysis)...")
        try:
            # Gather all necessary artifacts
            original_checklist_content = FilesUtil.read("checklist_login.txt")
            generated_test_cases_json_content = FilesUtil.read("generated/test_suite.json")
            ai_code_review_content = FilesUtil.read("generated/all_code_reviews.txt")
            
            # Read all generated autotest files
            autotest_dir = AutotestGenerator.OUTPUT_DIR
            all_autotest_code = ""
            # Ensure 'tests' directory exists before listing
            Path(autotest_dir).mkdir(parents=True, exist_ok=True) 
            for filename in os.listdir(autotest_dir):
                if filename.endswith(".py"):
                    file_path = Path(autotest_dir) / filename
                    all_autotest_code += f"\n--- FILE: {filename} ---\n\n"
                    all_autotest_code += FilesUtil.read(str(file_path))
            
            BugDetector.detect_bugs_from_artifacts(
                original_checklist=original_checklist_content,
                generated_test_cases_json=generated_test_cases_json_content,
                generated_autotests_code=all_autotest_code,
                ai_code_review=ai_code_review_content
            )
            print("-> Bug detection from artifacts completed.")
        except Exception as e:
            print(f"Error in Stage 12: Failed to detect bugs from artifacts: {e}")
            return # Exit pipeline on failure


        # --- STAGE 13 (was 12). GENERATE BUG REPORT (from real analysis) ---
        print("\nStage 13: Generating bug report (from real test run analysis)...")
        try:
            # Read the analysis output from Stage 11
            test_run_analysis_content = FilesUtil.read(str(test_run_analysis_output_path))
            
            # This content contains 'qa_summary' and 'detected_bugs'
            # We need to extract the bug reports from it if any
            test_run_analysis_output = TestRunAnalysisOutput.model_validate_json(test_run_analysis_content)

            if test_run_analysis_output.detected_bugs:
                for idx, bug_report_data in enumerate(test_run_analysis_output.detected_bugs):
                    # Convert Pydantic BugDetectionReport to string for BugReportGenerator
                    # BugReportGenerator expects failure_facts as a string, not structured data directly
                    # Re-prompting for each bug to fit the BugReportGenerator's prompt
                    # This is slightly redundant but keeps BugReportGenerator simple
                    bug_report_json_string = bug_report_data.model_dump_json(indent=2)
                    
                    # Call BugReportGenerator (which uses the old prompt for formatting)
                    # The prompt expects "failure_facts" so we pass the JSON representing the bug
                    BugReportGenerator.generate_bug_report(bug_report_json_string, suffix=f"_{idx+1}")
                print(f"-> {len(test_run_analysis_output.detected_bugs)} bug report(s) generated from test run analysis.")
            else:
                print("-> No bugs detected in test run, skipping bug report generation.")

        except Exception as e:
            print(f"Error in Stage 13: Failed to generate bug reports from analysis: {e}")
            print("This usually means the LLM did not return a valid JSON format in Stage 11.")
            return # Exit pipeline on failure


        print("\n=== AI QA PIPELINE FINISHED ===")


def main():
    """
    Script entry point, runs the main pipeline logic.
    """
    PipelineMain.run()

if __name__ == "__main__":
    main()
