from models.logger import Logs
from models.chatbot_logger import ChatbotLogs
import streamlit as st


def db_logger(func):
    def wrapper(*args, **kwargs):
        log = Logs()
        log.request_args = str(args)
        log.request_kwargs = str(kwargs)
        log.request_issuer = st.session_state['username'] if 'username' in st.session_state else None
        log.request_func = func.__qualname__
        log.log()
        return func(*args, **kwargs)

    return wrapper


def chatbot_logger(func):
    def wrapper(*args, **kwargs):
        log = ChatbotLogs()
        log.request_issuer = st.session_state['username'] if 'username' in st.session_state else None
        response, candidates = func(*args, **kwargs)
        log.query = args[1]  # args[1] is the user query
        log.response = response
        if candidates is not None:
            log.candidates = "|".join([f"{candidate.name} {candidate.surname}" for candidate in candidates.list_candidates])

        # insert the log
        st.session_state["query_id"] = log.log()
        return response

    return wrapper
