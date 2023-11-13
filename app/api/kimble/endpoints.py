from fastapi import UploadFile, File
from app.models.user import User
from fastapi import APIRouter
from .business import KimbleBusiness
router = APIRouter(prefix="/kimble")

@router.post("")
def process_kimble(file : UploadFile = File(...)):
    response = KimbleBusiness.start(file.file.read())
    return response


