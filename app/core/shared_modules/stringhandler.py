"""
Created by agarc at 01/10/2023
Features:
"""
import hashlib
from difflib import SequenceMatcher
from unidecode import unidecode
import re


class StringHandler:

    @staticmethod
    def normalize_string(string: str, remove_special_chars: bool = False) -> str:
        """ remove trailing spaces and new lines
        remove accents, non ascii characters and upper cases
        if remove_special_chars is True it will also remove any space"""
        try:
            string = string.strip()
            string = string.rstrip()
            string = string.lower()
            string = unidecode(string)
            if remove_special_chars:
                string = re.sub('[^a-zA-Z]', '', string)
        except Exception:
            pass
        return string

    @staticmethod
    def check_similarity_string(a, b, threshold=0.8) -> bool:
        """Check if two strings are similar based on a similarity threshold."""
        similarity = SequenceMatcher(None, a, b).ratio()
        return similarity >= threshold

    @staticmethod
    def remove_similar_strings(strings: list[str], threshold=0.8) -> list[str]:
        """Fuzzy string removal. Remove similar strings from a list based on a similarity threshold."""

        unique_strings = []
        for s in strings:
            if not any(StringHandler.check_similarity_string(s, u, threshold) for u in unique_strings):
                unique_strings.append(s)
        return unique_strings

    @staticmethod
    def generate_unique_id(input_string: str) -> str:
        """ Use Sha to create unique ids"""
        sha256 = hashlib.sha256()
        sha256.update(input_string.encode('utf-8'))
        unique_id = sha256.hexdigest()
        return unique_id

    @staticmethod
    def replace_in_string(input_string: str, string_replacements: dict = None) -> str:
        """ Replace characters in strings using a hashmap (keys mapped to values) """
        if string_replacements is None:
            string_replacements = {'not provided': '',
                                   '(': '',
                                   ')': '',
                                   '/': ',',
                                   '[': '',
                                   ']': '',
                                   '  ': ' ',
                                   '   ': ' '}

        for target, replacement in string_replacements.items():
            input_string = input_string.replace(target, replacement)
        output_string = input_string.strip()

        return output_string

    @staticmethod
    def string_to_list_with_separator(input_string: str, separator: str = ','):
        """Converts a text separated by the separator into a list of unique values.
        Args:
            separator: str
            input_string: str

        Returns:
            list[str]: List of unique values.
        """
        list_text = input_string.split(separator)
        unique_list_text = []
        for word in list_text:
            word = word.strip()
            if word not in unique_list_text:
                unique_list_text.append(word)
        return unique_list_text
