"""Created on Tue Aug  8 17:04:53 2023

@author: agarc

"""
import logging
import re

import pandas as pd
from tqdm import tqdm

from app.core.models.etl_pandasmodels import ChunkDF, EmbeddingDF
from app.core.shared_modules.embedderbackend import EmbedderBackend


class ChunkEmbedder:
    """Embed (vectorize) chunks obtained from the Chunker class.
    Adds a new columns chunk_embeddings
    """

    def __init__(self) -> None:
        # set up embedder backend
        self.embedder = EmbedderBackend()

    # =============================================================================
    #     user functions
    # =============================================================================

    def embed_chunk_dataframe(self, df_chunks: pd.DataFrame) -> pd.DataFrame | None:
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
        if not ChunkDF.validate_dataframe(df_chunks):
            return None

        log_string = f"Embedding {len(df_chunks)} chunks..."
        logging.info(log_string)
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
        text_to_embed = df_chunk_row[ChunkDF.chunk_text]
        prepared_string_to_embed = self._prep_string_to_embed(text_to_embed)
        # embed the string
        embedding = self.embedder.embed_string(prepared_string_to_embed)
        # Return a dictionary with previous data
        embedded_chunk_row = df_chunk_row.to_dict()
        # add an embeddings column
        embedded_chunk_row[EmbeddingDF.chunk_embeddings] = embedding

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
