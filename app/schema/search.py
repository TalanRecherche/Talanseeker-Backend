"""Created on 21/11/2023

@author: Youness

"""
from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class SearchRequest(BaseModel):
    region: Optional[list[str]] = None
    city: Optional[list[str]] = None
    grade: Optional[list[str]] = None
    assigned_until: Optional[str] = None
    availability_score: Optional[int] = None


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
    diplomas_certifications: Optional[list[str]] = None
    roles: Optional[list[str]] = None
    sectors: Optional[list[str]] = None
    companies: Optional[list[str]] = None
    soft_skills: Optional[list[str]] = None
    technical_skills: Optional[list[str]] = None


class CvsInformation(BaseModel):
    cv_name: Optional[str] = None
    cv_id: Optional[str] = None
    cv_link: Optional[str] = None


class Candidate(BaseModel):
    general_information: Optional[GeneralInformation] = None
    cvs_information: Optional[list[CvsInformation]] = None


class SearchResponse(BaseModel):
    candidates: Optional[list[Candidate]] = None
