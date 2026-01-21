# src/test_case_models.py
from typing import List, Optional, Union
from pydantic import BaseModel

class TestCase(BaseModel):
    """
    A Pydantic model representing a single test case, equivalent to the TestCase POJO.
    """
    id: str
    title: str
    type: str
    steps: List[str]
    expected: str

class TestSuite(BaseModel):
    """
    A Pydantic model representing a suite of test cases, equivalent to the TestSuite POJO.
    """
    testcases: List[TestCase]

class BugReport(BaseModel):
    """
    A Pydantic model representing a structured bug report.
    """
    title: str
    environment: str
    reproduction_steps: List[str]
    expected_result: str
    actual_result: str
    severity: str
    attachments: Optional[List[str]] = None # Attachments can be optional

class BugDetectionReport(BaseModel):
    """
    A Pydantic model representing a structured bug report detected by AI analysis.
    Corresponds to the JSON structure from the prompt.
    """
    title: str
    severity: str
    priority: str
    environment: str = "SauceDemo web" # Default value as per prompt
    preconditions: str
    reproduction_steps: List[str]
    actual_result: str
    expected_result: str
    probable_root_cause: str
    evidence: str # Could be references to specific test cases or review points

class NoBugsFoundStatus(BaseModel):
    """
    A Pydantic model for the 'no bugs found' status from AI analysis.
    """
    status: str = "NO_BUGS_FOUND"

# Use Union to indicate the output can be either a BugDetectionReport or NoBugsFoundStatus
BugDetectionOutput = Union[BugDetectionReport, NoBugsFoundStatus]

class TestRunAnalysisOutput(BaseModel):
    """
    A Pydantic model representing the structured output of AI analysis of a test run.
    It includes a QA summary and a list of detected bugs (if any).
    """
    qa_summary: str
    detected_bugs: List[BugDetectionReport]
