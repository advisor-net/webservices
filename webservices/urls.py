"""webservices URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from authentication.views import (
    CheckHandleView,
    GetOrCreateChatUserView,
    IndustrySearch,
    JobTitleSearch,
    LogoutView,
    MetropolitanAreaSearch,
    ProfileView,
    ReportUserView,
    UpdateChatTermsAgreementView,
    UpdateHandleView,
    UserDetailsView,
    UserListView,
)
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from rest_framework.authtoken import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/api_token_auth/', views.obtain_auth_token, name='api_token_auth'),
    path('api/logout/', LogoutView.as_view(), name='logout'),
    path('api/profile/', ProfileView.as_view(), name='auth_profile'),
    path(
        'api/user/check_handle/<str:uuid>/',
        CheckHandleView.as_view(),
        name='check_handle',
    ),
    path(
        'api/user/update_handle/<str:uuid>/',
        UpdateHandleView.as_view(),
        name='update_handle',
    ),
    path('api/user/profile/<str:uuid>/', UserDetailsView.as_view(), name='user_detail'),
    path(
        'api/user/chat_user/<str:uuid>/',
        GetOrCreateChatUserView.as_view(),
        name='get_or_create_chat_user',
    ),
    path(
        'api/user/chat_user_terms/<str:uuid>/',
        UpdateChatTermsAgreementView.as_view(),
        name='update_chat_terms',
    ),
    path('api/users/', UserListView.as_view(), name='user_list'),
    path('api/metros/', MetropolitanAreaSearch.as_view(), name='metro_list'),
    path('api/industries/', IndustrySearch.as_view(), name='industry_list'),
    path('api/job_titles/', JobTitleSearch.as_view(), name='job_title_list'),
    path('api/user/report_misconduct/', ReportUserView.as_view(), name='report_user'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
# https://docs.djangoproject.com/en/2.1/howto/static-files/#serving-files-uploaded-by-a-user-during-development
