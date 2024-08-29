import logging

import mlflow
from azure.ai.ml import MLClient
from azure.identity import EnvironmentCredential

from app.settings import settings


class AzureMLManager:

    def __init__(self) -> None:
        self.subscription_id = settings.azure_ml.subscription_id
        self.resource_group_name = settings.azure_ml.resource_group_name
        self.workspace_name = settings.azure_ml.workspace_name

        try:
            credential = EnvironmentCredential() #EnvironmentCredential()
        except Exception as ex:
            logging.exception("Azure credential exception %s", ex)

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

    def load_model(self, model_uri: str) -> mlflow.pyfunc.model:
        return mlflow.pyfunc.load_model(model_uri)