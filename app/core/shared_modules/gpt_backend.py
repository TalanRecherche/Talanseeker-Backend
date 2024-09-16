import logging
import time

import openai

from app.core.shared_modules.abc_llm_backend import AbcLlmBackend


class GptBackend(AbcLlmBackend):
    """backend for simple queries with the llm. Use only: send_receive_message"""

    def __init__(
        self, llm_model: str = "gpt-35-turbo", max_token_in_response: int = 300
    ) -> None:
        if llm_model not in ["gpt-4", "gpt-4-32k", "gpt-35-turbo",
                              "gpt-35-turbo-instruct" , "gpt-4o-mini"]:
            error_message = "Invalid GPT llm_model"
            logging.error(error_message)
            raise ValueError(error_message)
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
        if not response_message:
            err = "API call failed after reaching the maximum number of retries."
            raise RuntimeError(err)
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
        logging.info("payload :", payload)
        response_string = ""
        max_retries = 5
        for retry in range(max_retries):
            try:
                # get response
                logging.info("self.engine :", self.engine)
                if self.engine == "gpt-35-turbo-instruct":
                    prompt = "\n".join([item["content"] for item in payload])
                    response = openai.Completion.create(
                        engine=self.engine,
                        prompt=prompt,
                        temperature=self.temperature,
                        max_tokens=self.max_tokens,
                        top_p=self.top_p,
                        frequency_penalty=self.frequency_penalty,
                        presence_penalty=self.presence_penalty,
                        stop=self.stop,
                        request_timeout=self.request_timeout,
                    )
                    response_string = response["choices"][0]["text"]
                else:
                    logging.info("here")
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
                    logging.info("response :", response)
                    response_string = response["choices"][0]["message"]["content"]

                # exit the retry loop if the llm response is not None
                if response_string:
                    break
                # pause for API safety
                time.sleep(0.1)

            except Exception as error:
                logging.error(f"Error on attempt {retry + 1}/{max_retries}: {error}")
                logging.error(f"Payload: {payload}")
                logging.exception(error)
                # wait before retrying
                time.sleep(0.1 * retry)

        if not response_string:
            logging.error("API call failed after reaching the maximum number of retries.")
        return response_string
