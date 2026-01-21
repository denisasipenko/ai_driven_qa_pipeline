from pathlib import Path
import os

class FilesUtil:
    @staticmethod
    def read(path: str) -> str:
        """
        Reads the content of a file as a string.

        Args:
            path: The path to the file.

        Returns:
            The content of the file as a string.

        Raises:
            RuntimeError: If the file cannot be read.
        """
        try:
            return Path(path).read_text(encoding='utf-8')
        except Exception as e:
            raise RuntimeError(f"Cannot read file: {path}") from e

    @staticmethod
    def write(path: str, content: str):
        """
        Writes a string to a file, creating parent directories if they don't exist.

        Args:
            path: The path to the file.
            content: The string content to write.

        Raises:
            RuntimeError: If the file cannot be written.
        """
        try:
            file_path = Path(path)
            # Create parent directories if they don't exist
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content, encoding='utf-8')
        except Exception as e:
            raise RuntimeError(f"Cannot write file: {path}") from e
