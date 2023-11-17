# -*- coding: utf-8 -*-
"""
Created on Sun Sep 17 13:07:47 2023

@author: agarc

"""
import ast
import datetime
import logging
from typing import Optional

import pandas as pd

from app.exceptions.exceptions import InvalidColumnsError
from app.models import con_string
from app.core.models.PG_pandasmodels import CHUNK_PG
from app.core.models.PG_pandasmodels import COLLAB_PG
from app.core.models.PG_pandasmodels import CV_PG
from app.core.models.PG_pandasmodels import PROFILE_PG
from app.schema.chatbot import Filters, ChatbotRequest
from app.settings import Settings




class PGfetcher:
    """ Connects to postgres and fetches tables after filtering"""

    def __init__(self, settings):
        self.settings = settings
        pass

    # =============================================================================
    # internal functions
    # =============================================================================
    def fetch_all(self, filters: ChatbotRequest = None) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """
        Fetch all profiles from the PostGres db.
        The other tables (chunks, cvs, collabs) are only fetched if their collab_id is in profile

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
        collab_ids = df_profiles[PROFILE_PG.collab_id].tolist()

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
    def _build_filtered_request(query:str,  filters: Optional[Filters] = None) -> str:
        """
        :param req: is the start of the request e.g. select p.* from profiles p left join collabs c on p.collab_id = c.collab_id where true
        :param filters: filters object
        :return: request with filter
        """
        if filters:
            regions = filters.region
            if regions:
                query += f"and c.{COLLAB_PG.region} in {tuple(regions)} "
            cities = filters.city
            if cities:
                cities = [elem.lower() for elem in cities]
                query += f"and lower(c.{COLLAB_PG.city}) in {tuple(cities)} "
            grades = filters.grade
            if grades and len(grades) > 0:
                query += f"and c.{COLLAB_PG.grade} in {tuple(grades)} "

            date = filters.assigned_until
            availability_score = filters.availability_score

            if date or availability_score:
                query += " and (false "
                if date:
                    query += f" or c.assigned_until <= '{date}' "

                if availability_score:
                    query += f" or c.availability_score >= {float(availability_score)} "

                query += ")"
            query += ";"
            query = query.replace(',)', ')')
        return query
    def _fetch_profiles(self, filters: Optional[Filters]=None):
        query = "select p.* from profiles p left join collabs c on p.collab_id = c.collab_id where true "
        query = PGfetcher._build_filtered_request(query, filters)
        """ fetch the entire profile table"""
        logging.info(query)
        print(query)
        df_profiles_ = pd.read_sql(query, con_string)
        if not PROFILE_PG.validate_dataframe(df_profiles_):
            raise InvalidColumnsError("df_profiles is missing the required columns")
        return df_profiles_

    def filter_collabs(self, filters: Optional[Filters]=None):
        """ fetch the entire profile table"""
        query = 'select c.surname as "Nom", c."name" as "Prénom", c.email as "Email", c.manager as "Manager", c.city as "Ville", c."domain"  as "Métier" , c.grade  as "Grade", c.availability_score, c.assigned_until from collabs c where true '
        query = PGfetcher._build_filtered_request(query, filters)
        logging.info(query)
        df_profiles_ = pd.read_sql(query, con_string)
        date = filters.assigned_until
        if date and len(date) > 0:
            df_profiles_ = df_profiles_.apply(PGfetcher._adjust_availability_score, axis=1, start_date=date)

        df_profiles_.rename(columns={COLLAB_PG.availability_score: "Disponibilité"}, inplace=True)
        return df_profiles_

    @staticmethod
    def _adjust_availability_score(row: pd.Series, start_date) -> pd.Series:
        try:
            if row[COLLAB_PG.assigned_until] is None or datetime.datetime.strptime(row[COLLAB_PG.assigned_until],
                                                                                   '%Y-%m-%d').date() <= start_date:
                row[COLLAB_PG.availability_score] = 100
        except:
            logging.warning(f"Date not conform, skipping collab {row}")
        return row

    def _fetch_chunks(self, collab_ids_string):
        try:
            """ Create the SQL query using the formatted collab_ids_str """
            query = f"select * from chunks where collab_id in ({collab_ids_string})"
            logging.info(query)
            # Execute the query and fetch the result as a DataFrame
            df_chunks = pd.read_sql(query, con_string)
            # convert chunk embeddings to array[float]
            df_chunks[CHUNK_PG.chunk_embeddings] = df_chunks[CHUNK_PG.chunk_embeddings].apply(ast.literal_eval)
            if not CHUNK_PG.validate_dataframe(df_chunks):
                raise InvalidColumnsError("df_profiles is missing the required columns")

            return df_chunks

        except InvalidColumnsError as e:
            logging.error(e)
            raise

        except Exception as e:
            logging.error(f"An error occurred while executing the query: {e}")
            raise

    def _fetch_cvs(self, collab_ids_string):
        try:
            """ Create the SQL query using the formatted collab_ids_str """
            query = f"select * from cvs where collab_id in ({collab_ids_string})"
            logging.info(query)
            # Execute the query and fetch the result as a DataFrame
            df_cvs = pd.read_sql(query, con_string)
            if not CV_PG.validate_dataframe(df_cvs):
                raise InvalidColumnsError("df_cvs is missing the required columns")
            return df_cvs

        except InvalidColumnsError as e:
            logging.error(e)
            raise

        except Exception as e:
            logging.error(f"An error occurred while executing the query: {e}")
            raise

    def _fetch_collabs(self, collab_ids_string):
        try:
            """ Create the SQL query using the formatted collab_ids_str """
            query = f"select * from collabs where collab_id in ({collab_ids_string})"
            logging.info(query)
            # Execute the query and fetch the result as a DataFrame
            df_collabs = pd.read_sql(query, con_string)
            if not COLLAB_PG.validate_dataframe(df_collabs):
                raise InvalidColumnsError("df_collabs is missing the required columns")
            return df_collabs

        except InvalidColumnsError as e:
            logging.error(e)
            raise

        except Exception as e:
            logging.error(f"An error occurred while executing the query: {e}")
            raise

    def _make_collab_string(self, collab_ids):
        try:
            """ Wrap each collab_id in single quotes and join them with commas """
            collab_ids_string = ','.join([f'\'{id}\'' for id in collab_ids])
            return collab_ids_string
        except Exception as e:
            logging.error(f"An error occurred while parsing collab_ids: {e}")
            raise


if __name__ == '__main__':
    settings = Settings()
    fetcher = PGfetcher(settings)
    df_chunks, df_collabs, df_cvs, df_profiles = fetcher.fetch_all()
    print(df_chunks)
    print(df_collabs)
    print(df_cvs)
    print(df_profiles)
