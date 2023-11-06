from models import Base
from sqlalchemy import Column, Integer, String
class PG_CVs(Base):
    __tablename__ = "cvs"

    cv_id = Column(String, primary_key=True)
    profile_id = Column(String)
    file_full_name = Column(String)
    file_path = Column(String)
    file_extention = Column(String)

    def __repr__(self):
        return f"{self.cv_id} {self.profile_id} {self.file_full_name} {self.file_path} {self.file_extention}"
