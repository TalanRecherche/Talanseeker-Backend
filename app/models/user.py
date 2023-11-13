from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.dialects.postgresql import ARRAY

from app.models import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    pwd = Column(String)
    email = Column(String, unique=True)
    activated = Column(Boolean, default=True)
    authorizations = Column(ARRAY(Integer))


    def __repr__(self):
        return f"{self.f_name} {self.l_name} {self.email} {self.activated} {self.authorizations}"
