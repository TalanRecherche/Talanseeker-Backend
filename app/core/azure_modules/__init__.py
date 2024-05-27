from app.core.azure_modules.azure_ml_manager import AzureMLManager
from app.core.azure_modules.azure_pg_manager import AzurePGManager
from app.core.azure_modules.azureblobmanager import AzureBlobManager

azure_pg_manager = AzurePGManager()
azure_blob_manager = AzureBlobManager()
azure_ml_manager = AzureMLManager()
