from rest_framework import serializers


class HandleValidator(serializers.Serializer):
    handle = serializers.CharField(required=True, max_length=128)

    def validate_handle(self, value):
        if not value.isidentifier():
            raise serializers.ValidationError("Handle is not a valid identifier")
        return value
