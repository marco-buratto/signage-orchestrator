from rest_framework.request import Request
from rest_framework.response import Response

from backend.models.Event import Event

from backend.serializers.EventGroup import EventGroupsSerializer

from backend.controllers.CustomController import CustomController


class EventGroupsController(CustomController):
    def __init__(self, *args, **kwargs):
        super().__init__(subject="group", linkedSubject="event", *args, **kwargs)



    def post(self, request: Request, eventId: int) -> Response:
        def actionCall(**kwargs):
            return Event(id=kwargs.get("id")).linkToGroup(
                kwargs["data"]["group"]["id"]
            )

        return self.link(request=request, actionCall=actionCall, objectId=eventId, serializer=EventGroupsSerializer)
