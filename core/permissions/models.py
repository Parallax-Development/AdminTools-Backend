from django.db import models


class Permission(models.Model):
    key = models.CharField(max_length=128, unique=True)
    name = models.CharField(max_length=128)
    description = models.TextField(blank=True)
    group = models.CharField(max_length=128, blank=True)

    class Meta:
        indexes = [models.Index(fields=["group"])]


class Role(models.Model):
    key = models.CharField(max_length=128, unique=True)
    name = models.CharField(max_length=128)
    description = models.TextField(blank=True)
    is_system = models.BooleanField(default=False)
    permissions = models.ManyToManyField(Permission, blank=True, related_name="roles")
    created_at = models.DateTimeField(auto_now_add=True)
