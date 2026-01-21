# src/page_object_generator.py
import codecs
from pathlib import Path
import re

from .files_util import FilesUtil
from .mistral_client import MistralClient
from .test_case_parser import extract_assistant_content, extract_code_from_response # Updated imports

class PageObjectGenerator:
    GENERATION_PROMPT_PATH = "prompts/01_page_object_from_html.txt"
    OUTPUT_DIR = "pages" # Where the generated page objects will live

    @staticmethod
    def generate_page_object(html_content_path: str, page_name: str) -> str:
        """
        Generates a Page Object Model (POM) class based on provided HTML content.

        Args:
            html_content_path: Path to the HTML content file.
            page_name: The name of the page (e.g., "login", "products") to determine class name and file name.

        Returns:
            The path to the generated Page Object file.
        """
        try:
            html_content = FilesUtil.read(html_content_path)
        except Exception as e:
            print(f"Error: Could not read HTML content from '{html_content_path}': {e}")
            raise

        generation_prompt_template = FilesUtil.read(PageObjectGenerator.GENERATION_PROMPT_PATH)

        # Prepare the prompt for the LLM
        prompt_for_llm = generation_prompt_template.replace("{{PAGE_HTML}}", html_content)
        
        print(f"\nGenerating Page Object for page '{page_name}'...")
        try:
            raw_llm_response = MistralClient.call(prompt_for_llm)
            
            # Extract the assistant's content from the raw API response JSON
            llm_response_content = extract_assistant_content(raw_llm_response)
            
            # Extract clean code from markdown fences within the content
            generated_code_str = extract_code_from_response(llm_response_content)
            
            # Decode escape sequences like \n and \t into real characters
            final_code = codecs.decode(generated_code_str, 'unicode_escape')

            # Determine class name (e.g., "Login" -> "LoginPage")
            class_name = f"{page_name.capitalize()}Page"
            # Determine file name (e.g., "login" -> "login_page.py")
            file_name = f"{page_name.lower()}_page.py"
            output_file_path = Path(PageObjectGenerator.OUTPUT_DIR) / file_name

            # Make sure the output directory exists
            Path(PageObjectGenerator.OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
            
            FilesUtil.write(str(output_file_path), final_code)
            print(f"-> Generated Page Object saved to '{output_file_path}'")
            return str(output_file_path)

        except Exception as e:
            print(f"Error generating Page Object for '{page_name}': {e}")
            print(f"Raw LLM response (for debugging): {raw_llm_response}")
            raise
