from typing import Callable

from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status

from backend.controllers.CustomController import CustomController

from backend.helpers.Conditional import Conditional
from backend.helpers.Log import Log


class CustomControllerItem(CustomController):
    def __init__(self, subject: str, linkedSubject: str = "", *args, **kwargs):
        self.subject = subject
        self.linkedSubject = linkedSubject



    def info(self, request: Request, actionCall: Callable, objectId: int, serializer: Callable = None) -> Response:
        serializer = serializer or None
        Log.log(f"Information for {self.subject.capitalize()}")

        try:
            data = {
                "data": CustomController.validate(
                    actionCall(id=objectId),
                    serializer,
                    "value"
                )
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



    def modify(self, request: Request, actionCall: Callable, objectId: int, serializer: Callable = None) -> Response:
        serializer = serializer or None

        Log.log(f"{self.subject.capitalize()} modification")
        Log.log("User data: " + str(request.data))

        try:
            s = serializer(data=request.data.get("data", {}), partial=True)
            if s.is_valid():
                response = {
                    "data": actionCall(id=objectId, data=s.validated_data)
                }

                if not response["data"]:
                    response = None # no payload on empty returns.

                httpStatus = status.HTTP_200_OK
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



    def remove(self, request: Request, actionCall: Callable, objectId: int) -> Response:
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



    def unlink(self, request: Request, actionCall: Callable, objectId: int, linkedObjectId: int) -> Response:
        Log.log(f"Unlink {self.linkedSubject.capitalize()} from {self.subject.capitalize()}")

        try:
            response = {
                "data": actionCall(
                    id=objectId,
                    linkedId=linkedObjectId
                )
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
