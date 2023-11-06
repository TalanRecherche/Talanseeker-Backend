from fastapi import APIRouter
from app.schema.chatbot import ChatbotRequest, ChatbotResponse
from .business import chatbot_business

router = APIRouter(prefix="/chatbot")

@router.get("")
def chatbot(chatbot_request : ChatbotRequest)->ChatbotResponse:
    response = chatbot_business(chatbot_request)
    return response

