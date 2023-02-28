from authentication.models import User
from django.conf import settings
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken


class BaseJWTAPITestCase(APITestCase):
    def authenticate_with_access_token(self, access_token: str):
        self.client.credentials(
            HTTP_AUTHORIZATION=f"{settings.SIMPLE_JWT['AUTH_HEADER_TYPES'][0]} {access_token}"
        )

    def authenticate_with_generated_token(self, user: User) -> RefreshToken:
        refresh_token = RefreshToken.for_user(user)
        self.authenticate_with_access_token(str(refresh_token.access_token))
        return refresh_token
