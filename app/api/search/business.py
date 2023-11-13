from typing import List

import pandas as pd

from app.core.chatbot_features.PGfetcher import PGfetcher
from app.core.models.PG_pandasmodels import COLLAB_PG, PROFILE_PG, CV_PG
from app.schema.search import CvsInformation, SearchResponse, SearchRequest, Candidate, GeneralInformation
from app.settings import Settings


def df_to_candidate_schema(profiles_data: pd.DataFrame, cvs: pd.DataFrame) -> List[Candidate]:
    candidates = []
    profiles_data.apply(row_to_candidate_schema, axis=1, candidates=candidates, cvs=cvs)
    return candidates


def row_to_candidate_schema(row: pd.Series, candidates: List[Candidate], cvs: pd.DataFrame) -> None:
    candidate = Candidate()
    candidate.general_information = GeneralInformation(
        collab_id=row[COLLAB_PG.collab_id],
        manager=row[COLLAB_PG.manager],
        name=row[COLLAB_PG.name],
        surname=row[COLLAB_PG.surname],
        email=row[COLLAB_PG.email],
        grade=row[COLLAB_PG.grade],
        seniority=row[COLLAB_PG.grade],
        region=row[COLLAB_PG.region],
        city=row[COLLAB_PG.city],
        assigned_until=row[COLLAB_PG.assigned_until],
        availability_score=row[COLLAB_PG.availability_score],
        years=row[PROFILE_PG.years],
        diplomas_certifications=row[PROFILE_PG.diplomas_certifications],
        roles=row[PROFILE_PG.roles],
        sectors=row[PROFILE_PG.sectors],
        companies=row[PROFILE_PG.companies],
        soft_skills=row[PROFILE_PG.soft_skills],
        technical_skills=row[PROFILE_PG.technical_skills])

    # get cv of the profile
    collab_cvs = list(cvs[cvs[COLLAB_PG.collab_id] == row[COLLAB_PG.collab_id]][
                          [CV_PG.cv_id, CV_PG.file_full_name]].T.to_dict().values())
    # adjust naming file_full_name => cv_name
    candidate.cvs_information = [CvsInformation(cv_id=cv[CV_PG.cv_id], cv_name=cv[CV_PG.file_full_name]) for cv in
                                 collab_cvs]
    candidates.append(candidate)


def search_business(request: SearchRequest) -> SearchResponse:
    response = SearchResponse()
    settings = Settings()
    fetcher = PGfetcher(settings)
    chunks, collabs, cvs, profiles = fetcher.fetch_all(filters=request.filters)

    profiles_data = collabs.merge(profiles, on="collab_id")

    response.candidates = df_to_candidate_schema(profiles_data, cvs)

    return response
