r"""Created on Thu Sep 14 13:31:50 2023

@author: agarc
/!\ THIS TEST MAKES CALL TO THE OPENAI API AND WILL BE BILLED /!\
"""
import os

import pytest

from app.core.chatbot_features.querytransformer import QueryTransformer
from app.core.chatbot_features.scoreroverall import ScorerProfiles
from app.core.models.scoredprofiles_pandasmodels import ScoredChunksDF
from app.core.shared_modules.dataframehandler import DataFrameHandler
from app.settings.settings import Settings

settings = Settings()


@pytest.fixture(scope="module")
def setup_data():
    # load test structured query
    data_path = r"tests/data_test/"
    query_structured_path = os.path.join(data_path, "df_struct_query.pkl")
    structured_query = DataFrameHandler.load_df(query_structured_path)

    # prepare query
    transformer = QueryTransformer(settings)
    query_row = structured_query.iloc[[0]]
    query_keywords = transformer.get_keywords_query(query_row)
    query_embeddings = transformer.get_embedded_query(query_row)

    # load test tables
    df_chunks = DataFrameHandler.load_df(os.path.join(data_path, "PG_CHUNKS_001.pkl"))
    df_profiles = DataFrameHandler.load_df(
        os.path.join(data_path, "PG_PROFILES_001.pkl"),
    )

    return query_keywords, query_embeddings, df_chunks, df_profiles


@pytest.mark.skip_this(
    reason="Skipping test from running because it is calling OpenAI-API",
)
def test_score_by_keywords_columns(setup_data):
    query_keywords, query_embeddings, df_chunks, df_profiles = setup_data
    scorer = ScorerProfiles()

    scored_keywords = scorer.score_by_keywords(df_profiles, query_keywords)
    expected_cols = [
        "collab_id",
        "years",
        "diplomas_certifications",
        "roles",
        "sectors",
        "companies",
        "soft_skills",
        "technical_skills",
        "keywords_score",
    ]
    dataframe_cols = scored_keywords.columns
    assert (expected_cols == dataframe_cols).all()


@pytest.mark.skip_this(
    reason="Skipping test from running because it is calling OpenAI-API",
)
def test_score_by_semantic_columns(setup_data):
    query_keywords, query_embeddings, df_chunks, df_profiles = setup_data
    scorer = ScorerProfiles()

    scored_chunks = scorer.score_by_semantic(df_chunks, query_embeddings)
    assert ScoredChunksDF.validate_dataframe(scored_chunks)


@pytest.mark.skip_this(
    reason="Skipping test from running because it is calling OpenAI-API",
)
def test_assign_scores_to_profiles_columns(setup_data):
    query_keywords, query_embeddings, df_chunks, df_profiles = setup_data
    scorer = ScorerProfiles()

    scored_keywords = scorer.score_by_keywords(df_profiles, query_keywords)
    scored_chunks = scorer.score_by_semantic(df_chunks, query_embeddings)

    overall_scored = scorer.assign_scores_to_profiles(scored_keywords, scored_chunks)

    expected_cols = [
        "collab_id",
        "years",
        "diplomas_certifications",
        "roles",
        "sectors",
        "companies",
        "soft_skills",
        "technical_skills",
        "keywords_score",
        "semantic_score",
        "keywords_score_normalized",
        "semantic_score_normalized",
    ]
    dataframe_cols = overall_scored.columns
    assert (expected_cols == dataframe_cols).all()


if __name__ == "__main__":
    pytest.main()
