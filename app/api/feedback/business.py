from fastapi.responses import JSONResponse

from app.models.feedback import FeedbacksModel
from app.schema.feedback import FeedbackRequest


class FeedbackBusiness:
    @staticmethod
    def add_feedback(request=FeedbackRequest):
        feedback = FeedbacksModel(
            query_id=request.query_id,
            collab_id=request.collab_id,
            evaluation=request.feedback,
            user_id=request.user_id,
        )
        feedback.add()
        return JSONResponse(status_code=200, content="Success")

    @staticmethod
    def patch_feedback(request=FeedbackRequest):
        feedback = FeedbacksModel(
            query_id=request.query_id,
            collab_id=request.collab_id,
            evaluation=request.feedback,
            user_id=request.user_id,
        )
        feedback.patch()
        return JSONResponse(status_code=200, content="Success")
