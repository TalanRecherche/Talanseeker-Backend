from app.settings import Settings

from .azure_modules.azure_pg_manager import AzurePGManager
from .azure_modules.azureblobmanager import AzureBlobManager
from .kimble.updateDB import KimbleUpdater

azure_blob_manager = AzureBlobManager(Settings())
azure_pg_manager = AzurePGManager()
kimble_updater = KimbleUpdater()
