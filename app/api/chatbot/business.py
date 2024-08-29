import datetime
import logging
import tempfile
import time
from pathlib import Path

import pandas as pd
import pytz
from fastapi import Response
from pyinstrument import Profiler
from sqlalchemy import Column, Integer, Text, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.core.chatbot_features.candidatesselector import CandidatesSelector
from app.core.chatbot_features.chatbot import Chatbot
from app.core.chatbot_features.conversationmanager import ConversationManager
from app.core.chatbot_features.intentionfinder import IntentionFinder
from app.core.chatbot_features.pg_fetcher import PGfetcher
from app.core.chatbot_features.queryrouter import QueryRouter, QuerySynthesizer
from app.core.models.pg_pandasmodels import CollabPg, CvPg, ProfilePg
from app.core.models.query_pandasmodels import QueryStruct
from app.models import con_string
from app.models.conversations import Conversations
from app.schema.chatbot import (
    Candidate,
    ChatbotRequest,
    ChatbotResponse,
    GeneralInformation,
)
from app.schema.search import CvsInformation


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

def _create_cv_link(cv_id:str) -> str:
    """create the url request to download a cv for a given cv_id on talanseeker-PROD

    Args:
        cv_id (str): cv_id from sql tables CVS

    Returns:
        str: url to download the CV from talanseeker-PROD
    """
    return f"https://talanseeker-prod.azurewebsites.net/api/v1/cv_manager/download?cv_id={cv_id}&type=file"

