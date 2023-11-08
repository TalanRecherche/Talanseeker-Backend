from typing import List

import pandas as pd

from app.core.chatbot_features.intentionfinder import IntentionFinder
from app.core.chatbot_features.PGfetcher import PGfetcher
from app.core.chatbot_features.candidatesselector import CandidatesSelector
from app.core.chatbot_features.chatbot import Chatbot
from app.core.chatbot_features.queryrouter import QueryRouter
from app.core.models.PG_pandasmodels import COLLAB_PG, PROFILE_PG, CV_PG
from app.schema.chatbot import ChatbotRequest, ChatbotResponse, Candidate, GeneralInformation, SkillsTable
from app.schema.search import CvsInformation
from app.settings import Settings
from app.core.chatbot_features.dataviz import get_skills_table


def df_to_candidate_schema(profiles_data: pd.DataFrame, cvs: pd.DataFrame, skills_table: pd.DataFrame) -> List[
    Candidate]:
    candidates = []
    profiles_data.apply(row_to_candidate_schema, axis=1, candidates=candidates, cvs=cvs, skills_table=skills_table)
    return candidates


def row_to_candidate_schema(row: pd.Series, candidates: List[Candidate], cvs: pd.DataFrame,
                            skills_table: pd.DataFrame) -> None:
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

    skills = skills_table[row[COLLAB_PG.email]]
    skill_table = SkillsTable(
        global_skill=skills["competence"].to_list(),
        score=skills["n_occurence"].to_list(),
        skills=skills["skills"].to_list())

    candidate.skills_table = skill_table
    candidates.append(candidate)


def chatbot_business(chatbot_request: ChatbotRequest) -> ChatbotResponse:
    chatbot_response = ChatbotResponse()
    settings = Settings()

    # check if query is meaningful and related to staffing
    router = QueryRouter(settings)
    query_valid_bool = router.get_router_response(chatbot_request.user_query)
    if query_valid_bool:
        try:
            chatbot_business_helper(chatbot_request, settings, chatbot_response)
        except Exception as e:
            chatbot_response.question_valid = False
            chatbot_response.chatbot_response = "Aucun profil ne correspond aux critères demandés!"

    else:
        chatbot_response.question_valid = False
        chatbot_response.chatbot_response = "Je suis désolé, mais cette question ne concerne pas le staffing de consultants."

    return chatbot_response


def chatbot_business_helper(chatbot_request: ChatbotRequest, settings: Settings,
                            chatbot_response: ChatbotResponse) -> None:
    # Structure Query using IntentionFinderSettings
    intention_finder = IntentionFinder(settings)
    guessIntention_query = intention_finder.guess_intention(chatbot_request.user_query)

    # Fetch data from postgres
    fetcher = PGfetcher(settings)
    df_chunks, df_collabs, df_cvs, df_profiles = fetcher.fetch_all(filters=chatbot_request.filters)

    # Select best candidates
    selector = CandidatesSelector(settings)
    chunks, collabs, cvs, profiles = selector.select_candidates(df_chunks,
                                                                df_collabs,
                                                                df_cvs,
                                                                df_profiles,
                                                                guessIntention_query)
    skills_table = get_skills_table(chunks, collabs, cvs, profiles)

    profiles_data = collabs.merge(profiles, on="collab_id")

    chatbot_response.candidates = df_to_candidate_schema(profiles_data, cvs, skills_table)
    # Send candidates data to chatbot and get answer
    chatbot = Chatbot(settings)
    response, query_sent = chatbot.get_chatbot_response(guessIntention_query,
                                                        chunks,
                                                        collabs,
                                                        profiles)
    chatbot_response.chatbot_response = response
