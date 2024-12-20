"""Created on 21/11/2023

@author: Youness

"""
from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel


class CVUploadRequest(BaseModel):
    f_name: str
    l_name: str
    mail: Optional[str] = None


class CVDownloadRequest(BaseModel):
    cv_id: str
    type: Optional[Literal["link", "file"]] = "link"


class CVDownloadResponse(BaseModel):
    link: str
