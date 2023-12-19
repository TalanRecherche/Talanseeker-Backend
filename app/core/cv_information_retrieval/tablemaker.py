"""Created on Wed Aug 30 17:55:25 2023

@author: agarc

This whole thing is garbage for now.

Ideally :
    1. make the pg_collabs table from Kimble or the DA.
    2. make the pg_profile table : to each profile, find the collab_id using
    names/surnames in the pg_collab table.
    3. Now each profile_id is matched to a collab_id
    4. make the pg_cvs table: each cv is assigned a profile_id, which is also
    assigned a collab_id
    5. etc.
"""
import logging

import pandas as pd

from app.core.models.etl_pandasmodels import EmbeddingDF, StructProfileDF
from app.core.models.pg_pandasmodels import ChunkPg, CvPg, ProfilePg


class TableMaker:
    def __init__(self) -> None:
        pass

    # =============================================================================
    #     user functions
    # =============================================================================
    def make_pg_tables(
        self,
        df_profiles: pd.DataFrame,
        df_embeddings: pd.DataFrame,
    ) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame] | list[None]:
        # assert if input dataframe is of correct format (columns)
        if not StructProfileDF.validate_dataframe(df_profiles):
            return [None] * 3
        if not EmbeddingDF.validate_dataframe(df_embeddings):
            return [None] * 3

        pg_profiles = self._make_pg_profiles(df_profiles)
        pg_cvs = self._make_pg_cvs(df_profiles, df_embeddings)
        pg_chunks = self._make_pg_chunks(df_profiles, df_embeddings)

        logging.info("PG table done.")
        return pg_profiles, pg_chunks, pg_cvs

    # =============================================================================
    # internal functions
    # =============================================================================
    def _make_pg_profiles(self, df_profiles: pd.DataFrame) -> pd.DataFrame:
        """Drop irrelevant columns to prepare pg_profiles"""
        # reorder columns
        pg_profiles = df_profiles[ProfilePg.get_attributes()]
        return pg_profiles

    def _make_pg_cvs(
        self,
        df_profiles: pd.DataFrame,
        df_embeddings: pd.DataFrame,
    ) -> pd.DataFrame | None:
        # prepare output container
        # fill in using unique chunks from embeddings
        pg_cvs = df_embeddings.copy().drop_duplicates(subset=CvPg.file_full_name)
        # add empty profile_empty
        pg_cvs[CvPg.collab_id] = ""
        for idx in range(len(df_profiles)):
            cv_ids = df_profiles.iloc[idx][StructProfileDF.cv_id]
            for cv_id in cv_ids:
                pg_cvs_idx = pg_cvs[(pg_cvs[CvPg.cv_id] == cv_id)].index.values
                if pg_cvs_idx.size > 0:
                    collab_id = df_profiles.iloc[idx][StructProfileDF.collab_id]
                    pg_cvs.loc[pg_cvs_idx[0], CvPg.collab_id] = collab_id

        if pg_cvs.empty:
            logging.warning("returns empty")
            return None
        # reorder columns
        pg_cvs = pg_cvs[CvPg.get_attributes()]
        return pg_cvs

    def _make_pg_chunks(
        self,
        df_profiles: pd.DataFrame,
        df_embeddings: pd.DataFrame,
    ) -> pd.DataFrame | None:
        # prepare output container
        pg_chunks = pd.DataFrame(columns=ChunkPg.get_attributes())
        # get values from embeddings_df
        merge_cols = [
            col
            for col in ChunkPg.get_attributes()
            if col in EmbeddingDF.get_attributes()
        ]
        pg_chunks = pg_chunks.merge(df_embeddings, on=merge_cols, how="outer")

        for idx in range(len(df_profiles)):

            collab_ids = df_profiles.iloc[idx][StructProfileDF.collab_id]
            for collab_id in collab_ids:
                pg_cvs_idx = pg_chunks[(pg_chunks[ChunkPg.collab_id] == collab_id)].index.values
                if pg_cvs_idx.size > 0:
                    collab_id = df_profiles.iloc[idx][StructProfileDF.collab_id]
                    pg_chunks.loc[pg_cvs_idx, ChunkPg.collab_id] = collab_id

            """
            cv_ids = df_profiles.iloc[idx][StructProfileDF.cv_id]
            for cv_id in cv_ids:
                pg_cvs_idx = pg_chunks[(pg_chunks[ChunkPg.cv_id] == cv_id)].index.values
                if pg_cvs_idx.size > 0:
                    collab_id = df_profiles.iloc[idx][StructProfileDF.collab_id]
                    pg_chunks.loc[pg_cvs_idx, ChunkPg.collab_id] = collab_id
            """

        if pg_chunks.empty:
            logging.warning("returns empty")
            return None

        # reorder columns
        pg_chunks = pg_chunks[ChunkPg.get_attributes()]
        return pg_chunks
