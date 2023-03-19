from datetime import timedelta

from authentication.chat_engine_helper import ChatEngineHelper
from authentication.filters import (
    IndustryFilter,
    JobTitleFilter,
    MetropolitanAreaFilter,
    UserFilter,
)
from authentication.models import (
    Industry,
    JobTitle,
    MetropolitanArea,
    ReportedMisconduct,
    ResetPasswordLink,
    SignUpLink,
    User,
    VerifyEmailLink,
    WaitListEntry,
)
from authentication.serializers import (
    IndustrySerializer,
    JobTitleSerializer,
    MetropolitanAreaSerializer,
    ProfileSerializer,
    UserSerializer,
)
from authentication.validators import HandleValidator, UpdateUserValidator
from django.conf import settings
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django_filters import rest_framework as filters
from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError
from rest_framework.filters import SearchFilter
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from webservices.api.views import (
    CreateAPIView,
    DestroyAPIView,
    ListAPIView,
    RetrieveAPIView,
    UpdateAPIView,
)
from webservices.celery import send_email
from webservices.paginators import StandardPageNumberPagination
from webservices.permissions import AdminOrUserSelf, MethodSpecificPermission


class ProfileView(RetrieveAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ProfileSerializer
    queryset = User.objects.all()

    def get_object(self):
        return self.request.user


# TODO: ping this on the frontend
class LogoutView(DestroyAPIView):
    permission_classes = (IsAuthenticated,)

    def delete(self, *args, **kwargs):
        user = self.request.user
        user.auth_token.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


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
        if (
            User.objects.filter(handle=data['handle'])
            .exclude(id=request.user.id)
            .exists()
        ):
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
            User.objects.exclude(id=validator.instance.id)
            .filter(handle=handle_value)
            .exists()
        ):
            raise serializers.ValidationError('A user with this handle already exists')
        validator.instance.handle = handle_value
        try:
            chat_user = validator.instance.chat_user
            ChatEngineHelper().update_chat_user_username(chat_user, handle_value)
        except ObjectDoesNotExist:
            pass
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


# TODO: provide averages for major list metrics
# TODO: fix string lookups when there is a comma in them
#  for now, we are just going to search using the FK id
class UserListView(ListAPIView):
    permission_classes = (IsAuthenticated,)
    # ToDo: come up with a more lightweight serializer?
    serializer_class = UserSerializer
    queryset = User.objects.all().with_related_objects_selected()
    pagination_class = StandardPageNumberPagination
    filter_backends = [SearchFilter, filters.DjangoFilterBackend]
    search_fields = ['handle', 'uuid']
    filterset_class = UserFilter

    def get_queryset(self):
        order_by = self.request.query_params.get('order_by', 'net_worth')
        return (
            super().get_queryset().exclude(id=self.request.user.id).order_by(order_by)
        )


