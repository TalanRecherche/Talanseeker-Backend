"""This module is used to process the user query
and extract the intention of the user.
"""
import logging

import pandas as pd
from langchain.llms import AzureOpenAI

from app.core.models.query_pandasmodels import QueryStruct
from app.core.shared_modules.stringhandler import StringHandler
from app.settings import Settings


class IntentionFinder:
    """Class used to process the user query and extract the intention of the user. It
    uses prompt engineering to call the llm and extract the information from the output.

    Requires:
        - GUESSINTENTION__QUERY_EXAMPLES_PATH environment variable to be set to the
        path of the
            file containing the query examples. Set it in .env file.
        - GUESSINTENTION__SYSTEM_TEMPLATE_PATH environment variable to be set to the
        path of the file containing the system template. Set it in .env file.
        - GUESSINTENTION__LLM_DEPLOY_NAME environment variable to be set to the name
        of the deployment of the llm in azure resource. Set it in .env file.
        - Import the Settings class from app.settings.py which contains the settings of
        guessintention.

    Example:
    -------
        #>>> from app.settings import Settings
        #>>> from chatbot_app.core.guessintention import IntentionFinderSettings
        #>>> intention_finder = IntentionFinderSettings(Settings())
        #>>> query = "Trouve moi une équipe de développeurs pour une mission banque"
        #>>> res_to_send_to_cvranker = intention_finder(query)
        #>>> print(res_to_send_to_cvranker)
        #>>> res_to_send_to_cvranker.to_csv("test_guessintention1.csv", index=None)
    """

    def __init__(self, settings: Settings) -> None:
        """Initializes the class.

        Args:
        ----
            settings (Settings): Settings object containing the settings of the project.
        """
        self.settings = settings
        llm_model = self.settings.guess_intention_settings.guess_intention_llm_model
        self.llm = AzureOpenAI(deployment_name=llm_model, temperature=0)

        self.query_samples = (
            self.settings.guess_intention_settings.guess_intention_query_template
        )
        self.system_template = (
            self.settings.guess_intention_settings.guess_intention_system_template
        )
        self.roleseeker_system_template = (
            self.settings.guess_intention_settings.roleseeker_template
        )
        self.roleseeker_query_samples = (
            self.settings.guess_intention_settings.roleseeker_query_template
        )

    def guess_intention(
        self, user_query: str, _format: str = "dataframe"
    ) -> pd.DataFrame:
        """Process the user query and extract the intention of the user.

        Args:
        ----
            user_query (str): User query.
            _format (str, optional): The format preferred for the output. Defaults to
            'dataframe'.

        Returns:
        -------
            format: Result of the process in the format specified. Defaults to
            'dataframe'.
        """
        # prepare prompt for roleseeker llm
        role_seeker_template = self._prepare_roleseeker_template(user_query)
        # calling roleseeker llm with prompt
        output_roleseeker_llm = self.llm(role_seeker_template)
        # process output of roleseeker llm
        roles_dict = self._process_roleseeker_answer(output_roleseeker_llm)
        # extract infos with llm for each role
        res = self._extract_infos_per_role(user_query, _format, roles_dict)
        return res

    def _prepare_roleseeker_template(self, uquery: str) -> str:
        """Prepares the complete prompt to call the llm for the roleseeker.

        Args:
        ----
            uquery (str): User query.

        Returns:
        -------
            str: Complete prompt to use to call the llm.
        """
        uquery_template = self.roleseeker_system_template.replace(
            "{exemples}",
            self.roleseeker_query_samples,
        ).replace("{query}", uquery)
        return uquery_template

    def _process_roleseeker_answer(self, output_llm: str) -> dict:
        """Process the output of the roleseeker llm and extract the
            roles and number of required collabs per role.

        Example:
        -------
             output_llm = "roles : développeur, manager\n\n
             nombre : 4, 1"
             ans = _process_roleseeker_answer(output_llm)
             print(ans)
            {'roles': ['développeur', 'manager'], 'nb_profiles': ['4', '1']}

        Args:
        ----
            output_llm (str): Output of the llm.

        Returns:
        -------
            dict: Result of the process in a dictionary.
        """
        ans = {}
        ans[QueryStruct.roles] = StringHandler.string_to_list_with_separator(
            self._extract_text_from_llmoutput(output_llm, "roles"),
            separator=",",
        )
        ans[QueryStruct.nb_profiles] = StringHandler.string_to_list_with_separator(
            self._extract_text_from_llmoutput(output_llm, "nombre"),
            separator=",",
        )

        if len(ans[QueryStruct.roles]) != len(ans[QueryStruct.nb_profiles]):
            if len(ans[QueryStruct.roles]) > len(ans[QueryStruct.nb_profiles]):
                while len(ans[QueryStruct.roles]) > len(ans[QueryStruct.nb_profiles]):
                    ans[QueryStruct.nb_profiles].append("Non renseigné")
            else:
                while len(ans[QueryStruct.roles]) < len(ans[QueryStruct.nb_profiles]):
                    ans[QueryStruct.roles].append("Non renseigné")
        assert len(ans[QueryStruct.roles]) == len(ans[QueryStruct.nb_profiles]), (
            f"roles and nb_profiles have different lengths: \n"
            f"{ans[QueryStruct.roles]} and {ans[QueryStruct.nb_profiles]}"
        )
        return ans

    def _extract_infos_per_role(
        self, user_query: str, _format: str, roles: dict
    ) -> pd.DataFrame:
        """Extracts the information for each role.

        Args:
        ----
            user_query (str): User query.
            _format (str): The format preferred for the output.
            roles (dict): Dictionary containing the roles and number
                of required colabs per role.

        Raises:
        ------
            NotImplementedError: If the format specified is not implemented.
                Defaults to 'dataframe'.

        Returns:
        -------
            _format: Result of the process in the format specified.
        """
        res = []
        for role, n_role in zip(
            roles[QueryStruct.roles],
            roles[QueryStruct.nb_profiles],
        ):
            # prepare prompt for llm
            uquery_template = self._prepare_template(user_query, role)
            # calling llm with prompt
            output_llm = self.llm(uquery_template)
            # process output of llm
            ans = self._process_answer(output_llm, user_query, role, n_role)
            # prepare output and return it
            res.append(self._prepare_output(ans, _format))
        if _format == "dataframe":
            out = pd.concat(res)
        else:
            err = f"format {_format} not implemented. Use dataframe."
            raise NotImplementedError(err)
        return out

    def _extract_text_from_llmoutput(self, output_llm: str, field: str) -> str:
        """Extracts the value associated to the field to extract from the output of
        the llm.

        Example:
        -------
            output_llm = "simplified_query : Trouve moi une équipe de développeurs \
                pour une mission banque"
            field = "simplified_query"
            extracted_value = _extract_text_from_llmoutput(output_llm, field)
            print(extracted_value)
            Trouve moi une équipe de développeurs pour une mission banque

        Args:
        ----
            output_llm (str): Output of the llm.
            field (str): Field to extract inside the output of the llm.

        Returns:
        -------
            str: Text extracted from the output of the llm.
        """
        try:
            res = output_llm.split(f"{field}")[-1].split("\n")[0].split(":")[-1].strip()
        except IndexError as exc:
            logging.error(
                "llm output not as expected: %s.\n%s(field: %s)\n%s",
                output_llm,
                exc,
                field,
                output_llm.split(f"{field} : "),
            )
            res = "Non renseigné"
        return res

    # envoyer dans staticModules ListHandler
    def _wrap_txt_with_list(self, text: str) -> list[str]:
        """Wraps a text with a list.

        Args:
        ----
            text (str): Text to wrap.

        Returns:
        -------
            list[str]: List containing the text.
        """
        return [text]

    def _prepare_template(self, uquery: str, role: str) -> str:
        """Prepares the complete prompt to call the llm.
        To apply prompt engineering, assemble here:
        - the prompt template
        - sample questions and expected answer formats
        - the user query

        Args:
        ----
            uquery (str): User query.

        Returns:
        -------
            str: Complete prompt to use to call the llm.
        """
        uquery_template = (
            self.system_template.replace("{exemples}", self.query_samples)
            .replace("{query}", uquery)
            .replace("{role}", role)
        )
        return uquery_template

    def _process_answer(
        self, output_llm: str, uquery: str, role: str, n_role: int
    ) -> dict:
        """Process the output of the llm and extract the intention of the user.

        Example:
        -------
            >>> uquery = "Trouve moi une équipe de développeurs pour une mission banque"
            >>> ans = self._process_answer(uquery)
            >>> print(ans)
            {'bu': 'Non renseigné',
            'company': 'Non renseigné',
            'diplomas_certifications': ['Non renseigné'],
            'duration_mission': 'Non renseigné',
            'mission': 'développement',
            'nb_profiles': '4',
            'roles': ['chef de projet', ' développeur'],
            'sectors': 'banque',
            'simplified_query': 'mission développement banque',
            'soft_skills': ['Non renseigné'],
            'start_mission': 'Non renseigné',
            'technical_skills': ['développement'],
            'user_query': 'Trouve moi une équipe de développeurs pour une mission
            banque',
            'years': ['Non renseigné']}

        Args:
        ----
            uquery (str): User query.

        Raises:
        ------
            ValueError: If the output of the llm is not as expected.

        Returns:
        -------
            dict: Result of the process in a dictionary.
        """
        ans = {}
        ans[QueryStruct.user_query] = self._wrap_txt_with_list(uquery)
        ans[QueryStruct.simplified_query] = self._wrap_txt_with_list(
            self._extract_text_from_llmoutput(output_llm, "simplified_mission"),
        )
        ans[QueryStruct.nb_profiles] = [n_role]
        ans[QueryStruct.years] = StringHandler.string_to_list_with_separator(
            self._extract_text_from_llmoutput(output_llm, "Années d'expérience"),
            separator=",",
        )
        ans[
            QueryStruct.diplomas_certifications
        ] = StringHandler.string_to_list_with_separator(
            self._extract_text_from_llmoutput(output_llm, "Certifications"),
            separator=";",
        )
        ans[QueryStruct.soft_skills] = StringHandler.string_to_list_with_separator(
            self._extract_text_from_llmoutput(output_llm, "Compétences non techniques"),
            separator=";",
        )
        ans[QueryStruct.technical_skills] = StringHandler.string_to_list_with_separator(
            self._extract_text_from_llmoutput(output_llm, "Compétences techniques"),
            separator=";",
        )
        ans[QueryStruct.roles] = [role]
        ans[QueryStruct.missions] = self._wrap_txt_with_list(
            self._extract_text_from_llmoutput(output_llm, "Objectif mission"),
        )
        ans[QueryStruct.sectors] = self._wrap_txt_with_list(
            self._extract_text_from_llmoutput(output_llm, "Secteurs d'activité"),
        )
        ans[QueryStruct.companies] = self._wrap_txt_with_list(
            self._extract_text_from_llmoutput(output_llm, "Compagnie"),
        )
        return ans

    def _prepare_output(self, output: dict, _format: str) -> pd.DataFrame:
        """Prepares the output of the process in the format specified.

        Args:
        ----
            output (dict): Result of the process in a dictionary.
            _format (str): The format preferred for the output.

        Raises:
        ------
            NotImplementedError: If the format specified is not implemented.

        Returns:
        -------
            specified format: Result of the process in the format specified. \
                Defaults to 'dataframe'.
        """
        if _format == "dataframe":
            output_prepared = pd.DataFrame.from_dict([output])
        else:
            err = f"format {_format} not implemented"
            raise NotImplementedError(err)
        return output_prepared


if __name__ == "__main__":
    settings = Settings()
    QUERY_EXAMPLE = "Trouve moi deux data scientists"
    intention_finder = IntentionFinder(settings)
    result = intention_finder.guess_intention(QUERY_EXAMPLE)
    print(result)  # noqa: T201
    QueryStruct.validate_dataframe(result)
    from app.core.shared_modules.dataframehandler import DataFrameHandler

    DataFrameHandler.save_df(result, "tests/data_testdf_struct_query.pkl")
