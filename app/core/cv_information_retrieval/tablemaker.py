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

from app.core.models.ETL_pandasmodels import EMBEDDING_DF, STRUCTPROFILE_DF
from app.core.models.PG_pandasmodels import CHUNK_PG, CV_PG, PROFILE_PG
from app.core.shared_modules.dataframehandler import DataFrameHandler
from app.core.shared_modules.stringhandler import StringHandler


class TableMaker:
    def __init__(self):
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
        if not STRUCTPROFILE_DF.validate_dataframe(df_profiles):
            return [None] * 3
        if not EMBEDDING_DF.validate_dataframe(df_embeddings):
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
        """Drops irrelevant columns to prepare pg_profiles"""
        # reorder columns
        pg_profiles = df_profiles[PROFILE_PG.get_attributes()]
        return pg_profiles

    def _make_pg_cvs(
        self,
        df_profiles: pd.DataFrame,
        df_embeddings: pd.DataFrame,
    ) -> pd.DataFrame | None:
        # prepare output container
        # fill in using unique chunks from embeddings
        pg_cvs = df_embeddings.copy().drop_duplicates(subset=CV_PG.file_full_name)
        # add empty profile_empty
        pg_cvs[CV_PG.collab_id] = ""
        for idx in range(len(df_profiles)):
            cv_ids = df_profiles.iloc[idx][STRUCTPROFILE_DF.cv_id]
            for cv_id in cv_ids:
                pg_cvs_idx = pg_cvs[(pg_cvs[CV_PG.cv_id] == cv_id)].index.values
                if pg_cvs_idx.size > 0:
                    collab_id = df_profiles.iloc[idx][STRUCTPROFILE_DF.collab_id]
                    pg_cvs.loc[pg_cvs_idx[0], CV_PG.collab_id] = collab_id

        if pg_cvs.empty:
            logging.warning("returns empty")
            return None
        # reorder columns
        pg_cvs = pg_cvs[CV_PG.get_attributes()]
        return pg_cvs

    def _make_pg_chunks(
        self,
        df_profiles: pd.DataFrame,
        df_embeddings: pd.DataFrame,
    ) -> pd.DataFrame | None:
        # prepare output container
        pg_chunks = pd.DataFrame(columns=CHUNK_PG.get_attributes())
        # get values from embeddings_df
        merge_cols = [
            col
            for col in CHUNK_PG.get_attributes()
            if col in EMBEDDING_DF.get_attributes()
        ]
        pg_chunks = pg_chunks.merge(df_embeddings, on=merge_cols, how="outer")

        for idx in range(len(df_profiles)):
            cv_ids = df_profiles.iloc[idx][STRUCTPROFILE_DF.cv_id]
            for cv_id in cv_ids:
                pg_cvs_idx = pg_chunks[
                    (pg_chunks[CHUNK_PG.cv_id] == cv_id)
                ].index.values
                if pg_cvs_idx.size > 0:
                    collab_id = df_profiles.iloc[idx][STRUCTPROFILE_DF.collab_id]
                    pg_chunks.loc[pg_cvs_idx, CHUNK_PG.collab_id] = collab_id

        if pg_chunks.empty:
            logging.warning("returns empty")
            return None

        # reorder columns
        pg_chunks = pg_chunks[CHUNK_PG.get_attributes()]
        return pg_chunks


if __name__ == "__main__":
    from app.settings import Settings

    env = Settings()
    data_path = r"data_dev/data_1"
    # data_path = r'data_dev/data_1_1cv'

    # prepare {filenames : collab_id} map from the main
    from app.core.shared_modules.pathexplorer import PathExplorer

    files = PathExplorer.get_all_paths_with_extension_name(data_path)
    collab_ids = {
        files[ii]["file_full_name"]: StringHandler.generate_unique_id(str(ii))
        for ii in range(len(files))
    }

    # =============================================================================
    #     # extract text
    # =============================================================================
    from app.core.cv_information_retrieval.filemassextractor import FileMassExtractor

    extractor = FileMassExtractor()
    # get text dataframe. One row per documents
    df_text = extractor.read_all_documents(
        data_path,
        collab_ids,
        read_only_extensions=[],
        ignore_extensions=[],
    )
    print("1", df_text["collab_id"])
    # =============================================================================
    #     # make the chunks
    # =============================================================================
    from app.core.cv_information_retrieval.chunker import Chunker

    chunker = Chunker()
    # make chunks, One row per chunks
    df_chunks = chunker.chunk_documents(df_text)
    print("2", df_chunks["collab_id"])
    # =============================================================================
    #     # compute embeddings
    # =============================================================================
    from app.core.cv_information_retrieval.chunkembedder import ChunkEmbedder

    embedder = ChunkEmbedder(env)
    df_embeddings = embedder.embed_chunk_dataframe(df_chunks)
    DataFrameHandler.save_df(
        df_embeddings,
        save_to_file_path=data_path + r"\df_embeddings.pkl",
    )
    print("3", df_embeddings["collab_id"])
    # =============================================================================
    #     # parse the chunks
    # =============================================================================
    from app.core.cv_information_retrieval.LLMparser import LLMParser

    parser = LLMParser(env)
    parsed_chunks = parser.parse_all_chunks(df_chunks)
    DataFrameHandler.save_df(
        parsed_chunks,
        save_to_file_path=data_path + r"\df_parsed_chunks.pkl",
    )
    print("4", parsed_chunks["collab_id"])
    # =============================================================================
    #     # consolidate CVs
    # =============================================================================
    parsed_chunks = DataFrameHandler.load_df(data_path + r"\df_parsed_chunks.pkl")
    from app.core.cv_information_retrieval.CVstructurator import CvStructurator

    cvStructurator = CvStructurator()
    df_struct_cvs = cvStructurator.consolidate_cvs(parsed_chunks)
    print("5", df_struct_cvs["collab_id"])
    # =============================================================================
    #     # consolidate profiles
    # =============================================================================
    from app.core.cv_information_retrieval.profilestructurator import (
        ProfileStructurator,
    )

    structure = ProfileStructurator()
    df_profiles = structure.consolidate_profiles(df_struct_cvs)
    print("6", df_profiles["collab_id"])
    # =============================================================================
    #     # make pg tables
    # =============================================================================
    df_embeddings = DataFrameHandler.load_df(data_path + r"\df_embeddings.pkl")
    maker = TableMaker()
    pg_profiles, pg_chunks, pg_cvs = maker.make_pg_tables(df_profiles, df_embeddings)
