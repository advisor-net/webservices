from authentication.models import WaitListEntry
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase


class TestWaitlist(APITestCase):
    def setUp(self):
        self.url = reverse('waitlist')
        self.email = 'new_email@advisor.place'

    def test_join_waitlist(self):
        data = dict(
            email=self.email,
            how_did_you_hear_about_us="Internet",
            why_do_you_want_to_join="money",
        )
        response = self.client.post(self.url, data=data)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(1, WaitListEntry.objects.filter(email=self.email).count())

    def test_join_get_or_create_waitlist(self):
        data = dict(
            email=self.email,
            how_did_you_hear_about_us="Internet",
            why_do_you_want_to_join="money",
        )
        WaitListEntry.objects.create(**data)
        response = self.client.post(self.url, data=data)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(1, WaitListEntry.objects.filter(email=self.email).count())
