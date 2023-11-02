from models import Base
from sqlalchemy import Column, Integer, String
class PG_Collabs(Base):
    __tablename__ = "collabs"

    collab_id = Column(String, primary_key=True)
    name = Column(String)
    surname = Column(String)

    def __repr__(self):
        return f"{self.collab_id} {self.name} {self.surname}"
