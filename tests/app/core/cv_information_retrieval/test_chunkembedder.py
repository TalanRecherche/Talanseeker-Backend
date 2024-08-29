r"""Created on Tue Aug  8 17:04:53 2023

@author: agarc

/!\ THIS TEST SCRIPT CALL OPENAI AND WILL BE BILLED /!\
"""
import pytest

from app.core.cv_information_retrieval.chunkembedder import ChunkEmbedder
from app.core.cv_information_retrieval.chunker import Chunker
from app.core.cv_information_retrieval.filemassextractor import FileMassExtractor
from app.core.models.etl_pandasmodels import EmbeddingDF
from app.core.shared_modules.pathexplorer import PathExplorer
from app.settings.settings import Settings


@pytest.fixture(scope="module")
def setup_data():
    # prepare files
    directory = r"tests/data_test"
    files = PathExplorer.get_all_paths_with_extension_name(directory)
    collab_ids = {
        files[ii]["file_full_name"]: str(ii * 1231) for ii in range(len(files))
    }
    # extract text from CVs
    extractor = FileMassExtractor()
    text_df = extractor.read_all_documents(
        directory, collab_ids, read_only_extensions=[".pdf"]
    )
    # make chunks, One row per chunks
    chunker = Chunker()
    df_chunks = chunker.chunk_documents(text_df)
    # make embeddings
    embedder = ChunkEmbedder(Settings())
    df_embeddings = embedder.embed_chunk_dataframe(df_chunks)
    return df_embeddings


@pytest.mark.skip_this(
    reason="Skipping test from running because it is calling OpenAI-API",
)
def test_dataframe_type(setup_data):
    df_embeddings = setup_data
    assert EmbeddingDF.validate_dataframe(df_embeddings)


@pytest.mark.skip_this(
    reason="Skipping test from running because it is calling OpenAI-API",
)
def test_dataframe_length(setup_data):
    df_embeddings = setup_data
    assert len(df_embeddings) > 0


@pytest.mark.skip_this(
    reason="Skipping test from running because it is calling OpenAI-API",
)
def test_chunk_text_format(setup_data):
    df_embeddings = setup_data
    assert (
        df_embeddings[EmbeddingDF.chunk_text]
        .apply(lambda x: isinstance(x, str) and len(x) > 0)
        .all()
    )


@pytest.mark.skip_this(
    reason="Skipping test from running because it is calling OpenAI-API",
)
def test_chunk_embeddings_format(setup_data):
    df_embeddings = setup_data
    assert (
        df_embeddings[EmbeddingDF.chunk_embeddings]
        .apply(lambda x: isinstance(x, list) and len(x) == 1536)
        .all()
    )


if __name__ == "__main__":
    pytest.main()
