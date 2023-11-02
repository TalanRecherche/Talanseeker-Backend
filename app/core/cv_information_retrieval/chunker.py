# -*- coding: utf-8 -*-
"""
Created on Fri Aug 25 13:51:53 2023

@author: agarc

"""
import logging

import pandas as pd
from tqdm import tqdm

from app.core.models.pandascols import CHUNK_DF
from app.core.models.pandascols import TEXT_DF
from app.core.shared_modules.dataframehandler import DataFrameHandler
from app.core.shared_modules.stringhandler import StringHandler


class Chunker:

    def __init__(self):
        self.chunk_min_size = 256
        self.chunk_max_size = 512

    # =============================================================================
    # User function
    # =============================================================================
    def chunk_documents(self, df_documents: pd.DataFrame) -> pd.DataFrame | None:
        """
        Create chunks from all documents within df obtained from FileMassExtractor
        Parameters
        ----------
        df_documents : dataframe
            contains all documents and their text.
        Returns
        -------
        df_chunks : dataframe
            dataframe containing all chunks, metadata and embeddings. One row per chunk.
        """
        # assert if input dataframe is of correct format (columns)
        if DataFrameHandler.assert_df(df_documents, TEXT_DF) is False: return None

        # prepare output container
        df_chunks = pd.DataFrame(columns=CHUNK_DF.get_attributes_())

        # iterate through each CV
        for index, row in tqdm(df_documents.iterrows(), desc="Chunking document:", total=len(df_documents)):
            # get text
            text = row[TEXT_DF.file_text]
            # cut into chunks
            chunks = self._split_string_approx(text,
                                               min_length=self.chunk_min_size,
                                               max_length=self.chunk_max_size)
            # push each chunk in a new row of the output pandas dataframe
            for chunk in chunks:
                # temp container
                chunk_df_temp = pd.DataFrame(columns=CHUNK_DF.get_attributes_())
                common_cols = list(set(TEXT_DF.get_attributes_()).intersection(set(CHUNK_DF.get_attributes_())))
                chunk_df_temp.loc[0, common_cols] = row[common_cols].values
                # assign current chunk
                chunk_df_temp[CHUNK_DF.chunk_text] = chunk
                # compute chunk_id using hash
                chunk_df_temp[CHUNK_DF.chunk_id] = StringHandler.generate_unique_id(chunk.lower())
                # push to new row
                if not chunk_df_temp.empty:
                    df_chunks = pd.concat([df_chunks, chunk_df_temp])

        if df_chunks.empty:
            logging.error("chunk_documents : df_chunks is empty")
            return None

        logging.info("Chunk done")
        return df_chunks

    # =============================================================================
    # internal functions
    # =============================================================================
    def _split_string_approx(self, text: str, min_length: int = 500, max_length: int = 700) -> list[str]:
        """
        Cut a string into chunks.
        The function attempts to cut at triple, double and single linebreaks (with priority)
        This is just an attempt at replacing Lanchain's garbage text splitters which don't work

        Parameters
        ----------
        text : str
            string to cut in chunks.
        min_length : int, optional
        max_length : int, optional

        Returns
        -------
        list[str]
            list of chunks.
        """
        chunks = []
        start = 0
        end = max_length

        while start < len(text):
            if end < len(text):
                # Find the nearest triple, double, or single line break within the specified length range
                triple_break = text.rfind('\n\n\n', start, end)
                double_break = text.rfind('\n\n', start, end)
                single_break = text.rfind('\n', start, end)

                if triple_break != -1 and triple_break - start >= min_length:
                    end = triple_break
                elif double_break != -1 and double_break - start >= min_length:
                    end = double_break
                elif single_break != -1 and single_break - start >= min_length:
                    end = single_break

            sliced_chunk = text[start:end].strip()
            chunks.append(sliced_chunk)

            start = end
            end += max_length

        return chunks


if __name__ == "__main__":
    directory = r'data_dev'
    # prepare {filenames : collab_id} map from the main
    from app.core.shared_modules.pathexplorer import PathExplorer

    files = PathExplorer.get_all_paths_with_extension_name(directory)
    collab_ids = {files[ii]["file_full_name"]: str(ii * 1231) for ii in range(len(files))}

    from app.core.cv_information_retrieval.filemassextractor import FileMassExtractor

    extractor = FileMassExtractor()
    text_df = extractor.read_all_documents(directory, collab_ids)

    # make chunks, One row per chunks
    chunker = Chunker()
    chunks = chunker.chunk_documents(text_df)

    # display chunk length histogram
    import matplotlib.pyplot as plt

    chunks[CHUNK_DF.chunk_text].apply(lambda x: len(x)).plot.hist(bins=50)
    plt.show()
