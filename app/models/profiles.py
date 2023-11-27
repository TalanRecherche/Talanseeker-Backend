from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import ARRAY

from app.models import Base


class PG_Profiles(Base):  # noqa: N801
    __tablename__ = "profiles"

    collab_id = Column(String, primary_key=True)
    years = Column(String)
    diplomas_certifications = Column(ARRAY(String))
    roles = Column(ARRAY(String))
    sectors = Column(ARRAY(String))
    companies = Column(ARRAY(String))
    soft_skills = Column(ARRAY(String))
    technical_skills = Column(ARRAY(String))
