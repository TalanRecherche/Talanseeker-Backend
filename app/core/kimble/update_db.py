import logging

import pandas as pd

from app.core.azure_modules.azure_pg_manager import AzurePGManager
from app.core.azure_modules.models import UpsertPolicies
from app.core.models.pg_pandasmodels import CollabPg
from app.core.shared_modules.stringhandler import StringHandler
from app.models.chunks import PgChunks
from app.models.cvs import PgCvs
from app.models.profiles import PG_Profiles


class KimbleUpdater:
    @staticmethod
    def process_data(data: pd.DataFrame) -> pd.DataFrame:
        """Process kimble folder
        split name column
        rename column
        """
        logging.info("Start processing Kimble file")
        # split full name into name and surname
        data[CollabPg.name] = ""
        data[CollabPg.surname] = ""
        data = data.apply(KimbleUpdater.process_name, axis=1)

        # remove [EXT] alea
        data = data.apply(KimbleUpdater.remove_unnecessary_txt, axis=1)

        # generate collab_id
        data[CollabPg.collab_id] = data.apply(KimbleUpdater.generate_collab_id, axis=1)
        # drop collab_id duplicates
        data.drop_duplicates(subset=CollabPg.collab_id, inplace=True)

        # rename columns
        renaming_dict = {
            CollabPg.collab_id: CollabPg.collab_id,
            CollabPg.name: CollabPg.name,
            CollabPg.surname: CollabPg.surname,
            CollabPg.username_: CollabPg.email,
            CollabPg.bu_internal_: CollabPg.bu_internal,
            CollabPg.bu_: CollabPg.bu,
            CollabPg.bu_secondary_: CollabPg.bu_secondary,
            CollabPg.domain_: CollabPg.domain,
            CollabPg.community_: CollabPg.community,
            CollabPg.manager_: CollabPg.manager,
            CollabPg.start_date_: CollabPg.start_date,
            CollabPg.end_date_: CollabPg.end_date,
            CollabPg.revenue_: CollabPg.revenue,
            CollabPg.cost_: CollabPg.cost,
            CollabPg.cost_unit_: CollabPg.cost_unit,
            CollabPg.resource_type_: CollabPg.resource_type,
            CollabPg.grade_: CollabPg.grade,
            CollabPg.role_: CollabPg.role,
            CollabPg.sub_role_: CollabPg.sub_role,
            CollabPg.region_: CollabPg.region,
            CollabPg.city_: CollabPg.city,
            CollabPg.assigned_until_: CollabPg.assigned_until,
            CollabPg.availability_score_: CollabPg.availability_score,
        }
        data.rename(columns=renaming_dict, inplace=True)
        data = data[renaming_dict.values()]

        # format date
        data = data.apply(KimbleUpdater.format_date, axis=1)

        logging.info("Processing Kimble file finished")
        return data

    @staticmethod
    def generate_collab_id(row: pd.Series) -> str:
        full_name = StringHandler.normalize_string(
            row[CollabPg.resource_],
            remove_special_chars=True,
        )
        return StringHandler.generate_unique_id(full_name)

    @staticmethod
    def process_name(row: pd.Series) -> pd.Series:
        fullname = row[CollabPg.resource_]
        row[CollabPg.name] = " ".join(
            [elem for elem in fullname.split(" ") if not elem.isupper()],
        )
        row[CollabPg.surname] = " ".join(
            [elem for elem in fullname.split(" ") if elem.isupper()],
        )
        return row

    @staticmethod
    def remove_unnecessary_txt(row: pd.Series) -> pd.Series:
        row[CollabPg.resource_] = row[CollabPg.resource_].replace(
            CollabPg.ext_txt_,
            "",
        )
        return row

    @staticmethod
    def format_date(row: pd.Series) -> pd.Series:
        """Change cells date format"""
        for date_col in CollabPg.date_cols:
            row[date_col] = KimbleUpdater.format_date_helper(row[date_col])
        return row

    @staticmethod
    def format_date_helper(date_: str) -> str:
        """Convert date from dd/mm/yyyy to yyyy-mm-dd"""
        if str(date_) == "nan":
            return date_
        return "-".join(reversed(date_.split("/")))

    @staticmethod
    def update_db(file: bytes) -> None:
        """Erase the old data and insert new ones"""
        try:
            logging.warning("Start updating Kimble")
            data = pd.read_excel(file)
            data = KimbleUpdater.process_data(data)
            AzurePGManager.save_to_db("collabs", data, UpsertPolicies.ERASE)
            KimbleUpdater.clean_db()
            logging.warning("Update Kimble finished")
        except Exception as e:
            log_string = f"Failed to update Kimble {e}"
            logging.warning(log_string)

    @staticmethod
    def clean_db() -> None:
        """Define list of request to delete collabs that don't exist in kimble"""
        req = "DELETE FROM {} WHERE collab_id NOT IN (SELECT collab_id FROM collabs);"
        for table_name in [
            PgChunks.__tablename__,
            PgCvs.__tablename__,
            PG_Profiles.__tablename__,
        ]:
            AzurePGManager.execute_raw_req(req.format(table_name))
