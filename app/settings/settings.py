"""Settings script. Every settings is called from here."""
import logging
import os

import openai
from dotenv import load_dotenv

from app.exceptions.exceptions import SettingsError
from app.settings.load_llm_settings import load_llm_settings


# =============================================================================
# subclasses
# =============================================================================
class ETLSettings:
    """ETL settings."""

    def __init__(self) -> None:
        pass

    @property
    def ETL_query_template(self) -> str:  # noqa: N802
        """Query template for the ETL."""
        return os.environ.get("ETL__QUERY_TEMPLATE")

    @property
    def ETL_system_template(self) -> str:  # noqa: N802
        """System template for the ETL."""
        return os.environ.get("ETL__SYSTEM_TEMPLATE")

    @property
    def ETL_llm_model(self) -> str:  # noqa: N802
        """LLM model for the ETL."""
        return os.environ.get("ETL__LLM_MODEL")


class ChatbotUiSettings:
    """Chatbot UI settings."""

    def __init__(self) -> None:
        pass

    @property
    def logo_talan_path(self) -> str:
        """Logo path for Talan."""
        return os.environ.get("CHATBOTUI__UI_LOGO_TALAN")

    @property
    def logo_chatbot_path(self) -> str:
        """Logo path for the chatbot."""
        return os.environ.get("CHATBOTUI__UI_LOGO_CHATBOT")

    @property
    def dataviz_system_template(self) -> str:
        """System template for the chatbot."""
        return os.environ.get("CHATBOTUI__SYSTEM_TEMPLATE")

    @property
    def dataviz_LLM_model(self) -> str:  # noqa: N802
        """LLM model for the chatbot."""
        return os.environ.get("CHATBOTUI__LLM_MODEL")


class ChatbotSettings:
    """Chatbot settings."""

    def __init__(self) -> None:
        pass

    @property
    def chatbot_query_template(self) -> str:
        """Query template for the chatbot."""
        return os.environ.get("CHATBOT__QUERY_TEMPLATE")

    @property
    def chatbot_system_template(self) -> str:
        """System template for the chatbot."""
        return os.environ.get("CHATBOT__SYSTEM_TEMPLATE")

    @property
    def chatbot_context_template(self) -> str:
        """Context template for the chatbot."""
        return os.environ.get("CHATBOT__CONTEXT_TEMPLATE")

    @property
    def chatbot_LLM_model(self) -> str:  # noqa: N802
        """LLM model for the chatbot."""
        return os.environ.get("CHATBOT__LLM_MODEL")


class IntentionFinderSettings:
    """Intention finder settings."""

    def __init__(self) -> None:
        pass

    @property
    def guess_intention_query_template(self) -> str:
        """Query template for the guess intention module."""
        return os.environ.get("INTENTIONFINDER__GUESS_INTENTION_QUERY_EXAMPLES")

    @property
    def guess_intention_system_template(self) -> str:
        """Template for the guess intention module."""
        return os.environ.get("INTENTIONFINDER__GUESS_INTENTION_SYSTEM_TEMPLATE")

    @property
    def roleseeker_template(self) -> str:
        """Template for the role seeker module."""
        return os.environ.get("INTENTIONFINDER__ROLESEEKER_SYSTEM_TEMPLATE")

    @property
    def roleseeker_query_template(self) -> str:
        """Query template for the role seeker module."""
        return os.environ.get("INTENTIONFINDER__ROLESEEKER_QUERY_EXAMPLES")

    @property
    def guess_intention_llm_model(self) -> str:
        """LLM model for the guess intention module."""
        model_name = os.environ.get("INTENTIONFINDER__LLM_MODEL")
        model_version = os.environ.get("INTENTIONFINDER__LLM_VERSION")
        return f"models:/{model_name}/{model_version}"

class AzureMlSettings:
    """Azure Ml settings."""

    def __init__(self) -> None:
        pass

    @property
    def subscription_id(self) -> str:
        """Azure ml subscription id."""
        return os.environ.get("AZURE_ML__SUBSCRIPTION_ID")

    @property
    def resource_group_name(self) -> str:
        """Azure ml resource group."""
        return os.environ.get("AZURE_ML__RESOURCE_GROUP_NAME")

    @property
    def workspace_name(self) -> str:
        """Azure ml workspace name."""
        return os.environ.get("AZURE_ML__WORKSPACE_NAME")

class AzureStorageSettings:
    """Azure storage settings."""

    def __init__(self) -> None:
        pass

    @property
    def connection_string(self) -> str:
        """Azure storage connection string."""
        return os.environ.get("AZURE_STORAGE__CONNECTION_STRING")

    @property
    def container_name(self) -> str:
        """Azure storage container name."""
        return os.environ.get("AZURE_STORAGE__CONTAINER_NAME")


