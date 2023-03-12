from django.db import models
from django.utils import timezone


class SoftDeleteModelMixin:
    deleted_at = models.DateTimeField(blank=True, null=True, default=None)

    @property
    def is_live(self):
        return not bool(self.deleted_at)

    def do_soft_delete(self, save=True):
        self.deleted_at = timezone.now()
        if save:
            self.save(update_fields=['deleted_at'])

    def delete(self, hard_delete=False, *args, **kwargs):
        if not hard_delete:
            raise ValueError(
                'Can\'t hard delete an instance without ' '\'hard_delete\' flag'
            )

        return super().delete(*args, **kwargs)


class TimeStampedModel(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
