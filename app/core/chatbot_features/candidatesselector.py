# -*- coding: utf-8 -*-
"""
Created on Thu Sep 13 10:04:44 2023

@author: agarc

"""
from typing import Any

from app.settings import Settings

import pandas as pd
import time
import logging

from app.core.models.PGcols import PROFILE_PG
from app.core.models.PGcols import CHUNK_PG
from app.core.models.PGcols import CV_PG
from app.core.models.PGcols import COLLAB_PG
from app.core.models.querykeywordscols import QUERY_STRUCT
from app.core.models.scoredprofilescols import SCORED_PROFILES_DF
from app.core.models.scoredprofilescols import SCORED_CHUNKS_DF
from app.core.shared_modules.dataframehandler import DataFrameHandler
from app.core.chatbot_features.scoreroverall import ScorerOverall
from app.core.chatbot_features.core.querytransformer import QueryTransformer


class CandidatesSelector:
    """
    This class read the normalized/structured query from GuessIntention.
    It then finds best candidates and returns their dataframes
    """

    def __init__(self, settings):
        self.queryTransformer = QueryTransformer(settings)
        self.scorer = ScorerOverall()
        pass

    # =============================================================================
    # user functions
    # =============================================================================
    def select_candidates(self,
                          df_chunks: pd.DataFrame,
                          df_collabs: pd.DataFrame,
                          df_cvs: pd.DataFrame,
                          df_profiles: pd.DataFrame,
                          df_query: pd.DataFrame) -> (tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]
                                                      | list[None]):
        # assert df format coming from PostGres
        if not DataFrameHandler.assert_df(df_chunks, CHUNK_PG):
            return [None] * 4
        if not DataFrameHandler.assert_df(df_collabs, COLLAB_PG):
            return [None] * 4
        if not DataFrameHandler.assert_df(df_cvs, CV_PG):
            return [None] * 4
        if not DataFrameHandler.assert_df(df_profiles, PROFILE_PG):
            return [None] * 4
        if not DataFrameHandler.assert_df(df_query, QUERY_STRUCT):
            return [None] * 4

        t = time.time()
        # Prepare list of selected ids
        already_selected_profiles_ids = []
        # loop through sub queries from GuessIntention
        for _, row in df_query.iterrows():
            query_row = pd.DataFrame(row).T
            # get scores for profiles and chunks of this subquery
            df_chunks_scored, df_profiles_scored = self._get_scores_subquery(df_chunks, df_profiles, query_row)
            # number of identical profiles needed in this subquery            
            try:
                nb_profiles = int(query_row[QUERY_STRUCT.nb_profiles][0][0])
            except:
                nb_profiles = 3
            # find best profiles for this subquery, NOT in already_selected_profiles_ids
            selected_ids = self._select_profiles_ids(nb_profiles, already_selected_profiles_ids, df_profiles_scored)
            # place new profiles in already_selected_profiles_ids
            already_selected_profiles_ids.extend(selected_ids)

        # push  already_selected_profiles_ids candidates to output tables
        df_candidates_chunks, df_candidates_collabs, df_candidates_cvs, df_candidates_profiles = self._push_candidates(
            df_chunks_scored,
            df_collabs,
            df_cvs,
            df_profiles_scored,
            already_selected_profiles_ids)
        # assert df formats
        if not DataFrameHandler.assert_df(df_candidates_chunks, SCORED_CHUNKS_DF):
            return [None] * 4
        if not DataFrameHandler.assert_df(df_candidates_collabs, COLLAB_PG):
            return [None] * 4
        if not DataFrameHandler.assert_df(df_candidates_cvs, CV_PG):
            return [None] * 4
        if not DataFrameHandler.assert_df(df_candidates_profiles, SCORED_PROFILES_DF):
            return [None] * 4
        # return if all goes well
        logging.info("Selection done" + str(time.time() - t))
        return df_candidates_chunks, df_candidates_collabs, df_candidates_cvs, df_candidates_profiles

    # =============================================================================
    # internal functions
    # =============================================================================

    def _get_scores_subquery(self,
                             df_chunks: pd.DataFrame,
                             df_profiles: pd.DataFrame,
                             query_row: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
        """
         Gets the scores for each subquery.

         Args:
             df_chunks (pd.DataFrame): A dataframe containing chunk information.
             df_profiles (pd.DataFrame): A dataframe containing profile information.
             query_row (pd.Series): A series containing the query row information.

         Returns:
             pd.DataFrame, pd.DataFrame: Two dataframes containing the scored chunks and scored profiles.
        """

        # create query used for dataframe scoring (keyword scores)
        keywords_query = self.queryTransformer.get_keywords_query(query_row)

        # create query used for semantic scoring
        embedded_semantic_query = self.queryTransformer.get_embedded_query(query_row)

        # compute overall scores for each profiles
        df_chunks_scored, df_profiles_scored = self.scorer.get_overall_scores(df_chunks,
                                                                              df_profiles,
                                                                              keywords_query,
                                                                              embedded_semantic_query)
        return df_chunks_scored, df_profiles_scored

    def _select_profiles_ids(self, nb_profiles: int,
                             already_selected_profiles_ids: list[str],
                             df_scored_profiles: pd.DataFrame) -> list[str]:
        """
        Selects the profile IDs based on the given number of profiles required for a subquery
        already selected profile IDs are excluded 

        Args:
            nb_profiles (int): The number of profiles to select.
            already_selected_profiles_ids (str): A string containing the already selected profile IDs.
            df_scored_profiles (pd.DataFrame): A dataframe containing the scored profiles.

        Returns:
            list[int]: A list of selected profile IDs.
        """

        # sort profile by overall score
        sorted_ids = df_scored_profiles.sort_values(by=[SCORED_PROFILES_DF.overall_score], ascending=False)[
            SCORED_PROFILES_DF.collab_id].values
        # counters for loop
        added_ids = 0
        idx = 0
        subquery_selected_ids = []
        # fetch available candidate in a loop
        while (idx < len(sorted_ids)) and added_ids < nb_profiles:
            # exclude candidate already selected prior and during this subquery
            if (sorted_ids[idx] not in already_selected_profiles_ids) and (
                    sorted_ids[idx] not in subquery_selected_ids):
                subquery_selected_ids.append(sorted_ids[idx])
                added_ids += 1
            idx += 1
        return subquery_selected_ids

    def _push_candidates(self,
                         df_chunks_scored: pd.DataFrame,
                         df_collabs: pd.DataFrame,
                         df_cvs: pd.DataFrame,
                         df_profiles_scored: pd.DataFrame,
                         collab_ids: list[str]) -> tuple[Any, Any, Any, Any]:
        """
        Pushes the selected candidates to the output tables.

        Args:
            df_chunks_scored (pd.DataFrame): A dataframe containing the scored chunks.
            df_collabs (pd.DataFrame): A dataframe containing collaboration information.
            df_cvs (pd.DataFrame): A dataframe containing CV information.
            df_profiles_scored (pd.DataFrame): A dataframe containing the scored profiles.
            collab_ids (list[str]): A list of selected profile IDs.

        Returns:
            pd.DataFrame: same as args but filtered by collab_ids
        """
        # populate dataframes
        df_candidates_chunks = df_chunks_scored.loc[df_chunks_scored[SCORED_CHUNKS_DF.collab_id].isin(collab_ids)]
        df_candidates_profiles = df_profiles_scored.loc[df_profiles_scored[SCORED_PROFILES_DF.collab_id].isin(
            collab_ids)]
        df_candidates_cvs = df_cvs.loc[df_cvs[CV_PG.collab_id].isin(collab_ids)]

        collab_ids = df_candidates_profiles[SCORED_PROFILES_DF.collab_id].values
        df_candidates_collabs = df_collabs.loc[df_collabs[COLLAB_PG.collab_id].isin(collab_ids)]

        return df_candidates_chunks, df_candidates_collabs, df_candidates_cvs, df_candidates_profiles


# %%
if __name__ == '__main__':
    settings = Settings()
    # get fake Jordan query
    from app.core.chatbot_features.intentionfinder import IntentionFinder

    QUERY_EXAMPLE = "Trouve moi 3 consultants pour une mission dans la banque"
    intention_finder = IntentionFinder(settings)
    df_query = intention_finder.guess_intention(QUERY_EXAMPLE)
    print(df_query)

    # fetch from postgres with filters based on query
    from app.core.chatbot_features.PGfetcher import PGfetcher

    PGfetcher = PGfetcher(settings)
    df_chunks, df_collabs, df_cvs, df_profiles = PGfetcher.fetch_all()

    # select best candidates
    selector = CandidatesSelector(settings)
    candidates_chunks, candidates_collabs, candidates_cvs, candidates_profiles = selector.select_candidates(df_chunks,
                                                                                                            df_collabs,
                                                                                                            df_cvs,
                                                                                                            df_profiles,
                                                                                                            df_query)
