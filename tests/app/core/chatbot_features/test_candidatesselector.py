# -*- coding: utf-8 -*-
"""
Created on Thu Sep 13 10:04:44 2023

@author: agarc
"""
import pytest
from app.settings import Settings
from app.core.chatbot_features.candidatesselector import CandidatesSelector
from app.core.shared_modules.dataframehandler import DataFrameHandler
from app.core.models.scoredprofiles_pandasmodels import SCORED_PROFILES_DF
from app.core.models.scoredprofiles_pandasmodels import SCORED_CHUNKS_DF
from app.core.models.PG_pandasmodels import CV_PG
from app.core.models.PG_pandasmodels import COLLAB_PG

import os

settings = Settings()


@pytest.fixture(scope='module')
def setup_data():
    # load test structured query
    data_path = r'tests/data_test/dataframes'
    query_filename = 'df_struct_query.pkl'
    df_query = DataFrameHandler.load_df(os.path.join(data_path, query_filename))

    # load postgres test tables
    df_chunks = DataFrameHandler.load_df(os.path.join(data_path, "PG_CHUNKS_001.pkl"))
    df_collabs = DataFrameHandler.load_df(os.path.join(data_path, "PG_COLLABS_001.pkl"))
    df_cvs = DataFrameHandler.load_df(os.path.join(data_path, "PG_CVS_001.pkl"))
    df_profiles = DataFrameHandler.load_df(os.path.join(data_path, "PG_PROFILES_001.pkl"))

    # select best candidates
    selector = CandidatesSelector(settings)
    candidates_chunks, candidates_collabs, candidates_cvs, candidates_profiles = selector.select_candidates(df_chunks,
                                                                                                            df_collabs,
                                                                                                            df_cvs,
                                                                                                            df_profiles,
                                                                                                            df_query)
    return candidates_chunks, candidates_collabs, candidates_cvs, candidates_profiles


def test_candidates_chunks_format(setup_data):
    candidates_chunks, _, _, _ = setup_data
    assert SCORED_CHUNKS_DF.validate_dataframe(candidates_chunks)


def test_candidates_collabs_format(setup_data):
    _, candidates_collabs, _, _ = setup_data
    assert COLLAB_PG.validate_dataframe(candidates_collabs)


def test_candidates_cvs_format(setup_data):
    _, _, candidates_cvs, _ = setup_data
    assert CV_PG.validate_dataframe(candidates_cvs)


def test_candidates_profiles_format(setup_data):
    _, _, _, candidates_profiles = setup_data
    assert SCORED_PROFILES_DF.validate_dataframe(candidates_profiles)


if __name__ == '__main__':
    pytest.main()
