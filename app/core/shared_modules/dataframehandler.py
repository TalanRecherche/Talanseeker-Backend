"""
Created by agarc at 01/10/2023
app.core:
"""
import copy
import inspect
import logging
import os
import pandas as pd

from app.core.models import pandascols
from app.core.models import scoredprofilescols
from app.core.models import PGcols
from app.core.models import querykeywordscols


class DataFrameHandler:

    @staticmethod
    def save_df(df: pd.DataFrame, save_to_file_path: str):
        """
        Saves the embeddings or the chunks to a pickle file.

        Args:
            df (pd.DataFrame): A DataFrame containing the data, the new embeddings.
            save_to_file_path (str): The path to the output pickle file.
        """

        # Check if the folder exists, and create it if it doesn't
        output_folder = os.path.dirname(save_to_file_path)
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        # Save the DataFrame to a pickle file
        df.to_pickle(save_to_file_path)

    @staticmethod
    def load_df(load_file_path: str) -> pd.DataFrame | None:
        """
        Loads pd.DataFrame from a pickle file

        Also checks if the loaded file correspond to any known format in DataframesCols
        using assert_df()

        Args:
            load_file_path (str): The path to the input pickle file.

        Returns:
            pd.DataFrame: A DataFrame containing the original data and the embeddings column.
        """
        # Loading
        try:
            # Read pickle file (utf8 and cell.dtype are preserved by default)
            df_loaded = pd.read_pickle(load_file_path)
        except Exception:
            logging.exception(f"failed to read {load_file_path}")
            return None

        # Check columns is compliant with any DataframesCols
        # Get all classes in the DataframesCols module
        classes = [obj for name, obj in inspect.getmembers(pandascols) if
                   inspect.isclass(obj) and obj.__module__ == pandascols.__name__]

        classes += [obj for name, obj in inspect.getmembers(PGcols) if
                    inspect.isclass(obj) and obj.__module__ == PGcols.__name__]

        classes += [obj for name, obj in inspect.getmembers(querykeywordscols) if
                    inspect.isclass(obj) and obj.__module__ == querykeywordscols.__name__]

        classes += [obj for name, obj in inspect.getmembers(scoredprofilescols) if
                    inspect.isclass(obj) and obj.__module__ == scoredprofilescols.__name__]

        # Iteratively check if loaded df has columns corresponding to any allowed format (in DataframesCols)
        for tested_class in classes:
            # assert without logging
            logging.getLogger().disabled = True
            bool_assert = DataFrameHandler.assert_df(df_loaded, tested_class)
            logging.getLogger().disabled = False
            # return df if the format is recognized
            if bool_assert:
                logging.debug(f"Loaded {load_file_path}")
                return df_loaded

        logging.warning("DataFrame format is not allowed")
        return None

    @staticmethod
    def assert_df(df: pd.DataFrame, expected_type) -> bool:
        """
        Check if the passed object is a dataframe of the correct expected_type.
        expected_type are classes in DataframesCols

        Parameters
        ----------
        df : pd.DataFrame
            dataframe to be passed as argument in other functions.
        expected_type : DataframesCols class
            pass something like EMBEDDING_DF, CV_PG ... see pandascols.py file.

        Returns
        -------
        df : pd.DataFrame or None
        """
        # assert cases when passing a dataframe as argument
        # check if input is a dataframe
        if type(df) != pd.DataFrame:
            logging.error("Input must be a pd.DataFrames.")
            return False
        # check if dataframe is empty
        if df.empty:
            logging.error("Empty df!.")
            return False
        # check columns
        if set(df.columns) != set(expected_type.get_attributes_()):
            logging.error(
                "Wrong df: Input must be dataframe of type: {t}".format(t=expected_type.__name__)
            )
            return False

        return True

    @staticmethod
    def protect(dataframe: pd.DataFrame) -> pd.DataFrame:
        dataframe = pd.DataFrame(columns=dataframe.columns, data=copy.deepcopy(dataframe.values))
        return dataframe
