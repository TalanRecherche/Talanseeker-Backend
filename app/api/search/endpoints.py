from fastapi import APIRouter

from .business import search_business
from ...schema.search import SearchRequest, SearchResponse

router = APIRouter(prefix="/search")


@router.get("")
def chatbot(request: SearchRequest) -> SearchResponse:
    response = search_business(request)
    return response
