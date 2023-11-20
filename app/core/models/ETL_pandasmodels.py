"""Created on Wed Aug 30 13:40:23 2023

@author: agarc

"""
import pandera as pa
from pandera import Column

from app.core.models.parent_pandasmodels import ParentPandasModel

""" This file contains columns of all dataframes used in the pipeline"""


class TEXT_DF(ParentPandasModel):
    """columns FileMassExtractor df"""

    # unique identifier for the cv
    cv_id = "cv_id"
    collab_id = "collab_id"
    file_path = "file_path"
    file_name = "file_name"
    file_extension = "file_extension"
    file_full_name = "file_full_name"
    file_text = "file_text"

    schema = pa.DataFrameSchema(
        {
            cv_id: Column(str, nullable=True),
            collab_id: Column(str, nullable=True),
            file_path: Column(str, nullable=True),
            file_name: Column(str, nullable=True),
            file_extension: Column(str, nullable=True),
            file_full_name: Column(str, nullable=True),
            file_text: Column(str, nullable=True),
        },
    )


class CHUNK_DF(ParentPandasModel):
    """columns Chunker df"""

    chunk_id = "chunk_id"
    cv_id = "cv_id"
    collab_id = "collab_id"
    file_path = "file_path"
    file_name = "file_name"
    file_extension = "file_extension"
    file_full_name = "file_full_name"
    chunk_text = "chunk_text"

    schema = pa.DataFrameSchema(
        {
            chunk_id: Column(str, nullable=True),
            cv_id: Column(str, nullable=True),
            collab_id: Column(str, nullable=True),
            file_path: Column(str, nullable=True),
            file_name: Column(str, nullable=True),
            file_extension: Column(str, nullable=True),
            file_full_name: Column(str, nullable=True),
            chunk_text: Column(str, nullable=True),
        },
    )


class EMBEDDING_DF(ParentPandasModel):
    """columns EmbedderBackend df"""

    chunk_id = "chunk_id"
    cv_id = "cv_id"
    collab_id = "collab_id"
    file_path = "file_path"
    file_name = "file_name"
    file_extension = "file_extension"
    file_full_name = "file_full_name"
    chunk_text = "chunk_text"
    chunk_embeddings = "chunk_embeddings"

    schema = pa.DataFrameSchema(
        {
            chunk_id: Column(str, nullable=True),
            cv_id: Column(str, nullable=True),
            collab_id: Column(str, nullable=True),
            file_path: Column(str, nullable=True),
            file_name: Column(str, nullable=True),
            file_extension: Column(str, nullable=True),
            file_full_name: Column(str, nullable=True),
            chunk_text: Column(str, nullable=True),
            chunk_embeddings: Column(list[float], nullable=True),
        },
    )


class PARSED_DF(ParentPandasModel):
    """columns LLMParser df"""

    chunk_id = "chunk_id"
    cv_id = "cv_id"
    collab_id = "collab_id"
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

    schema = pa.DataFrameSchema(
        {
            chunk_id: Column(str, nullable=True),
            cv_id: Column(str, nullable=True),
            collab_id: Column(str, nullable=True),
            file_path: Column(str, nullable=True),
            file_name: Column(str, nullable=True),
            file_extension: Column(str, nullable=True),
            file_full_name: Column(str, nullable=True),
            chunk_text: Column(str, nullable=True),
            years: Column(int, nullable=True),
            diplomas_certifications: Column(list[str], nullable=True),
            roles: Column(list[str], nullable=True),
            sectors: Column(list[str], nullable=True),
            companies: Column(list[str], nullable=True),
            soft_skills: Column(list[str], nullable=True),
            technical_skills: Column(list[str], nullable=True),
        },
    )


class STRUCTCV_DF(ParentPandasModel):
    """columns ProfileStructurator df"""

    cv_id = "cv_id"
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

    schema = pa.DataFrameSchema(
        {
            cv_id: Column(str, nullable=True),
            collab_id: Column(str, nullable=True),
            years: Column(int, nullable=True),
            diplomas_certifications: Column(list[str], nullable=True),
            roles: Column(list[str], nullable=True),
            sectors: Column(list[str], nullable=True),
            companies: Column(list[str], nullable=True),
            soft_skills: Column(list[str], nullable=True),
            technical_skills: Column(list[str], nullable=True),
            file_path: Column(str, nullable=True),
            file_name: Column(str, nullable=True),
            file_extension: Column(str, nullable=True),
            file_full_name: Column(str, nullable=True),
        },
    )


class STRUCTPROFILE_DF(ParentPandasModel):
    """columns ProfileStructurator df"""

    collab_id = "collab_id"
    cv_id = "cv_id"
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

    schema = pa.DataFrameSchema(
        {
            collab_id: Column(str, nullable=True),
            cv_id: Column(list[str], nullable=True),
            years: Column(int, nullable=True),
            diplomas_certifications: Column(list[str], nullable=True),
            roles: Column(list[str], nullable=True),
            sectors: Column(list[str], nullable=True),
            companies: Column(list[str], nullable=True),
            soft_skills: Column(list[str], nullable=True),
            technical_skills: Column(list[str], nullable=True),
            file_path: Column(list[str], nullable=True),
            file_name: Column(list[str], nullable=True),
            file_extension: Column(list[str], nullable=True),
            file_full_name: Column(list[str], nullable=True),
        },
    )
