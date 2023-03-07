from authentication.models import Industry, JobTitle, MetropolitanArea, User
from django_filters import rest_framework as filters


class UserFilter(filters.FilterSet):
    age = filters.NumberFilter(field_name='age')
    age__lt = filters.NumberFilter(field_name='age', lookup_expr='lt')
    age__lte = filters.NumberFilter(field_name='age', lookup_expr='lte')
    age__gt = filters.NumberFilter(field_name='age', lookup_expr='gt')
    age__gte = filters.NumberFilter(field_name='age', lookup_expr='gte')
    gender__in = filters.BaseInFilter(field_name='gender')
    metro__in = filters.BaseInFilter(field_name='metro_id')
    industry__in = filters.BaseInFilter(field_name='industry_id')
    job_title__in = filters.BaseInFilter(field_name='job_title_id')
    level__in = filters.BaseInFilter(field_name='level')
    level__lt = filters.NumberFilter(field_name='level', lookup_expr='lt')
    level__lte = filters.NumberFilter(field_name='level', lookup_expr='lte')
    level__gt = filters.NumberFilter(field_name='level', lookup_expr='gt')
    level__gte = filters.NumberFilter(field_name='level', lookup_expr='gte')
    current_pfm__in = filters.BaseInFilter(field_name='current_pfm')
    inc_primary_annual__lt = filters.NumberFilter(
        field_name='inc_primary_annual', lookup_expr='lt'
    )
    inc_primary_annual__lte = filters.NumberFilter(
        field_name='inc_primary_annual', lookup_expr='lte'
    )
    inc_primary_annual__gt = filters.NumberFilter(
        field_name='inc_primary_annual', lookup_expr='gt'
    )
    inc_primary_annual__gte = filters.NumberFilter(
        field_name='inc_primary_annual', lookup_expr='gte'
    )
    inc_variable_monthly__lt = filters.NumberFilter(
        field_name='inc_variable_monthly', lookup_expr='lt'
    )
    inc_variable_monthly__lte = filters.NumberFilter(
        field_name='inc_variable_monthly', lookup_expr='lte'
    )
    inc_variable_monthly__gt = filters.NumberFilter(
        field_name='inc_variable_monthly', lookup_expr='gt'
    )
    inc_variable_monthly__gte = filters.NumberFilter(
        field_name='inc_variable_monthly', lookup_expr='gte'
    )
    inc_secondary_monthly__lt = filters.NumberFilter(
        field_name='inc_secondary_monthly', lookup_expr='lt'
    )
    inc_secondary_monthly__lte = filters.NumberFilter(
        field_name='inc_secondary_monthly', lookup_expr='lte'
    )
    inc_secondary_monthly__gt = filters.NumberFilter(
        field_name='inc_secondary_monthly', lookup_expr='gt'
    )
    inc_secondary_monthly__gte = filters.NumberFilter(
        field_name='inc_secondary_monthly', lookup_expr='gte'
    )
    exp_housing__lt = filters.NumberFilter(field_name='exp_housing', lookup_expr='lt')
    exp_housing__lte = filters.NumberFilter(field_name='exp_housing', lookup_expr='lte')
    exp_housing__gt = filters.NumberFilter(field_name='exp_housing', lookup_expr='gt')
    exp_housing__gte = filters.NumberFilter(field_name='exp_housing', lookup_expr='gte')
    inc_total_annual__lt = filters.NumberFilter(
        field_name='inc_total_annual', lookup_expr='lt'
    )
    inc_total_annual__lte = filters.NumberFilter(
        field_name='inc_total_annual', lookup_expr='lte'
    )
    inc_total_annual__gt = filters.NumberFilter(
        field_name='inc_total_annual', lookup_expr='gt'
    )
    inc_total_annual__gte = filters.NumberFilter(
        field_name='inc_total_annual', lookup_expr='gte'
    )
    net_monthly_profit_loss__lt = filters.NumberFilter(
        field_name='net_monthly_profit_loss', lookup_expr='lt'
    )
    net_monthly_profit_loss__lte = filters.NumberFilter(
        field_name='net_monthly_profit_loss', lookup_expr='lte'
    )
    net_monthly_profit_loss__gt = filters.NumberFilter(
        field_name='net_monthly_profit_loss', lookup_expr='gt'
    )
    net_monthly_profit_loss__gte = filters.NumberFilter(
        field_name='net_monthly_profit_loss', lookup_expr='gte'
    )
    assets_total__lt = filters.NumberFilter(field_name='assets_total', lookup_expr='lt')
    assets_total__lte = filters.NumberFilter(
        field_name='assets_total', lookup_expr='lte'
    )
    assets_total__gt = filters.NumberFilter(field_name='assets_total', lookup_expr='gt')
    assets_total__gte = filters.NumberFilter(
        field_name='assets_total', lookup_expr='gte'
    )
    lia_total__lt = filters.NumberFilter(field_name='lia_total', lookup_expr='lt')
    lia_total__lte = filters.NumberFilter(field_name='lia_total', lookup_expr='lte')
    lia_total__gt = filters.NumberFilter(field_name='lia_total', lookup_expr='gt')
    lia_total__gte = filters.NumberFilter(field_name='lia_total', lookup_expr='gte')
    net_worth__lt = filters.NumberFilter(field_name='net_worth', lookup_expr='lt')
    net_worth__lte = filters.NumberFilter(field_name='net_worth', lookup_expr='lte')
    net_worth__gt = filters.NumberFilter(field_name='net_worth', lookup_expr='gt')
    net_worth__gte = filters.NumberFilter(field_name='net_worth', lookup_expr='gte')

    class Meta:
        model = User
        fields = [
            'age',
            'gender',
            'metro',
            'industry',
            'job_title',
            'level',
            'current_pfm',
            'inc_primary_annual',
            'inc_variable_monthly',
            'inc_secondary_monthly',
            'exp_housing',
            'inc_total_annual',
            'net_monthly_profit_loss',
            'assets_total',
            'lia_total',
            'net_worth',
        ]


class MetropolitanAreaFilter(filters.FilterSet):
    id__in = filters.BaseInFilter(field_name='id')

    class Meta:
        model = MetropolitanArea
        fields = ['id']


class IndustryFilter(filters.FilterSet):
    id__in = filters.BaseInFilter(field_name='id')

    class Meta:
        model = Industry
        fields = ['id']


class JobTitleFilter(filters.FilterSet):
    id__in = filters.BaseInFilter(field_name='id')

    class Meta:
        model = JobTitle
        fields = ['id']
