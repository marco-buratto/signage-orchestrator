import logging
from django.http import request, response


class LogMiddleware:
    def __init__(self, resp: response) -> None:
        self.resp = resp
        self.log = logging.getLogger("django") # setup LOGGING in settings.py



    def __call__(self, req: request) -> response:
        self.log.debug("--> Request: " + str(req))

        resp = self.resp(req)

        self.log.debug("--> Response: " + str(resp))

        return resp
