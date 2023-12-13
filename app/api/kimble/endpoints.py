from fastapi import APIRouter, File, Response, UploadFile

from .business import KimbleBusiness

router = APIRouter(prefix="/kimble")


@router.post("")
def process_kimble(file: UploadFile = File(...)) -> Response:
    response = KimbleBusiness.start(file.file.read())
    return response
