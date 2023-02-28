from decimal import Decimal

from authentication.factories import (
    EmptyUserFactory,
    JobTitleFactory,
    MetropolitanAreaFactory,
    UserFactory,
)
from authentication.models import User
from rest_framework import status
from rest_framework.reverse import reverse

from webservices.test_utils import BaseJWTAPITestCase


class TestUpdateHandle(BaseJWTAPITestCase):
    def setUp(self):
        self.user = EmptyUserFactory()
        self.authenticate_with_generated_token(self.user)

    def test_check_handle_availability(self):
        url = reverse('check_handle')
        response = self.client.post(url, data=dict(handle='player1'))
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertTrue(response.data['available'])

        UserFactory(handle='new_handle')
        response = self.client.post(url, data=dict(handle='new_handle'))
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertFalse(response.data['available'])

    def test_update_handle(self):
        url = reverse('update_handle')
        response = self.client.patch(url, data=dict(handle='new_handle'))
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.user.refresh_from_db()
        self.assertEqual(self.user.handle, 'new_handle')

    def test_cannot_update_handle_if_conflicts_with_existing(self):
        EmptyUserFactory(handle='existing_handle')
        url = reverse('update_handle')
        response = self.client.patch(url, data=dict(handle='existing_handle'))
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_handle_is_valid(self):
        url = reverse('check_handle')
        response = self.client.post(url, data=dict(handle='Not identifier'))
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

        url = reverse('update_handle')
        response = self.client.patch(url, data=dict(handle='Not identifier'))
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)


