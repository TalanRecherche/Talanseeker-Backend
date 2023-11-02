import logging

from azure.storage.blob import BlobServiceClient


class AzureBlobManager:
    """
    manage files (upload, download, ...)
    """

    def __init__(self, settings):
        """
        create initial connection
        """
        blob_service_client = BlobServiceClient.from_connection_string(
            settings.azure_storage.connection_string
        )
        try:
            blob_service_client.create_container(settings.azure_storage.container_name)
        except Exception:
            pass
        self.container_client = blob_service_client.get_container_client(
            settings.azure_storage.container_name
        )

    def upload_file(self, file_name: str, file_data, overwrite: bool = True):
        """
        upload file to azure storage
        """
        logging.info(f"Upload {file_name}")
        self.container_client.upload_blob(file_name, file_data, overwrite=overwrite)

    def list_files(self) -> list:
        """
        list all present files in Azure storage
        """
        files = []
        blob_list = self.container_client.list_blobs()
        for blob in blob_list:
            files.append(blob.name)
        return files

    def download_file(self, file_name: str):
        return self.container_client.download_blob(file_name).readall()
