# -*- coding: utf-8 -*-
"""
Created on Tue Aug 22 14:59:58 2023

@author: agarc

/!\ THIS TESTS CALLS THE OPENAI API AND WILL BE BILLED /!\
"""
import pytest
from app.core.shared_modules.GPTbackend import GPTBackend
from app.settings import Settings

settings = Settings()
LLM_MODEL = settings.chatbot_settings.chatbot_llm_model
query = "What is the capital of France?"
system_function = "Answer questions about capitals."


@pytest.mark.skip_this(reason="Skipping test from running because it is calling OpenAI-API")
def test_send_receive_message_response_type():
    llm_backend = GPTBackend(LLM_MODEL)

    response = llm_backend.send_receive_message(query, system_function)
    assert isinstance(response, str)


def test_make_payload_format():
    llm_backend = GPTBackend(LLM_MODEL)
    payload = llm_backend._make_payload(query, system_function)
    assert isinstance(payload, list)
    assert len(payload) == 2
    assert isinstance(payload[0], dict)
    assert isinstance(payload[1], dict)


def test_make_payload_content():
    llm_backend = GPTBackend(LLM_MODEL)
    payload = llm_backend._make_payload(query, system_function)
    assert payload[0]["role"] == "system"
    assert payload[1]["role"] == "user"
    assert payload[0]["content"] == system_function
    assert payload[1]["content"] == query


if __name__ == "__main__":
    pytest.main()
