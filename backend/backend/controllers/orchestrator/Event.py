from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status

from backend.models.Event import Event

from backend.serializers.Event import EventSerializer as Serializer

from backend.controllers.CustomController import CustomController
from backend.helpers.Log import Log


class EventController(CustomController):
    @staticmethod
    def delete(request: Request, eventId: int) -> Response:
        try:
            Log.log("Event deletion")

            Event(id=eventId).delete()

            httpStatus = status.HTTP_200_OK
        except Exception as e:
            data, httpStatus, headers = CustomController.exceptionHandler(e)
            return Response(data, status=httpStatus, headers=headers)

        return Response(None, status=httpStatus, headers={
            "Cache-Control": "no-cache"
        })



    @staticmethod
    def patch(request: Request, eventId: int) -> Response:
        response = None

        try:
            Log.log("Event modification")
            Log.log("User data: "+str(request.data))

            serializer = Serializer(data=request.data.get("data", {}), partial=True)
            if serializer.is_valid():
                Event(id=eventId).modify(serializer.validated_data)

                httpStatus = status.HTTP_200_OK
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
