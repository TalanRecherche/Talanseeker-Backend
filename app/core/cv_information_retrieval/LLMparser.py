# -*- coding: utf-8 -*-
"""
Created on Tue Aug 22 14:55:20 2023

@author: agarc

"""
import logging

import pandas as pd
from tqdm import tqdm
from unidecode import unidecode

from app.core.models.pandascols import CHUNK_DF
from app.core.models.pandascols import PARSED_DF
from app.core.shared_modules.LLMbackend import LLMBackend
from app.core.shared_modules.dataframehandler import DataFrameHandler
from app.core.shared_modules.stringhandler import StringHandler
from app.settings import Settings


class LLMParser:
    """
    Handles parsing (extracting structured information from strings using llm)
    Loads a dataframe containing chunks (from the Chunker class)
    Each chunk text is sent to the backend llm with proper prompting
    The llm will attempt to extract relevant information
    This information is appended to a new dataframe one row per chunk
    """

    def __init__(self, settings):
        # set up openai environment
        # setup backend llm
        self.engine = settings.ETL_settings.ETL_llm_model
        self.BackEnd = LLMBackend(llm_model=self.engine, max_token_in_response=300)
        # prompting and query formatting for the backend./!\ modify this at your own risk.
        self.system_template_string = settings.ETL_settings.ETL_system_template
        self.query_template_string = settings.ETL_settings.ETL_query_template

        logging.debug("LLMParser init success")

        self.string_replacements = {'not provided': '',
                                    '(': '',
                                    ')': '',
                                    '/': '',
                                    '\n': '',
                                    '\t': '',
                                    r'\\': '',
                                    '[': '',
                                    ']': '',
                                    '  ': ' ',
                                    '   ': ' ',
                                    '"': '',
                                    ';': ',',
                                    '_': '',
                                    '-': ' '}
        pass

    # =============================================================================
    # User functions
    # =============================================================================
    def parse_all_chunks(self, df_chunks: pd.DataFrame) -> pd.DataFrame | None:
        """
        Extract information of each chunk using the llm

        Parameters
        ----------
        df_chunks : pandas dataframe
            from the embedder class.

        Returns
        -------
        df_parsed : pandas dataframe
            same dataframe with additional columns from the structuration
        """
        # assert if input dataframe is of correct format (columns)
        if DataFrameHandler.assert_df(df_chunks, CHUNK_DF) is False:
            return None

        all_chunks_hashmap = []
        logging.debug(
            "Parsing {l} chunks...".format(l=len(df_chunks))
        )
        # iter over rows (chunks)
        for _, row in tqdm(df_chunks.iterrows(), total=len(df_chunks), desc="Parsing:"):
            # get llm response (parsing)
            llm_response = self._parse_single_chunk(row)
            # push to hashmap (and normalize strings)
            response_hashmap = self._push_to_hashmap(llm_response)
            # only successfully parsed and stored responses are placed in the new df.
            if response_hashmap:
                for keys in row.keys():
                    response_hashmap[keys] = row[keys]

                all_chunks_hashmap.append(response_hashmap)

        df_parsed = pd.DataFrame.from_dict(all_chunks_hashmap)

        if df_parsed.empty:
            logging.warning("nothing parsed")
            return None

        # reorder columns
        df_parsed = df_parsed[PARSED_DF.get_attributes_()]
        logging.info("done")
        return df_parsed

    # =============================================================================
    # Internal functions
    # =============================================================================
    def _parse_single_chunk(self, chunk_row: pd.Series) -> str:
        """
        Parse a single row of the dataframe

        Parameters
        ----------
        chunk_row :  (pd.Series)

        Returns
        -------
        llm_response : str
            llm response string.
        """
        query = self._make_query(chunk_row)
        system_function = self._make_system()
        llm_response = self.BackEnd.send_receive_message(query, system_function)
        return llm_response

    def _push_to_hashmap(self, llm_response: str) -> dict:
        """
        Place the llm response string into a hashmap
        this will enable placing back the llm response into the original dataframe as new columns
        This step also "normalizes" the strings droping useless accents, lowercase etc.

        Parameters
        ----------
        llm_response : str
            llm response from _parse_single_chunk.

        Returns
        -------
        hashmap : hashmap
            structured information.
        """
        split_string = llm_response.split('\n')

        # prepare output container
        hashmap = {}
        hashmap_keys = PARSED_DF.parsed_keys_

        for idx, key in enumerate(hashmap_keys):
            try:
                # extract and clean the strings
                parsed_string = self._clean_string(split_string[idx].split("=")[1])
                # place in hashmap
                hashmap[key] = parsed_string
            except Exception as e:
                hashmap[key] = ''
                logging.warning("LLMParser: nothing parsed {}".format(e))

        return hashmap

    def _clean_string(self, string: str) -> str:
        """
        Normalize a single string.
        This is specific to this class so it should remain here and not in StaticMethods

        Parameters
        ----------
        string : str

        Returns
        -------
        string : str
        """

        # normalize string
        string = string.strip()
        string = string.rstrip()
        string = string.lower()
        string = unidecode(string)
        # get rid of useless characters
        string = StringHandler.replace_in_string(string, self.string_replacements)
        # split to parse better
        strings = string.split(',')
        # normalize
        strings = [string.strip() for string in strings if string != '']
        strings = [string.rstrip() for string in strings if string != '']
        # remove Nones and take uniques values
        strings = filter(None, strings)
        strings = set(strings)
        # rejoin
        string = ', '.join(strings)
        # clean string again
        string = StringHandler.replace_in_string(string, self.string_replacements)
        string = string.rstrip()
        return string

    def _make_query(self, chunk: pd.Series) -> str:
        """
        Generate the query from the template and cv content/metadata
        """
        # content of the query
        cv_text = chunk[CHUNK_DF.chunk_text]
        cv_source = chunk[CHUNK_DF.file_full_name]

        query_template = self.query_template_string
        cv_text = cv_text.replace('\n\n\n', '\n\n')
        query = query_template.format(source=cv_source, text=cv_text)
        return query

    def _make_system(self) -> str:
        """ place holder for future updates"""
        return self.system_template_string


if __name__ == "__main__":
    settings = Settings()
    directory = r'data_dev/data_1'
    # prepare {filenames : collab_id} map from the main
    from app.core.shared_modules.pathexplorer import PathExplorer
    files = PathExplorer.get_all_paths_with_extension_name(directory)
    collab_ids = {files[ii]["file_full_name"]: str(ii * 1231) for ii in range(len(files))}

    # extract text from CVs
    from app.core.cv_information_retrieval.filemassextractor import FileMassExtractor
    extractor = FileMassExtractor()
    text_df = extractor.read_all_documents(directory, collab_ids)

    # chunks documents
    from app.core.cv_information_retrieval.chunker import Chunker
    chunker = Chunker()
    df_chunks = chunker.chunk_documents(text_df)

    # parse the chunks
    parser = LLMParser(settings)
    parsed_chunks = parser.parse_all_chunks(df_chunks)

    print(parsed_chunks)
