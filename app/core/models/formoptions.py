import pandas as pd

from app.core.models.pg_pandasmodels import CollabPg
from app.models import con_string


class FormOptions:
    def __init__(self) -> None:
        self.get_form_options()
        self.region = ""
        self.city = ""
        self.grade = ""

    def get_form_options(self) -> None:
        self.region = self._get_options(CollabPg.region)
        self.city = [elem.capitalize() for elem in self._get_options(CollabPg.city)]
        self.grade = self._get_options(CollabPg.grade)

    def _get_options(self, col_name: str) -> list:
        req = "select distinct {} from collabs c where {} is not null;"
        return sorted(
            pd.read_sql(req.format(col_name, col_name), con_string)[col_name].to_list(),
        )
