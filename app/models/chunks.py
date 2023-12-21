from pgvector.sqlalchemy import Vector
from sqlalchemy import Column, String, select

from app.core.models.scoredprofilescols import ScoredChunksDF
from app.models import Base


class ChunkModel(Base):
    __tablename__ = "chunks"

    chunk_id = Column(String, primary_key=True)
    collab_id = Column(String)
    chunk_text = Column(String)
    chunk_embeddings = Column(Vector)

    @staticmethod
    def similarity_query(emb: list[float], limit_lines: int = 20) -> select:
        query = (select(ChunkModel, ChunkModel.chunk_embeddings
                        .cosine_distance(emb)
                        .label(ScoredChunksDF.semantic_score))
                 .limit(limit_lines))


        return query
