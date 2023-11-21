from sqlalchemy import Column, String, select
from sqlalchemy.orm import Session

from app.models import Base, engine


class PgCvs(Base):
    __tablename__ = "cvs"

    cv_id = Column(String, primary_key=True)
    collab_id = Column(String)
    file_full_name = Column(String)

    def __repr__(self) -> str:
        return f"{self.cv_id} {self.collab_id} {self.file_full_name}"

    def get_cv_name_by_id(self, cv_id: str) -> str | None:
        req = select(PgCvs.file_full_name).where(PgCvs.cv_id == cv_id)
        with Session(engine) as session:
            return session.execute(req).first()
