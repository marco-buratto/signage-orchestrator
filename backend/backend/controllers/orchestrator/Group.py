from rest_framework.request import Request
from rest_framework.response import Response

from backend.models.Group import Group

from backend.serializers.Group import GroupSerializer

from backend.controllers.CustomControllerItem import CustomControllerItem


class GroupController(CustomControllerItem):
    def __init__(self, *args, **kwargs):
        super().__init__(subject="group", *args, **kwargs)



    def get(self, request: Request, groupId: int) -> Response:
        def actionCall(**kwargs):
            return Group(
                id=kwargs.get("id"),
                loadPlayers=bool("loadPlayers" in request.GET)
            ).repr()

        return self.getItem(request=request, actionCall=actionCall, objectId=groupId, serializer=GroupSerializer)



    def patch(self, request: Request, groupId: int) -> Response:
        def actionCall(**kwargs):
            return Group(id=kwargs.get("id")).modify(kwargs.get("data"))

        return self.patchItem(request=request, actionCall=actionCall, objectId=groupId, serializer=GroupSerializer)



    def delete(self, request: Request, groupId: int) -> Response:
        def actionCall(**kwargs):
            return Group(id=kwargs.get("id")).delete()

        return self.deleteItem(request=request, actionCall=actionCall, objectId=groupId)
