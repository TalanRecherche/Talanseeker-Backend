import logging

import mlflow
from azure.ai.ml import MLClient
from azure.identity import EnvironmentCredential
from azure.identity import DefaultAzureCredential, InteractiveBrowserCredential

from app.settings import settings


class AzureMLManager:

    def __init__(self) -> None:
        self.subscription_id = settings.azure_ml.subscription_id
        self.resource_group_name = settings.azure_ml.resource_group_name
        self.workspace_name = settings.azure_ml.workspace_name

    def load_model(self, model_uri: str) -> mlflow.pyfunc.model:
        try:
            credential = DefaultAzureCredential()
            # Check if given credential can get token successfully.
            credential.get_token("https://management.azure.com/.default")
        except Exception as ex:
            # Fall back to InteractiveBrowserCredential in case DefaultAzureCredential not work
            credential = InteractiveBrowserCredential()

        try:
            ml_client = MLClient(
                credential=credential,
                subscription_id=self.subscription_id,
                resource_group_name=self.resource_group_name,
                workspace_name=self.workspace_name
                )
        except Exception as ex:
            logging.exception("Azure ML exception %s", ex)

        mlflow_tracking_uri = ml_client.workspaces.get(ml_client.workspace_name).mlflow_tracking_uri
        mlflow.set_tracking_uri(mlflow_tracking_uri)

        return mlflow.pyfunc.load_model(model_uri)
