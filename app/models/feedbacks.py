import logging

import streamlit_authenticator as stauth
from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Session

from models import Base, engine


class Feedbacks(Base):
    __tablename__ = "feedbacks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    time = Column(DateTime,default=func.now())
    query_id = Column(String)
    collab_id = Column(String)
    evaluation = Column(Integer)
    user_id = Column(String, unique=True)

    def __repr__(self):
        return f"{self.query_id} {self.collab_id} {self.evaluation} {self.user_id}"

    @staticmethod
    def create(feedback:"Feedbacks"):
        '''
        create or update a a feedback
        '''
        try:
            with Session(engine) as session:
                # find feedback of the same collab and the same query and the same user
                u = session.query(Feedbacks).filter(
                    Feedbacks.query_id == str(feedback.query_id)
                    and Feedbacks.collab_id == feedback.collab_id
                    and Feedbacks.user_id == feedback.user_id).first()
                if u:
                    u.evaluation = feedback.evaluation
                    logging.info(f"Feedback {u.user_id} Updated")
                else:
                    session.add(feedback)
                    logging.info(f"Feedback {feedback.user_id} Created")
                session.commit()
                session.flush()
                return True
        except Exception as e:
            logging.exception(f"Error creating feedback {e}")
            return False


    @staticmethod
    def count()->int:
        with Session(engine) as session:
            return session.query(Feedbacks).count()

