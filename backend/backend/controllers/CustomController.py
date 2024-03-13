from typing import Callable

from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status

from backend.controllers.CustomControllerBase import CustomControllerBase

from backend.helpers.Conditional import Conditional
from backend.helpers.Log import Log


class CustomController(CustomControllerBase):
    def __init__(self, subject: str, linkedSubject: str = "", *args, **kwargs):
        self.subject = subject
        self.linkedSubject = linkedSubject



    def info(self, request: Request, actionCall: Callable, objectId: int, serializer: Callable = None) -> Response:
        serializer = serializer or None
        Log.clog(f"Information for {self.subject.capitalize()}")

        try:
            data = {
                "data": CustomControllerBase.validate(
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
            data, httpStatus, headers = CustomControllerBase.exceptionHandler(e)
            return Response(data, status=httpStatus, headers=headers)

        return Response(data, status=httpStatus, headers={
            "ETag": etagCondition["responseEtag"],
            "Cache-Control": "must-revalidate"
        })



    def modify(self, request: Request, actionCall: Callable, objectId: int, serializer: Callable = None) -> Response:
        serializer = serializer or None

        Log.clog(f"{self.subject.capitalize()} modification")
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
            data, httpStatus, headers = CustomControllerBase.exceptionHandler(e)
            return Response(data, status=httpStatus, headers=headers)

        return Response(response, status=httpStatus, headers={
            "Cache-Control": "no-cache"
        })



    def remove(self, request: Request, actionCall: Callable, objectId: int) -> Response:
        Log.clog(f"{self.subject.capitalize()} deletion")

        try:
            response = {
                "data": actionCall(id=objectId)
            }

            if not response["data"]:
                response = None # no payload on empty returns.

            httpStatus = status.HTTP_200_OK
        except Exception as e:
            data, httpStatus, headers = CustomControllerBase.exceptionHandler(e)
            return Response(data, status=httpStatus, headers=headers)

        return Response(response, status=httpStatus, headers={
            "Cache-Control": "no-cache"
        })



    def unlink(self, request: Request, actionCall: Callable, objectId: int, linkedObjectId: int) -> Response:
        Log.clog(f"Unlink {self.linkedSubject.capitalize()} from {self.subject.capitalize()}")

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
            data, httpStatus, headers = CustomControllerBase.exceptionHandler(e)
            return Response(data, status=httpStatus, headers=headers)

        return Response(response, status=httpStatus, headers={
            "Cache-Control": "no-cache"
        })



    def ls(self, request: Request, actionCall: Callable, serializer: Callable = None) -> Response:
        serializer = serializer or None
        Log.clog(f"List of {self.subject.capitalize()}")

        try:
            data = {
                "data": {
                    "items": CustomControllerBase.validate(actionCall(), serializer, "list")
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
            data, httpStatus, headers = CustomControllerBase.exceptionHandler(e)
            return Response(data, status=httpStatus, headers=headers)

        return Response(data, status=httpStatus, headers={
            "ETag": etagCondition["responseEtag"],
            "Cache-Control": "must-revalidate"
        })



    def add(self, request: Request, actionCall: Callable, serializer: Callable = None) -> Response:
        serializer = serializer or None

        Log.clog(f"{self.subject.capitalize()} addition")
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
            data, httpStatus, headers = CustomControllerBase.exceptionHandler(e)
            return Response(data, status=httpStatus, headers=headers)

        return Response(response, status=httpStatus, headers={
            "Cache-Control": "no-cache"
        })



    def link(self, request: Request, actionCall: Callable, objectId: int, linkedObjectId: int, serializer: Callable = None) -> Response:
        serializer = serializer or None
        Log.clog(f"Link {self.linkedSubject.capitalize()} to {self.subject.capitalize()}")

        try:
            s = serializer(data=request.data.get("data", {}))
            if s.is_valid():
                response = {
                    "data": actionCall(
                        id=objectId,
                        linkedObjectId=linkedObjectId
                    )
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
            data, httpStatus, headers = CustomControllerBase.exceptionHandler(e)
            return Response(data, status=httpStatus, headers=headers)

        return Response(response, status=httpStatus, headers={
            "Cache-Control": "no-cache"
        })
