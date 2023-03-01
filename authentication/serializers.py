from authentication.models import Industry, JobTitle, MetropolitanArea, User
from rest_framework import serializers


class MetropolitanAreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = MetropolitanArea
        exclude = []


class IndustrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Industry
        exclude = []


class JobTitleSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobTitle
        exclude = ['industry']


class UserSerializer(serializers.ModelSerializer):
    metro = MetropolitanAreaSerializer()
    industry = IndustrySerializer()
    job_title = JobTitleSerializer()

    class Meta:
        model = User
        exclude = [
            'password',
            'username',
            'date_joined',
            'groups',
            'user_permissions',
            'deleted_at',
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
