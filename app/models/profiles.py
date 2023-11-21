from sqlalchemy import Column, String

from app.models import Base


class PG_Profiles(Base):  # noqa: N801
    __tablename__ = "profiles"

    profile_id = Column(String, primary_key=True)
    collab_id = Column(String)
    name = Column(String)
    surname = Column(String)
    years = Column(String)
    diploma_certification = Column(String)
    roles = Column(String)
    sectors = Column(String)
    company = Column(String)
    soft_skills = Column(String)
    technical_skills = Column(String)
