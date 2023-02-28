from authentication.models import User
from authentication.serializers import UserSerializer
from authentication.validators import HandleValidator
from rest_framework import serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from webservices.api.views import CreateAPIView, RetrieveAPIView, UpdateAPIView
from webservices.permissions import AdminOrUserHimself


class CheckHandleView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    validator_class = HandleValidator

    def post(self, request, *args, **kwargs):
        self.check_permissions(request)
        validator = self.get_validator(data=request.data)
        validator.is_valid(raise_exception=True)
        data = validator.validated_data
        if User.objects.filter(handle=data['handle']).exists():
            return Response(status=status.HTTP_200_OK, data=dict(available=False))
        else:
            return Response(status=status.HTTP_200_OK, data=dict(available=True))


class UpdateHandleView(UpdateAPIView):
    permission_classes = (IsAuthenticated,)
    validator_class = HandleValidator
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user

    def perform_update(self, validator):
        handle_value = validator.validated_data['handle']
        if (
            User.objects.exclude(email=validator.instance.email)
            .filter(handle=handle_value)
            .exists()
        ):
            raise serializers.ValidationError('A user with this handle already exists')
        validator.instance.handle = handle_value
        validator.instance.save()
        return validator.instance


class UserDetailsView(UpdateAPIView, RetrieveAPIView):
    permission_classes = (IsAuthenticated, AdminOrUserHimself)
    # ToDo: add better validation...only accept the non computed fields and set up a
    #  separate validator
    validator_class = UserSerializer
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user

    def perform_update(self, validator):
        return validator.save()


# TODO: maybe simplify these search filters later instead of needing to use smart components
#  need to think about initialization and how it renders...will need to get fancy with the display
#  and stuff like that
class MetropolitanAreaSearch(RetrieveAPIView):
    pass


class IndustrySearch(RetrieveAPIView):
    pass


class JobTitleSearch(RetrieveAPIView):
    pass
