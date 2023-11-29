import logging

from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from app.models import Base, engine


class ChatbotLogs(Base):
    __tablename__ = "chatbot_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    request_time = Column(DateTime, default=func.now())
    request_issuer = Column(String)
    query = Column(Text)
    response = Column(Text)
    candidates = Column(Text)

    def __repr__(self) -> str:
        return f"{self.request_issuer} {self.request} {self.response}"

    def log(self) -> int:
        try:
            logging.debug("Adding chatbot logs")
            with Session(engine) as session:
                session.add(self)
                session.commit()
                return self.id
        except Exception as e:
            log_string = f"An error occurred while adding logs: {e}"
            logging.exception(log_string)
