from django.http import request, response
from django.conf import settings


class HTTPMiddleware:
    def __init__(self, response: response) -> None:
        self.response = response



    def __call__(self, request: request) -> response:
        response = self.response(request)

        # Add headers.
        if settings.DEBUG:
            response['Access-Control-Allow-Origin'] = "*"
            response['Access-Control-Allow-Headers'] = "Authorization, Content-Type"
            response['Access-Control-Allow-Methods'] = "*"

        return response
