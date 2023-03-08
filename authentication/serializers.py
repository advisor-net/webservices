from authentication.models import Industry, JobTitle, MetropolitanArea, User
from rest_framework import serializers


class MetropolitanAreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = MetropolitanArea
        fields = ['id', 'name']


class IndustrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Industry
        fields = ['id', 'name']


class JobTitleSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobTitle
        fields = ['id', 'name']


class UserSerializer(serializers.ModelSerializer):
    metro = MetropolitanAreaSerializer()
    industry = IndustrySerializer()
    job_title = JobTitleSerializer()
    inc_primary_monthly_net = serializers.DecimalField(max_digits=12, decimal_places=2)
    inc_variable_monthly_net = serializers.DecimalField(max_digits=12, decimal_places=2)
    inc_secondary_monthly_net = serializers.DecimalField(
        max_digits=12, decimal_places=2
    )
    inc_total_monthly_net = serializers.DecimalField(max_digits=12, decimal_places=2)
    inc_annual_tax_net = serializers.FloatField()
    exp_total = serializers.DecimalField(max_digits=12, decimal_places=2)
    sav_total = serializers.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        model = User
        exclude = [
            'email',
            'password',
            'username',
            'date_joined',
            'groups',
            'user_permissions',
            'deleted_at',
            'is_active',
            'is_staff',
            'is_superuser',
            'last_login',
            'first_name',
            'last_name',
        ]
        read_only_fields = [
            'id',
            'uuid',
            'handle',
            'inc_total_annual',
            'net_monthly_profit_loss',
            'lia_total',
            'net_worth',
        ]


class ProfileSerializer(serializers.ModelSerializer):
    metro = MetropolitanAreaSerializer()

    class Meta:
        model = User
        fields = ['uuid', 'id', 'email', 'metro']
