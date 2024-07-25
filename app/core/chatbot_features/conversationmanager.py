import pandas as pd
from sqlalchemy import select

from app.core.azure_modules import azure_pg_manager
from app.models import con_string
from app.models.conversations import Conversations
from app.schema.chatbot import (
    ChatbotRequest,
)


class ConversationManager:
    def __init__(
        self,
        chatbotrequest:ChatbotRequest,
    ) -> None:

        return None

    @staticmethod
    def check_conversation_exist(conversation_id: str) -> bool:
        return azure_pg_manager.check_existence_conv(
            Conversations.__tablename__,
            conversation_id)

    @staticmethod
    def get_conversation(conversation_id: str)-> bool:
        return azure_pg_manager.get_conv(
            Conversations.__tablename__,
            conversation_id)

    @staticmethod
    def get_all_database()-> None:
        return azure_pg_manager.select_all_conv()

    @staticmethod
    def get_empty_database_conv()-> bool:
        req = (select(Conversations))

        return len(pd.read_sql(req, con_string)) == 0


