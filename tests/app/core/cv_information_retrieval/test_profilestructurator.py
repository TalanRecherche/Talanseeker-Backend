# -*- coding: utf-8 -*-
"""
Created on Fri Sep  1 17:00:41 2023

@author: agarc

"""
import pytest
from app.core.cv_information_retrieval.profilestructurator import ProfileStructurator
from app.core.shared_modules.dataframehandler import DataFrameHandler
from app.core.models.ETL_pandasmodels import STRUCTPROFILE_DF


@pytest.fixture(scope='module')
def setup_data():
    df_struct_cvs = r"tests/data_test/dataframes/df_struct_cvs.pkl"
    loaded_struct_cvs = DataFrameHandler.load_df(df_struct_cvs)
    structurator = ProfileStructurator()
    profile_struct = structurator.consolidate_profiles(loaded_struct_cvs)
    return profile_struct


def test_dataframe_type(setup_data):
    profile_struct = setup_data
    assert STRUCTPROFILE_DF.validate_dataframe(profile_struct)


def test_dataframe_length(setup_data):
    profile_struct = setup_data
    assert len(profile_struct) > 0


if __name__ == "__main__":
    pytest.main()
