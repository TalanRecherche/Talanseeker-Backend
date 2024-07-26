#!/usr/bin/env python3
from sqlalchemy import Column, String

from app.models import Base


class Conversations(Base):
    __tablename__ = "conversations"
    conversation_id = Column(String, primary_key=True)
    collabs_ids = Column(String)
    requests_content = Column(String)
    date_conv = Column(String)

    def __repr__(self) -> str:
        return f"{self.conversation_id} {self.collabs_ids} {self.requests_content}"
