from authentication.models import (
    ChatUser,
    Industry,
    JobTitle,
    MetropolitanArea,
    ReportedMisconduct,
    ResetPasswordLink,
    SignUpLink,
    User,
    VerifyEmailLink,
    WaitListEntry,
)
from django.contrib import admin
from django.contrib.auth.models import Group
from django_celery_results.models import GroupResult, TaskResult


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'email',
        'date_joined',
        'last_login',
        'is_active',
    )
    search_fields = ('email',)
    ordering = ('email',)


@admin.register(ChatUser)
class ChatUserAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'username',
        'chat_engine_id',
    )
    search_fields = (
        'user__email',
        'username',
    )
    ordering = ('user__email',)

    def user(self, chat_user):
        return chat_user.user.email

    def get_queryset(self, request):
        qs = ChatUser.objects.select_related('user')
        ordering = self.get_ordering(request)
        if ordering:
            qs = qs.order_by(*ordering)
        return qs


@admin.register(MetropolitanArea)
class MetropolitanAreaAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(Industry)
class IndustryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(JobTitle)
class JobTitleAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(SignUpLink)
class SignUpLinkAdmin(admin.ModelAdmin):
    list_display = ('email', 'uuid', 'link')
    search_fields = ('email', 'uuid')
    ordering = ('email',)


@admin.register(WaitListEntry)
class WaitListEntryAdmin(admin.ModelAdmin):
    list_display = ('email', 'how_did_you_hear_about_us', 'why_do_you_want_to_join')
    search_fields = ('email', 'how_did_you_hear_about_us', 'why_do_you_want_to_join')
    ordering = ('email',)


@admin.register(ResetPasswordLink)
class ResetPasswordLinkAdmin(admin.ModelAdmin):
    list_display = ('email', 'expires_on', 'link')
    search_fields = ('email',)
    ordering = ('email',)


@admin.register(VerifyEmailLink)
class VerifyEmailLinkAdmin(admin.ModelAdmin):
    list_display = ('user', 'link')
    search_fields = ('user__email',)
    ordering = ('user__email',)

    def user(self, verify_email_link):
        return verify_email_link.user.email

    def get_queryset(self, request):
        qs = VerifyEmailLink.objects.select_related('user')
        ordering = self.get_ordering(request)
        if ordering:
            qs = qs.order_by(*ordering)
        return qs


@admin.register(ReportedMisconduct)
class ReportedMisconductAdmin(admin.ModelAdmin):
    list_display = ('plaintiff', 'defendant', 'description', 'acknowledged_by_staff')
    search_fields = ('plaintiff__email', 'defendant__email', 'description')
    ordering = ('plaintiff__email', 'defendant__email')

    def plaintiff(self, reported_misconduct):
        return reported_misconduct.plaintiff.email

    def defendant(self, reported_misconduct):
        return reported_misconduct.defendant.email

    def get_queryset(self, request):
        qs = ReportedMisconduct.objects.select_related('plaintiff', 'defendant')
        ordering = self.get_ordering(request)
        if ordering:
            qs = qs.order_by(*ordering)
        return qs


admin.site.unregister(Group)
admin.site.unregister(GroupResult)
admin.site.unregister(TaskResult)
