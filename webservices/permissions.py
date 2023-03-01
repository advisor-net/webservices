from rest_framework.permissions import BasePermission


class AdminOrUserSelf(BasePermission):
    """
    This permission uses only for user profile update
    """

    def has_object_permission(self, request, view, user_obj):
        if request.user.is_superuser:
            return True
        return request.user == user_obj


class MethodSpecificPermission(BasePermission):
    def __init__(self, method: str, permission_class_instance: BasePermission):
        self.method = method
        self.permission_class_instance = permission_class_instance

    def has_permission(self, request, view):

        # We can't set permissions per request method basis, so just
        # ignore requests with methods which you don't care about
        if request.method.lower() != self.method.lower():
            return True

        return self.permission_class_instance.has_permission(request, view)

    def has_object_permission(self, request, view, obj):
        # We can't set permissions per request method basis, so just
        # ignore requests with methods which you don't care about
        if request.method.lower() != self.method.lower():
            return True

        return self.permission_class_instance.has_object_permission(request, view, obj)
