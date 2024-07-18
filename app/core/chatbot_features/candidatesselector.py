"""Created on Thu Sep 13 10:04:44 2023

@author: agarc

"""
import logging
from typing import Any

import pandas as pd

from app.core.chatbot_features.querytransformer import QueryTransformer
from app.core.chatbot_features.scoreroverall import ScorerOverall
from app.core.models.pg_pandasmodels import CollabPg, CvPg
from app.core.models.query_pandasmodels import QueryStruct
from app.core.models.scoredprofiles_pandasmodels import ScoredChunksDF, ScoredProfilesDF


class CandidatesSelector:
    """This class read the normalized/structured query from GuessIntention.
    It then finds best candidates and returns their dataframes
    """

    def __init__(self) -> None:
        self.queryTransformer = QueryTransformer()
        self.scorer = ScorerOverall()

    # =============================================================================
    # user functions
    # =============================================================================
    def select_candidates(
        self,
        df_chunks: pd.DataFrame,
        df_collabs: pd.DataFrame,
        df_cvs: pd.DataFrame,
        df_profiles: pd.DataFrame,
        df_query: pd.DataFrame,
        already_selected_profiles_ids: list,
    ) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame] | list[None]:
        # Prepare list of selected ids
        already_selected_profiles_ids = already_selected_profiles_ids
        # loop through sub queries from GuessIntention
        for _, row in df_query.iterrows():
            query_row = pd.DataFrame(row).T
            # get scores for profiles and chunks of this subquery
            df_chunks_scored, df_profiles_scored = self._get_scores_subquery(
                df_chunks,
                df_profiles,
                query_row,
            )
            # number of identical profiles needed in this subquery

            try:
                nb_profiles = int(query_row[QueryStruct.nb_profiles][0][0])
            except Exception as e:
                nb_profiles = 6
                logging.exception(e)

            # find best profiles for this subquery, NOT in already_selected_profiles_ids
            selected_ids = self._select_profiles_ids(
                nb_profiles,
                already_selected_profiles_ids,
                df_profiles_scored,
            )
            # place new profiles in already_selected_profiles_ids
            already_selected_profiles_ids.extend(selected_ids)


        # push  already_selected_profiles_ids candidates to output tables
        (
            df_candidates_chunks,
            df_candidates_collabs,
            df_candidates_cvs,
            df_candidates_profiles,
        ) = self._push_candidates(
            df_chunks_scored,
            df_collabs,
            df_cvs,
            df_profiles_scored,
            already_selected_profiles_ids,
        )
        return (
            df_candidates_chunks,
            df_candidates_collabs,
            df_candidates_cvs,
            df_candidates_profiles,
        )

    # =============================================================================
    # internal functions
    # =============================================================================

    def _get_scores_subquery(
        self,
        df_chunks: pd.DataFrame,
        df_profiles: pd.DataFrame,
        query_row: pd.DataFrame,
    ) -> tuple[pd.DataFrame, pd.DataFrame]:
        """Gets the scores for each subquery.

        Args:
        ----
            df_chunks (pd.DataFrame): A dataframe containing chunk information.
            df_profiles (pd.DataFrame): A dataframe containing profile information.
            query_row (pd.Series): A series containing the query row information.

        Returns: ------- pd.DataFrame, pd.DataFrame: Two dataframes containing the
        scored chunks and scored profiles.
        """
        # create query used for dataframe scoring (keyword scores)
        keywords_query = self.queryTransformer.get_keywords_query(query_row)

        # create query used for semantic scoring
        embedded_semantic_query = self.queryTransformer.get_embedded_query(query_row)

        # compute overall scores for each profiles
        df_chunks_scored, df_profiles_scored = self.scorer.get_overall_scores(
            df_chunks,
            df_profiles,
            keywords_query,
            embedded_semantic_query,
        )
        return df_chunks_scored, df_profiles_scored

    def _select_profiles_ids(
        self,
        nb_profiles: int,
        already_selected_profiles_ids: list[str],
        df_scored_profiles: pd.DataFrame,
    ) -> list[str]:
        """Selects the profile IDs based on the given number of profiles
        required for a subquery
        already selected profile IDs are excluded

        Args:
        ----
            nb_profiles (int): The number of profiles to select.
            already_selected_profiles_ids (str): A string containing the already
            selected profile IDs.
            df_scored_profiles (pd.DataFrame): A dataframe containing the
            scored profiles.

        Returns:
        -------
            list[int]: A list of selected profile IDs.
        """
        # sort profile by overall score
        sorted_ids = df_scored_profiles.sort_values(
            by=[ScoredProfilesDF.overall_score],
            ascending=False,
        )[ScoredProfilesDF.collab_id].values
        # counters for loop
        added_ids = 0
        idx = 0
        subquery_selected_ids = []
        # fetch available candidate in a loop
        while (idx < len(sorted_ids)) and added_ids < nb_profiles:
            # exclude candidate already selected prior and during this subquery
            if (sorted_ids[idx] not in already_selected_profiles_ids) and (
                sorted_ids[idx] not in subquery_selected_ids
            ):
                subquery_selected_ids.append(sorted_ids[idx])
                added_ids += 1
            idx += 1
        return subquery_selected_ids

    def _push_candidates(
        self,
        df_chunks_scored: pd.DataFrame,
        df_collabs: pd.DataFrame,
        df_cvs: pd.DataFrame,
        df_profiles_scored: pd.DataFrame,
        collab_ids: list[str],
    ) -> tuple[Any, Any, Any, Any]:
        """Pushes the selected candidates to the output tables.

        Args:
        ----
            df_chunks_scored (pd.DataFrame): A dataframe containing the scored chunks.
            df_collabs (pd.DataFrame): A dataframe containing collaboration information.
            df_cvs (pd.DataFrame): A dataframe containing CV information.
            df_profiles_scored (pd.DataFrame): A dataframe containing the
            scored profiles.
            collab_ids (list[str]): A list of selected profile IDs.

        Returns:
        -------
            pd.DataFrame: same as args but filtered by collab_ids
        """
        # populate dataframes
        df_candidates_chunks = df_chunks_scored.loc[
            df_chunks_scored[ScoredChunksDF.collab_id].isin(collab_ids)
        ]
        df_candidates_profiles = df_profiles_scored.loc[
            df_profiles_scored[ScoredProfilesDF.collab_id].isin(collab_ids)
        ]
        df_candidates_cvs = df_cvs.loc[df_cvs[CvPg.collab_id].isin(collab_ids)]

        collab_ids = df_candidates_profiles[ScoredProfilesDF.collab_id].values
        df_candidates_collabs = df_collabs.loc[
            df_collabs[CollabPg.collab_id].isin(collab_ids)
        ]

        return (
            df_candidates_chunks,
            df_candidates_collabs,
            df_candidates_cvs,
            df_candidates_profiles,
        )
