from models import Base
from sqlalchemy import Column, Integer, String
class PG_Profiles(Base):
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


    def __repr__(self):
        return f"{self.name} {self.surname} {self.years} {self.diploma_certification} {self.roles}"
