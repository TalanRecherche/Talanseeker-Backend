from __future__ import annotations

from pydantic import BaseModel

from typing import List, Optional


class Filters(BaseModel):
    region: Optional[List[str]] = None
    city: Optional[List[str]] = None
    grade: Optional[List[str]] = None
    assigned_until: Optional[str] = None
    availability_score: Optional[int] = 0


class SearchRequest(BaseModel):
    filters: Optional[Filters]

class GeneralInformation(BaseModel):
    collab_id: Optional[str] = None
    manager: Optional[str] = None
    name: Optional[str] = None
    surname: Optional[str] = None
    email: Optional[str] = None
    grade: Optional[str] = None
    seniority: Optional[str] = None
    region: Optional[str] = None
    city: Optional[str] = None
    assigned_until: Optional[str] = None
    availability_score: Optional[str] = None
    years: Optional[str] = None
    diplomas_certifications: Optional[List[str]] = None
    roles: Optional[List[str]] = None
    sectors: Optional[List[str]] = None
    companies: Optional[List[str]] = None
    soft_skills: Optional[List[str]] = None
    technical_skills: Optional[List[str]] = None


class CvsInformation(BaseModel):
    cv_name: Optional[str] = None
    cv_id: Optional[str] = None


class Candidate(BaseModel):
    general_information: Optional[GeneralInformation] = None
    cvs_information: Optional[List[CvsInformation]] = None

class SearchResponse(BaseModel):
    candidates: Optional[List[Candidate]] = None
