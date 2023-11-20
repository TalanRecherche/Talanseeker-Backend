"""Created by agarc at 23/10/2023
Features:
"""

from abc import ABC, abstractmethod


class ABCLLMBackend(ABC):
    """Abstract class for backends."""

    @abstractmethod
    def send_receive_message(self, query: str, system_function: str) -> str:
        """Send a single message and receive a response.

        Args:
        ----
        query (str): The user query.
        system_function (str): The system primer template.

        Returns:
        -------
        str: The response message.

        Note:
        ----
        if the return string (llm_response) is == '' we raise an error
        >> if not response_message:
            raise RuntimeError("API call failed after reaching the maximum number of
            retries.")
        """
