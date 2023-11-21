"""Created on Tue Aug  8 16:02:11 2023

@author: agarc

"""
import logging

import pandas as pd
from tqdm import tqdm

from app.core.cv_information_retrieval.filereader import FileReader
from app.core.models.etl_pandasmodels import TextDF
from app.core.shared_modules.pathexplorer import PathExplorer


class FileMassExtractor:
    """Read entire directories.

    read_all_documents(self, directory: str) -> list[dict]: To read documents without
    saving read_dump_and_copy_all_files(self, directory: str): To read documents
    and save .Txt

    Uses an instance of FileReader to read single documents
    """

    def __init__(self) -> None:
        # This instance handles the text and metadata extraction
        self.file_reader = FileReader()

    # =============================================================================
    # user functions
    # =============================================================================
    def read_all_documents(
        self,
        path: str,
        collab_ids: dict,
        read_only_extensions: list[str] = None,
        ignore_extensions: list[str] = None,
    ) -> pd.DataFrame | None:
        """Find files in path or directory
        Filter (un)wanted extensions
        Sequentially loads every document using FileReader.
        Push to text_df
        Each row in text_df is assigned to a collab_id (in argument)

        Parameters
        ----------
        path : str
            This can either be a directory OR a file path

        collab_ids:
            hashmap = {file_full_name : collab_id}
            Enables tracking the name of the user (collab_id) which is assigned to each
            file

        read_only_extensions :
            list, optional (type: '.txt', '.docx' etc.)
            A list of file extensions to include in the filtered list. If provided,
            only files with these extensions will be included.

        ignore_extensions :
            list, optional (type: '.txt', '.docx' etc.)
            A list of file extensions to exclude from the filtered list. If
            provided, files with these extensions will be excluded.

        Returns
        -------
        text_df
        """
        # check if the path is a directory, a file or if it doesn't exists
        if ignore_extensions is None:
            ignore_extensions = []
        if read_only_extensions is None:
            read_only_extensions = []
        path_type = PathExplorer.check_path_type(path)
        if path_type == "File":
            file_paths = [path]
        elif path_type == "Directory":
            # get all path from all files
            file_paths = PathExplorer.get_all_files_paths(path)
        else:
            logging.warning("dir or path empty")
            return None

        # prepare output df
        df_text = TextDF.generate_dataframe()
        # filter only files with extension provided:
        file_paths = self._filter_extensions(
            file_paths,
            read_only_extensions,
            ignore_extensions,
        )

        # loop read every found files and outputs a list of dictionary
        for file_path in tqdm(file_paths, desc="Reading Files:"):
            try:
                text_hashmap = self.file_reader.read_single_document(file_path)
                if text_hashmap:
                    # if not None : push to dataframe
                    temp_df = pd.DataFrame([text_hashmap])
                    df_text = pd.concat([df_text, temp_df])
            except Exception:
                log_string = f"Error at {file_path}"
                logging.exception(log_string)

        if df_text.empty:
            logging.warning("no text")
            return None

        # assign collab_id to each document
        df_text[TextDF.collab_id] = df_text[TextDF.file_full_name].map(collab_ids)

        logging.info("done")
        return df_text

    # =============================================================================
    # internal functions
    # =============================================================================
    def _filter_extensions(
        self,
        file_paths: list[str],
        read_only_extensions: list[str] = None,
        ignore_extensions: list[str] = None,
    ) -> list[str]:
        """Filter file paths based on their extensions.

        Parameters
        ----------
        file_paths : list
            A list of file paths to be filtered.
        read_only_extensions : list, optional
            A list of file extensions to include in the filtered list. If provided,
                only files with these extensions will be included.
        ignore_extensions : list, optional
            A list of file extensions to exclude from the filtered list. If
                provided, files with these extensions will be excluded.

        Returns
        -------
        list
            A list of filtered file paths based on the provided exclusion/inclusion
            criteria.
        """
        # If read_only_extensions is provided, filter file_paths to include only
        if ignore_extensions is None:
            ignore_extensions = []
        if read_only_extensions is None:
            read_only_extensions = []
        if read_only_extensions:
            filtered_file_paths = [
                file_path
                for file_path in file_paths
                if PathExplorer.get_single_file_extension(file_path)
                in read_only_extensions
            ]
            return filtered_file_paths

        # If ignore_extensions is provided, filter file_paths to exclude files with
        if ignore_extensions:
            filtered_file_paths = [
                file_path
                for file_path in file_paths
                if PathExplorer.get_single_file_extension(file_path)
                not in ignore_extensions
            ]
            return filtered_file_paths

        # If no exclusion criteria are provided, return the original file_paths list
        return file_paths


# =============================================================================
#     # extract text
# =============================================================================

if __name__ == "__main__":
    directory = r"data_dev/data_1"

    files = PathExplorer.get_all_paths_with_extension_name(directory)
    collab_ids = {
        files[ii]["file_full_name"]: str(ii * 1231) for ii in range(len(files))
    }

    extractor = FileMassExtractor()
    text_df = extractor.read_all_documents(directory, collab_ids)
    print(text_df)  # noqa: T201
