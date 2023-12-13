r"""Created on Mon Sep 18 10:57:22 2023

@author: agarc

/!\ THIS TEST CALLS THE OPENAI API AND WILL BE BILLED /!\
"""

import os

import pytest

from app.core.chatbot_features.candidate import Candidates
from app.core.chatbot_features.candidatesselector import CandidatesSelector
from app.core.chatbot_features.dataviz import DataViz
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
    selector = CandidatesSelector(settings)
    (
        candidates_chunks,
        candidates_collabs,
        candidates_cvs,
        candidates_profiles,
    ) = selector.select_candidates(df_chunks, df_collabs, df_cvs, df_profiles, df_query)
    # create candidates
    candidates = Candidates(
        candidates_chunks,
        candidates_collabs,
        candidates_cvs,
        candidates_profiles,
    )
    return candidates


@pytest.mark.skip_this(
    reason="Skipping test from running because it is calling OpenAI-API",
)
def test_dataviz_competences_columns(setup_data):
    candidates = setup_data
    for candidate in candidates.list_candidates:
        dataviz = DataViz(settings, candidate)
        df_competences = dataviz.get_df_competence()

        expected_cols = ["competence", "n_occurence", "skills"]
        returned_cols = df_competences.columns
        assert (expected_cols == returned_cols).all()


if __name__ == "__main__":
    pytest.main()
