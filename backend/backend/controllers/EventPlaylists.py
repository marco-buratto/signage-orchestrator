from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status

from backend.models.Event import Event

from backend.serializers.EventPlaylist import EventPlaylistsSerializer as Serializer

from backend.controllers.CustomController import CustomController
from backend.helpers.Log import Log


class EventPlaylistsController(CustomController):
    @staticmethod
    def post(request: Request, eventId: int) -> Response:
        response = None

        try:
            Log.log("Event linking to playlist")
            Log.log("User data: "+str(request.data))

            serializer = Serializer(data=request.data.get("data", {}))
            if serializer.is_valid():
                userdata = serializer.validated_data
                Event(id=eventId).linkToPlaylist(userdata["playlist"]["id"])

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
