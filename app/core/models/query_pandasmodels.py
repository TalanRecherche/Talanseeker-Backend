"""Created on 11.09.2023

@author: agarc

"""
import pandera as pa
from pandera import Column

from app.core.models.parent_pandasmodels import ParentPandasModel


class QUERY_STRUCT(ParentPandasModel):
    """information parsed from the user_query using GuessIntention."""

    # keys of the dataframe
    user_query = "user_query"  # appears on all rows
    simplified_query = "simplified_query"  # appears on all rows
    nb_profiles = "nb_profiles"  # number of row-wise profile to get
    years = "years"
    diplomas_certifications = "diplomas_certifications"
    soft_skills = "soft_skills"
    technical_skills = "technical_skills"
    roles = "roles"
    missions = "missions"
    sectors = "sectors"
    companies = "companies"

    schema = pa.DataFrameSchema(
        {
            user_query: Column(list[str], nullable=True),
            simplified_query: Column(list[str], nullable=True),
            nb_profiles: Column(list[str], nullable=True),
            years: Column(list[str], nullable=True),
            diplomas_certifications: Column(list[str], nullable=True),
            soft_skills: Column(list[str], nullable=True),
            technical_skills: Column(list[str], nullable=True),
            roles: Column(list[str], nullable=True),
            missions: Column(list[str], nullable=True),
            sectors: Column(list[str], nullable=True),
            companies: Column(list[str], nullable=True),
        },
    )


class QUERY_KEYWORDS(ParentPandasModel):
    """columns from QUERY_STRUCT used for scoring"""

    # keys of the dataframe
    diplomas_certifications = "diplomas_certifications"
    soft_skills = "soft_skills"
    technical_skills = "technical_skills"
    roles = "roles"
    missions = "missions"
    sectors = "sectors"
    companies = "companies"

    schema = pa.DataFrameSchema(
        {
            diplomas_certifications: Column(list[str], nullable=True),
            soft_skills: Column(list[str], nullable=True),
            technical_skills: Column(list[str], nullable=True),
            roles: Column(list[str], nullable=True),
            missions: Column(list[str], nullable=True),
            sectors: Column(list[str], nullable=True),
            companies: Column(list[str], nullable=True),
        },
    )
