from fastapi import APIRouter
from app.schema.feedback import FeedbackRequest
from .business import FeedbackBusiness
business = FeedbackBusiness()
router = APIRouter(prefix="/feedback")




@router.post("")
def chatbot(request : FeedbackRequest):
    response = business.add_feedback(request)
    return response

@router.patch("")
def chatbot(request : FeedbackRequest):
    response = business.patch_feedback(request)
    return response
