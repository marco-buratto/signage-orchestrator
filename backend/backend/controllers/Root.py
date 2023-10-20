from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.reverse import reverse_lazy


class RootController(APIView):
    @staticmethod
    def get(request: Request) -> Response:
        return Response({
            'asset': reverse_lazy('backend-assets', request=request)
        })
