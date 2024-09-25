from fastapi import APIRouter, Response

from app.schema.feedback import FeedbackRequest

from .business import FeedbackBusiness

business = FeedbackBusiness()
router = APIRouter(prefix="/feedback")


@router.post("")
def post_feedback(request: FeedbackRequest) -> Response:
    response = business.add_feedback(request)
    return response


@router.patch("")
def patch_feedback(request: FeedbackRequest) -> Response:
    response = business.patch_feedback(request)
    return response
