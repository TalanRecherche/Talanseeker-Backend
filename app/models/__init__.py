import logging

import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.settings import settings

try:
    Base = declarative_base()
    con_string = (f"postgresql://{settings.db_settings.username}:"
                  f"{settings.db_settings.pwd}@{settings.db_settings.host}:"
                  f"{settings.db_settings.port}/{settings.db_settings.name}")
    engine = create_engine(con_string)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
except Exception as e:
    logging.exception(e)

def get_db() -> SessionLocal:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def sql_to_pd(query: str) -> pd.DataFrame:
    return pd.read_sql(query, con_string)


def create_all_tables() -> None:
    try:
        Base.metadata.create_all(engine)
    except Exception as e:
        logging.exception(e)
