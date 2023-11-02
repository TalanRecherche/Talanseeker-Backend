from fastapi import Depends
from app.models import get_db
from sqlalchemy.orm import Session
from app.models.user import User
from fastapi import APIRouter
from app.schema.chatbot import ChatbotResponse, ChatbotRequest

router = APIRouter(prefix="/chatbot")

@router.get("")
def chatbot(chatbot_request : ChatbotResponse,db: Session = Depends(get_db)):
    print(chatbot_request)
    return chatbot_request

