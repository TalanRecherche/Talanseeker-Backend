r"""Created on Sun Sep 17 13:07:47 2023

@author: agarc
/!\ this test fetches data from the PostGres database /!\
"""
import pytest

from app.core.chatbot_features.pg_fetcher import PGfetcher
from app.core.models.pg_pandasmodels import ChunkPg, CollabPg, CvPg, ProfilePg
from app.settings.settings import Settings
import pandas as pd

settings = Settings()


@pytest.fixture(scope="module")
def setup_data():
    fetcher = PGfetcher()
    df_chunks, df_collabs, df_cvs, df_profiles = fetcher.fetch_all()
    return df_chunks, df_collabs, df_cvs, df_profiles


@pytest.mark.skip_this(reason="Skipping test from running because it is calling PG")
def test_01_fetched_chunks_format(setup_data):
    df_chunks, _, _, _ = setup_data
    assert ChunkPg.validate_dataframe(df_chunks)


@pytest.mark.skip_this(reason="Skipping test from running because it is calling PG")
def test_02_fetched_collabs_format(setup_data):
    _, df_collabs, _, _ = setup_data
    assert CollabPg.validate_dataframe(df_collabs)


@pytest.mark.skip_this(reason="Skipping test from running because it is calling PG")
def test_03_fetched_cvs_format(setup_data):
    _, _, df_cvs, _ = setup_data
    assert CvPg.validate_dataframe(df_cvs)


@pytest.mark.skip_this(reason="Skipping test from running because it is calling PG")
def test_04_fetched_profiles_format(setup_data):
    _, _, _, df_profiles = setup_data
    assert ProfilePg.validate_dataframe(df_profiles)


if __name__ == "__main__":
    pytest.main()
