import os
import openai
from dotenv import load_dotenv
from app.core.shared_modules.load_llm_settings import load_llm_settings


# =============================================================================
# Every call to properties, config and settings start from here
# =============================================================================
class Settings:

    def __init__(self):
        # load .env (for local secrets only, connection strings, db passwords etc.)
        load_dotenv()
        # load .yaml llm settings and push to env variables
        load_llm_settings()

        # openAI keys must be set to these environment variables (that's how Azure API works...)
        # openAI API variable must ALSO be set.
        os.environ['OPENAI_API_KEY'] = os.environ.get('OPENAI__API_KEY')
        os.environ['OPENAI_API_BASE'] = os.environ.get('OPENAI__API_BASE')
        os.environ['OPENAI_API_VERSION'] = os.environ.get('OPENAI__API_VERSION')
        os.environ['OPENAI_API_TYPE'] = os.environ.get('OPENAI__API_TYPE')
        openai.api_key = os.environ['OPENAI_API_KEY']
        openai.api_base = os.environ['OPENAI_API_BASE']
        openai.api_version = os.environ['OPENAI_API_VERSION']
        openai.api_type = os.environ['OPENAI_API_TYPE']

    @property
    def azure_storage(self):
        return AzureStorageSettings()

    @property
    def openai(self):
        return OpenAISettings()

    @property
    def chatbot_settings(self):
        return ChatbotSettings()

    @property
    def guess_intention_settings(self):
        return IntentionFinderSettings()

    @property
    def chatbot_ui_settings(self):
        return ChatbotUiSettings()

    @property
    def ETL_settings(self):
        return ETLSettings()

    @property
    def embedder_settings(self):
        return EmbedderSettings()

    @property
    def query_router_settings(self):
        return QueryRouterSettings()


# =============================================================================
# subclasses
# =============================================================================
class ETLSettings:
    def __init__(self):
        pass

    @property
    def ETL_query_template(self):
        return os.environ.get('ETL__QUERY_TEMPLATE')

    @property
    def ETL_system_template(self):
        return os.environ.get('ETL__SYSTEM_TEMPLATE')

    @property
    def ETL_llm_model(self):
        return os.environ.get('ETL__LLM_MODEL')


class ChatbotUiSettings:
    def __init__(self):
        pass

    @property
    def logo_talan_path(self):
        return os.environ.get('CHATBOTUI__UI_LOGO_TALAN')

    @property
    def logo_chatbot_path(self):
        return os.environ.get('CHATBOTUI__UI_LOGO_CHATBOT')

    @property
    def dataviz_system_template(self):
        return os.environ.get('CHATBOTUI__SYSTEM_TEMPLATE')

    @property
    def dataviz_llm_model(self):
        return os.environ.get('CHATBOTUI__LLM_MODEL')


class ChatbotSettings:
    def __init__(self):
        pass

    @property
    def chatbot_query_template(self):
        return os.environ.get('CHATBOT__QUERY_TEMPLATE')

    @property
    def chatbot_system_template(self):
        return os.environ.get('CHATBOT__SYSTEM_TEMPLATE')

    @property
    def chatbot_context_template(self):
        return os.environ.get('CHATBOT__CONTEXT_TEMPLATE')

    @property
    def chatbot_llm_model(self):
        return os.environ.get('CHATBOT__LLM_MODEL')


class IntentionFinderSettings:
    def __init__(self):
        pass

    @property
    def guess_intention_query_template(self):
        return os.environ.get('INTENTIONFINDER__GUESS_INTENTION_QUERY_EXAMPLES')

    @property
    def guess_intention_system_template(self):
        return os.environ.get('INTENTIONFINDER__GUESS_INTENTION_SYSTEM_TEMPLATE')

    @property
    def roleseeker_template(self):
        return os.environ.get('INTENTIONFINDER__ROLESEEKER_SYSTEM_TEMPLATE')

    @property
    def roleseeker_query_template(self):
        return os.environ.get('INTENTIONFINDER__ROLESEEKER_QUERY_EXAMPLES')

    @property
    def guess_intention_llm_model(self):
        return os.environ.get('INTENTIONFINDER__LLM_MODEL')


class AzureStorageSettings:
    def __init__(self):
        pass

    @property
    def connection_string(self):
        return os.environ.get('AZURE_STORAGE__CONNECTION_STRING')

    @property
    def container_name(self):
        return os.environ.get('AZURE_STORAGE__CONTAINER_NAME')


class OpenAISettings:
    def __init__(self):
        pass

    @property
    def api_key(self):
        return os.environ.get('OPENAI__API_KEY')

    @property
    def api_base(self):
        return os.environ.get('OPENAI__API_BASE')

    @property
    def api_version(self):
        return os.environ.get('OPENAI__API_VERSION')

    @property
    def api_type(self):
        return os.environ.get('OPENAI__API_TYPE')


class EmbedderSettings:
    def __init__(self):
        pass

    @property
    def embedder_model(self):
        return os.environ.get('EMBEDDER__EMBEDDER_MODEL')

    @property
    def encoding_name(self):
        return os.environ.get('EMBEDDER__ENCODING_NAME')


class QueryRouterSettings:
    def __init__(self):
        pass

    @property
    def query_router_query_template(self):
        return os.environ.get('QUERY_ROUTER__QUERY_TEMPLATE')

    @property
    def query_router_system_template(self):
        return os.environ.get('QUERY_ROUTER__SYSTEM_TEMPLATE')

    @property
    def query_router_llm_model(self):
        return os.environ.get('QUERY_ROUTER__LLM_MODEL')
