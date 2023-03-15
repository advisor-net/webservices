from authentication.factories import (
    IndustryFactory,
    JobTitleFactory,
    MetropolitanAreaFactory,
    UserFactory,
)
from authentication.models import Industry, JobTitle, MetropolitanArea
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase


class TestListMetropolitanAreas(APITestCase):
    def setUp(self):
        self.user = UserFactory()
        self.client.force_authenticate(self.user)
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

    def test_list_from_id_values(self):
        m1 = MetropolitanArea.objects.get(name='Tech1')
        m2 = MetropolitanArea.objects.get(name='Tech2')
        response = self.client.get(
            self.url, data=dict(id__in=','.join([str(m1.id), str(m2.id)]))
        )
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        data = response.data
        self.assertEqual(2, len(data['results']))
        self.assertEqual(data['results'][0]['name'], m1.name)
        self.assertEqual(data['results'][1]['name'], m2.name)


class TestListIndustries(APITestCase):
    def setUp(self):
        self.user = UserFactory()
        self.client.force_authenticate(self.user)
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

    def test_list_from_id_values(self):
        m1 = Industry.objects.get(name='Tech1')
        m2 = Industry.objects.get(name='Tech2')
        response = self.client.get(
            self.url, data=dict(id__in=','.join([str(m1.id), str(m2.id)]))
        )
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        data = response.data
        self.assertEqual(2, len(data['results']))
        self.assertEqual(data['results'][0]['name'], m1.name)
        self.assertEqual(data['results'][1]['name'], m2.name)


class TestListJobTitles(APITestCase):
    def setUp(self):
        self.user = UserFactory()
        self.client.force_authenticate(self.user)
        self.url = reverse('job_title_list')
        to_create = []
        for i in range(25):
            to_create.append(JobTitleFactory.build(name=f'Manager{i}'))
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

    def test_search(self):
        response = self.client.get(self.url, data=dict(search='24'))
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        data = response.data
        self.assertEqual(1, len(data['results']))

    def test_list_from_id_values(self):
        m1 = JobTitle.objects.get(name='Manager1')
        m2 = JobTitle.objects.get(name='Manager2')
        response = self.client.get(
            self.url, data=dict(id__in=','.join([str(m1.id), str(m2.id)]))
        )
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        data = response.data
        self.assertEqual(2, len(data['results']))
        self.assertEqual(data['results'][0]['name'], m1.name)
        self.assertEqual(data['results'][1]['name'], m2.name)
