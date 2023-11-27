import logging

from azure.storage.blob import BlobServiceClient

from app.settings.settings import Settings


class AzureBlobManager:
    """manage files (upload, download, ...)"""

    def __init__(self, settings: Settings) -> None:
        """Create initial connection"""
        blob_service_client = BlobServiceClient.from_connection_string(
            settings.azure_storage.connection_string,
        )

        try:
            if len(list(blob_service_client.list_containers(
                    name_starts_with=settings.azure_storage.container_name))) == 0:
                (blob_service_client.
                 create_container(settings.azure_storage.container_name))
        except Exception as e:
            logging.exception("Blob exception %s", e)
        self.container_client = blob_service_client.get_container_client(
            settings.azure_storage.container_name,
        )

    def upload_file(
        self, file_name: str, file_data: bytes, overwrite: bool = True
    ) -> None:
        """Upload file to azure storage"""
        log_string = f"Upload {file_name}"
        logging.info(log_string)
        self.container_client.upload_blob(file_name, file_data, overwrite=overwrite)

    def list_files(self) -> list:
        """List all present files in Azure storage"""
        files = []
        blob_list = self.container_client.list_blobs()
        for blob in blob_list:
            files.append(blob.name)
        return files

    def download_file(self, file_name: str) -> bytes:
        return self.container_client.download_blob(file_name).readall()

    def get_file_url(self, file_name: str) -> str:
        return self.container_client.get_blob_client(file_name).url
