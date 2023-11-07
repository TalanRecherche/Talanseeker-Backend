from fastapi import APIRouter
router = APIRouter(prefix="/api/v1")

from .user.endpoints import router as user_router
from .chatbot.endpoints import router as chatbot_router
from .search.endpoints import router as search_router

router.include_router(user_router)
router.include_router(chatbot_router)
router.include_router(search_router)

