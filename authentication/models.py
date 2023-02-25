from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    handle = models.CharField(max_length=128, blank=True, null=True, unique=True)

    class Meta:
        db_table = 'users'
