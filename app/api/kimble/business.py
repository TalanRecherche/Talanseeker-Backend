from app.core import kimble_updater
from fastapi import Response


class KimbleBusiness:
    @staticmethod
    def start(file: bytes):
        kimble_updater.update_db(file)
        return Response(status_code=200)