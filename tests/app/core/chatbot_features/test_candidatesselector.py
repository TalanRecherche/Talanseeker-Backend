"""Created on Thu Sep 13 10:04:44 2023

@author: agarc
"""
import os

import pytest

from app.core.chatbot_features.candidatesselector import CandidatesSelector
from app.core.models.pg_pandasmodels import CollabPg, CvPg
from app.core.models.scoredprofiles_pandasmodels import (
    ScoredChunksDF,
    ScoredProfilesDF,
)
from app.core.shared_modules.dataframehandler import DataFrameHandler
from app.settings.settings import Settings
import pandas as pd

settings = Settings()


@pytest.fixture(scope="module")
def setup_data():
    # load test structured query
    data_path = r"tests/data_test/"
    query_filename = "df_struct_query.pkl"
    df_query = pd.read_pickle(os.path.join(data_path, query_filename))

    # load postgres test tables
    df_chunks = pd.read_pickle(os.path.join(data_path, "PG_CHUNKS_001.pkl"))
    df_collabs = pd.read_pickle(os.path.join(data_path, "PG_COLLABS_001.pkl"))
    df_cvs = pd.read_pickle(os.path.join(data_path, "PG_CVS_001.pkl"))
    df_profiles = pd.read_pickle(
        os.path.join(data_path, "PG_PROFILES_001.pkl"),
    )

    # select best candidates
    selector = CandidatesSelector()
    (
        candidates_chunks,
        candidates_collabs,
        candidates_cvs,
        candidates_profiles,
    ) = selector.select_candidates(df_chunks, df_collabs, df_cvs, df_profiles, df_query)
    return candidates_chunks, candidates_collabs, candidates_cvs, candidates_profiles


@pytest.mark.skip_this()
def test_candidates_chunks_format(setup_data):
    candidates_chunks, _, _, _ = setup_data
    assert ScoredChunksDF.validate_dataframe(candidates_chunks)


@pytest.mark.skip_this()
def test_candidates_collabs_format(setup_data):
    _, candidates_collabs, _, _ = setup_data
    assert CollabPg.validate_dataframe(candidates_collabs)


@pytest.mark.skip_this()
def test_candidates_cvs_format(setup_data):
    _, _, candidates_cvs, _ = setup_data
    assert CvPg.validate_dataframe(candidates_cvs)


@pytest.mark.skip_this()
def test_candidates_profiles_format(setup_data):
    _, _, _, candidates_profiles = setup_data
    assert ScoredProfilesDF.validate_dataframe(candidates_profiles)


if __name__ == "__main__":
    pytest.main()
