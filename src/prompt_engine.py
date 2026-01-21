from .files_util import FilesUtil

class PromptEngine:
    @staticmethod
    def build_prompt(prompt_template_path: str, checklist_path: str, page_object_code: str = "") -> str:
        """
        Builds a prompt by replacing placeholders in a template with checklist content and page object code.

        Args:
            prompt_template_path: The path to the prompt template file.
            checklist_path: The path to the checklist file.
            page_object_code: The Python code of the Page Object to be included in the prompt.

        Returns:
            The constructed prompt string.
        """
        template = FilesUtil.read(prompt_template_path)
        checklist = FilesUtil.read(checklist_path)

        template = template.replace("{{CHECKLIST}}", checklist)
        template = template.replace("{{PAGE_OBJECT_CODE}}", page_object_code)

        return template
