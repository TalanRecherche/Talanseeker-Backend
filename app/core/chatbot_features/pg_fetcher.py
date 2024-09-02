"""Created on Sun Sep 17 13:07:47 2023

@author: agarc

"""
import datetime
import logging
from datetime import date
from typing import Optional

import pandas as pd
from sqlalchemy import select

from app.core.models.pg_pandasmodels import CollabPg, CvPg, ProfilePg
from app.core.models.scoredprofilescols import ScoredChunksDF
from app.exceptions.exceptions import InvalidColumnsError
from app.models import con_string
from app.models.chunks import ChunkModel
from app.models.collabs import PgCollabs
from app.models.cvs import PgCvs
from app.schema.chatbot import ChatbotRequest, Filters
from app.schema.search import SearchRequest
from app.settings import settings


class PGfetcher:
    """Connects to postgres and fetches tables after filtering"""

    def __init__(self) -> None:
        self.settings = settings

    # =============================================================================
    # internal functions
    # =============================================================================
    def fetch_all(
            self,
            filters: ChatbotRequest | SearchRequest = None,
    ) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """Fetch all profiles from the PostGres db.
        The other tables (chunks, cvs, collabs) are only fetched
        if their collab_id is in profile

        Returns
        -------
        df_profiles : pd.DataFrame
            profiles table.
        df_chunks : pd.DataFrame
            chunk table. Only if collab_id in df_profiles
        df_collabs : pd.DataFrame
            collab table. Only if collab_id in df_profiles
        df_cvs : pd.DataFrame
            cv tables. Only if collab_id in df_profiles

        """
        # fetch profiles
        df_profiles = self._fetch_profiles(filters=filters)
        # get all collab_ids in the profile table. Used to filter out candidates.
        collab_ids = df_profiles[ProfilePg.collab_id].tolist()

        # create string of collab_ids for the query
        collab_ids_string = self._make_collab_string(collab_ids)

        # fetch chunks
        df_chunks = self._fetch_chunks(collab_ids_string)

        # fetch cvs
        df_cvs = self._fetch_cvs(collab_ids_string)

        # fecth collabs
        df_collabs = self._fetch_collabs(collab_ids_string)

        return df_chunks, df_collabs, df_cvs, df_profiles

    # =============================================================================
    # internal function
    # =============================================================================
    @staticmethod
    def _build_filtered_request(query: str, filters: Optional[Filters] = None) -> str:
        """:param query: is the start of the request
        e.g. select p.* from profiles p left join collabs c
        on p.collab_id = c.collab_id where true
        :param filters: filters object
        :return: request with filter
        """
        if filters:
            regions = filters.region
            if regions != ["Non renseigné"]:
                regions = [r.lower() for r in regions]
                query += f"and lower(c.{CollabPg.region}) in {tuple(regions)} "
            cities = filters.city
            if cities != ["Non renseigné"]:
                cities = [elem.lower() for elem in cities]
                query += f"and lower(c.{CollabPg.city}) in {tuple(cities)} "
            bus = filters.bu
            if bus != ["Non renseigné"]:
                bus = [elem.lower() for elem in bus]
                query += f"and lower(c.{CollabPg.bu}) in {tuple(bus)} "
            bu_secondaries = filters.bu_secondary
            if bu_secondaries != ["Non renseigné"]:
                bu_secondaries = [elem.lower() for elem in bu_secondaries]
                query += f"and lower(c.{CollabPg.bu_secondary}) in {tuple(bu_secondaries)} "
            grades = filters.grade
            if grades and len(grades) > 0:
                query += f"and c.{CollabPg.grade} in {tuple(grades)} "

            date = filters.assigned_until
            availability_score = filters.availability_score

            if date != "Non renseigné" or availability_score:
                query += " and (false "
                if date:
                    query += f" or c.assigned_until <= '{date}' "

                if availability_score:
                    query += f" or c.availability_score >= {float(availability_score)} "

                query += ")"
            query += ";"
            query = query.replace(",)", ")")
        return query

    def _fetch_profiles(self, filters: Optional[Filters] = None) -> pd.DataFrame:
        query_all_profiles = (
            "select p.* from profiles p left join collabs c on p.collab_id = "
            "c.collab_id where true "
        )
        query_with_filters = PGfetcher._build_filtered_request(query_all_profiles, filters)
        """ fetch the entire profile table"""
        logging.info(query_with_filters)
        df_profiles_ = pd.read_sql(query_with_filters, con_string)

        #Si df_profiles_ est vide cela veut dire que l'un des filtres n'a pas fonctionné
        if df_profiles_.shape[0] == 0:
            #l'erreur peut être du à une ville, region, grade ou date qui n'existent pas
            #dans la jointure profiles et collabs
            logging.error(f"""the following SQL request fail to return at least 1 profile :
                          {query_with_filters}
                          To avoid a crash app we negligate the following filters : {filters}""")
            logging.info(query_all_profiles)
            df_profiles_ = pd.read_sql(query_all_profiles, con_string)

        return df_profiles_

    def filter_collabs(self, filters: Optional[Filters] = None) -> pd.DataFrame:
        """Fetch the entire profile table"""
        query = (
            'select c.surname as "Nom", c."name" as "Prénom", c.email as "Email", '
            'c.manager as "Manager", c.city as "Ville", c."domain"  as "Métier" '
            ', c.grade  as "Grade", c.availability_score, c.assigned_until from '
            "collabs c where true"
        )
        query = PGfetcher._build_filtered_request(query, filters)
        logging.info(query)
        df_profiles_ = pd.read_sql(query, con_string)
        date = filters.assigned_until
        if date and len(date) > 0:
            df_profiles_ = df_profiles_.apply(
                PGfetcher._adjust_availability_score,
                axis=1,
                start_date=date,
            )

        df_profiles_.rename(
            columns={CollabPg.availability_score: "Disponibilité"},
            inplace=True,
        )
        return df_profiles_

    @staticmethod
    def _adjust_availability_score(row: pd.Series, start_date: date) -> pd.Series:
        try:
            if (
                    row[CollabPg.assigned_until] is None
                    or datetime.datetime.strptime(
                row[CollabPg.assigned_until],
                "%Y-%m-%d",
            ).astimezone().date()
                    <= start_date
            ):
                row[CollabPg.availability_score] = 100
        except Exception as e:
            log_string = f"Date not conform, skipping collab {row} {e}"
            logging.warning(log_string)
            raise e
        return row

    @staticmethod
    def _sql_request_builder(req_target: str, **kwargs) -> str | None:
        """
        build sql queries based on their target
        f"select * from chunks where collab_id in ({collab_ids_string})"
        f"select * from cvs where collab_id in ({collab_ids_string})"
        f"select * from collabs where collab_id in ({collab_ids_string})"
        """
        req = None
        if req_target == "collab_chunks":
            req = select(ChunkModel).where(
                ChunkModel.collab_id.in_(kwargs["collab_ids_string"]))
        elif req_target == "select_collab_chunks":
                req = select(ChunkModel.chunk_id, ChunkModel.chunk_embeddings).where(
                    ChunkModel.collab_id.in_(kwargs["collab_ids_string"]))
        elif req_target == "selected_collab_chunks":
                req = select(ChunkModel.collab_id, ChunkModel.chunk_text,
                             ChunkModel.chunk_id).where(
                    ChunkModel.chunk_id.in_(kwargs["selected_chunk_ids"]))
        elif req_target == "collab_cvs":
            req = select(PgCvs).where(
                PgCvs.collab_id.in_(kwargs["collab_ids_string"]))
        elif req_target == "collabs":
            req = select(PgCollabs).where(
                PgCollabs.collab_id.in_(kwargs["collab_ids_string"]))
        return req

    def _fetch_chunks(self, collab_ids_string: str) -> pd.DataFrame | None:
        try:
            """Create the SQL query using the formatted collab_ids_str
            query = f"select * from chunks where collab_id in ({collab_ids_string})"

            """

            query = PGfetcher._sql_request_builder("collab_chunks",
                                                   collab_ids_string=tuple(
                                                       collab_ids_string.
                                                       replace("'", "").
                                                       split(",")))

            logging.info(query)
            # Execute the query and fetch the result as a DataFrame
            df_chunks = pd.read_sql(query, con_string)
            return df_chunks

        except InvalidColumnsError as e:
            logging.error(e)
            raise

        except Exception as e:
            log_string = f"An error occurred while executing the query: {e}"
            logging.error(log_string)
            raise

    @staticmethod
    def fetch_selected_chunks(selected_chunks:pd.DataFrame)->pd.DataFrame | None:
        try:
            """Create the SQL query using the formatted collab_ids_str
            query = f"select * from chunks where collab_id in ({collab_ids_string})"

            """
            chunk_ids = selected_chunks[ScoredChunksDF.chunk_id].to_list()
            query = PGfetcher._sql_request_builder("selected_collab_chunks",
                                                   selected_chunk_ids=tuple(
                                                       chunk_ids))

            logging.info(query)
            # Execute the query and fetch the result as a DataFrame
            df_chunks = pd.read_sql(query, con_string)

            selected_chunks = selected_chunks.merge(df_chunks)

            return selected_chunks

        except InvalidColumnsError as e:
            logging.error(e)
            raise

        except Exception as e:
            log_string = f"An error occurred while executing the query: {e}"
            logging.error(log_string)
            raise

    def _fetch_cvs(self, collab_ids_string: str) -> pd.DataFrame | None:
        """Create the SQL query using the formatted collab_ids_str
        query = f"select * from cvs where collab_id in ({collab_ids_string})"

        """
        query = PGfetcher._sql_request_builder("collab_cvs",
                                               collab_ids_string=tuple(
                                                   collab_ids_string.
                                                   replace("'", "").
                                                   split(",")))

        logging.info(query)
        # Execute the query and fetch the result as a DataFrame
        df_cvs = pd.read_sql(query, con_string)
        if not CvPg.validate_dataframe(df_cvs):
            err = "df_profiles is missing the required columns"
            raise InvalidColumnsError(err)
        return df_cvs

    def _fetch_collabs(self, collab_ids_string: str) -> pd.DataFrame | None:
        try:
            """Create the SQL query using the formatted collab_ids_str
            query = f"select * from collabs where collab_id in ({collab_ids_string})"
            """
            query = PGfetcher._sql_request_builder("collabs",
                                                   collab_ids_string=tuple(
                                                       collab_ids_string.
                                                       replace("'", "").
                                                       split(",")))

            logging.info(query)
            # Execute the query and fetch the result as a DataFrame
            df_collabs = pd.read_sql(query, con_string)
            if not CollabPg.validate_dataframe(df_collabs):
                err = "df_profiles is missing the required columns"
                raise InvalidColumnsError(err)
            return df_collabs

        except InvalidColumnsError as e:
            logging.error(e)
            raise

        except Exception as e:
            log_string = f"An error occurred while executing the query: {e}"
            logging.error(log_string)
            raise

    def _make_collab_string(self, collab_ids: list[str]) -> str | None:
        try:
            """Wrap each collab_id in single quotes and join them with commas"""
            collab_ids_string = ",".join([f"'{_id}'" for _id in collab_ids])
            return collab_ids_string
        except Exception as e:
            log_string = f"An error occurred while parsing collab_ids: {e}"
            logging.error(log_string)
            raise
