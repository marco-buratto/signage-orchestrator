from rest_framework.request import Request
from rest_framework.response import Response

from backend.models.Playlist import Playlist

from backend.serializers.Playlist import PlaylistSerializer

from backend.controllers.CustomControllerItem import CustomControllerItem


class PlaylistController(CustomControllerItem):
    def __init__(self, *args, **kwargs):
        super().__init__(subject="playlist", *args, **kwargs)



    def get(self, request: Request, playlistId: int) -> Response:
        def actionCall(**kwargs):
            return Playlist(id=kwargs.get("id")).repr()

        return self.info(request=request, actionCall=actionCall, objectId=playlistId, serializer=PlaylistSerializer)



    def patch(self, request: Request, playlistId: int) -> Response:
        def actionCall(**kwargs):
            return Playlist(id=kwargs.get("id")).modify(kwargs.get("data"))

        return self.modify(request=request, actionCall=actionCall, objectId=playlistId, serializer=PlaylistSerializer)



    def delete(self, request: Request, playlistId: int) -> Response:
        def actionCall(**kwargs):
            return Playlist(id=kwargs.get("id")).delete()

        return self.remove(request=request, actionCall=actionCall, objectId=playlistId)
