from authentication.models import User
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
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
