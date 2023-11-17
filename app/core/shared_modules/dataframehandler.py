"""
Created by agarc at 01/10/2023
Features:
"""
import copy
import logging
import os

import pandas as pd


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
        Args:
            load_file_path (str): The path to the input pickle file.

        Returns:
            pd.DataFrame: A DataFrame containing the original data
        """
        # Loading
        try:
            # Read pickle file (utf8 and cell.dtype are preserved by default)
            df_loaded = pd.read_pickle(load_file_path)
            return df_loaded
        except FileNotFoundError:
            logging.exception(f"File not found: {load_file_path}")
            raise FileNotFoundError(f"File not found: {load_file_path}")
        except (OSError, PermissionError):
            logging.exception(f"Error reading file: {load_file_path}")
            raise OSError(f"Error reading file: {load_file_path}")
        except Exception as e:
            logging.exception(f"An unexpected error occurred: {str(e)}")
            raise e


    @staticmethod
    def protect(dataframe: pd.DataFrame) -> pd.DataFrame:
        dataframe = pd.DataFrame(columns=dataframe.columns, data=copy.deepcopy(dataframe.values))
        return dataframe
