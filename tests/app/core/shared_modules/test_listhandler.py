"""Created by agarc at 01/10/2023
Features:
"""
import pytest

from app.core.shared_modules.listhandler import ListHandler


def test_01_flatten_list():  # noqa: D103
    input_list = [[1, 2, [3, 4]], [5, 6], 7, [8, [9]]]
    expected_output = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    assert ListHandler.flatten_list(input_list) == expected_output


def test_02_flatten_list_empty():  # noqa: D103
    input_list = []
    expected_output = []
    assert ListHandler.flatten_list(input_list) == expected_output


def test_03_flatten_list_some_emtpy():  # noqa: D103
    input_list = [[], [1, 2], [], [3, [4, [5]]], []]
    expected_output = [1, 2, 3, 4, 5]
    assert ListHandler.flatten_list(input_list) == expected_output


def test_04_remove_strings_in_list_some_default():  # noqa: D103
    input_list = ["a", "_", "b", "c", "_", "d"]
    expected_output = ["a", "b", "c", "d"]
    assert ListHandler.remove_strings_in_list(input_list) == expected_output


def test_05_remove_string_in_list_all_default():  # noqa: D103
    input_list = ["_", "_", "_", "_"]
    expected_output = []
    assert ListHandler.remove_strings_in_list(input_list) == expected_output


def test_06_remove_string_in_list_some_targets():  # noqa: D103
    input_list = ["a", "b", "c", "d"]
    targets = ["a", "b"]
    expected_output = ["c", "d"]
    assert ListHandler.remove_strings_in_list(input_list, targets) == expected_output


if __name__ == "__main__":
    pytest.main()
