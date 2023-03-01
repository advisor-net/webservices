from authentication.filters import UserFilter
from authentication.models import User
from authentication.serializers import UserSerializer
from authentication.validators import HandleValidator, UpdateUserValidator
from django_filters import rest_framework as filters
from rest_framework import serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from webservices.api.views import (
    CreateAPIView,
    ListAPIView,
    RetrieveAPIView,
    UpdateAPIView,
)
from webservices.paginators import StandardPageNumberPagination
from webservices.permissions import AdminOrUserSelf, MethodSpecificPermission


class CheckHandleView(CreateAPIView):
    permission_classes = (IsAuthenticated, AdminOrUserSelf)
    validator_class = HandleValidator
    queryset = User.objects.all()
    lookup_field = 'uuid'

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
    permission_classes = (IsAuthenticated, AdminOrUserSelf)
    validator_class = HandleValidator
    serializer_class = UserSerializer
    queryset = User.objects.all().with_related_objects_selected()
    lookup_field = 'uuid'

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
    permission_classes = (IsAuthenticated, AdminOrUserSelf)
    validator_class = UpdateUserValidator
    serializer_class = UserSerializer
    queryset = User.objects.all().with_related_objects_selected()
    lookup_field = 'uuid'

    def get_permissions(self):
        return [
            IsAuthenticated(),
            MethodSpecificPermission('PATCH', AdminOrUserSelf()),
            MethodSpecificPermission('PUT', AdminOrUserSelf()),
        ]

    def perform_update(self, validator):
        return validator.save()


class UserListView(ListAPIView):
    permission_classes = (IsAuthenticated,)
    # ToDo: come up with a more lightweight serializer?
    serializer_class = UserSerializer
    queryset = User.objects.all().with_related_objects_selected()
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = UserFilter
    pagination_class = StandardPageNumberPagination

    def get_queryset(self):
        order_by = self.request.query_params.get('order_by', 'net_worth')
        return (
            super().get_queryset().exclude(id=self.request.user.id).order_by(order_by)
        )


# TODO: maybe simplify these search filters later instead of needing to use smart components
#  need to think about initialization and how it renders...will need to get fancy with the display
#  and stuff like that
# TODO: search
class MetropolitanAreaSearch(RetrieveAPIView):
    pass


class IndustrySearch(RetrieveAPIView):
    pass


class JobTitleSearch(RetrieveAPIView):
    pass
