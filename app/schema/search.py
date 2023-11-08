from __future__ import annotations

from pydantic import BaseModel

from typing import List


class Filters(BaseModel):
    region: str
    city: str
    grade: str
    assigned_until: str
    availability_score: str


class SearchRequest(BaseModel):
    filters: Filters

class GeneralInformation(BaseModel):
    collab_id: str
    manager: str
    name: str
    surname: str
    email: str
    grade: str
    seniority: str
    region: str
    city: str
    assigned_until: str
    availability_score: str
    years: str
    diplomas_certifications: str
    roles: str
    sectors: str
    companies: str
    soft_skills: str
    technical_skills: str


class CvsInformation(BaseModel):
    cv_name: str
    cv_id: str


class Candidate(BaseModel):
    general_information: GeneralInformation
    cvs_information: List[CvsInformation]


class SearchResponse(BaseModel):
    candidates: List[Candidate]
