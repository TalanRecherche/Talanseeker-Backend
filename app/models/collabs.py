from sqlalchemy import FLOAT, Column, String

from app.models import Base


class PgCollabs(Base):
    __tablename__ = "collabs"

    collab_id = Column(String, primary_key=True)
    name = Column(String)
    surname = Column(String)
    revenue = Column(FLOAT)
    cost = Column(FLOAT)
    availability_score = Column(FLOAT)
    email = Column(String)
    bu_internal = Column(String)
    bu = Column(String)
    bu_secondary = Column(String)
    domain = Column(String)
    community = Column(String)
    manager = Column(String)
    start_date = Column(String)
    cost_unit = Column(String)
    resource_type = Column(String)
    grade = Column(String)
    role = Column(String)
    sub_role = Column(String)
    region = Column(String)
    city = Column(String)
    assigned_until = Column(String)
    end_date = Column(String)

    def __repr__(self) -> str:
        return f"{self.collab_id} {self.name} {self.surname}"
