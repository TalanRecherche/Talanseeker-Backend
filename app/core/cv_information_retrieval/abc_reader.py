"""Created by agarc at 23/10/2023
Features:
"""
from abc import ABC, abstractmethod


class ABCReader(ABC):
    """Abstract class for file readers:
    docx_reader.py
    pdf_reader.py
    pptx_reader.py
    txt_reader.py
    """

    @staticmethod
    @abstractmethod
    def read_text(file_path: str) -> str | None:
        """Read all text from a file.

        Args:
        ----
        file_path (str): The path of the file.

        Returns:
        -------
        str: The extracted text from the file.
        """
