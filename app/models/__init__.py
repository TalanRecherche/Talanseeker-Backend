from sqlalchemy.orm import declarative_base, sessionmaker
import os
from sqlalchemy import create_engine

Base = declarative_base()
con_string = f'postgresql://{os.environ.get("DB__USER_NAME")}:{os.environ.get("DB__PWD")}@{os.environ.get("DB__HOST")}:{os.environ.get("DB__PORT")}'
try:
    engine = create_engine(con_string)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
except Exception as e:
    engine = None
    SessionLocal = None

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()