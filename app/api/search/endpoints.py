from fastapi import APIRouter

from app.schema.search import SearchRequest, SearchResponse

from .business import search_business

router = APIRouter(prefix="/search")


@router.get("")
def chatbot(request: SearchRequest) -> SearchResponse:
    response = search_business(request)
    return response
