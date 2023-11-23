"""Created on Thu Sep 14 10:50:00 2023

@author: agarc

"""

import pandas as pd

from app.core.models.query_pandasmodels import QueryKeywords, QueryStruct
from app.core.shared_modules.embedderbackend import EmbedderBackend
from app.core.shared_modules.listhandler import ListHandler
from app.core.shared_modules.stringhandler import StringHandler
from app.settings.settings import Settings


class QueryTransformer:
    """This class generate the keywords/semantic queries to compute similarities."""

    def __init__(self, settings: Settings) -> None:
        # initialize embedder to vectorized query for semantic search
        self.embedder = EmbedderBackend(settings)

    # =============================================================================
    # user functions
    # =============================================================================
    def get_keywords_query(self, row_df_query: pd.DataFrame) -> list[str] | None:
        """Generate a list of keywords for the keyword search

        Parameters
        ----------
        row_df_query : pd.DataFrame
            subquery.

        Returns
        -------
        list of keywords.

        """
        # assert case
        if not QueryStruct.validate_dataframe(row_df_query):
            return None

        # filter only fields to be used to score
        filtered_df = row_df_query[QueryKeywords.get_attributes()]

        # concatenate keywords which will be used during the profile scoring
        list_keywords = ListHandler.flatten_list(filtered_df.values.tolist())
        # split
        list_keywords = [elem.split(",") for elem in list_keywords]
        # reflatten
        list_keywords = ListHandler.flatten_list(list_keywords)
        # normalise strings and remove empties
        list_keywords = [
            StringHandler.normalize_string(string)
            for string in list_keywords
            if string != ""
        ]
        # getting rid of duplicates
        list_keywords = list(set(list_keywords))
        # replace "useless" characters
        list_keywords = [
            StringHandler.replace_in_string(string) for string in list_keywords
        ]
        # remove useless keywords typically found in guessIntention
        to_remove = ["non renseigne", "", "_", "n.a.", "unknown", "renseigne"]
        list_keywords = [string for string in list_keywords if string not in to_remove]

        return list_keywords

    def get_embedded_query(self, row_df_query: pd.DataFrame) -> list[float]:
        """Generate the embedded query used during similarity search

        Parameters
        ----------
        row_df_query : pd.DataFrame
            subquery.

        Returns
        -------
        list[float]
            vector description of the query.

        """
        # get the string query
        string_query = self._get_semantic(row_df_query)
        # compute the string embeddings
        embedded_query = self._embed_query(string_query)

        return embedded_query

    # =============================================================================
    # internal functions
    # =============================================================================
    def _get_semantic(self, row_df_query: pd.DataFrame) -> str:
        """Select fields which will be used as k

        Parameters
        ----------
        row_df_query : pd.DataFrame
            DESCRIPTION.

        Returns
        -------
        None.

        """
        # add some logic here.. for now we just take the inputs
        try:  # try to get GuessIntension simplified query
            query_string = "Profil recherché:\n"
            query_string += row_df_query[QueryStruct.simplified_query].values[0]
        except Exception:  # else we take the user query
            query_string = row_df_query[QueryStruct.user_query].values[0]

        return query_string

    def _embed_query(self, query: str) -> list[float]:
        """Generate embeddings from a string using the llmbackend module

        Parameters
        ----------
        query : str

        Returns
        -------
        list[float]
            vector representation of the string query

        """
        embedded_query = self.embedder.embed_string(query)
        return embedded_query
