import random
import string
from decimal import Decimal

import factory
from authentication.models import Industry, JobTitle, MetropolitanArea, User
from faker import Faker
from faker.providers import company, internet, misc

fake = Faker()
factory.Faker.add_provider(internet)
factory.Faker.add_provider(company)
factory.Faker.add_provider(misc)


class MetropolitanAreaFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = MetropolitanArea
        django_get_or_create = ('name',)

    name = factory.Faker(
        'random_element',
        elements=[
            "New York-Newark-Jersey City, NY-NJ-PA",
            "Los Angeles-Long Beach-Anaheim, CA",
            "Chicago-Naperville-Elgin, IL-IN-WI",
            "Dallas-Fort Worth-Arlington, TX",
            "Houston-The Woodlands-Sugar Land, TX",
            "Washington-Arlington-Alexandria, DC-VA-MD-WV",
            "Philadelphia-Camden-Wilmington, PA-NJ-DE-MD",
            "Miami-Fort Lauderdale-West Palm Beach, FL",
            "Atlanta-Sandy Springs-Alpharetta, GA",
            "Boston-Cambridge-Newton, MA-NH",
        ],
    )


class IndustryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Industry
        django_get_or_create = ('name',)

    name = factory.Faker(
        'random_element',
        elements=[
            "Transportation",
            "Real Estate",
            "Software",
            "Consulting",
            "Finance",
        ],
    )


class JobTitleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = JobTitle
        django_get_or_create = ('name', 'industry')

    name = factory.Faker(
        'random_element',
        elements=[
            "Engineer",
            "Manager",
            "Analyst",
            "Consultant",
            "Associate",
        ],
    )
    industry = factory.SubFactory(IndustryFactory)


class EmptyUserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
        django_get_or_create = ('email',)

    email = factory.lazy_attribute(
        lambda u: ''.join(
            random.choice(string.ascii_letters + string.digits) for _ in range(12)
        )
        + f'@{fake.free_email_domain()}'
    )
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    password = factory.Faker(
        'password', length=8, digits=True, upper_case=True, lower_case=True
    )
    is_active = True
    is_staff = False
    is_superuser = False

    @factory.lazy_attribute
    def username(self):
        return self.email


class UserFactory(EmptyUserFactory):
    handle = factory.Sequence(lambda n: f'hockeyman{n}')
    age = factory.Faker('random_int', min=21, max=70)
    gender = factory.Faker('random_element', elements=User.GenderChoices.values)
    metro = factory.SubFactory(MetropolitanAreaFactory)
    industry = factory.SubFactory(IndustryFactory)
    level = factory.Faker('random_element', elements=User.LevelChoices.values)
    current_pfm = factory.Faker(
        'random_element', elements=User.CurrentPFMChoices.values
    )

    # income statement
    # income
    inc_primary_annual = factory.LazyAttribute(lambda u: random.randint(20, 200) * 1000)
    inc_primary_tax_fed = 20
    inc_primary_tax_state = 5
    inc_variable_monthly = factory.LazyAttribute(lambda u: random.randint(0, 10) * 100)
    inc_variable_tax_fed = 20
    inc_variable_tax_state = 5
    inc_secondary_monthly = factory.LazyAttribute(lambda u: random.randint(0, 10) * 100)
    inc_secondary_tax_fed = 20
    inc_secondary_tax_state = 5
    inc_total_annual = factory.LazyAttribute(
        lambda u: u.inc_primary_annual
        + (u.inc_variable_monthly + u.inc_secondary_monthly) * Decimal('12')
    )
    # monthly expenses
    exp_housing = factory.LazyAttribute(
        lambda user: user.inc_total_annual * Decimal(random.random() * 0.4 / 12)
    )
    exp_other_fixed = factory.LazyAttribute(
        lambda user: user.inc_total_annual * Decimal(random.random() * 0.4 / 12)
    )
    exp_other_variable = factory.LazyAttribute(
        lambda user: user.inc_total_annual * Decimal(random.random() * 0.4 / 12)
    )
    # monthly savings
    sav_retirement = factory.LazyAttribute(
        lambda user: user.inc_total_annual * Decimal(random.random() * 0.2 / 12)
    )
    sav_market = factory.LazyAttribute(
        lambda user: user.inc_total_annual * Decimal(random.random() * 0.1 / 12)
    )
    # computed fields updated in on save method

    # net worth
    # assets
    assets_savings = factory.LazyAttribute(lambda u: random.randint(0, 1000) * 1000)
    assets_property = factory.LazyAttribute(lambda u: random.randint(0, 100) * 1000)
    assets_misc = factory.LazyAttribute(lambda u: random.randint(0, 10) * 1000)
    # liabilities
    lia_loans = factory.LazyAttribute(lambda u: random.randint(0, 10) * 1000)
    lia_credit_card = factory.LazyAttribute(lambda u: random.randint(0, 10) * 1000)
    lia_misc = factory.LazyAttribute(lambda u: random.randint(0, 10) * 1000)
    # computed fields updated in the on save method

    @factory.lazy_attribute
    def job_title(self):
        if self.industry:
            return JobTitleFactory(industry=self.industry)
