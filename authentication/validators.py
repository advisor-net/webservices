from authentication.models import User
from rest_framework import serializers


# NOTE: FK fields come in with their ID, i.e. industry: 23
class UpdateUserValidator(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = []
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
    handle = serializers.CharField(required=True, max_length=128)

    def validate_handle(self, value):
        if not value.isidentifier():
            raise serializers.ValidationError("Handle is not a valid identifier")
        return value
