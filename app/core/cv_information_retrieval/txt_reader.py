"""Created on Wed Aug 30 14:29:24 2023

@author: agarc

"""
from pathlib import Path

from app.core.cv_information_retrieval.abc_reader import ABCReader


class TXTReader(ABCReader):
    @staticmethod
    def read_text(file_path: str) -> str | None:
        """Read all text from a .txt fie

        Parameters
        ----------
        file_path : str
            the path of the txt file.

        Returns
        -------
        str
            the extracted text from the txt file.

        """
        with Path(file_path).open(encoding="utf-8") as file:
            text = file.read()

        if text:
            return text
        else:
            return None