class OpenAISettings:
    """OpenAI settings."""

    def __init__(self) -> None:
        pass

    @property
    def API_key(self) -> str:  # noqa: N802
        """API key: see LLM API provider website."""
        return os.environ.get("OPENAI__API_KEY")

    @property
    def API_base(self) -> str:  # noqa: N802
        """API base: see LLM API provider website."""
        return os.environ.get("OPENAI__API_BASE")

    @property
    def API_version(self) -> str:  # noqa: N802
        """API version: see LLM API provider website."""
        return os.environ.get("OPENAI__API_VERSION")

    @property
    def API_type(self) -> str:  # noqa: N802
        """API type: 'azure' or 'openai'."""
        return os.environ.get("OPENAI__API_TYPE")


class DbSettings:
    """Database variables."""

    @property
    def name(self) -> str:  # noqa: N802
        """database name"""
        return os.environ.get("DB__NAME")

    @property
    def username(self) -> str:  # noqa: N802
        """database username"""
        return os.environ.get("DB__USER_NAME")

    @property
    def pwd(self) -> str:  # noqa: N802
        """database password
        make sure to encode the password"""
        return os.environ.get("DB__PWD")

    @property
    def host(self) -> str:  # noqa: N802
        """database host url"""
        return os.environ.get("DB__HOST")

    @property
    def port(self) -> str:  # noqa: N802
        """database port"""
        return os.environ.get("DB__PORT")

    @staticmethod
    def validate() -> None:
        if (DbSettings.name is None or DbSettings.username is None
                or DbSettings.pwd is None or DbSettings.host is None
                or DbSettings.port is None):
            logging.error("Missing Variables")
            raise SettingsError

class EmbedderSettings:
    """Embedder settings."""

    def __init__(self) -> None:
        pass

    @property
    def embedder_model(self) -> str:
        """Embedder model name."""
        return os.environ.get("EMBEDDER__EMBEDDER_MODEL")

    @property
    def encoding_name(self) -> str:
        """Encoding type name for the embedder.
        This is linked to the embedder you wish to use.
        """
        return os.environ.get("EMBEDDER__ENCODING_NAME")


class QueryRouterSettings:
    """Query router settings."""

    def __init__(self) -> None:
        pass

    @property
    def query_router_query_template(self) -> str:
        """Query template for the query router."""
        return os.environ.get("QUERY_ROUTER__QUERY_TEMPLATE")

    @property
    def query_router_system_template(self) -> str:
        """System template for the query router."""
        return os.environ.get("QUERY_ROUTER__SYSTEM_TEMPLATE")

    @property
    def query_router_llm_model(self) -> str:
        """LLM model for the query router."""
        return os.environ.get("QUERY_ROUTER__LLM_MODEL")


# =============================================================================
# Every call to properties, config and settings start from here
# =============================================================================
class Settings:
    """Application settings.
    Call every setting from here.
    """

    def __init__(self) -> None:
        # load .env (for local secrets only, connection strings, db passwords etc.)
        load_dotenv()
        # load .yaml llm settings and push to env variables
        load_llm_settings()

        # openAI keys must be set to these environment variables
        # (that's how Azure API works...)
        # openAI API variable must ALSO be set.
        os.environ["OPENAI_API_KEY"] = os.environ.get("OPENAI__API_KEY")
        os.environ["OPENAI_API_BASE"] = os.environ.get("OPENAI__API_BASE")
        os.environ["OPENAI_API_VERSION"] = os.environ.get("OPENAI__API_VERSION")
        os.environ["OPENAI_API_TYPE"] = os.environ.get("OPENAI__API_TYPE")
        openai.api_key = os.environ["OPENAI_API_KEY"]
        openai.api_base = os.environ["OPENAI_API_BASE"]
        openai.api_version = os.environ["OPENAI_API_VERSION"]
        openai.api_type = os.environ["OPENAI_API_TYPE"]

    @property
    def azure_ml(self) -> AzureMlSettings:
        """Azure machine learning settings."""
        return AzureMlSettings()

    @property
    def azure_storage(self) -> AzureStorageSettings:
        """Azure storage settings."""
        return AzureStorageSettings()

    @property
    def openai(self) -> OpenAISettings:
        """OpenAI settings."""
        return OpenAISettings()

    @property
    def chatbot_settings(self) -> ChatbotSettings:
        """Chatbot settings."""
        return ChatbotSettings()

    @property
    def guess_intention_settings(self) -> IntentionFinderSettings:
        """Intention finder settings."""
        return IntentionFinderSettings()

    @property
    def chatbot_ui_settings(self) -> ChatbotUiSettings:
        """Chatbot UI settings."""
        return ChatbotUiSettings()

    @property
    def ETL_settings(self) -> ETLSettings:  # noqa: N802
        """ETL settings."""
        return ETLSettings()

    @property
    def embedder_settings(self) -> EmbedderSettings:
        """Embedder settings."""
        return EmbedderSettings()

    @property
    def query_router_settings(self) -> QueryRouterSettings:
        """Query router settings."""
        return QueryRouterSettings()

    @property
    def db_settings(self) -> DbSettings:
        """Database settings."""
        return DbSettings()

    def validate(self) -> None:
        self.db_settings.validate()
