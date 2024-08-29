"""Created on Tue Aug  8 16:02:11 2023

@author: agarc

"""
import pytest

from app.core.cv_information_retrieval.filemassextractor import FileMassExtractor
from app.core.models.etl_pandasmodels import TextDF


@pytest.mark.skip_this()
@pytest.fixture(scope="module")
def setup_data():
    test_directory = "./tests/data_test"
    collab_ids = {f"file_{i}": f"collab_id_{i}" for i in range(10)}

    extractor = FileMassExtractor()
    text_df = extractor.read_all_documents(test_directory, collab_ids)
    return text_df


@pytest.mark.skip_this()
def test_dataframe_type(setup_data):
    text_df = setup_data
    assert TextDF.validate_dataframe(text_df)


@pytest.mark.skip_this()
def test_dataframe_length(setup_data):
    text_df = setup_data
    assert len(text_df) > 0


if __name__ == "__main__":
    pytest.main()
