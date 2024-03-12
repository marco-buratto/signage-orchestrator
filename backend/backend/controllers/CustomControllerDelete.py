from typing import Callable

from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status

from backend.controllers.CustomController import CustomController

from backend.helpers.Log import Log


class CustomControllerDelete(CustomController):
    def __init__(self, subject: str, *args, **kwargs):
        self.subject = subject



    def deleteItem(self, request: Request, actionCall: Callable, objectId: int) -> Response:
        Log.log(f"{self.subject.capitalize()} deletion")

        try:
            response = {
                "data": actionCall(id=objectId)
            }

            if not response["data"]:
                response = None # no payload on empty returns.

            httpStatus = status.HTTP_200_OK
        except Exception as e:
            data, httpStatus, headers = CustomController.exceptionHandler(e)
            return Response(data, status=httpStatus, headers=headers)

        return Response(response, status=httpStatus, headers={
            "Cache-Control": "no-cache"
        })
