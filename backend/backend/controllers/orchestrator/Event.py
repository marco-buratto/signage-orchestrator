from rest_framework.request import Request
from rest_framework.response import Response

from backend.models.Event import Event

from backend.serializers.Event import EventSerializer

from backend.controllers.CustomController import CustomController


class EventController(CustomController):
    def __init__(self, *args, **kwargs):
        super().__init__(subject="event", *args, **kwargs)



    def patch(self, request: Request, eventId: int) -> Response:
        def actionCall(**kwargs):
            return Event(id=kwargs.get("id")).modify(kwargs.get("data"))

        return self.modify(request=request, actionCall=actionCall, objectId=eventId, serializer=EventSerializer)



    def delete(self, request: Request, eventId: int) -> Response:
        def actionCall(**kwargs):
            return Event(id=kwargs.get("id")).delete()

        return self.remove(request=request, actionCall=actionCall, objectId=eventId)
