"""Created on Wed Aug 30 14:25:54 2023

@author: agarc

"""
from PyPDF2 import PdfReader

from app.core.cv_information_retrieval.ABCreader import ABCReader


class PDFReader(ABCReader):
    @staticmethod
    def read_text(file_path: str) -> str | None:
        """Read all text from a pdf file.

        Args:
        ----
        file_path (str): The path of the pdf file.

        Returns:
        -------
        str: The extracted text from the pdf file.

        Dependencies:
        from PyPDF2 import PdfReader
        """
        # creating a pdf reader object
        reader = PdfReader(file_path)
        # instantiate return
        text = ""
        # getting a specific page from the pdf file
        for page in reader.pages:
            # extracting text from page
            page_text = page.extract_text().strip()

            # remove non ascci character
            page_text = page_text.encode("latin-1", errors="ignore").decode("latin-1")
            # split by line
            lines = page_text.split("\n")
            # remove useless characters
            stripped_lines = [line.strip() for line in lines]
            page_text_processed = "\n".join(stripped_lines)

            if page_text_processed:
                text = text + page_text_processed + "\n\n\n"

        # remove trailing spaces and linebreaks
        text = text.rstrip("\n")
        text = text.strip()

        # return only if not empty
        if text:
            return text
        else:
            return None
