"""Created on Wed Aug 30 14:29:24 2023

@author: agarc

"""
import pytest

from app.core.cv_information_retrieval.txt_reader import TXTReader


def test_read_text():
    test_file_path = r"./tests/data_test/MelissaJohn.txt"
    result = TXTReader.read_text(test_file_path)

    # Check if the output is a non-empty string
    assert isinstance(result, str)
    assert len(result) > 0


if __name__ == "__main__":
    pytest.main()
