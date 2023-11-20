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
    region: Optional[list[str]] = Field(
        Query(None, description="Séléctionner des régions"),
    )
    city: Optional[list[str]] = Field(
        Query(None, description="Séléctionner des villes"),
    )
    grade: Optional[list[str]] = Field(
        Query(None, description="Séléctionner des grades"),
    )
    assigned_until: Optional[str] = Field(Query(None))
    availability_score: Optional[int] = Field(Query(None))


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


class SkillsTable(BaseModel):
    global_skill: Optional[list[str]] = None
    score: Optional[list[int]] = None
    skills: Optional[list[list[str]]] = None


class Candidate(BaseModel):
    general_information: Optional[GeneralInformation] = None
    cvs_information: Optional[list[CvsInformation]] = None
    skills_table: Optional[SkillsTable] = None


class ChatbotResponse(BaseModel):
    question_valid: bool = True
    query_id: Optional[str] = None
    chatbot_response: Optional[str] = None
    candidates: Optional[list[Candidate]] = None
