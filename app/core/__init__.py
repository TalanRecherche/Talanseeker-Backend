from app.settings import Settings

from .azure_modules.azureblobmanager import AzureBlobManager
from .azure_modules.azurePGmanager import AzurePGManager
from .kimble.updateDB import KimbleUpdater

azure_blob_manager = AzureBlobManager(Settings())
azure_pg_manager = AzurePGManager()
kimble_updater = KimbleUpdater()
