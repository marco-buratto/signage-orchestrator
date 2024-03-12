from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status

from backend.models.Player import Player

from backend.serializers.Player import PlayerSerializer
from backend.serializers.Players import PlayersSerializer

from backend.controllers.CustomController import CustomController
from backend.helpers.Conditional import Conditional
from backend.helpers.Cryptography import Cryptography
from backend.helpers.Log import Log


class PlayersController(CustomController):
    @staticmethod
    def get(request: Request) -> Response:
        loadGroup = False
        if "loadGroup" in request.GET:
            loadGroup = True

        try:
            Log.log("Players list")
            data = {
                "data": {
                    "items": CustomController.validate(
                        [r.repr() for r in Player.list(loadGroup=loadGroup)],
                        PlayersSerializer,
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
        try:
            Log.log("Player addition")
            Log.log("User data: "+str(request.data))

            serializer = PlayerSerializer(data=request.data.get("data", {}))
            if serializer.is_valid():
                Player.addOrUpdate(serializer.validated_data)

                # Always return Orchestrator SSH public key.
                # Yes, dirty and unrelated, but it avoids many players' connections.
                response = {
                    "data": {
                        "orchestrator_ssh_public_key": Cryptography.getPublicSshKey()
                    }
                }

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
