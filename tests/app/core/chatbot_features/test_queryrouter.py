"""Created by agarc at 11/10/2023
Features:
"""
import json

import pytest

from app.core.chatbot_features.queryrouter import QueryRouter
from app.settings.settings import Settings


@pytest.fixture(scope="module")
def setup_data():
    data_path = "tests/data_test/testset.JSON"
    with open(data_path, encoding="utf-8") as file:
        data = json.load(file)

    queries = {}
    for entry in data["questions"]:
        queries[entry["query"]] = entry["label"]

    return queries


@pytest.mark.skip_this(
    reason="Skipping test from running because it is calling OpenAI-API",
)
def test_queryrouter(setup_data):
    queries = setup_data

    settings = Settings()
    router = QueryRouter()

    for query, label in queries.items():
        response = router.get_router_response(query)
        assert response == label


if __name__ == "__main__":
    pytest.main()
