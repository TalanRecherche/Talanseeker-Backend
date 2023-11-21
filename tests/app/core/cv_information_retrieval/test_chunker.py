"""Created on Fri Aug 25 13:51:53 2023

@author: agarc

"""
import pytest

from app.core.cv_information_retrieval.chunker import Chunker
from app.core.models.etl_pandasmodels import ChunkDF
from app.core.shared_modules.dataframehandler import DataFrameHandler


# prepare files
@pytest.fixture(scope="module")
def setup_data():
    text_df = DataFrameHandler.load_df("tests/data_test/df_text.pkl")
    # make chunks, One row per chunks
    chunker = Chunker()
    df_chunks = chunker.chunk_documents(text_df)
    return df_chunks


def test_dataframe_type(setup_data):
    df_chunks = setup_data
    assert ChunkDF.validate_dataframe(df_chunks)


def test_dataframe_length(setup_data):
    df_chunks = setup_data
    assert len(df_chunks) > 0


def test_chunk_text_format(setup_data):
    df_chunks = setup_data
    assert (
        df_chunks[ChunkDF.chunk_text]
        .apply(lambda x: isinstance(x, str) and len(x) > 0)
        .all()
    )


if __name__ == "__main__":
    pytest.main()
