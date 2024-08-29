"""Created by agarc at 01/10/2023,
Features:
"""
import pytest

from app.core.shared_modules.stringhandler import StringHandler


def test_normalize_string() -> None:
    """Test that a string is normalized."""
    input_string = "Áccénted Chàràctèrs"
    expected_output = "accented characters"
    assert StringHandler.normalize_string(input_string) == expected_output

    input_string = "Spàces  Removèd"
    expected_output = "spacesremoved"
    assert (
            StringHandler.normalize_string(input_string, remove_special_chars=True)
            == expected_output
    )


def test_check_similarity_string() -> None:
    """Test that two strings are similar."""
    string_a = "hello world"
    string_b = "hello world"
    assert StringHandler.check_similarity_string(string_a, string_b) is True

    string_a = "hello world"
    string_b = "eating worms"
    assert (
            StringHandler.check_similarity_string(string_a, string_b, threshold=0.9)
            is False
    )


def test_remove_similar_strings() -> None:
    """Test that similar strings are removed."""
    input_strings = ["hello world", "helo wrld", "hello wrld", "goodbye world"]
    expected_output = ["hello world", "goodbye world"]
    assert (
            StringHandler.remove_similar_strings(input_strings, threshold=0.9)
            == expected_output
    )


def test_generate_unique_id() -> None:
    """Test that a unique ID is generated from a string."""
    input_string = "hello world"
    unique_id = StringHandler.generate_unique_id(input_string)
    assert len(unique_id) == 64


def test_replace_in_string() -> None:
    """Test that a string is replaced with a dictionary of replacements."""
    replacement = {"n": "N", "[": "", "]": ""}
    input_string = "not provided (example) [text] /with/  extra   spaces"
    expected_output = "Not provided (example) text /with/  extra   spaces"
    assert StringHandler.replace_in_string(input_string, replacement) == expected_output


def test_string_to_list_with_separator() -> None:
    """Test that a string is split into a list using a separator."""
    input_string = "apple, banana, orange"
    expected_output = ["apple", "banana", "orange"]
    assert StringHandler.string_to_list_with_separator(input_string) == expected_output


if __name__ == "__main__":
    pytest.main()
