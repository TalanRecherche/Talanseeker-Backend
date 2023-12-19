"""Created on Tue Aug 22 14:59:58 2023

@author: agarc

"""
import logging
import time

import openai


class LlmBackend:
    """back end for simple queries with the llm. Use only: _send_receive_message"""

    def __init__(self, llm_model: str, max_token_in_response: int = 300) -> None:
        # get llm chatbot engine
        self.engine = llm_model

        self.max_tokens = max_token_in_response
        self.temperature = 0
        self.top_p = 0.95
        self.frequency_penalty = 0
        self.presence_penalty = 0
        self.stop = None
        self.request_timeout = 30

    # =============================================================================
    # user functions
    # =============================================================================
    def send_receive_message(self, query: str, system_function: str) -> str:
        """Send single message: set role system and append to payload"""
        # make payload
        payload = self._make_payload(query, system_function)
        # get llm response
        response_message = self._send_payload(payload)
        return response_message

    # =============================================================================
    # internal functions
    # =============================================================================

    def _make_payload(self, query: str, system_function: str) -> list[dict]:
        """Generate the payload list[hashmap] according to openAI format

        Parameters
        ----------
        query : str
            Your query.
        system_function : str
            System primer template.

        Returns
        -------
        payload : list[dict]

        Args:
            query:
            system_function:
        """
        payload = [
            {"role": "system", "content": system_function},
            {"role": "user", "content": query},
        ]
        return payload

    def _send_payload(self, payload: list[dict]) -> str:
        """Send payload via API .create() function
        Response is dictionary containing responses and prompt
        """
        is_to_do = True
        try_counter = 0
        response_string = ""

        while is_to_do is True and try_counter < 10:
            time.sleep(0.1)
            try:
                # get response
                response = openai.ChatCompletion.create(
                    engine=self.engine,
                    messages=payload,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                    top_p=self.top_p,
                    frequency_penalty=self.frequency_penalty,
                    presence_penalty=self.presence_penalty,
                    stop=self.stop,
                    request_timeout=self.request_timeout,
                )
                response_string = response["choices"][0]["message"]["content"]
                if response_string:
                    is_to_do = False
            except Exception as e:
                try_counter += 1
                logging.exception(e, try_counter)
                # wait before retrying
                time.sleep(1)
        return response_string
