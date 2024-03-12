from rest_framework.request import Request
from rest_framework.response import Response

from backend.models.Playlist import Playlist

from backend.serializers.Playlist import PlaylistSerializer
from backend.serializers.Playlists import PlaylistsSerializer

from backend.controllers.CustomControllerItems import CustomControllerItems


class PlaylistsController(CustomControllerItems):
    def __init__(self, *args, **kwargs):
        super().__init__(subject="playlist", *args, **kwargs)



    def get(self, request: Request) -> Response:
        def actionCall():
            what = "all"
            if "filter" in request.GET:
                f = request.GET.get("filter")
                if "web" in f:
                    what = "web"
                if "slideshow" in f:
                    what = "slideshow"

            return [
                r.repr() for r in Playlist.list(
                    filter=what
                )
            ]

        return self.ls(request=request, actionCall=actionCall, serializer=PlaylistsSerializer)



    def post(self, request: Request) -> Response:
        def actionCall(**kwargs):
            return Playlist.add(**kwargs)

        return self.add(request=request, actionCall=actionCall, serializer=PlaylistSerializer)
