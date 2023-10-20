import re

from rest_framework.request import Request


class HTTP:
    @staticmethod
    def getQueryParams(request: Request) -> str:
        # Returns only the query params substring from request.
        hrefQueryParams = ""

        matches = re.search(r"/\?(.*)$", request.get_full_path())
        if matches:
            hrefQueryParams = str(matches.group(1)).strip()

        return hrefQueryParams
