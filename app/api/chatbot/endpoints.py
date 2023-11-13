from fastapi import APIRouter, Depends, Query
from typing import List, Optional

from app.schema.chatbot import ChatbotRequest, ChatbotResponse
from .business import chatbot_business

router = APIRouter(prefix="/chatbot")




@router.get("")
def chatbot(chatbot_request : ChatbotRequest =  Depends()) -> ChatbotResponse:
    response = chatbot_business(chatbot_request)
    return response
