"""Created by agarc at 01/10/2023
Features:
"""
import pandera as pa
from pandera import Column

from app.core.models.parent_pandasmodels import ParentPandasModel


class CollabPg(ParentPandasModel):
    """column main table on PostGres"""

    # information of this table will be extracted from Kimble and other ERPs"
    # primary key
    collab_id = "collab_id"
    name = "name"
    surname = "surname"
    email = "email"
    manager = "manager"
    bu_internal = "bu_internal"
    bu = "bu"
    bu_secondary = "bu_secondary"
    domain = "domain"
    community = "community"
    start_date = "start_date"
    end_date = "end_date"
    revenue = "revenue"
    cost = "cost"
    cost_unit = "cost_unit"
    resource_type = "resource_type"
    grade = "grade"
    role = "role"
    sub_role = "sub_role"
    region = "region"
    city = "city"
    assigned_until = "assigned_until"
    availability_score = "availability_score"

    # column names used to rename to the db columns names
    resource_ = "Resource"
    username_ = "Username"
    city_ = "Location City"
    bu_internal_ = "Resource BU (Internal) "
    bu_ = "Resource BU"
    bu_secondary_ = "Resource BU (Secondary)"
    domain_ = "Domaine: Domaine Name"
    community_ = "Communaute: Communaute Name"
    manager_ = "Resource Manager"
    start_date_ = "Start Date"
    end_date_ = "End Date"
    revenue_ = "Standard Revenue"
    cost_ = "Standard Cost"
    cost_unit_ = "Standard Cost Unit Type: Unit Type Name"
    resource_type_ = "Resource Type"
    grade_ = "Grade"
    role_ = "Job Family"
    sub_role_ = "Job Family Subgroup"
    region_ = "Location"
    assigned_until_ = "Assigned Until"
    availability_score_ = "Availability Score "

    date_cols = [start_date, end_date, assigned_until]
    ext_txt_ = "[EXT]"

    schema = pa.DataFrameSchema(
        {
            collab_id: Column(str, nullable=True),
            name: Column(str, nullable=True),
            surname: Column(str, nullable=True),
            email: Column(str, nullable=True),
            manager: Column(str, nullable=True),
            bu_internal: Column(str, nullable=True),
            bu: Column(str, nullable=True),
            bu_secondary: Column(str, nullable=True),
            domain: Column(str, nullable=True),
            community: Column(str, nullable=True),
            start_date: Column(str, nullable=True),
            end_date: Column(str, nullable=True),
            revenue: Column(float, nullable=True),
            cost: Column(float, nullable=True),
            cost_unit: Column(str, nullable=True),
            resource_type: Column(str, nullable=True),
            grade: Column(str, nullable=True),
            role: Column(str, nullable=True),
            sub_role: Column(str, nullable=True),
            region: Column(str, nullable=True),
            city: Column(str, nullable=True),
            assigned_until: Column(str, nullable=True),
            availability_score: Column(float, nullable=True),
        },
    )


class CvPg(ParentPandasModel):
    """column CV table on PostGres"""

    cv_id = "cv_id"
    collab_id = "collab_id"
    file_full_name = "file_full_name"

    schema = pa.DataFrameSchema(
        {
            cv_id: Column(str, nullable=True),
            collab_id: Column(str, nullable=True),
            file_full_name: Column(str, nullable=True),
        },
    )


class ChunkPg(ParentPandasModel):
    """column chunks & embeddings table on PostGres"""

    chunk_id = "chunk_id"
    collab_id = "collab_id"
    chunk_text = "chunk_text"
    chunk_embeddings = "chunk_embeddings"

    schema = pa.DataFrameSchema(
        {
            chunk_id: Column(str, nullable=True),
            collab_id: Column(str, nullable=True),
            chunk_text: Column(str, nullable=True),
            chunk_embeddings: Column(list[float], nullable=True),
        },
    )


class ProfilePg(ParentPandasModel):
    """column structured profiles table on PostGres"""

    # primary key
    collab_id = "collab_id"
    # attribut
    years = "years"
    diplomas_certifications = "diplomas_certifications"
    roles = "roles"
    sectors = "sectors"
    companies = "companies"
    soft_skills = "soft_skills"
    technical_skills = "technical_skills"

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
        },
    )
