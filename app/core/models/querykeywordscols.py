"""Created on 11.09.2023

@author: agarc

"""


class QueryStruct:
    """information parsed from the user_query using GuessIntention.
    !!!This table should contain one row per type of profile!!!
    """

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

    @classmethod
    def get_attributes_(cls) -> list[str]:
        return [attr for attr, value in vars(cls).items() if not attr.endswith("_")]


class QueryKeywords:
    """columns from QueryStruct used for scoring"""

    # keys of the dataframe
    diplomas_certifications = "diplomas_certifications"
    soft_skills = "soft_skills"
    technical_skills = "technical_skills"

    roles = "roles"
    missions = "missions"
    sectors = "sectors"
    companies = "companies"

    @classmethod
    def get_attributes_(cls) -> list[str]:
        return [attr for attr, value in vars(cls).items() if not attr.endswith("_")]


class QueryFilters:
    """columns from QueryStruct AND the front used for FILTERING (prior to scoring)"""

    # keys of the dataframe
    years = "years"
    bu = "bu"
    region = "region"

    start_mission = "start_mission"
    end_mission = "start_mission"
    duration_mission = "duration_mission"

    @classmethod
    def get_attributes_(cls) -> list[str]:
        return [attr for attr, value in vars(cls).items() if not attr.endswith("_")]
