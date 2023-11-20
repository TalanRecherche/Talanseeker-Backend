"""Created on Tue Aug  8 17:04:53 2023

@author: agarc

"""
import logging
import re

import pandas as pd
from tqdm import tqdm

from app.core.models.ETL_pandasmodels import CHUNK_DF, EMBEDDING_DF
from app.core.shared_modules.embedderbackend import EmbedderBackend


class ChunkEmbedder:
    """Embed (vectorize) chunks obtained from the Chunker class.
    Adds a new columns chunk_embeddings
    """

    def __init__(self, settings):
        # set up embedder backend
        self.embedder = EmbedderBackend(settings)

    # =============================================================================
    #     user functions
    # =============================================================================

    def embed_chunk_dataframe(self, df_chunks) -> pd.DataFrame | None:
        """Embeds an entire DataFrame by applying the _embed_single_chunk() function
        to each row.

        Args:
        ----
            df_chunks (pd.DataFrame): The input DataFrame containing the text chunks.

        Returns:
        -------
            pd.DataFrame: A DataFrame containing the original data and the new
            embeddings column.
        """
        # assert if input dataframe is of correct format (columns)
        if not CHUNK_DF.validate_dataframe(df_chunks):
            return None

        logging.info(f"Embeddings {len(df_chunks)} chunks...")
        # Use a list comprehension to apply the _embed_single_chunk() function
        # to each row of the input DataFrame
        embedded_rows = [
            self._embed_single_chunk(row)
            for _, row in tqdm(
                df_chunks.iterrows(),
                total=len(df_chunks),
                desc="Embeddings:",
            )
        ]

        # Convert the list of dictionaries to a DataFrame
        df_embedded_chunks = pd.DataFrame(embedded_rows)

        if df_embedded_chunks.empty:
            logging.warning("empty embeddings")
            return None

        logging.info("done")
        return df_embedded_chunks

    # =============================================================================
    # internal functions
    # =============================================================================
    def _embed_single_chunk(self, df_chunk_row: pd.Series) -> dict:
        """Row wise embedding. Embed a single chunk (row)

        Parameters
        ----------
        df_chunk_row : dataframe (single row)
            single row of a dataframe.

        Returns
        -------
        embedded_chunk_row : dataframe (single row)
            single-row dataframe with added embeddings.

        """
        # prepare the string
        text_to_embed = df_chunk_row[CHUNK_DF.chunk_text]
        prepared_string_to_embed = self._prep_string_to_embed(text_to_embed)
        # embed the string
        embedding = self.embedder.embed_string(prepared_string_to_embed)
        # Return a dictionary with previous data
        embedded_chunk_row = df_chunk_row.to_dict()
        # add an embeddings column
        embedded_chunk_row[EMBEDDING_DF.chunk_embeddings] = embedding

        return embedded_chunk_row

    def _prep_string_to_embed(self, string: str) -> str:
        r"""Clean string to embed
        add extra context
        /!\ a lot of fine tuning must go there
        """
        global_context_string = """Extrait du Curriculum Vitae: \n\n"""

        # remove multiple linebreaks and space
        cleaned_text = re.sub(r"\n\n+", "\n\n", string)
        cleaned_text = re.sub(r" +", " ", cleaned_text)
        # clean trailing spaces and linebreaks
        cleaned_text = cleaned_text.strip()
        cleaned_text = cleaned_text.rstrip("\n")

        string_to_embed = global_context_string + cleaned_text
        return string_to_embed


# %%
if __name__ == "__main__":
    directory = r"data_dev/data_1"
    # prepare {filenames : collab_id} map from the main
    from app.core.shared_modules.pathexplorer import PathExplorer

    files = PathExplorer.get_all_paths_with_extension_name(directory)
    collab_ids = {
        files[ii]["file_full_name"]: str(ii * 1231) for ii in range(len(files))
    }

    # extract text from CVs
    from app.core.cv_information_retrieval.filemassextractor import FileMassExtractor

    extractor = FileMassExtractor()
    text_df = extractor.read_all_documents(directory, collab_ids)

    # make chunks, One row per chunks
    from app.core.cv_information_retrieval.chunker import Chunker

    chunker = Chunker()
    df_chunks = chunker.chunk_documents(text_df)

    # make embeddings
    from app.settings import Settings

    embedder = ChunkEmbedder(Settings())
    df_embeddings = embedder.embed_chunk_dataframe(df_chunks)
