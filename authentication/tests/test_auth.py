import time
from datetime import timedelta

from authentication.models import User
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework_simplejwt.tokens import RefreshToken

from webservices.test_utils import BaseJWTAPITestCase


class TestJWTAuth(BaseJWTAPITestCase):
    def setUp(self):
        self.email = "test_user"
        self.eng_password = "test_password"
        self.user = User.objects.create_user(
            username=self.email,
            email=self.email,
            password=self.eng_password,
        )

    def test_cannot_access_without_jwt_token(self):
        url = reverse('auth_profile')
        response = self.client.get(path=url)
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)

    def test_direct_jwt_authentication(self):
        self.authenticate_with_generated_token(self.user)
        url = reverse('auth_profile')
        response = self.client.get(path=url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_token_obtain_pair(self):
        url = reverse('token_obtain_pair')
        response = self.client.post(
            url, data=dict(username=self.email, password=self.eng_password)
        )
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_reject_bad_credentials(self):
        url = reverse('token_obtain_pair')
        response = self.client.post(
            url, data=dict(username=self.email, password='other_password')
        )
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)

    def test_token_refresh(self):
        refresh_token = self.authenticate_with_generated_token(self.user)
        url = reverse('token_refresh')
        response = self.client.post(url, data=dict(refresh=str(refresh_token)))
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertIn('access', response.data)

    def test_token_refresh_with_expired_token(self):
        old_lifetime = RefreshToken.lifetime
        RefreshToken.lifetime = timedelta(seconds=1)
        refresh_token = RefreshToken.for_user(self.user)
        RefreshToken.lifetime = old_lifetime
        time.sleep(1)

        self.authenticate_with_access_token(str(refresh_token.access_token))
        url = reverse('token_refresh')
        response = self.client.post(url, data=dict(refresh=str(refresh_token)))
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)
