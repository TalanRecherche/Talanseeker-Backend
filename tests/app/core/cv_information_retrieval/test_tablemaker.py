"""Created on Wed Aug 30 17:55:25 2023

@author: agarc

"""
import pytest

from app.core.cv_information_retrieval.tablemaker import TableMaker
from app.core.models.pg_pandasmodels import ChunkPg, CvPg, ProfilePg
from app.core.shared_modules.dataframehandler import DataFrameHandler
from app.settings.settings import Settings
import pandas as pd

env = Settings()


@pytest.fixture(scope="module")
def setup_data():
    data_1_path = r"tests/data_test/df_profiles.pkl"
    data_2_path = r"tests/data_test/df_embeddings.pkl"
    df_profiles = pd.read_pickle(data_1_path)
    df_embeddings = pd.read_pickle(data_2_path)
    maker = TableMaker()
    pg_profiles, pg_chunks, pg_cvs = maker.make_pg_tables(df_profiles, df_embeddings)
    return pg_profiles, pg_chunks, pg_cvs


def test_profile(setup_data):
    pg_profiles, _, _ = setup_data
    assert ProfilePg.validate_dataframe(pg_profiles)


def test_chunks(setup_data):
    _, pg_chunks, _ = setup_data
    assert ChunkPg.validate_dataframe(pg_chunks)


def test_cvs(setup_data):
    _, _, pg_cvs = setup_data
    assert CvPg.validate_dataframe(pg_cvs)


if __name__ == "__main__":
    pytest.main()