def row_to_candidate_schema(
        row: pd.Series,
        candidates: list[Candidate],
        cvs: pd.DataFrame
) -> None:
    candidate = Candidate()
    candidate.general_information = GeneralInformation(
        description=row["description"], #ajouté en dur car c'est le LLM qui génère la description.
        collab_id=row[CollabPg.collab_id],
        bu=row[CollabPg.bu],
        bu_secondary=row[CollabPg.bu_secondary],
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
    candidate.cvs_information = []

    for cv in collab_cvs:
        cv_id = cv[CvPg.cv_id]
        cv_name = cv[CvPg.file_full_name]
        cv_link = _create_cv_link(cv[CvPg.cv_id])

        CvsInformation()
        cvs_info = CvsInformation(cv_id=cv_id, cv_name=cv_name, cv_link=cv_link)

        candidate.cvs_information.append(cvs_info)


    candidates.append(candidate)

    return candidates

# URL de connexion
DATABASE_URL = "postgresql://llm_cv:jw8s0F4@localhost:5432/llm_cv"

# Créez l'objet engine
engine = create_engine(DATABASE_URL)

# Créez une session locale
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Déclarez la base
Base = declarative_base()

# Définissez le modèle ajusté
class Conversation(Base):
    __tablename__ = "conversations"

    conversation_id = Column(Integer, primary_key=True, index=True)
    requests_content = Column(Text, nullable=False)

# Fonction pour récupérer et imprimer le contenu de la requête
def get_requests_content(conversation_id : int) -> str:
    session = SessionLocal()
    try:
        # Requête pour récupérer le requests_content du conversation_id donné
        conversation = session.query(Conversation).filter_by(
            conversation_id=conversation_id).first()
        if conversation:
            return conversation.requests_content  # Retourner le contenu dans chatbot_business
        else:

            return None  # Retourner None si la conversation n'existe pas
    except (ValueError, TypeError, KeyError) as e:
        logging.error(f"An error occurred: {e}")
        return None
    finally:
        session.close()



def chatbot_business(chatbot_request: ChatbotRequest) -> ChatbotResponse:
    chatbot_response = ChatbotResponse()
    # Récupération des valeurs de conversation_id et user_query
    conversation_id = chatbot_request.conversation_id
    user_query = chatbot_request.user_query
    # Récupérer le contenu précédent de la conversation
    previous_content = get_requests_content(conversation_id)

    if previous_content is not None:
        # Nettoyer previous_content
        cleaned_previous_content = previous_content.replace("{", "").replace(
            "}", "").replace('"', "").strip()

        # Synthétiser la requête avec le contexte
        synthesizer = QuerySynthesizer()
        synthesized_query  = synthesizer.get_synthesis_response(
            cleaned_previous_content, user_query)

        # Vérifier la pertinence de la requête synthétisée
        router = QueryRouter()
        query_valid_bool = router.get_router_response(synthesized_query)

        if query_valid_bool:
            chatbot_request.user_query = synthesized_query
            chatbot_business_helper(chatbot_request, chatbot_response)
        else:
            chatbot_response.question_valid = False
            chatbot_response.chatbot_response = (
                "Je suis désolé, mais cette question ne "
                "concerne pas le staffing de consultants."
            )
    else:
        # Vérifier directement la pertinence de la nouvelle requête
        router = QueryRouter()
        query_valid_bool = router.get_router_response(user_query)

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
    # Handle conversation
    conv = ConversationManager(chatbot_request)
    db_conv = conv.get_all_database()
    if chatbot_request.conversation_id is not None:
        # Vérifier si la table n'est pas vide
        if conv.get_empty_database_conv():
            chatbot_response.chatbot_response = "La BDD conversations est vide"
            chatbot_response.question_valid = False
            return
        elif not conv.check_conversation_exist(chatbot_request.conversation_id):
            chatbot_response.chatbot_response = "L'identifiant de conversation n'existe pas"
            chatbot_response.question_valid = False
            return
        else:
            # définir la liste en fonction de la BDD
            current_conv = conv.get_conversation(chatbot_request.conversation_id)
            already_selected_collabs = "".join(list(current_conv[1][1:-1])).split(",")

            already_selected_user_query = current_conv[2][1:-1].split(",")
            for i in range(len(already_selected_user_query)):
                already_selected_user_query[i] = already_selected_user_query[i][1:-1]

            new_conv_id = chatbot_request.conversation_id

    else:
        already_selected_collabs = []
        already_selected_user_query = []
        # on va definir un conv_id aleatoire
        new_conv_id = conv.define_random_conv_id()

    #conv_id defined, place it in the response
    chatbot_response.conversation_id = new_conv_id
    # Structure Query using IntentionFinderSettings
    intention_finder = IntentionFinder()
    guess_intention_query = intention_finder.guess_intention(chatbot_request.user_query)
    logging.info(f"IntentionFinder: {time.time() - t}")

    # Fetch data from postgres
    if chatbot_request.assigned_until is None :
        chatbot_request.assigned_until = guess_intention_query[QueryStruct.start_date].min()[0]
    if chatbot_request.region is None :
        chatbot_request.region = guess_intention_query[QueryStruct.region].min()
    if chatbot_request.city is None :
        chatbot_request.city = guess_intention_query[QueryStruct.city].min()
    if chatbot_request.bu is None :
        chatbot_request.bu = guess_intention_query[QueryStruct.bu].min()
    if chatbot_request.bu_secondary is None :
        chatbot_request.bu_secondary = guess_intention_query[QueryStruct.bu_secondary].min()
    fetcher = PGfetcher()
    df_chunks, df_collabs, df_cvs, df_profiles = fetcher.fetch_all(
        filters=chatbot_request,
    )
    logging.info(f"PGfetcher: {time.time() - t}")

    t = time.time()
    # Select best candidates
    selector = CandidatesSelector()
    # il faut modifier select candidates pour retirer ceux déjà listés

    chunks, collabs, cvs, profiles = selector.select_candidates(
        df_chunks,
        df_collabs,
        df_cvs,
        df_profiles,
        guess_intention_query,
        already_selected_collabs
    )
    logging.info(f"CandidatesSelector: {time.time() - t}")
    # vérification a ce moment de already selected collab

    t = time.time()
    chatbot = Chatbot()
    profiles_data = collabs.merge(profiles, on="collab_id")
    profiles_data = chatbot.add_candidates_description(profiles_data,
                                                        guess_intention_query,
                                                        chunks).sort_values(
                                                            by="overall_score",
                                                            ascending=False
                                                        )
    if not isinstance(already_selected_collabs, list):
        already_selected_collabs = [already_selected_collabs]
    if not isinstance(already_selected_user_query, list):
        already_selected_user_query = [already_selected_user_query]
    concat_user_query = already_selected_user_query + [chatbot_request.user_query]
    # now insert or update the conversation table with the already_selected_collabs
    timezone = pytz.timezone("UTC")
    new_conv = [
        int(new_conv_id),
        already_selected_collabs,
        concat_user_query,
        datetime.datetime.now(timezone)
    ]

    # nouvelle tentative

    new_data = pd.DataFrame(new_conv,
                            ["conversation_id","collabs_ids","requests_content","date_conv"]).T
    new_data["date_conv"] = pd.to_datetime(new_data["date_conv"])
    cond_conv = (len(db_conv) > 0) and (new_data["conversation_id"]
                                        .isin(db_conv["conversation_id"]).all())
    db_conv.set_index("conversation_id", inplace=True)
    new_data.set_index("conversation_id", inplace=True)
    if cond_conv:
        db_conv.update(new_data)
        result = db_conv.reset_index()
    elif len(db_conv) > 0:
        result = new_data.combine_first(db_conv).reset_index()
    else:
        result = new_data.reset_index()

    result.to_sql(Conversations.__tablename__, con_string, if_exists="replace", index=False)
    logging.info(f"profiles_data: {time.time() - t}")

    t = time.time()
    chatbot_response.candidates = df_to_candidate_schema(
        profiles_data,
        cvs
    )
    logging.info(f"Make candidates: {time.time() - t}")


    t = time.time()
    # Send candidates data to chatbot and get a short answer
    response = chatbot.get_chatbot_response(
        profiles_data,
        guess_intention_query,
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
