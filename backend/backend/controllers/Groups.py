from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status

from backend.models.Group import Group

from backend.serializers.Group import GroupSerializer
from backend.serializers.Groups import GroupsSerializer

from backend.controllers.CustomController import CustomController
from backend.helpers.Conditional import Conditional
from backend.helpers.Log import Log


class GroupsController(CustomController):
    @staticmethod
    def get(request: Request) -> Response:
        loadPlayers = False
        if "loadPlayers" in request.GET:
            loadPlayers = True

        try:
            Log.log("Groups list")
            data = {
                "data": {
                    "items": CustomController.validate(
                        [r.repr() for r in Group.list(loadPlayers=loadPlayers)],
                        GroupsSerializer,
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
            Log.log("Group addition")
            Log.log("User data: "+str(request.data))

            serializer = GroupSerializer(data=request.data.get("data", {}))
            if serializer.is_valid():
                Group.add(serializer.validated_data)

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
