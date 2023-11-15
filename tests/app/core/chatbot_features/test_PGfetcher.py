# -*- coding: utf-8 -*-
"""
Created on Sun Sep 17 13:07:47 2023

@author: agarc
/!\ this test fetches data from the PostGres database /!\
"""
import pytest

from app.core.chatbot_features.PGfetcher import PGfetcher
from app.core.models.PG_pandasmodels import CHUNK_PG
from app.core.models.PG_pandasmodels import COLLAB_PG
from app.core.models.PG_pandasmodels import CV_PG
from app.core.models.PG_pandasmodels import PROFILE_PG
from app.settings import Settings

settings = Settings()


@pytest.fixture(scope='module')
def setup_data():
    fetcher = PGfetcher(settings)
    df_chunks, df_collabs, df_cvs, df_profiles = fetcher.fetch_all()
    return df_chunks, df_collabs, df_cvs, df_profiles


def test_01_fetched_chunks_format(setup_data):
    df_chunks, _, _, _ = setup_data
    assert CHUNK_PG.validate_dataframe(df_chunks)


def test_02_fetched_collabs_format(setup_data):
    _, df_collabs, _, _ = setup_data
    assert COLLAB_PG.validate_dataframe(df_collabs)


def test_03_fetched_cvs_format(setup_data):
    _, _, df_cvs, _ = setup_data
    assert CV_PG.validate_dataframe(df_cvs)


def test_04_fetched_profiles_format(setup_data):
    _, _, _, df_profiles = setup_data
    assert PROFILE_PG.validate_dataframe(df_profiles)


if __name__ == "__main__":
    pytest.main()
