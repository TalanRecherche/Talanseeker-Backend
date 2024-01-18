r"""Created on Thu Sep 14 13:31:50 2023

@author: agarc
/!\ THIS TEST MAKES CALL TO THE OPENAI API AND WILL BE BILLED /!\
"""
import os

import pytest

from app.core.chatbot_features.querytransformer import QueryTransformer
from app.core.chatbot_features.scoreroverall import ScorerOverall
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
    query_structured_path = os.path.join(data_path, "df_struct_query.pkl")
    structured_query = pd.read_pickle(query_structured_path)

    # prepare query
    transformer = QueryTransformer()
    query_row = structured_query.iloc[[0]]
    query_keywords = transformer.get_keywords_query(query_row)
    query_embeddings = transformer.get_embedded_query(query_row)

    # load test tables
    df_chunks = pd.read_pickle(os.path.join(data_path, "PG_CHUNKS_001.pkl"))
    df_profiles = pd.read_pickle(
        os.path.join(data_path, "PG_PROFILES_001.pkl"),
    )

    return df_chunks, df_profiles, query_keywords, query_embeddings


@pytest.mark.skip_this(
    reason="Skipping test from running because it is calling OpenAI-API",
)
def test_get_overall_scores_chunks_columns(setup_data):
    df_chunks, df_profiles, query_keywords, query_embeddings = setup_data

    scorer = ScorerOverall()
    df_chunks_scored, _ = scorer.get_overall_scores(
        df_chunks,
        df_profiles,
        query_keywords,
        query_embeddings,
    )

    assert ScoredChunksDF.validate_dataframe(df_chunks_scored)


@pytest.mark.skip_this(
    reason="Skipping test from running because it is calling OpenAI-API",
)
def test_get_overall_scores_profiles_columns(setup_data):
    df_chunks, df_profiles, query_keywords, query_embeddings = setup_data

    scorer = ScorerOverall()
    _, df_profiles_scored = scorer.get_overall_scores(
        df_chunks,
        df_profiles,
        query_keywords,
        query_embeddings,
    )

    assert ScoredProfilesDF.validate_dataframe(df_profiles_scored)


if __name__ == "__main__":
    pytest.main()
