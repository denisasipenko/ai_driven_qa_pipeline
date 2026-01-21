# AI-Driven QA Pipeline for Automated Testing

## 🚀 Project Overview

This project implements an **AI-driven QA Pipeline** designed to automate various stages of the software quality assurance process, from test design to defect reporting. By integrating Large Language Models (LLMs) at key junctures, the pipeline enhances efficiency, consistency, and coverage in automated testing.

The pipeline is built with Python and leverages modern tools like `pytest`, `Selenium`, `Pydantic`, and `Mistral AI` (via API). It's designed to be fully automated, reproducible, and seamlessly integrated into CI/CD environments using GitHub Actions.

## ✨ Key Features

*   **Automated Page Object Model (POM) Generation:** Automatically generates Page Object classes (e.g., `LoginPage`) directly from the HTML source of a web page using LLMs. This accelerates test development by eliminating manual POM creation.
*   **Structured Test Case Design:** Generates detailed test scenarios and structured JSON test cases (`TestSuite`, `TestCase`) from a high-level business checklist.
*   **PII Guardrails:** Integrates robust Personally Identifiable Information (PII) detection and masking, ensuring sensitive data in prompts is automatically identified, filtered, and masked based on configurable rules and NLP techniques (Presidio).
*   **Autotest Code Generation:** Produces production-ready Python autotests using `pytest` and `Selenium WebDriver` based on the structured JSON test cases and the generated Page Objects.
*   **Consolidated AI Code Review:** Performs an automated, holistic code review of all generated autotests, providing a consolidated report on functional risks, design issues, stability, maintainability, and improvement suggestions.
*   **Automated Test Execution & Reporting:** Runs the generated autotests using `pytest`, captures execution logs, and automatically generates a comprehensive `Allure Report` for detailed test results visualization.
*   **AI Analysis of Test Run Results:** Analyzes the raw test execution logs (from `pytest` and Allure data) using LLMs to provide a QA summary and dynamically identify specific test failures and their potential root causes.
*   **AI Bug Detection from Artifacts:** Conducts a high-level AI analysis across all generated artifacts (checklist, test cases, autotest code, code review) to detect potential design flaws, inconsistencies, or missed validations in the overall QA strategy.
*   **Dynamic Bug Report Generation:** Automatically generates structured JSON bug reports (`BugDetectionReport`) for each identified defect, ready for integration into bug-tracking systems like Jira or TestRail.
*   **CI/CD Integration:** Configured for continuous integration and deployment using GitHub Actions, ensuring the entire pipeline runs automatically on code changes.

## 📐 Pipeline Architecture & Workflow

The pipeline is a multi-stage process orchestrated by `pipeline_main.py`. Here's a high-level overview of the stages:

1.  **Get Page Source:** Fetches the HTML content of the target web page.
2.  **Generate Page Object:** Generates Python Page Object code from the HTML.
3.  **Build Prompt from Checklist:** Creates a detailed prompt for test case generation, incorporating the business checklist and the generated Page Object code.
4.  **PII Check:** Scans and masks PII in the prompt.
5.  **Call Mistral API (Test Cases):** Sends the PII-cleaned prompt to Mistral AI to generate JSON test cases.
6.  **Extract LLM Response Content:** Extracts the JSON string from the LLM's response.
7.  **Parse and Save Test Cases:** Parses the JSON into `TestSuite` Pydantic models and saves to `generated/test_suite.json`.
8.  **Generate Autotests & Consolidated Code Review:** Generates `pytest` + `Selenium` autotests for each test case, then performs a consolidated AI code review for all generated tests.
9.  **Run Autotests & Collect Results:** Executes the generated autotests and collects `pytest` output and Allure raw data.
10. **Generate Allure Report:** Creates a human-readable Allure HTML report.
11. **AI Analyze Test Run Results:** AI analyzes `pytest` output with LLM to create a QA summary and identify test run failures.
12. **Detect Potential Bugs from Artifacts:** AI analyzes all generated artifacts (checklist, TCs, autotests, code review) to find design flaws.
13. **Generate Bug Reports:** Dynamically creates structured JSON bug reports for each detected defect.

## 🚀 Getting Started

Follow these steps to set up and run the AI QA Pipeline locally.

### Prerequisites

