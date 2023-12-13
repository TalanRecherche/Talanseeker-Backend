"""Created by agarc at 01/10/2023
Features:
"""
import tiktoken


class TokenHandler:
    @staticmethod
    def count_tokens_from_string(
        string: str,
        encoding_name: str = "cl100k_base",
        engine: str = "gpt-35-turbo",
    ) -> int:
        # compute number of tokens tokens
        if not isinstance(string, str):
            return 0
        encoding = tiktoken.get_encoding(encoding_name)
        num_tokens = len(encoding.encode(string))

        return num_tokens

    @staticmethod
    def count_tokens_from_hashmap(
        hashmap: dict,
        encoding_name: str = "cl100k_base",
        engine: str = "gpt-35-turbo",
    ) -> int:
        curr_len = 0
        for key in hashmap:
            string = hashmap[key]
            curr_len += TokenHandler.count_tokens_from_string(
                string,
                encoding_name,
                engine,
            )
        return curr_len
