"""Created on Thu Sep 14 13:31:50 2023

@author: agarc

"""
import numpy as np
import pandas as pd
from cdifflib import CSequenceMatcher

from app.core.models.pg_pandasmodels import ChunkPg, ProfilePg
from app.core.models.scoredprofiles_pandasmodels import (
    ScoredChunksDF,
    ScoredProfilesDF,
)
from app.core.shared_modules.listhandler import ListHandler
from app.models import sql_to_pd
from app.models.chunks import ChunkModel


class ScorerProfiles:
    def __init__(self) -> None:
        pass

    # =============================================================================
    # user functions
    # =============================================================================
    def score_by_keywords(
        self,
        df_profiles: pd.DataFrame,
        keywords_query: list[str],
    ) -> pd.DataFrame:
        """Keyword scoring using the profile dataframe"""
        scored_df = df_profiles
        # add a keyword_score column by scoring profiles one by one
        scored_df[ScoredProfilesDF.keywords_score] = scored_df.apply(
            self._score_by_keywords_single_profile,
            axis=1,
            args=(keywords_query,),
        )
        return scored_df

    def score_score_by_semantic_pg_vector(self, embedded_query: list[float])-> pd.DataFrame:
        query = ChunkModel.similarity_query(embedded_query)
        df_chunks = sql_to_pd(query)
        df_chunks[ScoredChunksDF.semantic_score] = 1 - df_chunks[ScoredChunksDF.semantic_score]
        return df_chunks
    def score_by_semantic(
        self,
        df_chunks: pd.DataFrame,
        embedded_query: list[float],
    ) -> pd.DataFrame:
        """Semantic scoring using the chunk dataframe"""
        # Convert the embedded_query to a NumPy array
        embedded_query_np = np.array(embedded_query)
        # normalise
        embedded_query_norm = embedded_query_np / np.linalg.norm(embedded_query_np)

        # Extract the chunk embeddings as a NumPy array
        chunk_embeddings = np.stack(df_chunks[ChunkPg.chunk_embeddings].values)
        # normalise
        chunk_embeddings_norm = chunk_embeddings / np.linalg.norm(
            chunk_embeddings,
            axis=1,
            keepdims=True,
        )

        # Compute the cosine similarity using vectorized operations
        dot_product = np.dot(chunk_embeddings_norm, embedded_query_norm)
        cosine_similarity = dot_product

        # Assign the computed cosine similarity to the DataFrame
        df_chunks[ScoredChunksDF.semantic_score] = cosine_similarity
        return df_chunks

    def assign_scores_to_profiles(
        self,
        scored_keywords: pd.DataFrame,
        scored_chunks: pd.DataFrame,
    ) -> pd.DataFrame:
        """Assigning chunks score and keywords (best) to profile table."""
        # Merge the best similarity score from scored_chunks to scored_keywords
        best_similarity = (
            scored_chunks.groupby(ScoredChunksDF.collab_id)[
                ScoredChunksDF.semantic_score
            ]
            .max()
            .reset_index()
        )
        df_profiles_scored = pd.merge(
            scored_keywords,
            best_similarity,
            on=ScoredChunksDF.collab_id,
            how="left",
        )

        # Rename the merged column to the correct name
        df_profiles_scored.rename(
            columns={
                ScoredChunksDF.semantic_score: ScoredProfilesDF.semantic_score,
            },
            inplace=True,
        )

        # Normalize 0-1
        df_profiles_scored[
            ScoredProfilesDF.keywords_score_normalized
        ] = self._normalize_column(
            df_profiles_scored,
            ScoredProfilesDF.keywords_score,
        )

        # Normalize 0-1
        df_profiles_scored[
            ScoredProfilesDF.semantic_score_normalized
        ] = self._normalize_column(
            df_profiles_scored,
            ScoredProfilesDF.semantic_score,
        )

        return df_profiles_scored

    # =============================================================================
    # internal functions
    # =============================================================================

    def _score_by_keywords_single_profile(self, row: pd.DataFrame, query: str) -> float:
        """Similarity scoring using keywords"""
        threshold = 0.8
        # prepare data to check
        fields_to_check = [
            ProfilePg.diplomas_certifications,
            ProfilePg.roles,
            ProfilePg.sectors,
            ProfilePg.companies,
            ProfilePg.soft_skills,
            ProfilePg.technical_skills,
        ]
        # place data in a list
        relevant_data = row[fields_to_check].values.tolist()
        relevant_data = ListHandler.flatten_list(relevant_data)
        # make unique (skills dont count twice)
        relevant_data = list(set(relevant_data))
        # loop through query keywords and find similar string within the relevant_data
        score = 0
        for query_keyword in query:
            for data_keyword in relevant_data:
                if query_keyword == data_keyword:
                    score += 1
                else:
                    similarity = CSequenceMatcher(
                        None,
                        query_keyword,
                        data_keyword,
                    ).ratio()
                    if similarity > threshold:
                        score += 1
        return score

    def _normalize_column(
        self,
        df_scored_profiles: pd.DataFrame,
        target_column: list[str],
    ) -> pd.Series:
        """Normalize a columns within 0-1"""
        keywords_score_min = df_scored_profiles[target_column].min()
        keywords_score_max = df_scored_profiles[target_column].max()
        if keywords_score_min != keywords_score_max:
            normalized_col = (
                df_scored_profiles[target_column] - keywords_score_min
            ) / (keywords_score_max - keywords_score_min)
        else:
            normalized_col = df_scored_profiles[target_column] / keywords_score_max

        return normalized_col
