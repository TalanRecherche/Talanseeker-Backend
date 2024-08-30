
import logging

from fastapi import APIRouter, Depends, Response

from app.schema.chatbot import ChatbotRequest, ChatbotResponse

from .business import chatbot_business, profile_chatbot_business

router = APIRouter(prefix="/chatbot")


@router.get("")
def chatbot(chatbot_request: ChatbotRequest = Depends()) -> ChatbotResponse:
    logging.info(chatbot_request.dict())
    return chatbot_business(chatbot_request)


@router.get("/profile")
def profile_chatbot(chatbot_request: ChatbotRequest = Depends()) -> Response:
    return profile_chatbot_business(chatbot_request)
