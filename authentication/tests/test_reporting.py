from authentication.factories import UserFactory
from authentication.models import ReportedMisconduct
from django.test import override_settings
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase


class TestListUsers(APITestCase):
    def setUp(self):
        self.user = UserFactory()
        self.client.force_authenticate(self.user)
        self.other_user = UserFactory()
        self.url = reverse('report_user')

    @override_settings(SEND_EMAILS=False)
    def test_report_user(self):
        response = self.client.post(
            self.url,
            data=dict(
                handle=self.other_user.handle, description="he was mean to me in chat"
            ),
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        report = ReportedMisconduct.objects.first()
        self.assertEqual(report.plaintiff.id, self.user.id)
        self.assertEqual(report.defendant.id, self.other_user.id)
        self.assertEqual(report.description, "he was mean to me in chat")
