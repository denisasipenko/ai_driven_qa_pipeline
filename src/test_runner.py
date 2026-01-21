# src/test_runner.py
import pytest
import os
import subprocess
import io
import shutil
from pathlib import Path
from typing import Tuple
import sys 
from contextlib import redirect_stdout
from .files_util import FilesUtil # New import


class TestRunner:
    PYTEST_OUTPUT_FILE = "generated/pytest_output.txt"
    ALLURE_RESULTS_DIR = "generated/allure-results"
    ALLURE_REPORT_DIR = "generated/allure-report"

    @staticmethod
    def _clean_old_results():
        """Cleans up old Allure results and report directories."""
        if Path(TestRunner.ALLURE_RESULTS_DIR).exists():
            shutil.rmtree(TestRunner.ALLURE_RESULTS_DIR)
        if Path(TestRunner.ALLURE_REPORT_DIR).exists():
            shutil.rmtree(TestRunner.ALLURE_REPORT_DIR)
        
        # Also clean up old pytest output
        if Path(TestRunner.PYTEST_OUTPUT_FILE).exists():
            os.remove(TestRunner.PYTEST_OUTPUT_FILE)


    @staticmethod
    def run_tests_and_collect_results(test_dir: str = "tests") -> Tuple[str, Path, Path]:
        """
        Runs pytest tests, captures output, and collects Allure results.

        Args:
            test_dir: The directory containing the tests to run.

        Returns:
            A tuple containing:
            - Path to the pytest raw output file (str).
            - Path to the Allure results directory (Path).
            - Path to the Allure report directory (Path).
        """
        TestRunner._clean_old_results()
        
        # Ensure 'generated' directory exists
        Path("generated").mkdir(parents=True, exist_ok=True)
        Path(TestRunner.ALLURE_RESULTS_DIR).mkdir(parents=True, exist_ok=True)


        # Capture stdout of pytest.main()
        captured_output_buffer = io.StringIO()
        original_stdout = sys.stdout # Save original stdout

        try:
            sys.stdout = captured_output_buffer # Redirect sys.stdout
            
            # Run pytest programmatically
            # -s to show print statements, -q for quiet output, --alluredir to collect allure data
            # -W ignore to ignore warnings that might clutter the output
            pytest_args = [
                test_dir,
                "--alluredir", TestRunner.ALLURE_RESULTS_DIR,
                "-s", "-q", "-W", "ignore::DeprecationWarning", # Ignore some common warnings
            ]
            
            print(f"Running pytest with args: {pytest_args}", file=original_stdout) # Print to original stdout
            pytest.main(pytest_args)
        finally:
            sys.stdout = original_stdout # Restore original stdout

        captured_output = captured_output_buffer.getvalue()

        # Save captured pytest output to a file
        FilesUtil.write(TestRunner.PYTEST_OUTPUT_FILE, captured_output)
        print(f"-> Pytest raw output saved to '{TestRunner.PYTEST_OUTPUT_FILE}'")


        return (
            TestRunner.PYTEST_OUTPUT_FILE,
            Path(TestRunner.ALLURE_RESULTS_DIR),
            Path(TestRunner.ALLURE_REPORT_DIR)
        )

    @staticmethod
    def generate_allure_report(allure_results_dir: Path, allure_report_dir: Path):
        """
        Generates the Allure HTML report from collected results.

        Args:
            allure_results_dir: Path to the directory containing Allure raw results.
            allure_report_dir: Path to the directory where the HTML report will be generated.
        """
        print(f"\nGenerating Allure report from '{allure_results_dir}' to '{allure_report_dir}'...")
        try:
            # Ensure report directory exists (it should be created by allure generate, but good practice)
            allure_report_dir.mkdir(parents=True, exist_ok=True)
            subprocess.run(
                ["allure", "generate", str(allure_results_dir), "-o", str(allure_report_dir), "--clean"],
                check=True,
                capture_output=True,
                text=True
            )
            print(f"-> Allure report generated successfully at '{allure_report_dir}/index.html'")
        except FileNotFoundError:
            print("Error: 'allure' command not found. Please install Allure Commandline.")
            print("  For macOS: 'brew install allure'")
            print("  For other systems: https://allurereport.org/docs/gettingstarted-installation/")
            raise
        except subprocess.CalledProcessError as e:
            print(f"Error generating Allure report: {e}")
            print(f"Stdout: {e.stdout}")
            print(f"Stderr: {e.stderr}")
            raise
        except Exception as e:
            print(f"An unexpected error occurred during Allure report generation: {e}")
            raise
