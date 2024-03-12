from rest_framework.views import APIView
from rest_framework import status

from backend.helpers.Exception import CustomException
from backend.helpers.Log import Log


class CustomController(APIView):
    @staticmethod
    def validate(data, serializer, validationType: str):
        cleanData = None
        mismatch = False

        try:
            if serializer:
                if validationType == "value":
                    serializer = serializer(data=data)
                    if serializer.is_valid():
                        cleanData = serializer.validated_data
                    else:
                        mismatch = True
                elif validationType == "list":
                    serializer = serializer(data={"items": data}) # serializer needs an "items" key.
                    if serializer.is_valid():
                        cleanData = serializer.validated_data["items"]
                    else:
                        mismatch = True
                else:
                    raise NotImplemented

                if mismatch:
                    Log.log("Upstream data incorrect: " + str(serializer.errors))
                    raise CustomException(
                        status=500,
                        payload={"Signage Orchestrator Backend": "Upstream data mismatch."}
                    )
                else:
                    return cleanData
            else:
                return data
        except Exception as e:
            raise e



    @staticmethod
    def exceptionHandler(e: Exception) -> tuple:
        Log.logException(e)

        data = dict()
        headers = { "Cache-Control": "no-cache" }

        if e.__class__.__name__ in ("ConnectionError", "Timeout", "ConnectTimeout", "TooManyRedirects", "SSLError", "HTTPError"):
            httpStatus = status.HTTP_503_SERVICE_UNAVAILABLE
            data["error"] = {
                "network": e.__str__()
            }
        elif e.__class__.__name__ == "CustomException":
            httpStatus = e.status
            if e.payload:
                data["error"] = e.payload
            else:
                data = None
        elif e.__class__.__name__ == "ParseError":
            data = None
            httpStatus = status.HTTP_400_BAD_REQUEST # json parse.
        else:
            data = None
            httpStatus = status.HTTP_500_INTERNAL_SERVER_ERROR # generic.

        return data, httpStatus, headers
