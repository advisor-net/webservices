from authentication.factories import UserFactory
from authentication.models import SignUpLink, User, VerifyEmailLink
from django.test import override_settings
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase


@override_settings(SEND_EMAILS=False)
class TestSignup(APITestCase):
    def setUp(self):
        self.email = "new_email@advisor.place"
        self.link = SignUpLink.objects.create(email=self.email)

    def test_signup_and_verify_email(self):
        url = reverse('sign_up')
        data = dict(
            sign_up_link_uuid=str(self.link.uuid),
            email=self.email,
            password='Password!123',
        )
        response = self.client.post(url, data=data)
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        user = User.objects.get(email=self.email)
        verify_link = VerifyEmailLink.objects.filter(user=user).first()
        self.assertIsNotNone(verify_link)
        self.assertFalse(user.email_verified)

        self.assertEqual(0, SignUpLink.objects.filter(email=self.email).count())

        self.client.force_authenticate(user)
        url = reverse('verify_email')
        data = dict(verify_link_uuid=str(verify_link.uuid))
        response = self.client.post(url, data=data)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        user.refresh_from_db()
        self.assertTrue(user.email_verified)
        self.assertEqual(
            0, VerifyEmailLink.objects.filter(uuid=verify_link.uuid).count()
        )

    def test_cannot_signup_with_different_email(self):
        url = reverse('sign_up')
        data = dict(
            sign_up_link_uuid=str(self.link.uuid),
            email='other_email@advisor.place',
            password='Password!123',
        )
        response = self.client.post(url, data=data)
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_cannot_signup_with_bad_password(self):
        url = reverse('sign_up')
        data = dict(
            sign_up_link_uuid=str(self.link.uuid), email=self.email, password='password'
        )
        response = self.client.post(url, data=data)
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_resend_email_verification(self):
        user = UserFactory()
        self.client.force_authenticate(user)
        url = reverse('resend_email_verification')
        response = self.client.post(url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        verify_link = VerifyEmailLink.objects.filter(user=user).first()
        self.assertIsNotNone(verify_link)
