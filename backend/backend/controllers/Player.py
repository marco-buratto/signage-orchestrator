from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status

from backend.models.Player import Player

from backend.serializers.Player import PlayerSerializer as Serializer

from backend.controllers.CustomController import CustomController
from backend.helpers.Conditional import Conditional
from backend.helpers.Log import Log


class PlayerController(CustomController):
    @staticmethod
    def get(request: Request, playerId: int) -> Response:
        loadGroup = False
        if "loadGroup" in request.GET:
            loadGroup = True

        try:
            Log.log("Player information")
            data = {
                "data": CustomController.validate(
                    Player(id=playerId, loadGroup=loadGroup).repr(),
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
