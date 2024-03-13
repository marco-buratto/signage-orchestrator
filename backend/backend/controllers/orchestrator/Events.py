from rest_framework.request import Request
from rest_framework.response import Response

from backend.models.Event import Event

from backend.serializers.Event import EventSerializer
from backend.serializers.Events import EventsSerializer

from backend.controllers.CustomControllerItems import CustomControllerItems


class EventsController(CustomControllerItems):
    def __init__(self, *args, **kwargs):
        super().__init__(subject="event", *args, **kwargs)



    def get(self, request: Request) -> Response:
        eventsCount = 0

        def actionCall():
            events = []
            for ev in Event.list(
                groupId=int(request.GET.get("group_id", 0)),
                startDate=request.GET.get("start_date", ""),
                endDate=request.GET.get("end_date", ""),
                loadGroup=bool("loadGroup" in request.GET),
                loadGroupPlayers=bool("loadGroup" in request.GET),
                loadPlaylist=bool("loadPlaylist" in request.GET)
            ):
                events.append(ev.repr())

            return events

        r: Response = self.ls(request=request, actionCall=actionCall, serializer=EventsSerializer)

        # Add events' count and players' count for each group
        # (information needed by the consumer).
        for item in r.data["data"].get("items", []):
            eventsCount += 1
            if "group" in item:
                item["group"]["players_count"] = len(item["group"].get("players", []))

        r.data["data"].update({
            "count": eventsCount,
        })

        return r



    def post(self, request: Request) -> Response:
        def actionCall(**kwargs):
            return Event.add(**kwargs)

        return self.add(request=request, actionCall=actionCall, serializer=EventSerializer)