class MetropolitanAreaSearch(ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = MetropolitanAreaSerializer
    queryset = MetropolitanArea.objects.all().order_by('name')
    pagination_class = StandardPageNumberPagination
    filter_backends = [SearchFilter, filters.DjangoFilterBackend]
    search_fields = ['name']
    filterset_class = MetropolitanAreaFilter


class IndustrySearch(ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = IndustrySerializer
    queryset = Industry.objects.all().order_by('name')
    pagination_class = StandardPageNumberPagination
    filter_backends = [SearchFilter, filters.DjangoFilterBackend]
    search_fields = ['name']
    filterset_class = IndustryFilter


class JobTitleSearch(ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = JobTitleSerializer
    queryset = JobTitle.objects.all().order_by('name')
    pagination_class = StandardPageNumberPagination
    filter_backends = [SearchFilter, filters.DjangoFilterBackend]
    search_fields = ['name']
    filterset_class = JobTitleFilter


# NOTE: this lets one user create a chat user for another member, somewhat at will...this is because
# we are creating chat users on demand as users try to chat to save cost with ChatEngine.io
# That is why we are excluding the AdminOrUserSelf permission here
class GetOrCreateChatUserView(CreateAPIView):
    class Validator(serializers.Serializer):
        agreed_to_terms = serializers.BooleanField(required=True)

    queryset = User.objects.all()
    lookup_field = 'uuid'
    permission_classes = (IsAuthenticated,)
    validator_class = Validator
    serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):
        self.check_permissions(request)
        validator = self.get_validator(data=request.data)
        validator.is_valid(raise_exception=True)
        data = validator.validated_data
        user = self.get_object()
        # TODO: prefetching?
        ChatEngineHelper().get_or_create_chat_user(user, data["agreed_to_terms"])
        return Response(
            status=status.HTTP_201_CREATED, data=self.get_serializer(instance=user).data
        )


class UpdateChatTermsAgreementView(CreateAPIView):
    class Validator(serializers.Serializer):
        agreed_to_terms = serializers.BooleanField(required=True)

    queryset = User.objects.all()
    lookup_field = 'uuid'
    permission_classes = (IsAuthenticated, AdminOrUserSelf)
    validator_class = Validator
    serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):
        self.check_permissions(request)
        validator = self.get_validator(data=request.data)
        validator.is_valid(raise_exception=True)
        data = validator.validated_data
        user = self.get_object()
        chat_user = user.chat_user
        chat_user.agreed_to_terms = data["agreed_to_terms"]
        chat_user.save()
        return Response(
            status=status.HTTP_200_OK, data=self.get_serializer(instance=user).data
        )


class ReportUserView(CreateAPIView):
    class Validator(serializers.Serializer):
        handle = serializers.CharField(required=True)
        description = serializers.CharField(required=True)

    validator_class = Validator
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user

    def post(self, request, *args, **kwargs):
        self.check_permissions(request)
        validator = self.get_validator(data=request.data)
        validator.is_valid(raise_exception=True)
        data = validator.validated_data
        user = self.get_object()
        other_user = get_object_or_404(User, handle=data["handle"])
        ReportedMisconduct.objects.create(
            plaintiff=user,
            defendant=other_user,
            description=data["description"],
        )
        send_email(
            f'{user.handle} has reported {other_user.handle} for misconduct',
            data["description"],
            settings.ADMIN_EMAIL,
        )
        return Response(status=status.HTTP_200_OK)


class JoinWaitlistView(CreateAPIView):
    class Validator(serializers.Serializer):
        email = serializers.EmailField(required=True)
        how_did_you_hear_about_us = serializers.CharField(required=True)
        why_do_you_want_to_join = serializers.CharField(required=True)

    validator_class = Validator
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        self.check_permissions(request)
        validator = self.get_validator(data=request.data)
        validator.is_valid(raise_exception=True)
        data = validator.validated_data
        WaitListEntry.objects.get_or_create(
            email=data.pop('email'),
            defaults=data,
        )
        return Response(status=status.HTTP_200_OK)


class SignUpView(CreateAPIView):
    class Validator(serializers.Serializer):
        sign_up_link_uuid = serializers.UUIDField(required=True)
        email = serializers.EmailField(required=True)
        password = serializers.CharField(required=True, min_length=8)

        def validate(self, attrs):
            if not SignUpLink.objects.filter(
                uuid=attrs["sign_up_link_uuid"], email=attrs["email"]
            ).exists():
                raise ValidationError('Invalid sign up link information')
            try:
                validate_password(attrs['password'])
            except Exception as e:
                raise ValidationError(str(e))
            return attrs

    validator_class = Validator
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        self.check_permissions(request)
        validator = self.get_validator(data=request.data)
        validator.is_valid(raise_exception=True)
        data = validator.validated_data

        user = User.objects.create_user(
            username=data['email'],
            email=data['email'],
            password=data['password'],
        )

        # delete sign up link, personal to only that user
        SignUpLink.objects.filter(
            uuid=data["sign_up_link_uuid"], email=data["email"]
        ).delete()

        verify_link = VerifyEmailLink.objects.create(
            user=user,
        )

        # send the verify email link to the inbox
        send_email(
            subject="Verify email address for Advisor",
            body=f"Click this link to verify your email address:\n"
            f"{settings.SITE_URL}/verify_email/{str(verify_link.uuid)}",
            to=user.email,
        )
        return Response(status=status.HTTP_201_CREATED)


class ResendEmailVerificationLinkView(CreateAPIView):
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user

    def post(self, request, *args, **kwargs):
        self.check_permissions(request)
        user = self.get_object()
        verify_link, _ = VerifyEmailLink.objects.get_or_create(user=user)

        send_email(
            subject="Verify email address for Advisor",
            body=f"Click this link to verify your email address:\n"
            f"{settings.SITE_URL}/verify_email/{str(verify_link.uuid)}",
            to=user.email,
        )

        return Response(status=status.HTTP_200_OK)


class VerifyEmailView(CreateAPIView):
    class Validator(serializers.Serializer):
        verify_link_uuid = serializers.UUIDField(required=True)

    permission_classes = (IsAuthenticated,)
    validator_class = Validator
    serializer_class = ProfileSerializer

    def get_object(self):
        return self.request.user

    def post(self, request, *args, **kwargs):
        self.check_permissions(request)
        validator = self.get_validator(data=request.data)
        validator.is_valid(raise_exception=True)
        data = validator.validated_data
        user = self.get_object()
        verify_link = VerifyEmailLink.objects.filter(
            user=user, uuid=data["verify_link_uuid"]
        ).first()
        if not verify_link:
            raise ValidationError('Invalid verification link')
        user.email_verified = True
        user.save()
        VerifyEmailLink.objects.filter(user=user).delete()
        return Response(
            status=status.HTTP_200_OK, data=self.get_serializer(instance=user).data
        )


class RequestResetPasswordView(CreateAPIView):
    class Validator(serializers.Serializer):
        email = serializers.EmailField(required=True)

    validator_class = Validator
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        self.check_permissions(request)
        validator = self.get_validator(data=request.data)
        validator.is_valid(raise_exception=True)
        data = validator.validated_data
        user = User.objects.filter(email=data['email']).first()
        if not user:
            # NOTE: we are hiding any details of the error here
            return Response(status=status.HTTP_200_OK)

        reset_link, created = ResetPasswordLink.objects.get_or_create(
            email=data['email'],
            defaults=dict(
                email=data['email'],
                expires_on=timezone.now() + timedelta(days=1),
            ),
        )
        if not created:
            reset_link.expires_on = timezone.now() + timedelta(days=1)
            reset_link.save()

        send_email(
            subject="Reset password for Advisor",
            body=f"Click this link to reset your password:\n"
            f"{settings.SITE_URL}/reset_password/{str(reset_link.uuid)}",
            to=data['email'],
        )
        return Response(status=status.HTTP_200_OK)


class ResetPasswordView(CreateAPIView):
    class Validator(serializers.Serializer):
        reset_link_uuid = serializers.UUIDField(required=True)
        email = serializers.EmailField(required=True)
        password = serializers.CharField(required=True, min_length=8)

        def validate(self, attrs):
            if not User.objects.filter(email=attrs['email']).exists():
                raise ValidationError('Unknown error')
            reset_link = ResetPasswordLink.objects.filter(
                uuid=attrs["reset_link_uuid"], email=attrs["email"]
            ).first()
            if not reset_link:
                raise ValidationError('Invalid reset password link information')
            if timezone.now() > reset_link.expires_on:
                raise ValidationError(
                    'Reset password link has expired, please request another one'
                )
            try:
                validate_password(attrs['password'])
            except Exception as e:
                raise ValidationError(str(e))
            return attrs

    validator_class = Validator
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        self.check_permissions(request)
        validator = self.get_validator(data=request.data)
        validator.is_valid(raise_exception=True)
        data = validator.validated_data
        user = User.objects.filter(email=data['email']).first()
        user.set_password(data['password'])
        user.email_verified = True
        user.save(update_fields=['password', 'email_verified'])
        # delete auth token
        try:
            user.auth_token.delete()
        except ObjectDoesNotExist:
            pass
        # now delete the reset password link
        ResetPasswordLink.objects.filter(email=data['email']).delete()
        return Response(status=status.HTTP_200_OK)


class ChangePasswordView(CreateAPIView):
    class Validator(serializers.Serializer):
        current_password = serializers.CharField(required=True)
        new_password = serializers.CharField(required=True)

        def validate_new_password(self, value):
            try:
                validate_password(value)
            except Exception as e:
                raise ValidationError(str(e))
            return value

    permission_classes = (IsAuthenticated,)
    validator_class = Validator

    def get_object(self):
        return self.request.user

    def post(self, request, *args, **kwargs):
        self.check_permissions(request)
        validator = self.get_validator(data=request.data)
        validator.is_valid(raise_exception=True)
        data = validator.validated_data
        user = self.get_object()
        if user.check_password(data['current_password']):
            user.set_password(data['new_password'])
            user.save()
        else:
            raise ValidationError('Invalid existing password')
        return Response(status=status.HTTP_200_OK)
