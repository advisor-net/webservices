from authentication.factories import (
    IndustryFactory,
    JobTitleFactory,
    MetropolitanAreaFactory,
    UserFactory,
)
from authentication.models import User
from rest_framework import status
from rest_framework.reverse import reverse

from webservices.test_utils import BaseJWTAPITestCase


class TestListUsers(BaseJWTAPITestCase):
    def setUp(self):
        self.user = UserFactory()
        self.authenticate_with_generated_token(self.user)
        self.url = reverse('user_list')

    def test_list_pagination(self):
        UserFactory.create_batch(25, age=25)
        response = self.client.get(self.url, data=dict(age__gt=21))
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        data = response.data
        self.assertEqual(25, data['count'])
        self.assertEqual(20, len(data['results']))

        response = self.client.get(self.url, data=dict(age__gt=21, page=2))
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        data = response.data
        self.assertEqual(25, data['count'])
        self.assertEqual(5, len(data['results']))

        response = self.client.get(self.url, data=dict(age__gt=21, page_size=25))
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        data = response.data
        self.assertEqual(25, data['count'])
        self.assertEqual(25, len(data['results']))

    def test_list_ordering(self):
        ind1 = IndustryFactory(name='Tech')
        ind2 = IndustryFactory(name='Manufacturing')
        UserFactory(age=21, industry=ind1)
        UserFactory(age=22, industry=ind1)
        UserFactory(age=23, industry=ind2)
        order_key = 'age'
        response = self.client.get(self.url, data=dict(order_by=order_key))
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        data = response.data
        self.assertGreater(
            data['results'][-1][order_key], data['results'][0][order_key]
        )

        response = self.client.get(self.url, data=dict(order_by=f'-{order_key}'))
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        data = response.data
        self.assertLess(data['results'][-1][order_key], data['results'][0][order_key])

        order_key = 'net_worth'
        convert = float
        response = self.client.get(self.url, data=dict(order_by=order_key))
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        data = response.data
        self.assertGreater(
            convert(data['results'][-1][order_key]),
            convert(data['results'][0][order_key]),
        )

        response = self.client.get(self.url, data=dict(order_by=f'-{order_key}'))
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        data = response.data
        self.assertLess(
            convert(data['results'][-1][order_key]),
            convert(data['results'][0][order_key]),
        )

        order_key = 'industry__name'
        response = self.client.get(self.url, data=dict(order_by=order_key))
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        data = response.data
        self.assertGreater(
            data['results'][-1]['industry']['name'],
            data['results'][0]['industry']['name'],
        )

        response = self.client.get(self.url, data=dict(order_by=f'-{order_key}'))
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        data = response.data
        self.assertLess(
            data['results'][-1]['industry']['name'],
            data['results'][0]['industry']['name'],
        )

    def test_list_multi_filters(self):
        UserFactory(age=21, level=User.LevelChoices.IC.value, inc_primary_annual=100000)
        UserFactory(
            age=23, level=User.LevelChoices.IC_ASSOCIATE.value, inc_primary_annual=90000
        )
        UserFactory(
            age=23, level=User.LevelChoices.MANAGER.value, inc_primary_annual=100000
        )
        UserFactory(
            age=30, level=User.LevelChoices.DIRECTOR.value, inc_primary_annual=120000
        )
        response = self.client.get(
            self.url,
            data=dict(
                age__gte=23,
                level__gte=User.LevelChoices.MANAGER.value,
                inc_primary_annual__gt=110000,
                order_by='age',
            ),
        )
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        data = response.data
        self.assertEqual(1, len(data['results']))

    def assertNumericFieldFiltersWork(
        self, field_name, low_value, high_value, computed=False
    ):
        u1 = UserFactory(**{field_name: low_value})
        u2 = UserFactory(**{field_name: high_value})
        if computed:
            # need to circumvent the auto recompute behavior on save
            User.objects.filter(id=u1.id).update(**{field_name: low_value})
            User.objects.filter(id=u2.id).update(**{field_name: high_value})
        response = self.client.get(self.url, data={f'{field_name}__lt': high_value})
        self.assertEqual(1, len(response.data['results']))
        response = self.client.get(self.url, data={f'{field_name}__lte': high_value})
        self.assertEqual(2, len(response.data['results']))
        response = self.client.get(self.url, data={f'{field_name}__gt': low_value})
        self.assertEqual(1, len(response.data['results']))
        response = self.client.get(self.url, data={f'{field_name}__gte': low_value})
        self.assertEqual(2, len(response.data['results']))
        User.objects.filter(id__in=[u1.id, u2.id]).delete()

    def assertInFilterWorks(self, field_name, value1, value2):
        u1 = UserFactory(**{field_name: value1})
        u2 = UserFactory(**{field_name: value2})
        response = self.client.get(self.url, data={f'{field_name}__in': value1})
        self.assertEqual(1, len(response.data['results']))
        response = self.client.get(self.url, data={f'{field_name}__in': value2})
        self.assertEqual(1, len(response.data['results']))
        response = self.client.get(
            self.url, data={f'{field_name}__in': ','.join([str(value1), str(value2)])}
        )
        self.assertEqual(2, len(response.data['results']))
        User.objects.filter(id__in=[u1.id, u2.id]).delete()

    def assertFkInFilterWorks(
        self, filter_name, fk_name, factory_class, value1, value2
    ):
        f1 = factory_class(name=value1)
        f2 = factory_class(name=value2)
        u1 = UserFactory(**{fk_name: f1})
        u2 = UserFactory(**{fk_name: f2})
        response = self.client.get(self.url, data={f'{filter_name}__in': f1.id})
        self.assertEqual(1, len(response.data['results']))
        response = self.client.get(self.url, data={f'{filter_name}__in': f2.id})
        self.assertEqual(1, len(response.data['results']))
        response = self.client.get(
            self.url, data={f'{filter_name}__in': ','.join([str(f1.id), str(f2.id)])}
        )
        self.assertEqual(2, len(response.data['results']))
        User.objects.filter(id__in=[u1.id, u2.id]).delete()

    def test_list_filters_numeric_fields(self):
        self.assertNumericFieldFiltersWork('age', 21, 23)
        self.assertNumericFieldFiltersWork('inc_primary_annual', 10000, 20000)
        self.assertNumericFieldFiltersWork('inc_variable_monthly', 1000, 2000)
        self.assertNumericFieldFiltersWork('inc_secondary_monthly', 1000, 2000)
        self.assertNumericFieldFiltersWork('exp_housing', 1000, 2000)
        self.assertNumericFieldFiltersWork(
            'level', User.LevelChoices.IC.value, User.LevelChoices.DIRECTOR.value
        )
        self.assertInFilterWorks(
            'level', User.LevelChoices.IC.value, User.LevelChoices.DIRECTOR.value
        )

    def test_list_filters_computed_fields(self):
        self.assertNumericFieldFiltersWork(
            'inc_total_annual', 10000, 20000, computed=True
        )
        self.assertNumericFieldFiltersWork(
            'net_monthly_profit_loss', -500, 500, computed=True
        )
        self.assertNumericFieldFiltersWork('assets_total', 10000, 20000, computed=True)
        self.assertNumericFieldFiltersWork('lia_total', 10000, 20000, computed=True)
        self.assertNumericFieldFiltersWork('net_worth', 100000, 200000, computed=True)

    def test_list_filters_fk_fields(self):
        self.assertFkInFilterWorks(
            'metro',
            'metro',
            MetropolitanAreaFactory,
            'Boston',
            'New York',
        )
        self.assertFkInFilterWorks(
            'industry',
            'industry',
            IndustryFactory,
            'Finance',
            'Tech',
        )
        self.assertFkInFilterWorks(
            'job_title',
            'job_title',
            JobTitleFactory,
            'Janitor',
            'Zamboni Driver',
        )

    def test_list_filters_string_fields(self):
        self.assertInFilterWorks(
            'gender', User.GenderChoices.MALE.value, User.GenderChoices.FEMALE.value
        )
        self.assertInFilterWorks(
            'current_pfm',
            User.CurrentPFMChoices.MINT.value,
            User.CurrentPFMChoices.ROCKET_MONEY.value,
        )

    def test_search_by_handle(self):
        UserFactory(handle='other_name1')
        UserFactory(handle='other_name2')
        UserFactory(handle='other_name3')
        response = self.client.get(self.url, data=dict(search="other_name"))
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(3, len(response.data['results']))
