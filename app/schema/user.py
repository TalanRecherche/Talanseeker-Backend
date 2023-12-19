"""Created on 21/11/2023

@author: Youness

"""
from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class UserCreate(BaseModel):
    pwd: str
    email: str
    authorizations: list[int]


class UserUpdate(BaseModel):
    pwd: Optional[str] = None
    email: str
    authorizations: Optional[list[int]] = None


class UserResponse(BaseModel):
    email: str
    authorizations: list[int]
