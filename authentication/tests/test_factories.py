from authentication.factories import UserFactory
from authentication.models import User
from django.test import TestCase


class TestFactoriesTestCase(TestCase):
    def test_user_factory(self):
        UserFactory()
        user = User.objects.get()
        self.assertIsNotNone(user.inc_total_annual)
        self.assertIsNotNone(user.net_monthly_profit_loss)
        self.assertIsNotNone(user.assets_total)
        self.assertIsNotNone(user.lia_total)
        self.assertIsNotNone(user.net_worth)
