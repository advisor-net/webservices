from rest_framework.permissions import BasePermission


class AdminOrUserHimself(BasePermission):
    """
    This permission uses only for user profile update
    """

    def has_object_permission(self, request, view, user_obj):
        if request.user.is_superuser:
            return True
        return request.user == user_obj
