from rest_framework.request import Request
from rest_framework.response import Response

from backend.models.Group import Group

from backend.controllers.CustomController import CustomController


class GroupPlayerController(CustomController):
    def __init__(self, *args, **kwargs):
        super().__init__(subject="group", linkedSubject="player", *args, **kwargs)



    def delete(self, request: Request, groupId: int, playerId: int) -> Response:
        def actionCall(**kwargs):
            return Group(id=kwargs.get("id")).unlinkPlayer(kwargs.get("linkedId"))

        return self.unlink(request=request, actionCall=actionCall, objectId=groupId, linkedObjectId=playerId)
