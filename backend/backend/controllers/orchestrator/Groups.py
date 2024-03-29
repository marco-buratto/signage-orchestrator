from rest_framework.request import Request
from rest_framework.response import Response

from backend.models.Group import Group

from backend.serializers.Group import GroupSerializer
from backend.serializers.Groups import GroupsSerializer

from backend.controllers.CustomController import CustomController


class GroupsController(CustomController):
    def __init__(self, *args, **kwargs):
        super().__init__(subject="group", *args, **kwargs)



    def get(self, request: Request) -> Response:
        def actionCall():
            return [
                r.repr() for r in Group.list(
                    loadPlayers=bool("loadPlayers" in request.GET)
                )
            ]

        return self.ls(request=request, actionCall=actionCall, serializer=GroupsSerializer)



    def post(self, request: Request) -> Response:
        def actionCall(**kwargs):
            return Group.add(**kwargs)

        return self.add(request=request, actionCall=actionCall, serializer=GroupSerializer)
