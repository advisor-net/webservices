from authentication.models import ChatUser, Industry, JobTitle, MetropolitanArea, User
from django.core.exceptions import ObjectDoesNotExist
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


class ChatUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatUser
        fields = ['chat_engine_id', 'username', 'password', 'agreed_to_terms']


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
    chat_user = serializers.SerializerMethodField()

    def get_chat_user(self, instance):
        try:
            return ChatUserSerializer(instance=instance.chat_user).data
        except ObjectDoesNotExist:
            return None

    class Meta:
        model = User
        exclude = [
            'email',
            'password',
            'username',
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
    chat_user = serializers.SerializerMethodField()
    metro = MetropolitanAreaSerializer()

    def get_chat_user(self, instance):
        try:
            return ChatUserSerializer(instance=instance.chat_user).data
        except ObjectDoesNotExist:
            return None

    class Meta:
        model = User
        fields = ['uuid', 'id', 'email', 'chat_user', 'metro', 'email_verified']
