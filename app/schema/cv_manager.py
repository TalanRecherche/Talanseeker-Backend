from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel


class CVUploadRequest(BaseModel):
    f_name: str
    l_name: str


class CVDownloadRequest(BaseModel):
    cv_id: str
    type: Optional[Literal["link", "file"]] = "link"


class CVDownloadResponse(BaseModel):
    link: str
