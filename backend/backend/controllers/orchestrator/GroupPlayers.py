from rest_framework.request import Request
from rest_framework.response import Response

from backend.models.Group import Group

from backend.serializers.GroupPlayer import GroupPlayerSerializer

from backend.controllers.CustomController import CustomController


class GroupPlayersController(CustomController):
    def __init__(self, *args, **kwargs):
        super().__init__(subject="group", linkedSubject="player", *args, **kwargs)



    def post(self, request: Request, groupId: int) -> Response:
        def actionCall(**kwargs):
            return Group(id=kwargs.get("id")).linkPlayer(
                kwargs["data"]["player"]["id"]
            )

        return self.link(request=request, actionCall=actionCall, objectId=groupId, serializer=GroupPlayerSerializer)
