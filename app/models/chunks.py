from app.models import Base
from sqlalchemy import Column, Integer, String
class PG_Chunks(Base):
    __tablename__ = "chunks"

    chunk_id = Column(String, primary_key=True)
    cv_id = Column(String)
    profile_id = Column(String)
    chunk_text = Column(String)
    chunk_embeddings = Column(String) #TODO: change to array of floats

