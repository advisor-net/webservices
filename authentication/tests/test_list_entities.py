from authentication.factories import (
    IndustryFactory,
    JobTitleFactory,
    MetropolitanAreaFactory,
    UserFactory,
)
from authentication.models import Industry, JobTitle, MetropolitanArea
from rest_framework import status
from rest_framework.reverse import reverse

from webservices.test_utils import BaseJWTAPITestCase


class TestListMetropolitanAreas(BaseJWTAPITestCase):
    def setUp(self):
        self.user = UserFactory()
        self.authenticate_with_generated_token(self.user)
        self.url = reverse('metro_list')
        to_create = []
        for i in range(25):
            to_create.append(MetropolitanAreaFactory.build(name=f'Tech{i}'))
        MetropolitanArea.objects.bulk_create(to_create)

    def test_list_metros_pagination(self):
        response = self.client.get(self.url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        data = response.data
        self.assertEqual(20, len(data['results']))

        response = self.client.get(self.url, data=dict(page_size=50))
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        data = response.data
        self.assertEqual(26, len(data['results']))

    def test_search(self):
        response = self.client.get(self.url, data=dict(search='24'))
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        data = response.data
        self.assertEqual(1, len(data['results']))


class TestListIndustries(BaseJWTAPITestCase):
    def setUp(self):
        self.user = UserFactory()
        self.authenticate_with_generated_token(self.user)
        self.url = reverse('industry_list')
        to_create = []
        for i in range(25):
            to_create.append(IndustryFactory.build(name=f'Tech{i}'))
        Industry.objects.bulk_create(to_create)

    def test_list_industries_pagination(self):
        response = self.client.get(self.url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        data = response.data
        self.assertEqual(20, len(data['results']))

        response = self.client.get(self.url, data=dict(page_size=50))
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        data = response.data
        self.assertEqual(26, len(data['results']))

    def test_search(self):
        response = self.client.get(self.url, data=dict(search='24'))
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        data = response.data
        self.assertEqual(1, len(data['results']))


class TestListJobTitles(BaseJWTAPITestCase):
    def setUp(self):
        self.user = UserFactory()
        self.authenticate_with_generated_token(self.user)
        self.url = reverse('job_title_list')
        to_create = []
        self.ind1 = IndustryFactory(name='Tech')
        ind2 = IndustryFactory(name='Manufacturing')
        for i in range(25):
            if i % 2 == 0:
                ind = self.ind1
            else:
                ind = ind2
            to_create.append(JobTitleFactory.build(name=f'Manager{i}', industry=ind))
        JobTitle.objects.bulk_create(to_create)

    def test_list_industries_pagination(self):
        response = self.client.get(self.url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        data = response.data
        self.assertEqual(20, len(data['results']))

        response = self.client.get(self.url, data=dict(page_size=50))
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        data = response.data
        self.assertEqual(26, len(data['results']))

    def test_industry_filter(self):
        response = self.client.get(self.url, data=dict(industry=self.ind1.name))
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        data = response.data
        self.assertEqual(13, len(data['results']))

    def test_search(self):
        response = self.client.get(self.url, data=dict(search='24'))
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        data = response.data
        self.assertEqual(1, len(data['results']))
