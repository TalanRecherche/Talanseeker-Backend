"""Created by agarc at 11/10/2023
Features:
"""
from app.core.shared_modules.gpt_backend import GptBackend
from app.core.shared_modules.stringhandler import StringHandler
from app.settings import Settings


class QueryRouter:
    def __init__(self, settings: Settings) -> None:
        # engine
        self.engine = settings.query_router_settings.query_router_llm_model
        # get query and system template

        self.system_string = settings.query_router_settings.query_router_system_template
        self.query_string = settings.query_router_settings.query_router_query_template

        # set tokens memory of the engine
        max_tokens_in_response = 1  # only one token is needed here ! "oui/non"
        max_tokens = 2000
        buffer_tokens = 500
        # rest of available tokens
        self.max_token_context = max_tokens - max_tokens_in_response - buffer_tokens
        # initialize the number of token in context
        self.current_nb_tokens = 0

        # initialize the backend llm
        self.llm_backend = GptBackend(
            self.engine,
            max_token_in_response=max_tokens_in_response,
        )

        # encoding name is used to compute number of tokens in context
        self.encoding_name = settings.embedder_settings.encoding_name

        # string matching variables
        self.threshold = 0.9
        self.target_strings = ["oui", "non"]

    #####################################################
    #   ## user functions
    #####################################################

    def get_router_response(self, user_query: str) -> bool:
        """This function sends the user_query to the llm.
        If the LLM answers yes no no, or something close (fuzzy matching) -> we return
        a bool
        Else, the query is resent to the llm with the added mention that the format was
        not correct.

        output: bool
            True : the query is a staffing question
            False: the query is outside the scope of staffing
        """
        query_string = self._make_query_string(user_query)
        system_string = self._make_system_string()
        # get first response from the chatbot
        llm_response = self._get_llm_response(query_string, system_string)
        # check if the llm response is satisfactory
        llm_good_response = self._check_llm_response(llm_response)

        # if the response is satisfactory, we send back its results
        if llm_good_response:
            is_good_query = self._parse_llm_response(llm_response)
            return is_good_query
        # if the response is not satisfactory we try another time.
        else:
            print("query needs correcting")
            # the new query will include the mention that the chatbot made an error
            new_query_string = self._make_newquery_string(user_query, llm_response)
            # get a new response from the chatbot
            llm_response = self._get_llm_response(new_query_string, system_string)
            # check if the llm response is satisfactory
            llm_good_response = self._check_llm_response(llm_response)
            if llm_good_response:
                is_good_query = self._parse_llm_response(llm_response)
            else:
                is_good_query = False

        return is_good_query

    #####################################################
    #   ## internal functions
    #####################################################
    def _parse_llm_response(self, llm_response: str) -> bool:
        # normalize string
        llm_response = StringHandler.normalize_string(
            llm_response,
            remove_special_chars=True,
        )

        # check if the answer is yes
        if llm_response == self.target_strings[0]:
            return True

        # check if the answer is close to yes
        if StringHandler.check_similarity_string(
            llm_response,
            self.target_strings[0],
            self.threshold,
        ):
            return True

        # return False is llm_response is far from yes
        return False

    def _check_llm_response(self, llm_response: str) -> bool:
        # normalize string
        llm_response = StringHandler.normalize_string(
            llm_response,
            remove_special_chars=True,
        )

        # check if string is empty
        if len(llm_response) == 0:
            return False

        # check if the string is no too long. We add 2 to allow for error
        if len(llm_response) > max([len(string) for string in self.target_strings]) + 2:
            return False

        # check if string is any targets
        if llm_response in self.target_strings:
            return True

        # check if string is close to any targets
        for target in self.target_strings:
            if StringHandler.check_similarity_string(
                llm_response,
                target,
                self.threshold,
            ):
                return True

        # we return False if no condition is met
        return False

    def _make_system_string(self) -> str:
        system_string = self.system_string
        return system_string

    def _make_query_string(self, user_query: str) -> str:
        query_string = self.query_string.format(query=user_query)
        return query_string

    def _make_newquery_string(self, user_query: str, llm_response: str) -> str:
        # second attempt with new query
        newquery_query_string = self.query_string + llm_response + "\n\n"
        newquery_query_string += (
            "**Votre réponse n'est pas au bon format. Répondez par oui ou non.**\n"
        )
        newquery_query_string += "Utilisateur: {query_2}\n"
        newquery_query_string += "Agent: "
        newquery_query_string = newquery_query_string.format(
            query=user_query,
            query_2=user_query,
        )
        return newquery_query_string

    def _get_llm_response(self, query_string: str, system_string: str) -> str:
        response = self.llm_backend.send_receive_message(query_string, system_string)
        return response


if __name__ == "__main__":
    import json

    def load_queries_from_json(json_file: json) -> dict:
        with open(json_file, encoding="utf-8") as file:
            data = json.load(file)

        queries = {}
        for entry in data["questions"]:
            queries[entry["query"]] = entry["label"]

        return queries

    queries = load_queries_from_json("tests/data_test/queryrouter_json/testset.JSON")

    settings = Settings()
    router = QueryRouter(settings)

    for query, label in queries.items():
        response = router.get_router_response(query)
        print("---")
        print(query)
        print("réponse:", response, "label:", label)
