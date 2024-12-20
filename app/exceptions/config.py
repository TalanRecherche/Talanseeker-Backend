from dataclasses import dataclass


@dataclass
class ExceptionMetaData:
    status_code: int
    message: str


class ExceptionConfig:
    invalid_columns_error = ExceptionMetaData(
        status_code=400,
        message="Aucun profil ne correspond aux critères demandés!",
    )
    request_validation_error = ExceptionMetaData(
        status_code=422,
        message="Paramètre manquant!",
    )
    user_integrity_exception = ExceptionMetaData(
        status_code=422,
        message="Impossible de créer l'utilisateur!",
    )
    not_found_exception = ExceptionMetaData(
        status_code=404,
        message="!!!",
    )
    db_exception = ExceptionMetaData(
        status_code=500,
        message="DB Error",
    )
    settings_exception = ExceptionMetaData(
        status_code=500,
        message="Settings Error",
    )
    blob_storage_exception = ExceptionMetaData(
        status_code=500,
        message="BS Error",
    )
