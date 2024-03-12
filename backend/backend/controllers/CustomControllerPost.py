from typing import Callable

from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status

from backend.controllers.CustomController import CustomController

from backend.helpers.Log import Log


class CustomControllerPost(CustomController):
    def __init__(self, subject: str, *args, **kwargs):
        self.subject = subject



    def postItem(self, request: Request, actionCall: Callable, serializer: Callable = None) -> Response:
        serializer = serializer or None

        Log.log(f"Item addition for {self.subject.capitalize()}")
        Log.log("User data: " + str(request.data))

        try:
            s = serializer(data=request.data.get("data", {}))
            if s.is_valid():
                response = {
                    "data": actionCall(data=s.validated_data)
                }

                if not response["data"]:
                    response = None # no payload on empty returns.

                httpStatus = status.HTTP_201_CREATED
            else:
                httpStatus = status.HTTP_400_BAD_REQUEST
                response = {
                    "Signage Orchestrator Backend": {
                        "error": str(s.errors)
                    }
                }

                Log.log("User data incorrect: "+str(response))
        except Exception as e:
            data, httpStatus, headers = CustomController.exceptionHandler(e)
            return Response(data, status=httpStatus, headers=headers)

        return Response(response, status=httpStatus, headers={
            "Cache-Control": "no-cache"
        })