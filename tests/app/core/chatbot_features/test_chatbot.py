r"""Created on Mon Sep 18 10:57:22 2023

@author: agarc

/!\ THIS TEST CALLS THE OPENAI API AND WILL BE BILLED /!\
"""
import os

import pytest

from app.core.chatbot_features.candidatesselector import CandidatesSelector
from app.core.chatbot_features.chatbot import Chatbot
from app.settings.settings import Settings
import pandas as pd

settings = Settings()


@pytest.fixture(scope="module")
def setup_data():
    data_path = r"tests/data_test/"
    query_filename = "df_struct_query.pkl"
    # load test structured query
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
        _,
        candidates_profiles,
    ) = selector.select_candidates(df_chunks, df_collabs, df_cvs, df_profiles, df_query)
    # get chatbot response
    chatbot = Chatbot(settings)
    response, query_sent = chatbot.get_chatbot_response(
        df_query,
        candidates_chunks,
        candidates_collabs,
        candidates_profiles,
    )
    return response, query_sent


@pytest.mark.skip_this(
    reason="Skipping test from running because it is calling OpenAI-API",
)
def test_response_type(setup_data):
    response, _ = setup_data
    assert isinstance(response, str)


@pytest.mark.skip_this(
    reason="Skipping test from running because it is calling OpenAI-API",
)
def test_response_len(setup_data):
    response, _ = setup_data
    assert len(response) > 0


@pytest.mark.skip_this(
    reason="Skipping test from running because it is calling OpenAI-API",
)
def test_query_sent_type(setup_data):
    _, query_sent = setup_data
    assert isinstance(query_sent, str)


@pytest.mark.skip_this(
    reason="Skipping test from running because it is calling OpenAI-API",
)
def test_query_sent_len(setup_data):
    _, query_sent = setup_data
    assert len(query_sent) > 0


if __name__ == "__main__":
    pytest.main()
