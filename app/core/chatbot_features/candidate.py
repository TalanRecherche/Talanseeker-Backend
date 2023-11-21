"""Created on 14.09.2023.

@author: damienj
"""

import pandas as pd

from app.core.models.pg_pandasmodels import ChunkPg, CollabPg, CvPg, ProfilePg
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
            current_collab_id = row[CollabPg.collab_id]
            rows_pg_chunks = pg_chunks[
                pg_chunks[ChunkPg.collab_id] == current_collab_id
            ]
            rows_pg_collabs = pg_collabs[
                pg_collabs[CollabPg.collab_id] == current_collab_id
            ]
            rows_pg_cvs = pg_cvs[pg_cvs[CvPg.collab_id] == current_collab_id]
            rows_pg_profiles = pg_profiles[
                pg_profiles[ProfilePg.collab_id] == current_collab_id
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
        self.name = self.get_value_or_default(row_pg_collabs, CollabPg.name).title()
        self.surname = self.get_value_or_default(
            row_pg_collabs,
            CollabPg.surname,
        ).upper()
        self.email = self.get_value_or_default(row_pg_collabs, CollabPg.email).lower()
        self.role = self.get_value_or_default(row_pg_collabs, CollabPg.role).title()
        self.sub_role = self.get_value_or_default(
            row_pg_collabs,
            CollabPg.sub_role,
        ).title()
        self.grade = self.get_value_or_default(row_pg_collabs, CollabPg.grade).title()
        self.region = self.get_value_or_default(
            row_pg_collabs,
            CollabPg.region,
        ).title()
        self.city = self.get_value_or_default(row_pg_collabs, CollabPg.city).title()
        self.manager = self.get_value_or_default(
            row_pg_collabs,
            CollabPg.manager,
        ).title()

        # from PROFILE table
        self.years_of_exp = self.get_value_or_default(row_pg_profiles, ProfilePg.years)
        self.roles_profile = ListHandler.capitalize_list(
            self.get_value_or_default(
                row_pg_profiles,
                ProfilePg.roles,
                value_is_list=True,
            ),
        )
        self.soft_skills = ListHandler.capitalize_list(
            self.get_value_or_default(
                row_pg_profiles,
                ProfilePg.soft_skills,
                value_is_list=True,
            ),
        )
        self.technical_skills = ListHandler.capitalize_list(
            self.get_value_or_default(
                row_pg_profiles,
                ProfilePg.technical_skills,
                value_is_list=True,
            ),
        )
        self.skills = self.technical_skills + self.soft_skills
        self.diplomas_certifications = ListHandler.capitalize_list(
            self.get_value_or_default(
                row_pg_profiles,
                ProfilePg.diplomas_certifications,
                value_is_list=True,
            ),
        )

        self.pg_chunks = row_pg_chunks
        self.pg_collabs = row_pg_collabs
        self.pg_cvs = row_pg_cvs
        self.pg_profiles = row_pg_profiles

        self.cv_path = self.pg_cvs[CvPg.file_full_name].tolist()
        self.cv_extension = ["." + filename.split(".")[-1] for filename in self.cv_path]

    def get_value_or_default(
        self,
        row: pd.DataFrame,
        column: pd.DataFrame,
        default_value: str = "",
        value_is_list: bool = False,
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

        return [] if len(value) == 0 else value
