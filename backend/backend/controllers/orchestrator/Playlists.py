from rest_framework.request import Request
from rest_framework.response import Response

from backend.models.Playlist import Playlist

from backend.serializers.Playlist import PlaylistSerializer
from backend.serializers.Playlists import PlaylistsSerializer

from backend.controllers.CustomController import CustomController


class PlaylistsController(CustomController):
    def __init__(self, *args, **kwargs):
        super().__init__(subject="playlist", *args, **kwargs)



    def get(self, request: Request) -> Response:
        def actionCall():
            show = "all"
            if "filter" in request.GET:
                f = request.GET.get("filter")
                if "web" in f:
                    show = "web"
                if "slideshow" in f:
                    show = "slideshow"

            return [
                r.repr() for r in Playlist.list(
                    filter=show
                )
            ]

        return self.ls(request=request, actionCall=actionCall, serializer=PlaylistsSerializer)



    def post(self, request: Request) -> Response:
        def actionCall(**kwargs):
            return Playlist.add(**kwargs)

        return self.add(request=request, actionCall=actionCall, serializer=PlaylistSerializer)
