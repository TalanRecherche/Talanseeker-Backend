from collections.abc import Callable

from app.models.chatbot_logger import ChatbotLogs
from app.models.logger import Logs


def db_logger(func: Callable) -> Callable:
    def wrapper(*args, **kwargs) -> Callable:
        log = Logs()
        log.request_args = str(args)
        log.request_kwargs = str(kwargs)
        log.request_issuer = "test"
        log.request_func = func.__qualname__
        log.log()
        return func(*args, **kwargs)

    return wrapper


def chatbot_logger(func: Callable) -> Callable:
    def wrapper(*args, **kwargs) -> Callable:
        log = ChatbotLogs()
        response, candidates = func(*args, **kwargs)
        log.query = args[1]  # args[1] is the user query
        log.response = response
        if candidates is not None:
            log.candidates = "|".join(
                [
                    f"{candidate.name} {candidate.surname}"
                    for candidate in candidates.list_candidates
                ],
            )

        # insert the log
        return response

    return wrapper
