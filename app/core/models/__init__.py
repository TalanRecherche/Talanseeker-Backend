from app.settings import Settings
env = Settings()
from sqlalchemy.orm import declarative_base
import os
from sqlalchemy import create_engine

Base = declarative_base()
con_string = f'postgresql://{os.environ.get("DB__USER_NAME")}:{os.environ.get("DB__PWD")}@{os.environ.get("DB__HOST")}:{os.environ.get("DB__PORT")}'
try:
    engine = create_engine(con_string)
except Exception as e:
    engine = None


