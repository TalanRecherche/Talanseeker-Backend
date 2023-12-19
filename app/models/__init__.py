import os

import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()
con_string = f'postgresql://{os.environ.get("DB__USER_NAME")}:{os.environ.get("DB__PWD")}@{os.environ.get("DB__HOST")}:{os.environ.get("DB__PORT")}/{os.environ.get("DB__NAME")}'
engine = create_engine(con_string)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> SessionLocal:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def sql_to_pd(query: str) -> pd.DataFrame:
    return pd.read_sql(query, con_string)
