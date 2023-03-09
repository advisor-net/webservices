from authentication.models import User
from rest_framework import serializers


# NOTE: FK fields come in with their ID, i.e. industry: 23
class UpdateUserValidator(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude: list = []
        read_only_fields = [
            'id',
            'uuid',
            'handle',
            'inc_total_annual',
            'net_monthly_profit_loss',
            'lia_total',
            'net_worth',
        ]


class HandleValidator(serializers.Serializer):
    handle = serializers.CharField(required=True, min_length=4, max_length=24)

    def validate_handle(self, value):
        if not value.isidentifier():
            raise serializers.ValidationError(
                "Cannot contain special characters other than an underscore"
            )
        return value
