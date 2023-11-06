# -*- coding: utf-8 -*-
"""
Created on Mon Sep 18 11:00:43 2023

@author: agarc

"""

import openai
from langchain.embeddings.openai import OpenAIEmbeddings
import time
import logging


class EmbedderBackend:

    def __init__(self, settings):
        # embeddings setup
        self.embedding_model = settings.embedder_settings.embedder_model
        self.embedding_function = OpenAIEmbeddings(model=self.embedding_model, chunk_size=1)
        pass

    # =============================================================================
    # user function
    # =============================================================================
    def embed_string(self, text_to_embed: str) -> list[float] | None:
        if len(text_to_embed) == 0:
            logging.error("Query embeddings failed: empty query string")
            return None

        max_retries = 10
        for retry in range(max_retries):
            try:
                # pause for API safety
                time.sleep(0.1)
                response = openai.Embedding.create(engine=self.embedding_model, input=text_to_embed)

                embeddings = response['data'][0]['embedding']
                # exit the retry loop if the llm response is not None
                if embeddings is not None:
                    return embeddings

            except Exception as e:
                logging.exception(f"openAI embedding API failed. Waiting and retry: {retry} : Exception {e}")
                # wait before retrying
                time.sleep(1)

        logging.error("Embeddings backend failed")
        return None
