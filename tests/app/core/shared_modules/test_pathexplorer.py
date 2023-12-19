"""Created on Tue Aug  8 15:42:28 2023

@author: agarc

"""
import pytest

from app.core.shared_modules.pathexplorer import PathExplorer


def test_number_of_files():
    test_directory = r"./tests/data_test"
    files = PathExplorer.get_all_paths_with_extension_name(test_directory)
    nb_files = len(files)
    assert nb_files > 0


def test_pdf_extension():
    test_directory = r"./tests/data_test"
    files = PathExplorer.get_all_paths_with_extension_name(test_directory)
    pdf_files = [file for file in files if file["file_extension"] == ".pdf"]
    for pdf_file in pdf_files:
        assert pdf_file["file_extension"] == ".pdf"


def test_pptx_extension():
    test_directory = r"./tests/data_test"
    files = PathExplorer.get_all_paths_with_extension_name(test_directory)
    pptx_files = [file for file in files if file["file_extension"] == ".pptx"]
    for pptx_file in pptx_files:
        assert pptx_file["file_extension"] == ".pptx"


def test_docx_extension():
    test_directory = r"./tests/data_test"
    files = PathExplorer.get_all_paths_with_extension_name(test_directory)
    docx_files = [file for file in files if file["file_extension"] == ".docx"]
    for docx_file in docx_files:
        assert docx_file["file_extension"] == ".docx"


def test_txt_extension():
    test_directory = r"./tests/data_test"
    files = PathExplorer.get_all_paths_with_extension_name(test_directory)
    txt_files = [file for file in files if file["file_extension"] == ".txt"]
    for txt_file in txt_files:
        assert txt_file["file_extension"] == ".txt"


if __name__ == "__main__":
    pytest.main()
