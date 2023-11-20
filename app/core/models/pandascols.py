"""Created on Wed Aug 30 13:40:23 2023

@author: agarc

"""

""" This file contains columns of all dataframes used in the pipeline"""


class TEXT_DF:
    """columns FileMassExtractor df"""

    # unique identifier for the cv
    cv_id = "cv_id"
    collab_id = "collab_id"
    file_path = "file_path"
    file_name = "file_name"
    file_extension = "file_extension"
    file_full_name = "file_full_name"
    file_text = "file_text"

    @classmethod
    def get_attributes_(cls):
        return [attr for attr, value in vars(cls).items() if not attr.endswith("_")]


class CHUNK_DF:
    """columns Chunker df"""

    # primaty key
    chunk_id = "chunk_id"
    # ref
    cv_id = "cv_id"
    collab_id = "collab_id"
    # attribut
    file_path = "file_path"
    file_name = "file_name"
    file_extension = "file_extension"
    file_full_name = "file_full_name"
    # profile_id = 'profile_id'
    chunk_text = "chunk_text"

    @classmethod
    def get_attributes_(cls):
        return [attr for attr, value in vars(cls).items() if not attr.endswith("_")]


class EMBEDDING_DF:
    """columns EmbedderBackend df"""

    # primaty key
    chunk_id = "chunk_id"
    # ref
    cv_id = "cv_id"
    collab_id = "collab_id"
    # attribut
    file_path = "file_path"
    file_name = "file_name"
    file_extension = "file_extension"
    file_full_name = "file_full_name"
    chunk_text = "chunk_text"
    chunk_embeddings = "chunk_embeddings"

    @classmethod
    def get_attributes_(cls):
        return [attr for attr, value in vars(cls).items() if not attr.endswith("_")]


class PARSED_DF:
    """columns LLMParser df"""

    # primaty key
    chunk_id = "chunk_id"
    # ref
    cv_id = "cv_id"
    collab_id = "collab_id"
    # attribut
    file_path = "file_path"
    file_name = "file_name"
    file_extension = "file_extension"
    file_full_name = "file_full_name"
    chunk_text = "chunk_text"
    years = "years"
    diplomas_certifications = "diplomas_certifications"
    roles = "roles"
    sectors = "sectors"
    companies = "companies"
    soft_skills = "soft_skills"
    technical_skills = "technical_skills"

    # those keys.values are "inferred" by the llm
    parsed_keys_ = [
        years,
        diplomas_certifications,
        roles,
        sectors,
        companies,
        soft_skills,
        technical_skills,
    ]

    @classmethod
    def get_attributes_(cls):
        return [attr for attr, value in vars(cls).items() if not attr.endswith("_")]


class STRUCTCV_DF:
    """columns ProfileStructurator df"""

    # primary key
    cv_id = "cv_id"
    # attribut
    collab_id = "collab_id"
    years = "years"
    diplomas_certifications = "diplomas_certifications"
    roles = "roles"
    sectors = "sectors"
    companies = "companies"
    soft_skills = "soft_skills"
    technical_skills = "technical_skills"
    file_path = "file_path"
    file_name = "file_name"
    file_extension = "file_extension"
    file_full_name = "file_full_name"

    # columns of the dataframe output
    static_columns_ = [
        file_path,
        file_name,
        file_extension,
        file_full_name,
        cv_id,
        collab_id,
    ]

    numerical_columns_ = [years]

    string_columns_ = [
        roles,
        diplomas_certifications,
        sectors,
        companies,
        soft_skills,
        technical_skills,
    ]

    @classmethod
    def get_attributes_(cls):
        return [attr for attr, value in vars(cls).items() if not attr.endswith("_")]


class STRUCTPROFILE_DF:
    """columns ProfileStructurator df"""

    # primary key
    collab_id = "collab_id"
    # ref
    cv_id = "cv_id"
    # attribute
    years = "years"
    diplomas_certifications = "diplomas_certifications"
    roles = "roles"
    sectors = "sectors"
    companies = "companies"
    soft_skills = "soft_skills"
    technical_skills = "technical_skills"
    file_path = "file_path"
    file_name = "file_name"
    file_extension = "file_extension"
    file_full_name = "file_full_name"

    # columns of the dataframe output
    static_columns_ = [
        file_path,
        file_name,
        file_extension,
        file_full_name,
        cv_id,
        collab_id,
    ]

    numerical_columns_ = [years]

    string_columns_ = [
        roles,
        diplomas_certifications,
        sectors,
        companies,
        soft_skills,
        technical_skills,
    ]

    @classmethod
    def get_attributes_(cls):
        return [attr for attr, value in vars(cls).items() if not attr.endswith("_")]
