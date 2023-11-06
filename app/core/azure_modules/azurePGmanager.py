import pandas as pd
import logging

from sqlalchemy.orm import Session
from sqlalchemy import text

from app.models.cvs import PG_CVs
from app.models.profiles import PG_Profiles
from app.models.pg_chunks import PG_Chunks
from app.models import con_string, engine
from app.core.models.ETL_pandasmodels import STRUCTCV_DF
from app.core.models.PG_pandasmodels import PROFILE_PG, CHUNK_PG
from app.core.azure_modules.models import UpsertPolicies


class AzurePGManager:
    """
    Save dataframes to Postgres
    """

    @staticmethod
    def save_to_db(table_name: str, data: pd.DataFrame, policy: str) -> None:
        """
        save dataframe to PG

        input:
        table_name
        data : dataframe to save
        """
        if policy == UpsertPolicies.ERASE:
            data.to_sql(table_name, con_string, if_exists="replace", index=False)
        elif policy == UpsertPolicies.PROFILE_UPDATE or policy == UpsertPolicies.CHUNK_UPDATE:
            data.apply(AzurePGManager.upsert, axis=1, table_name=table_name, policy=policy)
        elif policy == UpsertPolicies.APPEND:
            try:
                data.to_sql(table_name, con_string, if_exists="append", index=False)
                logging.info("Insert in cv table done")
            except Exception:
                logging.exception("failed to save to DB")

    @staticmethod
    def get_collab_cvs(collab_id:str)->list:
        req = f"select c.file_full_name from cvs c where c.collab_id  = '{collab_id}';"
        return pd.read_sql(req, con_string)[str(STRUCTCV_DF.file_full_name)].to_list()

    @staticmethod
    def execute_raw_req(req: str):
        req = text(req)
        with Session(engine) as session:
            session.execute(req)
            session.commit()

    @staticmethod
    def upsert(row: pd.Series, table_name: str, policy: str) -> None:
        """
        Insert data if it doesn't exist
        Update data if it exists
        Data is updated by merging data of each column and removing duplicates

        # Input
        policy : either replace or insert
        """
        new_data = None
        if policy == UpsertPolicies.PROFILE_UPDATE:
            logging.info("Profiles Table")
            req = text("SELECT * FROM {} WHERE collab_id = '{}'".format(table_name, row[PROFILE_PG.collab_id]))
            data = pd.read_sql(req, con_string)
            if len(data) == 0:
                logging.info(f"Adding new profile of {row[PROFILE_PG.collab_id]} ")
                new_data = pd.DataFrame(row, row.index).T

            else:
                logging.info(f"Delete old profile of {row[PROFILE_PG.collab_id]}")
                req = text(f"delete from profiles where collab_id = '{row[PROFILE_PG.collab_id]}'")
                with Session(engine) as session:
                    session.execute(req)
                    session.commit()

                logging.info(f"Consolidating a profile of {row[PROFILE_PG.collab_id]} ")
                data.loc[len(data)] = row

                # todo: change this behavior
                # userless cols
                useless_cols = [STRUCTCV_DF.cv_id, STRUCTCV_DF.file_path, STRUCTCV_DF.file_name,
                                STRUCTCV_DF.file_extension, STRUCTCV_DF.file_full_name]
                data[useless_cols] = None

                from app.core.cv_information_retrieval.profilestructurator import ProfileStructurator
                stucture = ProfileStructurator()
                new_data = stucture.consolidate_profiles(data)
                new_data.drop(useless_cols, axis=1, inplace=True)

        elif policy == UpsertPolicies.CHUNK_UPDATE:
            logging.info("Chunks Table")
            req = text(
                "select * from {} where (chunk_id, collab_id) = ('{}','{}');".format(table_name, row[CHUNK_PG.chunk_id],
                                                                                     row[CHUNK_PG.collab_id]))
            data = pd.read_sql(req, con_string)
            if len(data) == 0:
                logging.info("Adding new chunks")
                logging.info(f"Adding new profile of {row[PROFILE_PG.collab_id]} ")
                new_data = pd.DataFrame(row, row.index).T
            else:
                logging.info('Chunk already exists!')

        if new_data is not None:
            try:
                new_data.to_sql(table_name, con_string, if_exists="append", index=False)
            except Exception as e:
                logging.exception(f"Error updating chunks table {e}")

    @staticmethod
    def check_existance(table_name: str, id_tag: str, id_value: str) -> bool:
        req = text(f"SELECT * FROM {table_name} WHERE {id_tag} = '{id_value}'")
        return len(pd.read_sql(req, con_string)) != 0

    @staticmethod
    def save(
            pg_profiles: pd.DataFrame,
            pg_chunks: pd.DataFrame,
            pg_cvs: pd.DataFrame,
    ):
        AzurePGManager.save_to_db(PG_Profiles.__tablename__, pg_profiles, UpsertPolicies.PROFILE_UPDATE)
        AzurePGManager.save_to_db(PG_CVs.__tablename__, pg_cvs, UpsertPolicies.APPEND)
        AzurePGManager.save_to_db(PG_Chunks.__tablename__, pg_chunks, UpsertPolicies.CHUNK_UPDATE)

