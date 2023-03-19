from datetime import timedelta

from authentication.models import ResetPasswordLink, User
from django.core.exceptions import ObjectDoesNotExist
from django.test import override_settings
from django.utils import timezone
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase


@override_settings(SEND_EMAILS=False)
class TestResetPassword(APITestCase):
    def setUp(self):
        self.email = "test_user@advisor.place"
        self.eng_password = "test_password"
        self.user = User.objects.create_user(
            username=self.email,
            email=self.email,
            password=self.eng_password,
        )

    def test_request_reset(self):
        url = reverse('request_password_reset')
        data = dict(email=self.user.email)
        response = self.client.post(url, data=data)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(
            1, ResetPasswordLink.objects.filter(email=self.user.email).count()
        )

    def test_reset_password(self):
        # go through login flow to get an auth token created
        url = reverse('api_token_auth')
        response = self.client.post(
            url, data=dict(username=self.email, password=self.eng_password)
        )
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.user.refresh_from_db()
        self.assertIsNotNone(self.user.auth_token)

        # now go through reset flow
        reset_link = ResetPasswordLink.objects.create(
            email=self.user.email, expires_on=timezone.now() + timedelta(days=1)
        )
        url = reverse('reset_password')
        data = dict(
            reset_link_uuid=str(reset_link.uuid),
            email=self.user.email,
            password="NewPassword!123",
        )
        response = self.client.post(url, data=data)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(
            0, ResetPasswordLink.objects.filter(email=self.user.email).count()
        )
        self.user.refresh_from_db()
        self.assertTrue(self.user.email_verified)
        with self.assertRaises(ObjectDoesNotExist):
            self.user.auth_token

    def test_does_not_work_if_reset_link_expired(self):
        reset_link = ResetPasswordLink.objects.create(
            email=self.user.email, expires_on=timezone.now() - timedelta(minutes=5)
        )
        url = reverse('reset_password')
        data = dict(
            reset_link_uuid=str(reset_link.uuid),
            email=self.user.email,
            password="NewPassword!123",
        )
        response = self.client.post(url, data=data)
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_do_not_reveal_email(self):
        url = reverse('request_password_reset')
        data = dict(email='random_email@advisor.place')
        response = self.client.post(url, data=data)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(
            0,
            ResetPasswordLink.objects.filter(
                email='random_email@advisor.place'
            ).count(),
        )

    def test_cannot_reset_to_bad_password(self):
        reset_link = ResetPasswordLink.objects.create(
            email=self.user.email, expires_on=timezone.now() + timedelta(days=1)
        )
        url = reverse('reset_password')
        data = dict(
            reset_link_uuid=str(reset_link.uuid),
            email=self.user.email,
            password="password",
        )
        response = self.client.post(url, data=data)
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_cannot_reset_without_uuid_and_email_pair(self):
        reset_link = ResetPasswordLink.objects.create(
            email=self.user.email, expires_on=timezone.now() + timedelta(days=1)
        )
        url = reverse('reset_password')
        data = dict(
            reset_link_uuid=str(reset_link.uuid),
            email='other_email@advisor.place',
            password="password",
        )
        response = self.client.post(url, data=data)
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
