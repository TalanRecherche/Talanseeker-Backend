from sqlalchemy import Column, String

from app.models import Base


class PgCollabs(Base):
    __tablename__ = "collabs"

    collab_id = Column(String, primary_key=True)
    name = Column(String)
    surname = Column(String)

    def __repr__(self) -> str:
        return f"{self.collab_id} {self.name} {self.surname}"
