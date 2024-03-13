import logging
import tempfile
import time
from pathlib import Path

import pandas as pd
from fastapi import Response
from pyinstrument import Profiler

from app.core.chatbot_features.candidatesselector import CandidatesSelector
from app.core.chatbot_features.chatbot import Chatbot
from app.core.chatbot_features.intentionfinder import IntentionFinder
from app.core.chatbot_features.pg_fetcher import PGfetcher
from app.core.chatbot_features.queryrouter import QueryRouter
from app.core.models.pg_pandasmodels import CollabPg, CvPg, ProfilePg
from app.schema.chatbot import (
    Candidate,
    ChatbotRequest,
    ChatbotResponse,
    GeneralInformation,
)
from app.schema.search import CvsInformation
from app.core.models.query_pandasmodels import QueryStruct


def df_to_candidate_schema(
        profiles_data: pd.DataFrame, cvs: pd.DataFrame
) -> list[Candidate]:
    candidates = []
    profiles_data.apply(
        row_to_candidate_schema,
        axis=1,
        candidates=candidates,
        cvs=cvs
    )
    return candidates


def row_to_candidate_schema(
        row: pd.Series,
        candidates: list[Candidate],
        cvs: pd.DataFrame
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


def chatbot_business(chatbot_request: ChatbotRequest) -> ChatbotResponse:
    chatbot_response = ChatbotResponse()

    # check if query is meaningful and related to staffing
    router = QueryRouter()
    query_valid_bool = router.get_router_response(chatbot_request.user_query)
    if query_valid_bool:
        chatbot_business_helper(chatbot_request, chatbot_response)

    else:
        chatbot_response.question_valid = False
        chatbot_response.chatbot_response = (
            "Je suis désolé, mais cette question ne "
            "concerne pas le staffing de consultants."
        )

    return chatbot_response


def chatbot_business_helper(
        chatbot_request: ChatbotRequest,
        chatbot_response: ChatbotResponse,
) -> None:
    t = time.time()
    # Structure Query using IntentionFinderSettings
    intention_finder = IntentionFinder()
    guess_intention_query = intention_finder.guess_intention(chatbot_request.user_query)

    # Fetch data from postgres
    chatbot_request.assigned_until = guess_intention_query[QueryStruct.start_date][0][0]
    fetcher = PGfetcher()
    df_chunks, df_collabs, df_cvs, df_profiles = fetcher.fetch_all(
        filters=chatbot_request,
    )
    logging.info(f"IntentionFinder: {time.time() - t}")

    t = time.time()
    # Select best candidates
    selector = CandidatesSelector()
    chunks, collabs, cvs, profiles = selector.select_candidates(
        df_chunks,
        df_collabs,
        df_cvs,
        df_profiles,
        guess_intention_query,
    )
    logging.info(f"CandidatesSelector: {time.time() - t}")

    t = time.time()
    profiles_data = collabs.merge(profiles, on="collab_id")
    logging.info(f"profiles_data: {time.time() - t}")

    t = time.time()
    chatbot_response.candidates = df_to_candidate_schema(
        profiles_data,
        cvs
    )
    logging.info(f"Make candidates: {time.time() - t}")

    t = time.time()
    # Send candidates data to chatbot and get answer
    chatbot = Chatbot()
    response, query_sent = chatbot.get_chatbot_response(
        guess_intention_query,
        chunks,
        collabs,
        profiles,
    )
    logging.info(f"Chatbot response: {time.time() - t}")

    chatbot_response.chatbot_response = response


def profile_chatbot_business(chatbot_request: ChatbotRequest) -> Response:
    with tempfile.TemporaryDirectory() as dir_:
        file_name = Path(dir_) / "profiling.html"
        # profile process
        profiler = Profiler()
        profiler.start()
        chatbot_business(chatbot_request)
        profiler.stop()
        profiler.write_html(file_name)

        with Path(file_name).open("rb") as file:
            return Response(
                status_code=200,
                content=file.read(),
                media_type="application/octet-stream",
            )
