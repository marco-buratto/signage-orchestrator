from rest_framework.request import Request
from rest_framework.response import Response

from backend.models.Group import Group

from backend.serializers.Group import GroupSerializer

from backend.controllers.CustomController import CustomController


class GroupController(CustomController):
    def __init__(self, *args, **kwargs):
        super().__init__(subject="group", *args, **kwargs)



    def get(self, request: Request, groupId: int) -> Response:
        def actionCall(**kwargs):
            return Group(
                id=kwargs.get("id"),
                loadPlayers=bool("loadPlayers" in request.GET)
            ).repr()

        return self.info(request=request, actionCall=actionCall, objectId=groupId, serializer=GroupSerializer)



    def patch(self, request: Request, groupId: int) -> Response:
        def actionCall(**kwargs):
            return Group(id=kwargs.get("id")).modify(kwargs.get("data"))

        return self.modify(request=request, actionCall=actionCall, objectId=groupId, serializer=GroupSerializer)



    def delete(self, request: Request, groupId: int) -> Response:
        def actionCall(**kwargs):
            return Group(id=kwargs.get("id")).delete()

        return self.remove(request=request, actionCall=actionCall, objectId=groupId)
