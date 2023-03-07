import random
import time

from authentication.factories import UserFactory
from authentication.models import Industry, JobTitle, MetropolitanArea, User
from django.conf import settings
from django.db import transaction

METRO_AREAS = [
    "New York-Newark-Jersey City, NY-NJ-PA",
    "Chicago-Naperville-Elgin, IL-IN-WI",
    "Dallas-Fort Worth-Arlington, TX",
    "Miami-Fort Lauderdale-West Palm Beach, FL",
    "Boston-Cambridge-Newton, MA-NH",
]

INDUSTRIES = ['SaaS Software', 'Consulting', 'Finance', 'Manufacturing', 'Real Estate']

JOB_TITLES = [
    'Engineer',
    'Product Manager',
    'Account Executive',
    'Analyst',
    'Project Manager',
]


def wipe_database():
    assert settings.IS_LOCAL
    MetropolitanArea.objects.all().delete()
    JobTitle.objects.all().delete()
    Industry.objects.all().delete()
    User.objects.filter(is_superuser=False).delete()


def build_entities():
    metros = []
    for area in METRO_AREAS:
        metros.append(MetropolitanArea(name=area))
    MetropolitanArea.objects.bulk_create(metros)

    industries = []
    for industry_name in INDUSTRIES:
        industries.append(Industry(name=industry_name))
    Industry.objects.bulk_create(industries)

    job_titles = []
    for title in JOB_TITLES:
        job_titles.append(JobTitle(name=title))
    JobTitle.objects.bulk_create(job_titles)

    return metros, industries, job_titles


# TODO: come back and make this actually realistic
#  make hard side more sparse and have salaries and investments reflect position and level
@transaction.atomic
def build_simulated_dataset(users_per_metro=1000):
    t1 = time.time()
    wipe_database()
    metros, indutries, job_titles = build_entities()

    users = []
    for metro in metros:
        for i in range(users_per_metro):
            u = UserFactory.build(
                metro=metro,
                job_title=random.choice(job_titles),
                industry=random.choice(indutries),
            )
            u.recompute_fields()
            users.append(u)
    User.objects.bulk_create(users, batch_size=1000)
    print(f'Simulation building time: {round(time.time() - t1, 2)} seconds')
