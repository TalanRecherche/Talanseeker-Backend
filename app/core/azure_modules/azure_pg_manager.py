import logging

import pandas as pd
from sqlalchemy import and_, delete, select, text
from sqlalchemy.orm import Session

from app.core.azure_modules.models import UpsertPolicies
from app.core.models.etl_pandasmodels import StructCvDF
from app.core.models.pg_pandasmodels import ChunkPg, ProfilePg
from app.models import Base, con_string, engine
from app.models.chunks import ChunkModel
from app.models.collabs import PgCollabs
from app.models.cvs import PgCvs
from app.models.profiles import PG_Profiles


class AzurePGManager:
    """Save dataframes to Postgres"""

    @staticmethod
    def save_to_db(table: Base, data: pd.DataFrame, policy: str) -> None:
        """Save dataframe to PG

        input:
        table_name
        data : dataframe to save
        """
        if policy == UpsertPolicies.ERASE:
            data.to_sql(table.__tablename__, con_string, if_exists="replace",
                        index=False)
        elif (
                policy == UpsertPolicies.PROFILE_UPDATE
                or policy == UpsertPolicies.CHUNK_UPDATE
        ):
            data.apply(
                AzurePGManager.upsert,
                axis=1,
                table=table,
                policy=policy,
            )
        elif policy == UpsertPolicies.APPEND:
            try:
                data.to_sql(table.__tablename__, con_string, if_exists="append", index=False)
                logging.info("Insert in cv table done")
            except Exception:
                logging.exception("failed to save to DB")

    @staticmethod
    def get_collab_cvs(collab_id: str) -> list:
        """req = f"select c.file_full_name from cvs c where c.collab_id  = '{collab_id}';"""
        req = AzurePGManager._sql_req_creator("collab_cvs",
                                              table = PgCvs,
                                              collab_id=collab_id)
        return pd.read_sql(req, con_string)[str(StructCvDF.file_full_name)].to_list()

    @staticmethod
    def execute_raw_req(req: str) -> None:
        req = text(req)
        with Session(engine) as session:
            session.execute(req)
            session.commit()

    @staticmethod
    def _sql_req_creator(req_target: str, **kwargs) -> str:
        """
        create sql requests
        azure_pg_manager.check_existence(
            PgCollabs.__tablename__,
            CollabPg.collab_id,
            collab_id,
        )

        text(f"SELECT * FROM {table_name} WHERE {id_tag} = '{id_value}'")

        """
        req = None
        if req_target == "collab_by_id":
            req = (select(kwargs["table"]).
                   where(PG_Profiles.collab_id == kwargs["collab_id"]))
        elif req_target == "delete_profile_by_id":
            req = (delete(kwargs["table"]).
                   where(PG_Profiles.collab_id == kwargs["collab_id"]))
        elif req_target == "collab_cvs":
            req = (select(kwargs["table"]).
                   where(PgCvs.collab_id == kwargs["collab_id"]))
        elif req_target == "cv_chunks":
            req = (select(kwargs["table"]).
                   where(and_(ChunkModel.collab_id == kwargs["collab_id"],
                              ChunkModel.chunk_id == kwargs["chunk_id"])))
        elif req_target == "check_existence":
            req = (select(kwargs["table"]).
                   where(PgCollabs.collab_id == kwargs["collab_id"]))

        return req

    @staticmethod
    def upsert(row: pd.Series, table: Base, policy: str) -> None:
        """Insert data if it doesn't exist
        Update data if it exists
        Data is updated by merging data of each column and removing duplicates

        # Input
        policy : either replace or insert
        """
        new_data = None
        if policy == UpsertPolicies.PROFILE_UPDATE:
            logging.info("Profiles Table")
            """
            req = text(
                "SELECT * FROM {} WHERE collab_id = '{}'".format(
                    table_name,
                    row[ProfilePg.collab_id],
                ),
            )
            """
            req = AzurePGManager._sql_req_creator("collab_by_id",
                                                  table=table,
                                                  collab_id=row[ProfilePg.collab_id])
            data = pd.read_sql(req, con_string)
            if len(data) == 0:
                log_string = f"Adding new profile of {row[ProfilePg.collab_id]} "
                logging.info(log_string)
                new_data = pd.DataFrame(row, row.index).T

            else:
                log_string = f"Delete old profile of {row[ProfilePg.collab_id]}"
                logging.info(log_string)
                """req = text(
                    f"delete from profiles where collab_id = "
                    f"'{row[ProfilePg.collab_id]}'",
                )
                """
                req = AzurePGManager._sql_req_creator("delete_profile_by_id",
                                                      table=table,
                                                      collab_id=row[
                                                          ProfilePg.collab_id])

                with Session(engine) as session:
                    session.execute(req)
                    session.commit()
                    session.flush()

                log_string = f"Consolidating a profile of {row[ProfilePg.collab_id]} "
                logging.info(log_string)
                data.loc[len(data)] = row

                # TODO@<Youness>: change this behavior
                # userless cols
                useless_cols = [
                    StructCvDF.cv_id,
                    StructCvDF.file_path,
                    StructCvDF.file_name,
                    StructCvDF.file_extension,
                    StructCvDF.file_full_name,
                ]
                data[useless_cols] = None

                from app.core.cv_information_retrieval.profilestructurator import (
                    ProfileStructurator,
                )

                stucture = ProfileStructurator()
                new_data = stucture.consolidate_profiles(data)
                new_data.drop(useless_cols, axis=1, inplace=True)

        elif policy == UpsertPolicies.CHUNK_UPDATE:
            logging.info("Chunks Table")
            """req = text(
                "select * from {} where (chunk_id, collab_id) = ('{}','{}');".format(
                    table_name,
                    row[ChunkPg.chunk_id],
                    row[ChunkPg.collab_id],
                ),
            )"""
            req = AzurePGManager._sql_req_creator("cv_chunks",
                                                  table=table,
                                                  collab_id=row[ChunkPg.collab_id],
                                                  chunk_id=row[ChunkPg.chunk_id])
            data = pd.read_sql(req, con_string)
            if len(data) == 0:
                logging.info("Adding new chunks")
                log_string = f"Adding new profile of {row[ProfilePg.collab_id]} "
                logging.info(log_string)
                new_data = pd.DataFrame(row, row.index).T
            else:
                logging.info("Chunk already exists!")

        if new_data is not None:
            try:
                new_data.to_sql(table.__tablename__, con_string, if_exists="append", index=False)
            except Exception as e:
                log_string = f"Error updating chunks table {e}"
                logging.exception(log_string)

    @staticmethod
    def check_existence(table_name: str, id_value: str) -> bool:
        """req = text(f"SELECT * FROM {table_name} WHERE {id_tag} = '{id_value}'")"""
        req = AzurePGManager._sql_req_creator("check_existence",
                                              table=PgCollabs,
                                              collab_id=id_value,
                                              )

        return len(pd.read_sql(req, con_string)) != 0

    @staticmethod
    def check_existence_email(table_name: str, id_value: str) -> bool:
        """req = text(f"SELECT * FROM {table_name} WHERE {id_tag} = '{id_value}'")"""
        req = (select(PgCollabs).
                   where(PgCollabs.email == id_value))

        return len(pd.read_sql(req, con_string)) != 0

    @staticmethod
    def get_collabs_associated_email(table_name: str, id_value: str) -> bool:
        """req = text(f"SELECT * FROM {table_name} WHERE {id_tag} = '{id_value}'")"""
        req = (select(PgCollabs).
                   where(PgCollabs.email == id_value))
        return (pd.read_sql(req, con_string))["collab_id"].values[0]

    @staticmethod
    def save(
            pg_profiles: pd.DataFrame,
            pg_chunks: pd.DataFrame,
            pg_cvs: pd.DataFrame,
    ) -> None:
        AzurePGManager.save_to_db(
            PG_Profiles,
            pg_profiles,
            UpsertPolicies.PROFILE_UPDATE,
        )
        AzurePGManager.save_to_db(PgCvs, pg_cvs, UpsertPolicies.APPEND)
        AzurePGManager.save_to_db(
            ChunkModel,
            pg_chunks,
            UpsertPolicies.CHUNK_UPDATE,
        )
