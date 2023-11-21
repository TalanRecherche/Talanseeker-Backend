from sqlalchemy import Column, String

from app.models import Base


class PgChunks(Base):
    __tablename__ = "chunks"

    chunk_id = Column(String, primary_key=True)
    cv_id = Column(String)
    profile_id = Column(String)
    chunk_text = Column(String)
    chunk_embeddings = Column(String)
