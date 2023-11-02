# -*- coding: utf-8 -*-
"""
Created on Fri Sep  1 17:00:41 2023

@author: agarc

"""
import logging

import pandas as pd

from app.core.models.pandascols import STRUCTCV_DF
from app.core.models.pandascols import STRUCTPROFILE_DF
from app.core.shared_modules.dataframehandler import DataFrameHandler
from app.core.shared_modules.listhandler import ListHandler
from app.core.shared_modules.stringhandler import StringHandler


class ProfileStructurator:

    def __init__(self):
        self.similarity_threshold = 0.8
        # forbidden names/surname
        self.forbidden_names = ['talan']
        pass

    # =============================================================================
    # user functions
    # =============================================================================
    def consolidate_profiles(self, df_consolidated_cvs: pd.DataFrame) -> pd.DataFrame | None:
        """
        Pass the consolidated CV to this function.
        It will consolidate by profile (one row per profile)

        Parameters
        ----------
        df_consolidated_cvs : pd.DataFrame
            one row per CV dataframe with parsed information.

        Returns
        -------
        None.
        """
        # assert if input dataframe is of correct format (columns)
        if DataFrameHandler.assert_df(df_consolidated_cvs, STRUCTCV_DF) is False:
            return None

        # assign collab_ids to consolidated cvs
        # prepare output dataframe
        df_consolidated_profiles = pd.DataFrame(columns=STRUCTPROFILE_DF.get_attributes_())

        # get unique profiles
        hashmap_collabid_cvsid = self._get_unique_profiles(df_consolidated_cvs)

        # loop through each profiles and consolidate to single row
        # loop through each profile and their chunks
        for collab_id, cv_ids in hashmap_collabid_cvsid.items():
            # filter chunks to current profile
            df_filtered_cvs = df_consolidated_cvs[df_consolidated_cvs[STRUCTPROFILE_DF.cv_id].isin(cv_ids)]
            # consolidate all rows into a single profile row
            df_single_profile = self._consolidate_single_profile(df_filtered_cvs)
            # push to new pandas df
            if not df_single_profile.empty:
                df_single_profile[STRUCTPROFILE_DF.collab_id] = collab_id
                df_consolidated_profiles = pd.concat(
                    [df_consolidated_profiles, df_single_profile], axis=0, ignore_index=True)

        if df_consolidated_profiles.empty:
            logging.warning("dataframe is empty")
            return None

        logging.info("done")
        return df_consolidated_profiles

    # =============================================================================
    # internal functions
    # =============================================================================

    def _get_unique_profiles(self, df_consolidated_cvs: pd.DataFrame) -> dict:
        """        
        identifies unique profiles and assigns cv_id to them.
        returns a hashmap mapping profile_id to list[cv_ids]

        Parameters
        ----------
        df_consolidated_cvs : pd.DataFrame

        Returns
        -------
        dict
            {profile_id to list[cv_ids]}

        """

        grouped = df_consolidated_cvs.groupby(STRUCTCV_DF.collab_id)[STRUCTCV_DF.cv_id].apply(list)
        hashmap_collabid_cvsid = {key: value for key, value in grouped.items()}
        return hashmap_collabid_cvsid

    def _consolidate_single_profile(self, df_filtered_cvs: pd.DataFrame) -> pd.DataFrame:
        """
        Consolidate all cvs of a profile into a single row pd.dataframe

        Parameters
        ----------
        df_filtered_cvs : pd.DataFrame
            all consolidated cv of a single profiles (one row per cv).

        Returns
        -------
        df_consolidated_profile : pd.DataFrame
            single-row dataframe (cvs are consolidated into a single profile)

        """
        # prepare output container hashmap
        hashmap_consolidated_profile = {}

        # I. static columns are not transformed we just take a single value
        for column in STRUCTCV_DF.static_columns_:
            static_value = self._merge_static_columns(column, df_filtered_cvs)
            hashmap_consolidated_profile[column] = static_value

        # II. for numeric, we take the maximum values (years of experiences)
        for column in STRUCTCV_DF.numerical_columns_:
            numerical_value = self._merge_numerical_columns(column, df_filtered_cvs)
            hashmap_consolidated_profile[column] = numerical_value

        # III. for string (eg roles_profile sector etc.), things are more complicated
        for column in STRUCTCV_DF.string_columns_:
            string_values = self._merge_string_columns(column, df_filtered_cvs)
            hashmap_consolidated_profile[column] = string_values

        df_consolidated_profile = pd.Series(hashmap_consolidated_profile).to_frame().T
        return df_consolidated_profile

    def _merge_string_columns(self, column, df_filtered_cvs) -> list[str]:
        try:
            string_values = ListHandler.flatten_list(df_filtered_cvs[column].to_list())
            # unique strings
            string_values = list(set(string_values))
            # 5 fuzzy string matching to remove pseudo-duplicates (this is O(n2), a C++ version exists see Cdiflib)
            string_values = StringHandler.remove_similar_strings(string_values, threshold=self.similarity_threshold)
        except Exception as e:
            string_values = []
            logging.warning("ProfileStructurator : string columns structuration failed: {}".format(e))
        return string_values

    def _merge_numerical_columns(self, column, df_filtered_cvs) -> int:
        # try is here because sometime the integer is impossible to get
        try:
            numerical_extract = max(df_filtered_cvs[column].dropna())
            numerical_value = int(numerical_extract)
        except Exception as e:
            numerical_value = 0
            logging.warning("ProfileStructurator : numerical columns structuration failed: {}".format(e))
        return numerical_value

    def _merge_static_columns(self, column, df_filtered_cvs) -> list:
        try:
            static_value = list(df_filtered_cvs[column])
        except Exception as e:
            static_value = []
            logging.warning("ProfileStructurator : static columns structuration failed: {}".format(e))
        return static_value


if __name__ == "__main__":
    directory = r'data_dev/data_1'
    # prepare {filenames : collab_id} map from the main
    from app.core.shared_modules.pathexplorer import PathExplorer
    files = PathExplorer.get_all_paths_with_extension_name(directory)
    collab_ids = {files[ii]["file_full_name"]: str(ii) for ii in range(len(files))}

    from app.core.cv_information_retrieval.filemassextractor import FileMassExtractor
    extractor = FileMassExtractor()
    text_df = extractor.read_all_documents(directory, collab_ids)

    from app.core.cv_information_retrieval.chunker import Chunker
    chunker = Chunker()
    df_chunks = chunker.chunk_documents(text_df)

    # parse the chunks
    from app.settings import Settings
    from app.core.cv_information_retrieval.LLMparser import LLMParser
    parser = LLMParser(Settings())
    parsed_chunks = parser.parse_all_chunks(df_chunks)

    # consolidate cvs
    from app.core.cv_information_retrieval.CVstructurator import CvStructurator
    structure = CvStructurator()
    cvs_struct = structure.consolidate_cvs(parsed_chunks)

    # consolidate profiles
    structurator = ProfileStructurator()
    consolidated_profiles = structurator.consolidate_profiles(cvs_struct)

    # some prints
    columns = consolidated_profiles.columns.tolist()
    for _, i in cvs_struct.iterrows():
        for c in columns:
            print(c)
            print(i[c])
            print("############")
