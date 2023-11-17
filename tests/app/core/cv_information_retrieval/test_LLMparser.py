# -*- coding: utf-8 -*-
"""
Created on Tue Aug 22 14:55:20 2023

@author: agarc

/!\ THIS TEST SCRIPT CALL OPENAI AND WILL BE BILLED /!\
"""
import pytest
from app.core.shared_modules.pathexplorer import PathExplorer
from app.core.shared_modules.dataframehandler import DataFrameHandler
from app.core.cv_information_retrieval.filemassextractor import FileMassExtractor
from app.core.cv_information_retrieval.chunker import Chunker
from app.core.cv_information_retrieval.LLMparser import LLMParser
from app.core.models.ETL_pandasmodels import PARSED_DF
from app.settings import Settings

settings = Settings()


@pytest.fixture(scope='module')
def setup_data():
    directory = r'tests/data_test/CV_pptx'
    files = PathExplorer.get_all_paths_with_extension_name(directory)
    collab_ids = {files[ii]["file_full_name"]: str(ii) for ii in range(len(files))}

    # extract text from CVs
    extractor = FileMassExtractor()
    text_df = extractor.read_all_documents(directory, collab_ids)

    # chunks documents
    chunker = Chunker()
    df_chunks = chunker.chunk_documents(text_df)
    # parse the chunks
    parser = LLMParser(settings)
    parsed_chunks = parser.parse_all_chunks(df_chunks)
    return parsed_chunks


@pytest.mark.skip_this(reason="Skipping test from running because it is calling OpenAI-API")
def test_dataframe_type(setup_data):
    parsed_chunks = setup_data
    assert PARSED_DF.validate_dataframe(parsed_chunks)


@pytest.mark.skip_this(reason="Skipping test from running because it is calling OpenAI-API")
def test_dataframe_length(setup_data):
    parsed_chunks = setup_data
    assert len(parsed_chunks) > 0


if __name__ == "__main__":
    pytest.main()
