from fastapi import APIRouter

from .chatbot.endpoints import router as chatbot_router
from .cv_manager.endpoints import router as cv_uploader_router
from .feedback.endpoints import router as feedback_router
from .kimble.endpoints import router as kimble_router
from .search.endpoints import router as search_router
from .user.endpoints import router as user_router

router = APIRouter(prefix="/api/v1")

router.include_router(user_router)
router.include_router(chatbot_router)
router.include_router(search_router)
router.include_router(cv_uploader_router)
router.include_router(kimble_router)
router.include_router(feedback_router)
