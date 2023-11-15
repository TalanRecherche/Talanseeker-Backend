# -*- coding: utf-8 -*-
"""
Created on Sun Sep 17 13:07:47 2023

@author: agarc
/!\ This test call the openAI API and will be billed /!\
"""
import pytest

from app.core.chatbot_features.intentionfinder import IntentionFinder
from app.core.models.query_pandasmodels import QUERY_STRUCT
from app.settings import Settings


@pytest.mark.skip_this(reason="Skipping test from running because it is calling OpenAI-API")
def test_01_structured_query_format():
    settings = Settings()
    user_query = "Trouve moi deux data scientists"
    intention_finder = IntentionFinder(settings)
    structured_query = intention_finder.guess_intention(user_query)

    assert QUERY_STRUCT.validate_dataframe(structured_query)



if __name__ == "__main__":
    pytest.main()
