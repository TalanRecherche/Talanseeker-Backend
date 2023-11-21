import logging

from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from app.models import Base, engine


class Logs(Base):
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    request_time = Column(DateTime, default=func.now())
    request_issuer = Column(String)
    request_func = Column(Text)
    request_args = Column(Text)
    request_kwargs = Column(Text)

    def log(self):
        try:
            logging.debug("Adding logs")
            with Session(engine) as session:
                session.add(self)
                session.commit()
        except Exception as e:
            logging.error(f"Logs not working {e}")
