import logging

from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from app.models import Base, engine


class Logs(Base):
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    request_time = Column(DateTime, default=func.now())
    user_id = Column(String)
    session_id = Column(String, default=None)
    url_path = Column(String)
    status_code = Column(Integer)

    def log(self) -> None:
        try:
            logging.debug("Adding logs")
            with Session(engine) as session:
                session.add(self)
                session.commit()
        except Exception as e:
            log_string = f"An error occurred while adding logs: {e}"
            logging.exception(log_string)