class TestUpdateProfile(BaseJWTAPITestCase):
    def setUp(self):
        self.user = UserFactory(
            age=20,
            gender=User.GenderChoices.FEMALE.value,
            level=User.LevelChoices.IC_ASSOCIATE.value,
            current_pfm=User.CurrentPFMChoices.MINT.value,
            inc_primary_annual=Decimal('110000'),
            inc_primary_tax_fed=0.2,
            inc_primary_tax_state=0.2,
            inc_variable_monthly=Decimal('11000'),
            inc_variable_tax_fed=0.2,
            inc_variable_tax_state=0.2,
            inc_secondary_monthly=Decimal('11000'),
            inc_secondary_tax_fed=0.2,
            inc_secondary_tax_state=0.2,
            exp_housing=Decimal('1100'),
            exp_other_fixed=Decimal('1100'),
            exp_other_variable=Decimal('1100'),
            sav_retirement=Decimal('1100'),
            sav_market=Decimal('1100'),
            assets_savings=Decimal('1100'),
            assets_property=Decimal('1100'),
            assets_misc=Decimal('1100'),
            lia_loans=Decimal('1100'),
            lia_credit_card=Decimal('1100'),
            lia_misc=Decimal('1100'),
        )
        self.authenticate_with_generated_token(self.user)
        self.url = reverse('user_detail')

    def test_get_details(self):
        response = self.client.get(self.url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(self.user.email, response.data['email'])

    def test_partial_update_profile_info(self):
        old_user = User.objects.get()
        new_metro = MetropolitanAreaFactory()
        new_job = JobTitleFactory()
        payload = dict(
            age=25,
            gender=User.GenderChoices.MALE.value,
            metro=new_metro.id,
            industry=new_job.industry.id,
            job_title=new_job.id,
            level=User.LevelChoices.IC.value,
            current_pfm=User.CurrentPFMChoices.PEN_PAPER.value,
        )
        response = self.client.patch(self.url, data=payload)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        refreshed_user = User.objects.get()
        self.assertEqual(refreshed_user.age, 25)
        self.assertEqual(refreshed_user.gender, User.GenderChoices.MALE.value)
        self.assertEqual(refreshed_user.metro, new_metro)
        self.assertEqual(refreshed_user.industry, new_job.industry)
        self.assertEqual(refreshed_user.job_title, new_job)
        self.assertEqual(refreshed_user.level, User.LevelChoices.IC.value)
        self.assertEqual(
            refreshed_user.current_pfm, User.CurrentPFMChoices.PEN_PAPER.value
        )
        # ensure other fields were NOT updated
        self.assertEqual(refreshed_user.handle, old_user.handle)
        self.assertEqual(refreshed_user.inc_primary_annual, old_user.inc_primary_annual)
        self.assertEqual(refreshed_user.assets_savings, old_user.assets_savings)

    def test_partial_update_income_statement(self):
        old_user = User.objects.get()
        payload = dict(
            inc_primary_annual='120000',
            inc_primary_tax_fed=0.1,
            inc_primary_tax_state=0.1,
            inc_variable_monthly='10000',
            inc_variable_tax_fed=0.1,
            inc_variable_tax_state=0.1,
            inc_secondary_monthly='10000',
            inc_secondary_tax_fed=0.1,
            inc_secondary_tax_state=0.1,
            exp_housing='1000',
            exp_other_fixed='1000',
            exp_other_variable='1000',
            sav_retirement='1000',
            sav_market='1000',
        )
        response = self.client.patch(self.url, data=payload)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        refreshed_user = User.objects.get()
        self.assertEqual(refreshed_user.inc_primary_annual, Decimal('120000'))
        self.assertEqual(refreshed_user.inc_primary_tax_fed, 0.1)
        self.assertEqual(refreshed_user.inc_primary_tax_state, 0.1)
        self.assertEqual(refreshed_user.inc_variable_monthly, Decimal('10000'))
        self.assertEqual(refreshed_user.inc_variable_tax_fed, 0.1)
        self.assertEqual(refreshed_user.inc_variable_tax_state, 0.1)
        self.assertEqual(refreshed_user.inc_secondary_monthly, Decimal('10000'))
        self.assertEqual(refreshed_user.inc_secondary_tax_fed, 0.1)
        self.assertEqual(refreshed_user.inc_secondary_tax_state, 0.1)
        self.assertEqual(refreshed_user.exp_housing, Decimal('1000'))
        self.assertEqual(refreshed_user.exp_other_fixed, Decimal('1000'))
        self.assertEqual(refreshed_user.exp_other_variable, Decimal('1000'))
        self.assertEqual(refreshed_user.sav_retirement, Decimal('1000'))
        self.assertEqual(refreshed_user.sav_market, Decimal('1000'))
        self.assertNotEqual(
            refreshed_user.net_monthly_profit_loss, old_user.net_monthly_profit_loss
        )
        # ensure other fields were NOT updated
        self.assertEqual(refreshed_user.handle, old_user.handle)
        self.assertEqual(refreshed_user.gender, old_user.gender)
        self.assertEqual(refreshed_user.assets_savings, old_user.assets_savings)

    def test_partial_update_net_worth(self):
        old_user = User.objects.get()
        payload = dict(
            assets_savings='100000',
            assets_property='1000',
            assets_misc='1000',
            lia_loans='1000',
            lia_credit_card='1000',
            lia_misc='1000',
        )
        response = self.client.patch(self.url, data=payload)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        refreshed_user = User.objects.get()
        self.assertEqual(refreshed_user.assets_savings, Decimal('100000'))
        self.assertEqual(refreshed_user.assets_property, Decimal('1000'))
        self.assertEqual(refreshed_user.assets_misc, Decimal('1000'))
        self.assertEqual(refreshed_user.lia_loans, Decimal('1000'))
        self.assertEqual(refreshed_user.lia_credit_card, Decimal('1000'))
        self.assertEqual(refreshed_user.lia_misc, Decimal('1000'))
        self.assertNotEqual(refreshed_user.assets_total, old_user.assets_total)
        self.assertNotEqual(refreshed_user.net_worth, old_user.net_worth)
        # ensure other fields were NOT updated
        self.assertEqual(refreshed_user.handle, old_user.handle)
        self.assertEqual(refreshed_user.gender, old_user.gender)
        self.assertEqual(refreshed_user.inc_primary_annual, old_user.inc_primary_annual)

    def test_bad_fields(self):
        payload = dict(age='dfvfdvfsd')
        response = self.client.patch(self.url, data=payload)
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_cannot_change_handle(self):
        payload = dict(handle='different handle', age=30)
        response = self.client.patch(self.url, data=payload)
        refreshed_user = User.objects.get()
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertNotEqual(refreshed_user.handle, payload['handle'])
        self.assertEqual(refreshed_user.age, payload['age'])
