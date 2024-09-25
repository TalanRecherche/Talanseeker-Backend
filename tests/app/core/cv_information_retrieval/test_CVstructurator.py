"""Created on Wed Aug 23 10:00:25 2023

@author: agarc

"""
import pytest

from app.core.cv_information_retrieval.cv_structurator import CvStructurator
from app.core.models.etl_pandasmodels import StructCvDF
from app.core.shared_modules.dataframehandler import DataFrameHandler
import pandas as pd


@pytest.fixture(scope="module")
def setup_data():
    chunked_parsed_path = r"tests/data_test/df_parsed_chunks.pkl"
    loaded_parsed_chunks = pd.read_pickle(chunked_parsed_path)
    structurator = CvStructurator()
    cvs_struct = structurator.consolidate_cvs(loaded_parsed_chunks)
    return cvs_struct


def test_dataframe_type(setup_data):
    cvs_struct = setup_data
    assert StructCvDF.validate_dataframe(cvs_struct)


def test_dataframe_length(setup_data):
    cvs_struct = setup_data
    assert len(cvs_struct) > 0


if __name__ == "__main__":
    pytest.main()
