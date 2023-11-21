r"""Created on Thu Sep 14 10:50:00 2023

@author: agarc
/!\ THIS TEST CALLS THE OPENAI API AND WILL BE BILLED /!\
"""
import pandas as pd
import pytest

from app.core.chatbot_features.querytransformer import QueryTransformer
from app.core.shared_modules.dataframehandler import DataFrameHandler
from app.settings.settings import Settings

settings = Settings()


@pytest.fixture(scope="module")
def setup_data():
    query_structured_path = r"tests/data_test/df_struct_query.pkl"
    structured_query = DataFrameHandler.load_df(query_structured_path)
    return structured_query


def test_keywords_retrieval_output_format(setup_data):
    structured_query = setup_data
    transformer = QueryTransformer(settings)
    for _, row in structured_query.iterrows():
        query_row = pd.DataFrame(row).T
        keywords = transformer.get_keywords_query(query_row)
        assert isinstance(keywords, list)


@pytest.mark.skip_this(
    reason="Skipping test from running because it is calling OpenAI-API",
)
def test_embeddings_retrieval_output_format(setup_data):
    structured_query = setup_data
    transformer = QueryTransformer(settings)
    for _, row in structured_query.iterrows():
        query_row = pd.DataFrame(row).T
        embeddings = transformer.get_embedded_query(query_row)
        assert isinstance(embeddings, list)
        assert len(embeddings) == 1536
        assert sum(embeddings) != 0


if __name__ == "__main__":
    pytest.main()
