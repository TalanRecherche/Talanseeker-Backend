"""
Created by agarc at 01/10/2023
Features:
"""
import pytest
from app.core.shared_modules.tokenshandler import TokenHandler


def test_count_tokens_from_string():
    input_string = "This is a test string."
    expected_token_count = 6  # 5 words + 1 for the end-of-sequence token
    assert TokenHandler.count_tokens_from_string(input_string) == expected_token_count

    input_string = ""
    expected_token_count = 0
    assert TokenHandler.count_tokens_from_string(input_string) == expected_token_count

    input_string = 12345  # Non-string input
    expected_token_count = 0
    assert TokenHandler.count_tokens_from_string(input_string) == expected_token_count


def test_count_tokens_from_hashmap():
    input_hashmap = {
        "key1": "This is a test string.",
        "key2": "Another test string."
    }
    expected_tokens_count = 10  # 1 tokens for each word and stop token
    assert TokenHandler.count_tokens_from_hashmap(input_hashmap) == expected_tokens_count

    input_hashmap = {}  # Empty hashmap
    expected_tokens_count = 0
    assert TokenHandler.count_tokens_from_hashmap(input_hashmap) == expected_tokens_count


if __name__ == "__main__":
    pytest.main()
