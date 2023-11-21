"""Created on 14.09.2023.

@author: damienj
"""

import pandas as pd

from app.core.models.PG_pandasmodels import CHUNK_PG, COLLAB_PG, CV_PG, PROFILE_PG
from app.core.shared_modules.listhandler import ListHandler


class Candidates:
    """List of candidates."""

    def __init__(
        self,
        pg_chunks: pd.DataFrame,
        pg_collabs: pd.DataFrame,
        pg_cvs: pd.DataFrame,
        pg_profiles: pd.DataFrame,
    ) -> None:
        self.list_candidates = []
        for _, row in pg_collabs.iterrows():
            # filter out rows of the current candidate
            current_collab_id = row[COLLAB_PG.collab_id]
            rows_pg_chunks = pg_chunks[
                pg_chunks[CHUNK_PG.collab_id] == current_collab_id
            ]
            rows_pg_collabs = pg_collabs[
                pg_collabs[COLLAB_PG.collab_id] == current_collab_id
            ]
            rows_pg_cvs = pg_cvs[pg_cvs[CV_PG.collab_id] == current_collab_id]
            rows_pg_profiles = pg_profiles[
                pg_profiles[PROFILE_PG.collab_id] == current_collab_id
            ]
            # instantiate a candidate
            candidate = Candidate(
                rows_pg_chunks,
                rows_pg_collabs,
                rows_pg_cvs,
                rows_pg_profiles,
            )
            # append to list of candidates
            self.list_candidates.append(candidate)


class Candidate:
    """Candidate object."""

    def __init__(
        self,
        row_pg_chunks: pd.DataFrame,
        row_pg_collabs: pd.DataFrame,
        row_pg_cvs: pd.DataFrame,
        row_pg_profiles: pd.DataFrame,
    ) -> None:
        # from COLLAB table
        self.name = self.get_value_or_default(row_pg_collabs, COLLAB_PG.name).title()
        self.surname = self.get_value_or_default(
            row_pg_collabs,
            COLLAB_PG.surname,
        ).upper()
        self.email = self.get_value_or_default(row_pg_collabs, COLLAB_PG.email).lower()
        self.role = self.get_value_or_default(row_pg_collabs, COLLAB_PG.role).title()
        self.sub_role = self.get_value_or_default(
            row_pg_collabs,
            COLLAB_PG.sub_role,
        ).title()
        self.grade = self.get_value_or_default(row_pg_collabs, COLLAB_PG.grade).title()
        self.region = self.get_value_or_default(
            row_pg_collabs,
            COLLAB_PG.region,
        ).title()
        self.city = self.get_value_or_default(row_pg_collabs, COLLAB_PG.city).title()
        self.manager = self.get_value_or_default(
            row_pg_collabs,
            COLLAB_PG.manager,
        ).title()

        # from PROFILE table
        self.years_of_exp = self.get_value_or_default(row_pg_profiles, PROFILE_PG.years)
        self.roles_profile = ListHandler.capitalize_list(
            self.get_value_or_default(
                row_pg_profiles,
                PROFILE_PG.roles,
                value_is_list=True,
            ),
        )
        self.soft_skills = ListHandler.capitalize_list(
            self.get_value_or_default(
                row_pg_profiles,
                PROFILE_PG.soft_skills,
                value_is_list=True,
            ),
        )
        self.technical_skills = ListHandler.capitalize_list(
            self.get_value_or_default(
                row_pg_profiles,
                PROFILE_PG.technical_skills,
                value_is_list=True,
            ),
        )
        self.skills = self.technical_skills + self.soft_skills
        self.diplomas_certifications = ListHandler.capitalize_list(
            self.get_value_or_default(
                row_pg_profiles,
                PROFILE_PG.diplomas_certifications,
                value_is_list=True,
            ),
        )

        self.pg_chunks = row_pg_chunks
        self.pg_collabs = row_pg_collabs
        self.pg_cvs = row_pg_cvs
        self.pg_profiles = row_pg_profiles

        self.cv_path = self.pg_cvs[CV_PG.file_full_name].tolist()
        self.cv_extension = ["." + filename.split(".")[-1] for filename in self.cv_path]

    def get_value_or_default(
        self, row, column, default_value="", value_is_list=False
    ) -> str:
        """Get the value from the row for the given column,
        return the default value if it's null.

        :param row: The row from the DataFrame.
        :param column: The column name to get the value from.
        :param default_value: The default value to return if the value is null.
        :param value_is_list: Boolean to indicate if the value is a list.
        :return: The value from the row for the given column, or the default value
        if it's null.
        """
        value = row[column].values[0]
        if not value_is_list:
            return default_value if pd.isnull(value) else value
        else:
            return [] if len(value) == 0 else value
