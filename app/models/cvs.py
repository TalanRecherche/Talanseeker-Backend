from sqlalchemy import Column, String, select
from sqlalchemy.orm import Session

from app.models import Base, engine


class PG_CVs(Base):
    __tablename__ = "cvs"

    cv_id = Column(String, primary_key=True)
    collab_id = Column(String)
    file_full_name = Column(String)

    def __repr__(self):
        return f"{self.cv_id} {self.collab_id} {self.file_full_name}"

    def get_cv_name_by_id(self, cv_id: str) -> str | None:
        req = select(PG_CVs.file_full_name).where(PG_CVs.cv_id == cv_id)
        res = None
        with Session(engine) as session:
            res = session.execute(req).first()
        return res
