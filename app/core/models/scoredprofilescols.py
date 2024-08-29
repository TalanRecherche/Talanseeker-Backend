class ScoredProfilesDF:
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

    @classmethod
    def get_attributes_(cls) -> list[str]:
        return [attr for attr, value in vars(cls).items() if not attr.endswith("_")]


class ScoredChunksDF:
    chunk_id = "chunk_id"
    cv_id = "cv_id"
    collab_id = "collab_id"
    chunk_text = "chunk_text"
    chunk_embeddings = "chunk_embeddings"

    semantic_score = "semantic_score"

    @classmethod
    def get_attributes_(cls) -> list[str]:
        return [attr for attr, value in vars(cls).items() if not attr.endswith("_")]
