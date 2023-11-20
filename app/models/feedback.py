import logging

from sqlalchemy import Column, DateTime, Integer, String, func
from sqlalchemy.orm import Session

from app.models import Base, engine


class FeedbacksModel(Base):
    __tablename__ = "feedbacks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    time = Column(DateTime, default=func.now())
    query_id = Column(String)
    collab_id = Column(String)
    evaluation = Column(Integer)
    user_id = Column(String)

    @staticmethod
    def create(feedback: "FeedbacksModel"):
        """Create or update a a feedback"""
        with Session(engine) as session:
            # find feedback of the same collab and the same query and the same user
            u = (
                session.query(FeedbacksModel)
                .filter(
                    FeedbacksModel.query_id == str(feedback.query_id)
                    and FeedbacksModel.collab_id == feedback.collab_id
                    and FeedbacksModel.user_id == feedback.user_id,
                )
                .first()
            )
            if u:
                u.evaluation = feedback.evaluation
                logging.info(f"Feedback {u.user_id} Updated")
            else:
                session.add(feedback)
                logging.info(f"Feedback {feedback.user_id} Created")
            session.commit()
            session.flush()
            return True

    def add(self):
        with Session(engine) as session:
            session.add(self)
            session.commit()
            session.flush()
            logging.info(f"Feedback {self.user_id} added")
            return True

    def patch(self):
        with Session(engine) as session:
            u = (
                session.query(FeedbacksModel)
                .filter(
                    FeedbacksModel.query_id == str(self.query_id)
                    and FeedbacksModel.collab_id == self.collab_id
                    and FeedbacksModel.user_id == self.user_id,
                )
                .first()
            )
            if u:
                u.evaluation = self.evaluation
                session.commit()
                session.flush()
                logging.info(f"Feedback {self.user_id} added")
                return True
        return False

    @staticmethod
    def count() -> int:
        with Session(engine) as session:
            return session.query(FeedbacksModel).count()
