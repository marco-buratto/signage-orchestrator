from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status

from backend.models.Group import Group

from backend.controllers.CustomController import CustomController
from backend.helpers.Log import Log


class GroupPlayerController(CustomController):
    @staticmethod
    def delete(request: Request, groupId: int, playerId: int) -> Response:
        try:
            Log.log("Player unlinking from group")

            Group(id=groupId).unlinkPlayer(playerId)

            httpStatus = status.HTTP_200_OK
        except Exception as e:
            data, httpStatus, headers = CustomController.exceptionHandler(e)
            return Response(data, status=httpStatus, headers=headers)

        return Response(None, status=httpStatus, headers={
            "Cache-Control": "no-cache"
        })