*   **Python 3.13+**: Ensure Python is installed on your system.
*   **Git**: For cloning the repository.
*   **Allure Commandline Tool**: Required for generating Allure reports.
    *   **macOS**: `brew install allure`
    *   **Ubuntu/Debian**:
        ```bash
        sudo apt-add-repository ppa:qameta/allure -y
        sudo apt-get update
        sudo apt-get install allure -y
        ```
    *   **Other systems**: Refer to [Allure Installation Guide](https://allurereport.org/docs/gettingstarted-installation/)

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/your-repo-name.git
    cd your-repo-name
    ```
    *(Replace `your-username/your-repo-name` with your actual GitHub repository URL)*

2.  **Create and activate a virtual environment:**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate  # macOS/Linux
    # .venv\Scripts\activate   # Windows
    ```

3.  **Install Python dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Download spaCy model for Presidio:**
    ```bash
    .venv/bin/python -m spacy download en_core_web_lg
    ```

5.  **Set up Mistral AI API Key:**
    *   Obtain an API key from [Mistral AI](https://mistral.ai/).
    *   Create a file named `.env` in the root of your project:
        ```
        MISTRAL_API_KEY="YOUR_MISTRAL_API_KEY_HERE"
        ```
    *   Replace `"YOUR_MISTRAL_API_KEY_HERE"` with your actual API key.
    *   (Note: `.env` is already in `.gitignore` for security.)

### Local Usage

Once installed, you can run the entire pipeline from the project root directory:

```bash
.venv/bin/python -m src.pipeline_main
```

The pipeline will execute all stages, generating various artifacts in the `generated/` and `tests/` directories.

### Output Artifacts

All generated output files are saved in the `generated/` and `tests/` directories:

*   `generated/page_source.html`: Raw HTML of the target web page.
*   `pages/login_page.py`: Generated Page Object Model code.
*   `generated/final_prompt_test_cases.txt`: Final prompt used for test case generation.
*   `generated/pii_report.txt`: Report on PII found in the prompt.
*   `generated/masked_prompt.txt`: Prompt after PII masking.
*   `generated/raw_response_test_cases.json`: Raw LLM response for test cases.
*   `generated/llm_response_content_test_cases.txt`: Extracted content for test cases.
*   `generated/test_suite.json`: Structured JSON representation of test cases.
*   `tests/test_*.py`: Generated Python autotests.
*   `generated/all_code_reviews.txt`: Consolidated AI code review for all autotests.
*   `generated/pytest_output.txt`: Raw console output from `pytest` run.
*   `generated/allure-results/`: Raw data collected by Allure.
*   `generated/allure-report/`: HTML Allure report (open `index.html` in your browser).
*   `generated/test_run_analysis.json`: AI's analysis of the test run results (QA summary, detected bugs).
*   `generated/detected_bugs.json`: AI's analysis of potential design flaws from artifacts.
*   `generated/bug_report_*.json`: Structured JSON bug reports generated from test run failures.

## ⚙️ Configuration

*   **`config.yaml`**: Define PII detection patterns and masking strategies.
*   **`prompts/`**: Modify existing prompts or add new ones to fine-tune LLM behavior.
*   **`checklist_login.txt`**: Your input checklist of business requirements.
*   **`PipelineMain.TARGET_URL`**: Change this variable in `src/pipeline_main.py` to point to your desired target web application.

## 🌐 CI/CD Integration (GitHub Actions)

The project includes a GitHub Actions workflow (`.github/workflows/main.yml`) to automate the entire pipeline.

### Setup for GitHub Actions

1.  **Commit your code** to a GitHub repository.
2.  **Add `MISTRAL_API_KEY` as a GitHub Secret**:
    *   In your GitHub repository, navigate to `Settings` -> `Secrets and variables` -> `Actions`.
    *   Click `New repository secret`.
    *   Name the secret: `MISTRAL_API_KEY`.
    *   Paste your actual Mistral AI API key into the `Value` field.
    *   Click `Add secret`.
    *   **(This is critical for the LLM calls in CI/CD)**

3.  **Trigger the Workflow**: Push changes to `main` or open a Pull Request.

The workflow will run on an Ubuntu environment, install all dependencies, run the pipeline, and upload the Allure report and other generated artifacts as workflow artifacts.
