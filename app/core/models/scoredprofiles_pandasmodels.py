import pandera as pa
from pandera import Column

from app.core.models.parent_pandasmodels import ParentPandasModel


class ScoredProfilesDF(ParentPandasModel):
    """column structured profiles table on PostGres"""

    collab_id = "collab_id"
    years = "years"
    diplomas_certifications = "diplomas_certifications"
    roles = "roles"
    sectors = "sectors"
    companies = "companies"
    soft_skills = "soft_skills"
    technical_skills = "technical_skills"
    keywords_score = "keywords_score"
    semantic_score = "semantic_score"
    keywords_score_normalized = "keywords_score_normalized"
    semantic_score_normalized = "semantic_score_normalized"
    overall_score = "overall_score"

    schema = pa.DataFrameSchema(
        {
            collab_id: Column(str, nullable=True),
            years: Column(int, nullable=True),
            diplomas_certifications: Column(list[str], nullable=True),
            roles: Column(list[str], nullable=True),
            sectors: Column(list[str], nullable=True),
            companies: Column(list[str], nullable=True),
            soft_skills: Column(list[str], nullable=True),
            technical_skills: Column(list[str], nullable=True),
            keywords_score: Column(int, nullable=True),
            semantic_score: Column(float, nullable=True),
            keywords_score_normalized: Column(float, nullable=True),
            semantic_score_normalized: Column(float, nullable=True),
            overall_score: Column(float, nullable=True),
        },
    )


class ScoredChunksDF(ParentPandasModel):
    chunk_id = "chunk_id"
    collab_id = "collab_id"
    chunk_text = "chunk_text"
    chunk_embeddings = "chunk_embeddings"
    semantic_score = "semantic_score"

    schema = pa.DataFrameSchema(
        {
            chunk_id: Column(str, nullable=True),
            collab_id: Column(str, nullable=True),
            chunk_text: Column(str, nullable=True),
            chunk_embeddings: Column(list[float], nullable=True),
            semantic_score: Column(float, nullable=True),
        },
    )
