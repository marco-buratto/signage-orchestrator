from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status

from backend.models.Playlist import Playlist

from backend.serializers.Playlist import PlaylistSerializer
from backend.serializers.Playlists import PlaylistsSerializer

from backend.controllers.CustomController import CustomController
from backend.helpers.Conditional import Conditional
from backend.helpers.Log import Log


class PlaylistsController(CustomController):
    @staticmethod
    def get(request: Request) -> Response:
        filter = ""
        if "filter" in request.GET:
            f = request.GET.get("filter")
            if "web" in f:
                filter = "web"
            if "slideshow" in f:
                filter = "slideshow"

        try:
            Log.log("Playlists list")
            data = {
                "data": {
                    "items": CustomController.validate(
                        [r.repr() for r in Playlist.list(filter)],
                        PlaylistsSerializer,
                        "list"
                    )
                }
            }

            # Check the response's ETag validity (against client request).
            conditional = Conditional(request)
            etagCondition = conditional.responseEtagFreshnessAgainstRequest(data["data"])
            if etagCondition["state"] == "fresh":
                data = None
                httpStatus = status.HTTP_304_NOT_MODIFIED
            else:
                httpStatus = status.HTTP_200_OK
        except Exception as e:
            data, httpStatus, headers = CustomController.exceptionHandler(e)
            return Response(data, status=httpStatus, headers=headers)

        return Response(data, status=httpStatus, headers={
            "ETag": etagCondition["responseEtag"],
            "Cache-Control": "must-revalidate"
        })



    @staticmethod
    def post(request: Request) -> Response:
        response = None

        try:
            Log.log("Playlist addition")
            Log.log("User data: "+str(request.data))

            serializer = PlaylistSerializer(data=request.data.get("data", {}))
            if serializer.is_valid():
                Playlist.add(serializer.validated_data)

                httpStatus = status.HTTP_201_CREATED
            else:
                httpStatus = status.HTTP_400_BAD_REQUEST
                response = {
                    "Signage Orchestrator Backend": {
                        "error": str(serializer.errors)
                    }
                }

                Log.log("User data incorrect: "+str(response))
        except Exception as e:
            data, httpStatus, headers = CustomController.exceptionHandler(e)
            return Response(data, status=httpStatus, headers=headers)

        return Response(response, status=httpStatus, headers={
            "Cache-Control": "no-cache"
        })
