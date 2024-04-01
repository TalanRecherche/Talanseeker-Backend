"""Created on Tue Aug 22 14:55:20 2023

@author: agarc

"""
import ast
import json
import logging
import re

import pandas as pd
from tqdm import tqdm
from unidecode import unidecode

from app.core.models.etl_pandasmodels import ChunkDF, ParsedDF
from app.core.shared_modules.gpt_backend import GptBackend
from app.core.shared_modules.stringhandler import StringHandler
from app.settings import settings


class LLMParser:
    """Handles parsing (extracting structured information from strings using llm)
    Loads a dataframe containing chunks (from the Chunker class)
    Each chunk text is sent to the backend llm with proper prompting
    The llm will attempt to extract relevant information
    This information is appended to a new dataframe one row per chunk
    """

    def __init__(self) -> None:
        # set up openai environment
        # setup backend llm
        self.engine = settings.ETL_settings.ETL_llm_model
        self.BackEnd = GptBackend(llm_model=self.engine, max_token_in_response=300)
        # prompting and query formatting for the backend. modify this at your own risk.
        self.system_template_string = settings.ETL_settings.ETL_system_template
        self.query_template_string = settings.ETL_settings.ETL_query_template

        logging.debug("LLMParser init success")

        self.string_replacements = {
            "not provided": "",
            "(": "",
            ")": "",
            "/": "",
            "\n": "",
            "\t": "",
            r"\\": "",
            "[": "",
            "]": "",
            "  ": " ",
            "   ": " ",
            ";": ",",
            "_": "",
            "-": " ",
            '"': "",
            "'": "",
        }

    # =============================================================================
    # User functions
    # =============================================================================
    def parse_all_chunks(self, df_chunks: pd.DataFrame) -> pd.DataFrame | None:
        """Extract information of each chunk using the llm

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
        if not ChunkDF.validate_dataframe(df_chunks):
            return None

        all_chunks_hashmap = []
        log_string = f"parsing {len(df_chunks)} chunks"
        logging.debug(log_string)

        # iter over rows (chunks)
        for _, row in tqdm(df_chunks.iterrows(), total=len(df_chunks), desc="Parsing:"):
            # get llm response (parsing)
            llm_response = self._read_single_chunk(row)
            # prepare string to JSON format
            json_string = self._prepare_json_string(llm_response)
            # push llm response to hashmap
            response_hashmap = self._push_response_to_hashmap(json_string)
            # clean llm response
            response_hashmap = self._clean_response(response_hashmap)
            # if response is not empty: add row fields and place into output hashmap
            if response_hashmap:
                for keys in row.keys():
                    # add rows fiels to final hashmap
                    response_hashmap[keys] = row[keys]
                # place response hashmap to final hashmap list
                all_chunks_hashmap.append(response_hashmap)

        df_parsed = pd.DataFrame.from_dict(all_chunks_hashmap)

        if df_parsed.empty:
            logging.warning("nothing parsed")
            return None

        # reorder columns
        df_parsed = df_parsed[ParsedDF.get_attributes()]
        logging.info("done")
        return df_parsed

    # =============================================================================
    # Internal functions
    # =============================================================================
    def _read_single_chunk(self, chunk_row: pd.Series) -> str:
        """Parse a single row of the dataframe

        Parameters
        ----------
        chunk_row :
            (pd.Series)

        Returns
        -------
        llm_response : str
            llm response string.
        """
        query = self._make_query(chunk_row)
        system_function = self._make_system()
        llm_response = self.BackEnd.send_receive_message(query, system_function)
        return llm_response

    def _prepare_json_string(self, llm_response: str) -> str:
        """Clean the llm response string into JSONable string"""
        # keep only string between brackets
        try:
            # get rid of everything that is not between double brackets
            json_string = llm_response.split("{", 1)[1].split("}")[0]
            json_string = "{\n" + json_string + "\n}"
            # replace single quote to double quote for JSON format
            json_string = json_string.replace("'", '"')
            # Replace double quotes within string values with escaped double quotes
            json_string = re.sub(r'(?<=[^])"(?=[^:,}]s])', r'\\"', json_string)
            # convert to raw string
            json_string = rf"{json_string}"
            return json_string

        except Exception as e:
            log_string = f"_prepare_JSON_string: failed {e}"
            logging.exception(log_string)
            return ""

    def _push_response_to_hashmap(self, json_string: str) -> dict:
        """Place the llm response string into a hashmap
        this will enable placing back the llm response into the original dataframe as
        new columns
        This step also "normalizes" the strings droping useless accents, lowercase etc.

        Parameters
        ----------
        json_string :
            str

        Returns
        -------
        hashmap : hashmap
            structured information.
        """
        try:
            # parse JSON to dict using JSON load
            hashmap_response = json.loads(json_string)
        except Exception as e:
            log_string = f"LLMParser_push_response_to_hashmap: nothing parsed {e}. "
            logging.exception(log_string)
            try:
                # if JSON load failed, we try manually
                hashmap_response = ast.literal_eval(json_string)
            except Exception as e:
                log_string = f"LLMParser_push_response_to_hashmap: nothing parsed {e}. "
                logging.exception(log_string)
                # if everything fails we send back an empty dict
                hashmap_response = {}

        return hashmap_response

    def _clean_response(self, response_hashmap: dict) -> dict:
        if not response_hashmap:
            return {}

        clean_hashmap = {}
        keys = ParsedDF.parsed_keys_
        # place response hashmap to output final hashmap
        for _, key in enumerate(keys):
            # non-years fields are list[str]
            if key != ParsedDF.years:
                try:
                    parsed_string = str(response_hashmap.get(key))
                    parsed_string = self._clean_string(parsed_string)
                    # place in hashmap
                    clean_hashmap[key] = parsed_string
                except Exception as e:
                    clean_hashmap[key] = []
                    log_string = f"_clean_response: {key} not caught {e}"
                    logging.exception(log_string)
            else:
                # year field is int
                try:
                    # attempt to grab the max integer from the list
                    found_integers = [
                        int(elem) for elem in response_hashmap.get(ParsedDF.years)
                    ]
                    clean_hashmap[ParsedDF.years] = max(found_integers)
                except Exception as e:
                    clean_hashmap[ParsedDF.years] = 0
                    log_string = f"_clean_response: .years not caught {e}"
                    logging.exception(log_string)

        if response_hashmap:
            return clean_hashmap
        else:
            return {}

    def _clean_string(self, string: str) -> list[str]:
        """Normalize a single string.
        This is specific to this class so it should remain here and not in StaticMethods

        Parameters
        ----------
        string :
            str

        Returns
        -------
        string :
            str
        """
        # normalize string
        string = string.strip()
        string = string.strip("\n")
        string = string.lower()
        string = unidecode(string)
        # get rid of useless characters
        string = StringHandler.replace_in_string(string, self.string_replacements)
        # split to parse better
        strings = string.split(",")
        # normalize
        strings = [string.strip() for string in strings if string != ""]
        strings = [string.rstrip() for string in strings if string != ""]
        # remove Nones and take uniques values
        strings = filter(None, strings)
        strings = set(strings)
        # rejoin
        string = ", ".join(strings)
        # clean string again
        string = StringHandler.replace_in_string(string, self.string_replacements)
        string = string.strip()
        string = string.strip("\n")
        # turn into list again
        strings = string.split(",")
        strings = [string.strip() for string in strings if string != ""]
        return strings

    def _make_query(self, chunk: pd.Series) -> str:
        """Generate the query from the template and cv content/metadata"""
        # content of the query
        cv_text = chunk[ChunkDF.chunk_text]
        cv_source = chunk[ChunkDF.file_full_name]

        query_template = self.query_template_string
        cv_text = cv_text.replace("\n\n\n", "\n\n")
        query = query_template.replace("{source}", cv_source)
        query = query.replace("{text}", cv_text)

        return query

    def _make_system(self) -> str:
        """Place holder for future updates"""
        return self.system_template_string
