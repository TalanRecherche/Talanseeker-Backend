"""Created on Tue Aug  8 15:47:38 2023

@author: agarc

"""
import pytest

from app.core.cv_information_retrieval.filereader import FileReader


@pytest.fixture(scope="module")
def setup_data():
    data_path = r"tests/data_test/AthurAndersen.docx"
    reader = FileReader()
    data = reader.read_single_document(data_path)
    return data


def test_file_path(setup_data):
    data = setup_data
    assert data["file_path"] == "tests/data_test/AthurAndersen.docx"


def test_file_name(setup_data):
    data = setup_data
    assert data["file_name"] == "AthurAndersen"


def test_file_extension(setup_data):
    data = setup_data
    assert data["file_extension"] == ".docx"


def test_file_full_name(setup_data):
    data = setup_data
    assert data["file_full_name"] == "AthurAndersen.docx"


def test_file_text(setup_data):
    data = setup_data
    assert isinstance(data["file_text"], str)
    assert len(data["file_text"]) > 0


def test_cv_id(setup_data):
    data = setup_data
    assert (
        data["cv_id"]
        == "e05a689d030ceae6296a06adf9c3ba29e7cc0269b1bb35a73451dd048634b233"
    )


if __name__ == "__main__":
    pytest.main()
