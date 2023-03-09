from decimal import Decimal
from typing import List, Optional
from uuid import uuid4

from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import UserManager as BaseUserManager
from django.db import models

from webservices.models import SoftDeleteModelMixin, TimeStampedModel


class MetropolitanArea(TimeStampedModel):
    name: str = models.CharField(max_length=128, blank=False, null=False, unique=True)


class Industry(TimeStampedModel):
    name: str = models.CharField(max_length=128, blank=False, null=False, unique=True)


class JobTitle(TimeStampedModel):
    name: str = models.CharField(max_length=128, blank=False, null=False, unique=True)


class UserQuerySet(models.QuerySet):
    def with_related_objects_selected(self):
        return self.select_related('metro', 'industry', 'job_title')


class UserManager(BaseUserManager):
    def get_queryset(self):
        return UserQuerySet(self.model, using=self._db)


class User(AbstractUser, SoftDeleteModelMixin):
    class GenderChoices(models.TextChoices):
        MALE = 'male', 'Male'
        FEMALE = 'female', 'Female'
        TRANSGENDER = 'transgender', 'Transgender'
        PREFER_NOT_TO_SAY = 'prefer_not_to_say', 'Prefer not to say'

    class LevelChoices(models.IntegerChoices):
        IC_ASSOCIATE = 1, 'Individual Contributor, Associate'
        IC = 2, 'Individual Contributor'
        IC_SENIOR = 3, 'Individual Contributor, Senior'
        IC_STAFF = 4, 'Individual Contributor, Staff'
        IC_PRINCIPAL = 5, 'Individual Contributor, Principal'
        MANAGER = 6, 'Manager'
        DIRECTOR = 7, 'Director'
        DIRECTOR_SR = 8, 'Director, Senior'
        VP = 9, 'VP'
        VP_SENIOR = 10, 'VP, Senior'
        C_SUITE = 11, 'C-Suite'
        FOUNDER = 12, 'Founder'

    class CurrentPFMChoices(models.TextChoices):
        MINT = 'mint', 'Mint'
        ROCKET_MONEY = 'rocket money', 'Rocket Money'
        QUICKEN = 'quicken', 'Quicken'
        CHIME = 'chime', 'Chime'
        SPLITWISE = 'splitwise', 'Splitwise'
        PEN_PAPER = 'pen paper', 'Pen & paper'
        NONE = 'none', 'None'

    # for profile urls
    uuid = models.UUIDField(default=uuid4, editable=False, null=False)

    # profile setup
    handle: Optional[str] = models.CharField(
        max_length=24, blank=True, null=True, unique=True
    )
    age: Optional[int] = models.IntegerField(null=True, db_index=True)
    gender: Optional[str] = models.CharField(
        choices=GenderChoices.choices, null=True, max_length=20, blank=False
    )
    metro: Optional[MetropolitanArea] = models.ForeignKey(
        to=MetropolitanArea, related_name='users', on_delete=models.SET_NULL, null=True
    )
    industry: Optional[Industry] = models.ForeignKey(
        to=Industry, related_name='users', on_delete=models.SET_NULL, null=True
    )
    job_title: Optional[JobTitle] = models.ForeignKey(
        to=JobTitle, related_name='users', on_delete=models.SET_NULL, null=True
    )
    level: Optional[int] = models.IntegerField(choices=LevelChoices.choices, null=True)
    current_pfm: Optional[str] = models.CharField(
        choices=CurrentPFMChoices.choices, null=True, max_length=20, blank=False
    )

    # TODO: add why are here and financial goal fields

    # income statement
    # income
    inc_primary_annual: Optional[Decimal] = models.DecimalField(
        default=None, max_digits=12, decimal_places=2, null=True, db_index=True
    )
    inc_primary_tax_fed: Optional[float] = models.FloatField(default=None, null=True)
    inc_primary_tax_state: Optional[float] = models.FloatField(default=None, null=True)
    inc_variable_monthly: Optional[Decimal] = models.DecimalField(
        default=None, max_digits=12, decimal_places=2, null=True
    )
    inc_variable_tax_fed: Optional[float] = models.FloatField(default=None, null=True)
    inc_variable_tax_state: Optional[float] = models.FloatField(default=None, null=True)
    inc_secondary_monthly: Optional[Decimal] = models.DecimalField(
        default=None, max_digits=12, decimal_places=2, null=True
    )
    inc_secondary_tax_fed: Optional[float] = models.FloatField(default=None, null=True)
    inc_secondary_tax_state: Optional[float] = models.FloatField(
        default=None, null=True
    )
    # monthly expenses
    exp_housing: Optional[Decimal] = models.DecimalField(
        default=None, max_digits=12, decimal_places=2, null=True, db_index=True
    )
    exp_other_fixed: Optional[Decimal] = models.DecimalField(
        default=None, max_digits=12, decimal_places=2, null=True
    )
    exp_other_variable: Optional[Decimal] = models.DecimalField(
        default=None, max_digits=12, decimal_places=2, null=True
    )
    # monthly savings
    sav_retirement: Optional[Decimal] = models.DecimalField(
        default=None, max_digits=12, decimal_places=2, null=True
    )
    sav_market: Optional[Decimal] = models.DecimalField(
        default=None, max_digits=12, decimal_places=2, null=True
    )
    # computed fields
    inc_total_annual: Optional[Decimal] = models.DecimalField(
        default=None, max_digits=12, decimal_places=2, null=True, db_index=True
    )
    net_monthly_profit_loss: Optional[Decimal] = models.DecimalField(
        default=None, max_digits=12, decimal_places=2, null=True, db_index=True
    )
    # TODO: add total expenses, total savings

    # net worth
    # assets
    assets_savings: Optional[Decimal] = models.DecimalField(
        default=None, max_digits=14, decimal_places=2, null=True
    )
    assets_property: Optional[Decimal] = models.DecimalField(
        default=None, max_digits=14, decimal_places=2, null=True
    )
    assets_misc: Optional[Decimal] = models.DecimalField(
        default=None, max_digits=12, decimal_places=2, null=True
    )
    # liabilities
    lia_loans: Optional[Decimal] = models.DecimalField(
        default=None, max_digits=12, decimal_places=2, null=True
    )
    lia_credit_card: Optional[Decimal] = models.DecimalField(
        default=None, max_digits=12, decimal_places=2, null=True
    )
    lia_misc: Optional[Decimal] = models.DecimalField(
        default=None, max_digits=12, decimal_places=2, null=True
    )
    # computed fields
    assets_total: Optional[Decimal] = models.DecimalField(
        default=None, max_digits=14, decimal_places=2, null=True, db_index=True
    )
    lia_total: Optional[Decimal] = models.DecimalField(
        default=None, max_digits=14, decimal_places=2, null=True, db_index=True
    )
    net_worth: Optional[Decimal] = models.DecimalField(
        default=None, max_digits=14, decimal_places=2, null=True, db_index=True
    )

    objects = UserManager()

    class Meta:
        db_table = 'users'

    def recompute_inc_total_annual(self) -> bool:
        if (
            self.inc_primary_annual is not None
            and self.inc_variable_monthly is not None
            and self.inc_secondary_monthly is not None
        ):
            new_value = (
                self.inc_primary_annual
                + self.inc_variable_monthly * Decimal('12')
                + self.inc_secondary_monthly * Decimal('12')
            )
            changed = new_value != self.inc_total_annual
            self.inc_total_annual = new_value
        else:
            changed = self.inc_total_annual is not None
            self.inc_total_annual = None
        return changed

    def recompute_net_monthly_profit_loss(self) -> bool:
        if (
            self.inc_primary_annual is not None
            and self.inc_variable_monthly is not None
            and self.inc_secondary_monthly is not None
            and self.inc_primary_tax_fed is not None
            and self.inc_primary_tax_state is not None
            and self.inc_variable_tax_fed is not None
            and self.inc_variable_tax_state is not None
            and self.inc_secondary_tax_fed is not None
            and self.inc_secondary_tax_state is not None
            and self.exp_housing is not None
            and self.exp_other_fixed is not None
            and self.exp_other_variable is not None
            and self.sav_retirement is not None
            and self.sav_market is not None
        ):
            net_primary = self.inc_primary_annual * Decimal(
                (1 - self.inc_primary_tax_fed / 100 + self.inc_primary_tax_state / 100)
                / 12
            )
            net_variable = self.inc_variable_monthly * Decimal(
                1 - self.inc_variable_tax_fed / 100 + self.inc_variable_tax_state / 100
            )
            net_secondary = self.inc_secondary_monthly * Decimal(
                1 - self.inc_secondary_tax_fed / 100 + self.inc_variable_tax_state / 100
            )
            total_expenses = (
                self.exp_housing + self.exp_other_fixed + self.exp_other_variable
            )
            total_savings = self.sav_retirement + self.sav_market
            new_value = (
                net_primary
                + net_variable
                + net_secondary
                - total_expenses
                - total_savings
            )
            changed = new_value != self.net_monthly_profit_loss
            self.net_monthly_profit_loss = new_value
        else:
            changed = self.net_monthly_profit_loss is not None
            self.net_monthly_profit_loss = None
        return changed

    def recompute_assets_total(self) -> bool:
        if (
            self.assets_savings is not None
            and self.assets_property is not None
            and self.assets_misc is not None
        ):
            new_value = self.assets_savings + self.assets_property + self.assets_misc
            changed = new_value != self.assets_total
            self.assets_total = new_value
        else:
            changed = self.assets_total is not None
            self.assets_total = None
        return changed

    def recompute_lia_total(self) -> bool:
        if (
            self.lia_loans is not None
            and self.lia_credit_card is not None
            and self.lia_misc is not None
        ):
            new_value = self.lia_loans + self.lia_credit_card + self.lia_misc
            changed = new_value != self.lia_total
            self.lia_total = new_value
        else:
            changed = self.lia_total is not None
            self.lia_total = None
        return changed

    def recompute_net_worth(self) -> bool:
        if self.assets_total is not None and self.lia_total is not None:
            new_value = self.assets_total - self.lia_total
            changed = new_value != self.net_worth
            self.net_worth = new_value
        else:
            changed = self.net_worth is not None
            self.net_worth = None
        return changed

    def recompute_fields(self) -> List[str]:
        update_fields = []
        if self.recompute_inc_total_annual():
            update_fields.append('inc_total_annual')
        if self.recompute_net_monthly_profit_loss():
            update_fields.append('net_monthly_profit_loss')
        if self.recompute_assets_total():
            update_fields.append('assets_total')
        if self.recompute_lia_total():
            update_fields.append('lia_total')
        if self.recompute_net_worth():
            update_fields.append('net_worth')
        return update_fields

    @property
    def inc_primary_monthly_net(self) -> Optional[Decimal]:
        if (
            self.inc_primary_annual is not None
            and self.inc_primary_tax_fed is not None
            and self.inc_primary_tax_state is not None
        ):
            return self.inc_primary_annual * Decimal(
                (1 - (self.inc_primary_tax_fed + self.inc_primary_tax_state) / 100) / 12
            )
        return None

    @property
    def inc_variable_monthly_net(self) -> Optional[Decimal]:
        if (
            self.inc_variable_monthly is not None
            and self.inc_variable_tax_fed is not None
            and self.inc_variable_tax_state is not None
        ):
            return self.inc_variable_monthly * Decimal(
                1 - (self.inc_variable_tax_fed + self.inc_variable_tax_state) / 100
            )
        return None

    @property
    def inc_secondary_monthly_net(self) -> Optional[Decimal]:
        if (
            self.inc_secondary_monthly is not None
            and self.inc_secondary_tax_fed is not None
            and self.inc_secondary_tax_state is not None
        ):
            return self.inc_secondary_monthly * Decimal(
                1 - (self.inc_secondary_tax_fed + self.inc_secondary_tax_state) / 100
            )
        return None

    @property
    def inc_total_monthly_net(self) -> Optional[Decimal]:
        net_primary = self.inc_primary_monthly_net
        net_variable = self.inc_variable_monthly_net
        net_secondary = self.inc_secondary_monthly_net
        if (
            net_primary is not None
            and net_variable is not None
            and net_secondary is not None
        ):
            return net_primary + net_variable + net_secondary
        return None

    @property
    def inc_annual_tax_net(self) -> Optional[float]:
        monthly_total_net = self.inc_total_monthly_net
        if self.inc_total_annual is not None and monthly_total_net is not None:
            total_net = monthly_total_net * Decimal('12')
            return 100 - float(total_net / self.inc_total_annual) * 100
        return None

    @property
    def exp_total(self) -> Optional[Decimal]:
        if (
            self.exp_housing is not None
            and self.exp_other_fixed is not None
            and self.exp_other_variable is not None
        ):
            return self.exp_housing + self.exp_other_fixed + self.exp_other_variable
        return None

    @property
    def sav_total(self) -> Optional[Decimal]:
        if self.sav_market is not None and self.sav_retirement is not None:
            return self.sav_market + self.sav_retirement
        return None

    def save(self, update_fields=None, *args, **kwargs) -> 'User':
        recompute_update_fields = self.recompute_fields()
        if update_fields is not None:
            update_fields.extend(recompute_update_fields)
        return super().save(update_fields=update_fields, *args, **kwargs)
