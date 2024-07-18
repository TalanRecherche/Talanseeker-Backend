"""Created on 21/11/2023

@author: Youness

"""
from __future__ import annotations

from typing import Optional

from fastapi import Query
from pydantic import BaseModel, Field


class Filters(BaseModel):
    region: Optional[list[str]] = None
    city: Optional[list[str]] = None
    grade: Optional[list[str]] = None
    assigned_until: Optional[str] = None
    availability_score: Optional[int] = 0


class ChatbotRequest(BaseModel):
    user_query: str
    conversation_id: Optional[str] = None
    region: Optional[list[str]] = Field(
        Query(None, description="Séléctionner des régions"),
    )
    city: Optional[list[str]] = Field(
        Query(None, description="Séléctionner des villes"),
    )
    grade: Optional[list[str]] = Field(
        Query(None, description="Séléctionner des grades"),
    )
    bu: Optional[list[str]] = Field(
        Query(None, description="Sélectionner des BU"),
    )
    bu_secondary: Optional[list[str]] = Field(
        Query(None, description="Sélectionner des BU secondaires"),
    )
    assigned_until: Optional[str] = Field(Query(None))
    availability_score: Optional[int] = Field(Query(None))


class GeneralInformation(BaseModel):
    description: Optional[str] = None
    collab_id: Optional[str] = None
    bu: Optional[str] = None
    bu_secondary: Optional[str] = None
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


class ChatbotResponse(BaseModel):
    question_valid: bool = True
    query_id: Optional[str] = None
    chatbot_response: Optional[str] = None
    conversation_id: Optional[int] = None
    candidates: Optional[list[Candidate]] = None

