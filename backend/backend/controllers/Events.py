from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status

from backend.models.Event import Event

from backend.serializers.Event import EventSerializer
from backend.serializers.Events import EventsSerializer

from backend.controllers.CustomController import CustomController
from backend.helpers.Conditional import Conditional
from backend.helpers.Log import Log


class EventsController(CustomController):
    @staticmethod
    def get(request: Request) -> Response:
        eventsCount = 0
        events = []
        groupId = 0
        if "group_id" in request.GET:
            groupId = int(request.GET.get("group_id"))

        startDate = endDate = ""
        if "start_date" in request.GET:
            startDate = request.GET.get("start_date")
        if "end_date" in request.GET:
            endDate = request.GET.get("end_date")

        loadGroup = False
        if "loadGroup" in request.GET:
            loadGroup = True

        loadPlaylist = False
        if "loadPlaylist" in request.GET:
            loadPlaylist = True

        try:
            Log.log("Events list")
            for ev in Event.list(
                    groupId=groupId, startDate=startDate, endDate=endDate,
                    loadGroup=loadGroup, loadGroupPlayers=loadGroup, loadPlaylist=loadPlaylist
            ):
                events.append(ev.repr())
                eventsCount += 1

            validatedEvents = CustomController.validate(events, EventsSerializer, "list")
            for vev in validatedEvents:
                if "group" in vev:
                    vev["group"]["players_count"] = len(vev["group"].get("players", [])) # add addresses count.

            data = {
                "data": {
                    "count": eventsCount,
                    "items": validatedEvents
                }
            }

            # Check the response's ETag validity (against client request).
            conditional = Conditional(request)
            etagCondition = conditional.responseEtagFreshnessAgainstRequest(data["data"])
            if etagCondition["state"] == "fresh":
                data = None
                httpStatus = status.HTTP_304_NOT_MODIFIED
            else:
                httpStatus = status.HTTP_200_OK
        except Exception as e:
            data, httpStatus, headers = CustomController.exceptionHandler(e)
            return Response(data, status=httpStatus, headers=headers)

        return Response(data, status=httpStatus, headers={
            "ETag": etagCondition["responseEtag"],
            "Cache-Control": "must-revalidate"
        })



    @staticmethod
    def post(request: Request) -> Response:
        response = None

        try:
            Log.log("Event addition")
            Log.log("User data: "+str(request.data))

            serializer = EventSerializer(data=request.data.get("data", {}))
            if serializer.is_valid():
                Event.add(serializer.validated_data)

                httpStatus = status.HTTP_201_CREATED
            else:
                httpStatus = status.HTTP_400_BAD_REQUEST
                response = {
                    "Signage Orchestrator Backend": {
                        "error": str(serializer.errors)
                    }
                }

                Log.log("User data incorrect: "+str(response))
        except Exception as e:
            data, httpStatus, headers = CustomController.exceptionHandler(e)
            return Response(data, status=httpStatus, headers=headers)

        return Response(response, status=httpStatus, headers={
            "Cache-Control": "no-cache"
        })
