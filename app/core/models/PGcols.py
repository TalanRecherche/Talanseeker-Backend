# -*- coding: utf-8 -*-
"""
Created by agarc at 01/10/2023
app.core:
"""


class COLLAB_PG:
    """ column main table on PostGres """
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

    @classmethod
    def get_attributes_(cls):
        return [attr for attr, value in vars(cls).items() if
                not (attr.startswith('_') or attr.endswith('_') or attr == 'date_cols')]


class CV_PG:
    """ column CV table on PostGres"""
    # primary key
    cv_id = 'cv_id'
    # foreign key
    collab_id = 'collab_id'
    # attribut
    file_full_name = 'file_full_name'

    @classmethod
    def get_attributes_(cls):
        return [attr for attr, value in vars(cls).items() if not attr.endswith('_')]


class CHUNK_PG:
    """ column chunks & embeddings table on PostGres """
    # primary key
    chunk_id = 'chunk_id'
    # foreign key
    cv_id = 'cv_id'
    collab_id = 'collab_id'
    chunk_text = 'chunk_text'
    chunk_embeddings = 'chunk_embeddings'

    @classmethod
    def get_attributes_(cls):
        return [attr for attr, value in vars(cls).items() if not attr.endswith('_')]


class PROFILE_PG:
    """ column structured profiles table on PostGres """
    # primary key
    collab_id = 'collab_id'
    # attribut
    years = 'years'
    diplomas_certifications = 'diplomas_certifications'
    roles = 'roles'
    sectors = 'sectors'
    companies = 'companies'
    soft_skills = 'soft_skills'
    technical_skills = 'technical_skills'

    @classmethod
    def get_attributes_(cls):
        return [attr for attr, value in vars(cls).items() if not attr.endswith('_')]