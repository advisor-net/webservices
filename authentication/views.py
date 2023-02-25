from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView


class TestView(APIView):
    authentication_classes: list = []
    permission_classes = (AllowAny,)

    def post(self, request: Request):
        print('another value here...what about this ')
        print('maybe this........')
        return Response(data="yeah we made it", status=status.HTTP_200_OK)
