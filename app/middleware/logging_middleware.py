from collections.abc import Callable
from json import loads as json_loader

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.models.chatbot_logger import ChatbotLogs


class LoggingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        response_body = b""
        async for chunk in response.body_iterator:
            response_body += chunk

        if request.url.path == "/api/v1/chatbot":
            await self.chatbot_logger(request, response_body)

        return Response(content=response_body, status_code=response.status_code,
                        headers=dict(response.headers), media_type=response.media_type)

    async def chatbot_logger(self, request: Request, response: bytes) -> None:

        logger = ChatbotLogs()
        logger.user_query = request.query_params.get(ChatbotLogs.user_query.key)
        logger.region = request.query_params.get(ChatbotLogs.region.key)
        logger.assigned_until = request.query_params.get(ChatbotLogs.assigned_until.key)
        logger.availability_score = (
            request.query_params.get(ChatbotLogs.availability_score.key))

        response = json_loader(response.decode())

        logger.chatbot_response = response[ChatbotLogs.chatbot_response.key]
        logger.question_valid = response[ChatbotLogs.question_valid.key]
        logger.candidates = str(response[ChatbotLogs.candidates.key])
        logger.log()
