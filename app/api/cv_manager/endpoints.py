from fastapi import APIRouter, Depends, File, Response, UploadFile

from app.api.cv_manager.business import CVManagerBusiness
from app.schema.cv_manager import CVDownloadRequest, CVUploadRequest

router = APIRouter(prefix="/cv_manager")


@router.post("/upload")
def etl_process(
    request: CVUploadRequest = Depends(), file: UploadFile = File(...)
) -> dict:
    response = CVManagerBusiness.etl_business(request, file)
    return response


@router.get("/download")
def download(request: CVDownloadRequest = Depends()) -> Response:
    response = CVManagerBusiness.download_cv(request)
    return response
