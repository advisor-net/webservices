from authentication.models import User
from rest_framework import serializers
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import IsAuthenticated


class ProfileView(RetrieveAPIView):
    class Serializer(serializers.ModelSerializer):
        class Meta:
            model = User
            fields = (
                'email',
                'handle',
                'date_joined',
            )

    permission_classes = (IsAuthenticated,)
    serializer_class = Serializer
    queryset = User.objects.all()

    def get_object(self):
        return self.request.user
