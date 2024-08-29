"""Created on 21/11/2023

@author: Youness

"""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel


class FeedbackRequest(BaseModel):
    query_id: str
    collab_id: str
    user_id: str
    feedback: Literal[-1, 1]
