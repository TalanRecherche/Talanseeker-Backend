"""Created on 21/11/2023

@author: Youness

"""
from __future__ import annotations

from pydantic import BaseModel


class ErrorResponse(BaseModel):
    message: str
