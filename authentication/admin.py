from authentication.models import User
from django.contrib import admin


class UserAdmin(admin.ModelAdmin):
    pass


admin.site.register(User, UserAdmin)
