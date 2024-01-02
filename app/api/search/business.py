import pandas as pd

from app.core.chatbot_features.pg_fetcher import PGfetcher
from app.core.models.pg_pandasmodels import CollabPg, CvPg, ProfilePg
from app.schema.search import (
    Candidate,
    CvsInformation,
    GeneralInformation,
    SearchRequest,
    SearchResponse,
)


def df_to_candidate_schema(
    profiles_data: pd.DataFrame,
    cvs: pd.DataFrame,
) -> list[Candidate]:
    candidates = []
    profiles_data.apply(row_to_candidate_schema, axis=1, candidates=candidates, cvs=cvs)
    return candidates


def row_to_candidate_schema(
    row: pd.Series,
    candidates: list[Candidate],
    cvs: pd.DataFrame,
) -> None:
    candidate = Candidate()
    candidate.general_information = GeneralInformation(
        collab_id=row[CollabPg.collab_id],
        manager=row[CollabPg.manager],
        name=row[CollabPg.name],
        surname=row[CollabPg.surname],
        email=row[CollabPg.email],
        grade=row[CollabPg.grade],
        seniority=row[CollabPg.grade],
        region=row[CollabPg.region],
        city=row[CollabPg.city],
        assigned_until=row[CollabPg.assigned_until],
        availability_score=row[CollabPg.availability_score],
        years=row[ProfilePg.years],
        diplomas_certifications=row[ProfilePg.diplomas_certifications],
        roles=row[ProfilePg.roles],
        sectors=row[ProfilePg.sectors],
        companies=row[ProfilePg.companies],
        soft_skills=row[ProfilePg.soft_skills],
        technical_skills=row[ProfilePg.technical_skills],
    )

    # get cv of the profile
    collab_cvs = list(
        cvs[cvs[CollabPg.collab_id] == row[CollabPg.collab_id]][
            [CvPg.cv_id, CvPg.file_full_name]
        ]
        .T.to_dict()
        .values(),
    )
    # adjust naming file_full_name => cv_name
    candidate.cvs_information = [
        CvsInformation(cv_id=cv[CvPg.cv_id], cv_name=cv[CvPg.file_full_name])
        for cv in collab_cvs
    ]
    candidates.append(candidate)


def search_business(request: SearchRequest) -> SearchResponse:
    response = SearchResponse()
    fetcher = PGfetcher()
    chunks, collabs, cvs, profiles = fetcher.fetch_all(filters=request)

    profiles_data = collabs.merge(profiles, on="collab_id")

    response.candidates = df_to_candidate_schema(profiles_data, cvs)

    return response
