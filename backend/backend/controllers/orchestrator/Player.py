from rest_framework.request import Request
from rest_framework.response import Response

from backend.models.Player import Player

from backend.serializers.Player import PlayerSerializer

from backend.controllers.CustomController import CustomController


class PlayerController(CustomController):
    def __init__(self, *args, **kwargs):
        super().__init__(subject="player", *args, **kwargs)



    def get(self, request: Request, playerId: int) -> Response:
        def actionCall(**kwargs):
            return Player(
                id=kwargs.get("id"),
                loadGroup=bool("loadGroup" in request.GET)
            ).repr()

        return self.info(request=request, actionCall=actionCall, objectId=playerId, serializer=PlayerSerializer)
