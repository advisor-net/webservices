from authentication.models import User
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase


class TestTokenAuth(APITestCase):
    def setUp(self):
        self.email = "test_user"
        self.eng_password = "test_password"
        self.user = User.objects.create_user(
            username=self.email,
            email=self.email,
            password=self.eng_password,
        )

    def test_cannot_access_without_token(self):
        url = reverse('auth_profile')
        response = self.client.get(path=url)
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)

    def test_login(self):
        url = reverse('api_token_auth')
        response = self.client.post(
            url, data=dict(username=self.email, password=self.eng_password)
        )
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {response.data['token']}")
        url = reverse('auth_profile')
        response = self.client.get(path=url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_reject_bad_credentials(self):
        url = reverse('api_token_auth')
        response = self.client.post(
            url, data=dict(username=self.email, password='other_password')
        )
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_logout(self):
        url = reverse('api_token_auth')
        response = self.client.post(
            url, data=dict(username=self.email, password=self.eng_password)
        )
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {response.data['token']}")
        url = reverse('auth_profile')
        response = self.client.get(path=url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        url = reverse('logout')
        response = self.client.delete(path=url)
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)
        url = reverse('auth_profile')
        response = self.client.get(path=url)
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)

    def test_force_authenticate(self):
        self.client.force_authenticate(self.user)
        url = reverse('auth_profile')
        response = self.client.get(path=url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_change_password_success(self):
        self.client.force_authenticate(self.user)
        url = reverse('change_password')
        data = dict(current_password=self.eng_password, new_password="NewPassword!123")
        response = self.client.post(path=url, data=data)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        url = reverse('api_token_auth')
        response = self.client.post(
            url, data=dict(username=self.email, password=self.eng_password)
        )
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        response = self.client.post(
            url, data=dict(username=self.email, password="NewPassword!123")
        )
        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_change_password_unsuccessful_with_bad_current_password(self):
        self.client.force_authenticate(self.user)
        url = reverse('change_password')
        data = dict(current_password="wrong password", new_password="NewPassword!123")
        response = self.client.post(url, data=data)
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_change_password_unsuccessful_with_bad_new_password(self):
        self.client.force_authenticate(self.user)
        url = reverse('change_password')
        data = dict(current_password=self.eng_password, new_password="password")
        response = self.client.post(url, data=data)
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
