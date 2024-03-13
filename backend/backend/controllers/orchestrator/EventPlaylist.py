from rest_framework.request import Request
from rest_framework.response import Response

from backend.models.Event import Event

from backend.controllers.CustomController import CustomController


class EventPlaylistController(CustomController):
    def __init__(self, *args, **kwargs):
        super().__init__(subject="playlist", linkedSubject="event", *args, **kwargs)



    def delete(self, request: Request, eventId: int, playlistId: int) -> Response:
        def actionCall(**kwargs):
            return Event(id=kwargs.get("id")).unlinkFromPlaylist(
                kwargs.get("linkedObjectId")
            )

        return self.unlink(request=request, actionCall=actionCall, objectId=eventId, linkedObjectId=playlistId)
