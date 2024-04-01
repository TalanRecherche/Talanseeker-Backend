from fastapi import Response

from app.core.kimble import kimble_updater


class KimbleBusiness:
    @staticmethod
    def start(file: bytes) -> Response:
        kimble_updater.update_db(file)
        return Response(status_code=200)
