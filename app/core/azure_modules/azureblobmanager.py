import logging

from azure.storage.blob import BlobServiceClient, ExponentialRetry

from app.exceptions.exceptions import BlobStorageError
from app.settings import settings


class AzureBlobManager:
    """manage files (upload, download, ...)"""

    def __init__(self) -> None:
        """Create initial connection"""
        self.container_client = None

    def connect_to_bloc(self) -> None:
        faster_retry = ExponentialRetry(initial_backoff=1, increment_base=1)

        blob_service_client = BlobServiceClient.from_connection_string(
            settings.azure_storage.connection_string, retry_policy=faster_retry
        )

        try:
            if len(list(blob_service_client.list_containers(
                    name_starts_with=settings.azure_storage.container_name))) == 0:
                (blob_service_client.
                 create_container(settings.azure_storage.container_name))
        except Exception as e:
            logging.exception("Blob exception %s", e)
            raise BlobStorageError from None

        self.container_client = blob_service_client.get_container_client(
            settings.azure_storage.container_name,
        )

    def close_connection(self) -> None:
        self.container_client.close()

    def upload_file(
        self, file_name: str, file_data: bytes, overwrite: bool = True
    ) -> None:
        """Upload file to azure storage"""
        self.connect_to_bloc()
        log_string = f"Upload {file_name}"
        logging.info(log_string)
        self.container_client.upload_blob(file_name, file_data, overwrite=overwrite)
        self.close_connection()
    def list_files(self) -> list:
        """List all present files in Azure storage"""
        self.connect_to_bloc()
        files = []
        blob_list = self.container_client.list_blobs()
        for blob in blob_list:
            files.append(blob.name)
        self.close_connection()
        return files

    def download_file(self, file_name: str) -> bytes:
        self.connect_to_bloc()
        result = self.container_client.download_blob(file_name).readall()
        self.close_connection()
        return result

    def get_file_url(self, file_name: str) -> str:
        self.connect_to_bloc()
        result = self.container_client.get_blob_client(file_name).url
        self.close_connection()
        return result
