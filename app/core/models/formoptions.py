import pandas as pd

from app.core.models.PG_pandasmodels import COLLAB_PG
from app.models import con_string


class FormOptions:
    def __init__(self):
        self.get_form_options()
    def get_form_options(self):
        self.region = self._get_options(COLLAB_PG.region)
        self.city = [elem.capitalize() for elem in self._get_options(COLLAB_PG.city)]
        self.grade = self._get_options(COLLAB_PG.grade)


    def _get_options(self, col_name:str)->list:
        req = "select distinct {} from collabs c where {} is not null;"
        return sorted(pd.read_sql(req.format(col_name, col_name), con_string)[col_name].to_list())