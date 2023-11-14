import logging

import pandas as pd

from app.models.chunks import PG_Chunks
from app.models.cvs import PG_CVs
from app.models.profiles import PG_Profiles
from app.core.azure_modules.azurePGmanager import AzurePGManager
from app.core.shared_modules.stringhandler import StringHandler
from app.core.azure_modules.models import UpsertPolicies
from app.core.models.PG_pandasmodels import COLLAB_PG


class KimbleUpdater:
    @staticmethod
    def process_data(data: pd.DataFrame) -> pd.DataFrame:
        """
        process kimble folder
        split name column
        rename column
        """
        logging.info("Start processing Kimble file")
        # split full name into name and surname
        data[COLLAB_PG.name] = ""
        data[COLLAB_PG.surname] = ""
        data = data.apply(KimbleUpdater.process_name, axis=1)

        # remove [EXT] alea
        data = data.apply(KimbleUpdater.remove_unnecessary_txt, axis=1)

        #generate collab_id
        data[COLLAB_PG.collab_id] = data.apply(KimbleUpdater.generate_collab_id, axis=1)
        # drop collab_id duplicates
        data.drop_duplicates(subset=COLLAB_PG.collab_id, inplace=True)

        # rename columns
        renaming_dict = {COLLAB_PG.collab_id: COLLAB_PG.collab_id,
                         COLLAB_PG.name: COLLAB_PG.name,
                         COLLAB_PG.surname: COLLAB_PG.surname,
                         COLLAB_PG.username_: COLLAB_PG.email,
                         COLLAB_PG.bu_internal_: COLLAB_PG.bu_internal,
                         COLLAB_PG.bu_: COLLAB_PG.bu,
                         COLLAB_PG.bu_secondary_: COLLAB_PG.bu_secondary,
                         COLLAB_PG.domain_: COLLAB_PG.domain,
                         COLLAB_PG.community_: COLLAB_PG.community,
                         COLLAB_PG.manager_: COLLAB_PG.manager,
                         COLLAB_PG.start_date_: COLLAB_PG.start_date,
                         COLLAB_PG.end_date_: COLLAB_PG.end_date,
                         COLLAB_PG.revenue_: COLLAB_PG.revenue,
                         COLLAB_PG.cost_: COLLAB_PG.cost,
                         COLLAB_PG.cost_unit_: COLLAB_PG.cost_unit,
                         COLLAB_PG.resource_type_: COLLAB_PG.resource_type,
                         COLLAB_PG.grade_: COLLAB_PG.grade,
                         COLLAB_PG.role_: COLLAB_PG.role,
                         COLLAB_PG.sub_role_: COLLAB_PG.sub_role,
                         COLLAB_PG.region_: COLLAB_PG.region,
                         COLLAB_PG.city_: COLLAB_PG.city,
                         COLLAB_PG.assigned_until_: COLLAB_PG.assigned_until,
                         COLLAB_PG.availability_score_: COLLAB_PG.availability_score,
                         }
        data.rename(columns=renaming_dict, inplace=True)
        data = data[renaming_dict.values()]

        #format date
        data = data.apply(KimbleUpdater.format_date, axis=1)

        logging.info("Processing Kimble file finished")
        return data

    @staticmethod
    def generate_collab_id(row:pd.Series):
        full_name = StringHandler.normalize_string(row[COLLAB_PG.resource_], remove_special_chars=True)
        return StringHandler.generate_unique_id(full_name)
    @staticmethod
    def process_name(row: pd.Series):
        fullname = row[COLLAB_PG.resource_]
        row[COLLAB_PG.name] = " ".join([elem for elem in fullname.split(" ") if not elem.isupper()])
        row[COLLAB_PG.surname] = " ".join([elem for elem in fullname.split(" ") if elem.isupper()])
        return row

    @staticmethod
    def remove_unnecessary_txt(row:pd.Series)->pd.Series:
        row[COLLAB_PG.resource_] = row[COLLAB_PG.resource_].replace(COLLAB_PG.ext_txt_,"")
        return row


    @staticmethod
    def format_date(row:pd.Series)->pd.Series:
        """
        change cells date format
        """
        for date_col in COLLAB_PG.date_cols:
            row[date_col] = KimbleUpdater.format_date_helper(row[date_col])
        return row

    @staticmethod
    def format_date_helper(date_:str)->str:
        """
        convert date from dd/mm/yyyy to yyyy-mm-dd
        """
        if str(date_) == "nan":
            return date_
        return '-'.join(reversed(date_.split('/')))

    @staticmethod
    def update_db(file:bytes):
        """
        erase the old data and insert new ones
        """
        try:
            logging.warning("Start updating Kimble")
            data = pd.read_excel(file)
            data = KimbleUpdater.process_data(data)
            AzurePGManager.save_to_db("collabs", data, UpsertPolicies.ERASE)
            KimbleUpdater.clean_db()
            logging.warning("Update Kimble finished")
        except Exception as e:
            logging.warning(f"Failed to update Kimble {e}")

    @staticmethod
    def clean_db():
        """
        define list of request to delete collabs that don't exist in kimble
        """
        req = "DELETE FROM {} WHERE collab_id NOT IN (SELECT collab_id FROM collabs);"
        for table_name in [PG_Chunks.__tablename__, PG_CVs.__tablename__, PG_Profiles.__tablename__]:
            AzurePGManager.execute_raw_req(req.format(table_name))

