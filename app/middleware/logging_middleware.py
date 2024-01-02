from collections.abc import Callable
from json import loads as json_loader

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import StreamingResponse
from starlette.types import ASGIApp

from app.models.chatbot_logger import ChatbotLogs
from app.models.logger import Logs


class LoggingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)

        self.general_logger(request, response)

        response_body = await self._build_request_body(response)

        if request.url.path == "/api/v1/chatbot":
            self.chatbot_logger(request, response_body)

        return Response(content=response_body, status_code=response.status_code,
                        headers=dict(response.headers), media_type=response.media_type)

    async def _build_request_body(self, response: StreamingResponse) -> str:
        response_body = b""
        async for chunk in response.body_iterator:
            response_body += chunk
        return response_body.decode()

    def chatbot_logger(self, request: Request, response: str) -> None:
        """
        log chatbot calls : request and reponse
        """
        logger = ChatbotLogs()
        logger.user_query = request.query_params.get(ChatbotLogs.user_query.key)
        logger.region = request.query_params.get(ChatbotLogs.region.key)
        logger.assigned_until = request.query_params.get(ChatbotLogs.assigned_until.key)
        logger.availability_score = (
            request.query_params.get(ChatbotLogs.availability_score.key))

        response = json_loader(response)

        logger.chatbot_response = response[ChatbotLogs.chatbot_response.key]
        logger.question_valid = response[ChatbotLogs.question_valid.key]
        logger.candidates = ",".join([elem["general_information"]["collab_id"] for
                                      elem in response[ChatbotLogs.candidates.key]])
        logger.log()

    def general_logger(self, request: Request, response: Response) -> None:
        """
        log all api calls with their status code
        """
        logger = Logs()
        logger.url_path = request.url.path
        logger.status_code = response.status_code
        logger.log()

    def cv_manager_logger(self, request: Request, response: str) -> None:
        pass
