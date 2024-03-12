from rest_framework.request import Request
from rest_framework.response import Response

from backend.models.Player import Player

from backend.serializers.Player import PlayerSerializer
from backend.serializers.Players import PlayersSerializer

from backend.controllers.CustomControllerItems import CustomControllerItems
from backend.helpers.Cryptography import Cryptography


class PlayersController(CustomControllerItems):
    def __init__(self, *args, **kwargs):
        super().__init__(subject="player", *args, **kwargs)



    def get(self, request: Request) -> Response:
        def actionCall():
            return [
                r.repr() for r in Player.list(
                    loadGroup=bool("loadGroup" in request.GET)
                )
            ]

        return self.getList(request=request, actionCall=actionCall, serializer=PlayersSerializer)



    def post(self, request: Request) -> Response:
        def actionCall(**kwargs):
            return Player.addOrUpdate(**kwargs)

        # Always return Orchestrator SSH public key.
        # Yes, dirty and unrelated, but it avoids many players' connections.
        r = self.postItem(request=request, actionCall=actionCall, serializer=PlayerSerializer)
        r.data = {
            "data": {
                "orchestrator_ssh_public_key": Cryptography.getPublicSshKey()
            }
        }

        return r
