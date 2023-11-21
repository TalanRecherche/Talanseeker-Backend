"""Created on Wed Aug 23 10:00:25 2023

@author: agarc

"""
import logging

import pandas as pd

from app.core.models.ETL_pandasmodels import PARSED_DF, STRUCTCV_DF
from app.core.shared_modules.listhandler import ListHandler
from app.core.shared_modules.stringhandler import StringHandler


class CvStructurator:
    """Load parsed chunks from LLMParser.
    Consolidate each chunks of a single profile into one row (using list[str])
    """

    def __init__(self):
        """Getting rid of strings that are too long (roles_profile and skills should
        be short!)
        """
        self.max_string_len = 40
        """similarity threshold to get rid of a string (e.g. data science vs data
         scientist)"""
        self.similarity_threshold = 0.8

        # strings to get rid of during processing
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
            '"': "",
            ";": ",",
            "_": "",
            "-": " ",
        }

    # =============================================================================
    # User functions
    # =============================================================================
    def consolidate_cvs(self, df_profile_chunks: pd.DataFrame) -> pd.DataFrame | None:
        """Parameters
        ----------
        df_profile_chunks : pandas dataframe
            One row per chunks.

        Returns
        -------
        consolidated_cvs_df : pandas dataframe
            One row per cv. All chunks information have been merged
        """
        # assert if input dataframe is of correct format (columns)
        # if not PARSED_DF.validate_dataframe(df_profile_chunks): return None

        # prepare output dataframe
        df_consolidated_cvs = STRUCTCV_DF.generate_dataframe()
        # create a hashmap of unique profile using similarity on profile_id
        hashmap_profile_filename = self._get_unique_cvs(df_profile_chunks)

        # loop through each profile and their chunks
        for cv_id, _ in hashmap_profile_filename.items():
            # filter chunks to current profile
            df_filtered_profile = df_profile_chunks[
                df_profile_chunks[STRUCTCV_DF.cv_id] == cv_id
            ]
            # consolidate all chunks into a single profile row
            df_single_profile = self._consolidate_single_cv(df_filtered_profile)
            # push to new pandas df
            if not df_single_profile.empty:
                df_consolidated_cvs = pd.concat(
                    [df_consolidated_cvs, df_single_profile],
                    axis=0,
                    ignore_index=True,
                )

        if df_consolidated_cvs.empty:
            logging.warning("dataframe is empty")
            return None

        logging.info("done")
        return df_consolidated_cvs

    # =============================================================================
    #     Internal functions.
    # =============================================================================
    def _consolidate_single_cv(self, df_chunks_profile: pd.DataFrame) -> pd.DataFrame:
        """Consolidate all chunks of a single cv into a single row

        Parameters
        ----------
        df_chunks_profile : pandas dataframe
            one rows per chunks. All belongs to the same profile.

        Returns
        -------
        pandas dataframe
            single-row dataframe. All chunks information have been merged.
        """
        # prepare the profile hashmap
        hashmap_single_cv = {}

        # looping through columns types
        for column in STRUCTCV_DF.static_columns_:
            hashmap_single_cv[column] = self._merge_static_columns(
                column,
                df_chunks_profile,
            )

        for column in STRUCTCV_DF.numerical_columns_:
            hashmap_single_cv[column] = self._merge_numerical_columns(
                column,
                df_chunks_profile,
            )

        for column in STRUCTCV_DF.string_columns_:
            hashmap_single_cv[column] = self._merge_string_columns(
                column,
                df_chunks_profile,
            )

        # create a dataframe from the hashmap
        df_single_cv = pd.DataFrame([hashmap_single_cv])
        return df_single_cv

    def _merge_static_columns(self, column, df_chunks_profile):
        """Static columns are not transformed: we take the first value"""
        return df_chunks_profile.iloc[0][column]

    def _merge_numerical_columns(self, column, df_chunks_profile) -> int:
        """For numeric columns we take the maximum values (years of experiences)"""
        try:
            numerical_extract = (
                df_chunks_profile[column].dropna().apply(self._extract_integer)
            )
            numerical_value = int(max(numerical_extract))
        except Exception as e:
            numerical_value = 0
            logging.warning(
                f"CVStructurator : numerical columns structuration failed {e}",
            )
        return numerical_value

    def _extract_integer(self, cell) -> int | None:
        if isinstance(cell, str):
            num = ""
            for char in cell:
                if char.isdigit():
                    num += char
                else:
                    break
            return int(num) if num else None
        elif isinstance(cell, (int, float)):
            return int(cell)
        return None

    def _merge_string_columns(
        self,
        column: str,
        df_chunks_profile: pd.DataFrame,
    ) -> list[str]:
        """Merge logic for string columns
        Make a list with all strings, then clean/unique/fuzzy matching remove
        returns the list of string
        """
        try:
            # cast values of columns into a list
            values = df_chunks_profile[column].tolist()
            values = ListHandler.flatten_list(values)
            # get rid of useless strings
            values = [
                value for value in values if value not in self.string_replacements
            ]
            # remove trailing spaces and new lines
            values = [value.strip() for value in values]
            values = [value.strip("\n") for value in values]
            # clean strings
            values = [StringHandler.replace_in_string(value) for value in values]
            # normalize strings
            values = [StringHandler.normalize_string(value) for value in values]
            # unique strings
            values = list(set(values))
            # remove useless strings
            values = ListHandler.remove_strings_in_list(values)
            if column != STRUCTCV_DF.diplomas_certifications:
                # 4 remove strings that are too longs. we do not for diploma
                values = [
                    value for value in values if len(value) <= self.max_string_len
                ]
            # 5 fuzzy string matching to remove pseudo-duplicates (this is O(n2),
            # a C++ version exists see Cdiflib)
            values = StringHandler.remove_similar_strings(
                values,
                threshold=self.similarity_threshold,
            )
        except Exception as e:
            values = []
            logging.warning(
                f"CVStructurator : string columns structuration failed: {e}",
            )
        return values

    def _get_unique_cvs(self, df_profile_chunks: pd.DataFrame) -> dict:
        """Finds all unique chunks of a cv

        Parameters
        ----------
        df_profile_chunks : pandas dataframe
            all chunks from all cvs.

        Returns
        -------
        hashmap_profile_chunks : hashmap
            {profile_id : list[chunk_id]}.
        """
        unique_cvs = set(
            ListHandler.flatten_list(list(df_profile_chunks[PARSED_DF.cv_id])),
        )
        hashmap_cv_chunks = {}

        for cv in unique_cvs:
            filtered_df_profile_chunks = df_profile_chunks[
                df_profile_chunks[PARSED_DF.cv_id] == cv
            ]
            hashmap_cv_chunks[cv] = list(
                filtered_df_profile_chunks[PARSED_DF.chunk_id].values,
            )
        return hashmap_cv_chunks


# %%
if __name__ == "__main__":
    directory = r"tests/data_test/CV_pptx"
    # prepare {filenames : collab_id} map from the main
    from app.core.shared_modules.pathexplorer import PathExplorer

    files = PathExplorer.get_all_paths_with_extension_name(directory)
    collab_ids = {files[ii]["file_full_name"]: str(ii) for ii in range(len(files))}

    from app.core.cv_information_retrieval.filemassextractor import FileMassExtractor

    extractor = FileMassExtractor()
    text_df = extractor.read_all_documents(directory, collab_ids)

    from app.core.cv_information_retrieval.chunker import Chunker

    chunker = Chunker()
    df_chunks = chunker.chunk_documents(text_df)

    # parse the chunks
    from app.core.cv_information_retrieval.LLMparser import LLMParser
    from app.settings import Settings

    parser = LLMParser(Settings())
    parsed_chunks = parser.parse_all_chunks(df_chunks)

    # consolidate profile
    structure = CvStructurator()
    cvs_struct = structure.consolidate_cvs(parsed_chunks)
    print(cvs_struct)
