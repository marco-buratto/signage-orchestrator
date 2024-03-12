from typing import Callable

from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status

from backend.controllers.CustomController import CustomController

from backend.helpers.Conditional import Conditional
from backend.helpers.Log import Log


class CustomControllerList(CustomController):
    def __init__(self, subject: str, *args, **kwargs):
        self.subject = subject



    def getList(self, request: Request, actionCall: Callable, serializer: Callable = None) -> Response:
        serializer = serializer or None
        Log.log(f"List of {self.subject.capitalize()}")

        try:
            data = {
                "data": {
                    "items": CustomController.validate(actionCall(), serializer, "list")
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
