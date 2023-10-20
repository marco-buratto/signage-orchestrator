from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status

from backend.models.Group import Group

from backend.serializers.Group import GroupSerializer as Serializer

from backend.controllers.CustomController import CustomController
from backend.helpers.Conditional import Conditional
from backend.helpers.Log import Log


class GroupController(CustomController):
    @staticmethod
    def get(request: Request, groupId: int) -> Response:
        loadPlayers = False
        if "loadPlayers" in request.GET:
            loadPlayers = True

        try:
            Log.log("Group information")
            data = {
                "data": CustomController.validate(
                    Group(id=groupId, loadPlayers=loadPlayers).repr(),
                    Serializer,
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



    @staticmethod
    def delete(request: Request, groupId: int) -> Response:
        try:
            Log.log("Group deletion")

            Group(id=groupId).delete()

            httpStatus = status.HTTP_200_OK
        except Exception as e:
            data, httpStatus, headers = CustomController.exceptionHandler(e)
            return Response(data, status=httpStatus, headers=headers)

        return Response(None, status=httpStatus, headers={
            "Cache-Control": "no-cache"
        })



    @staticmethod
    def patch(request: Request, groupId: int) -> Response:
        response = None

        try:
            Log.log("Group modification")
            Log.log("User data: "+str(request.data))

            serializer = Serializer(data=request.data.get("data", {}), partial=True)
            if serializer.is_valid():
                Group(id=groupId).modify(serializer.validated_data)

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
