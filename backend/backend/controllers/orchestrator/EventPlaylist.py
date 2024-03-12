from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status

from backend.models.Event import Event

from backend.controllers.CustomController import CustomController
from backend.helpers.Log import Log


class EventPlaylistController(CustomController):
    @staticmethod
    def delete(request: Request, eventId: int, playlistId: int) -> Response:
        try:
            Log.log("Event unlinking from playlist")

            Event(id=eventId).unlinkFromPlaylist(playlistId)

            httpStatus = status.HTTP_200_OK
        except Exception as e:
            data, httpStatus, headers = CustomController.exceptionHandler(e)
            return Response(data, status=httpStatus, headers=headers)

        return Response(None, status=httpStatus, headers={
            "Cache-Control": "no-cache"
        })
