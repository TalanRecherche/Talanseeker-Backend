from app.core.azure_modules.azure_pg_manager import AzurePGManager
from app.core.azure_modules.azureblobmanager import AzureBlobManager
from app.core.kimble.update_db import KimbleUpdater
from app.settings.settings import Settings

azure_blob_manager = AzureBlobManager(Settings())
azure_pg_manager = AzurePGManager()
kimble_updater = KimbleUpdater()
