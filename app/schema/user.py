from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel


class UserCreate(BaseModel):
    pwd: str
    email: str
    authorizations: List[int]

class UserUpdate(BaseModel):
    pwd: Optional[str] = None
    email: str
    authorizations: Optional[List[int]] = None

class UserResponse(BaseModel):
    email: str
    authorizations: List[int]


