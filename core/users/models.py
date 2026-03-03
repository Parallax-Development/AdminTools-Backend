import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    minecraft_uuid = models.UUIDField(null=True, blank=True, unique=True, default=None)
    display_name = models.CharField(max_length=64, blank=True)
    is_online = models.BooleanField(default=False)
    last_seen_at = models.DateTimeField(null=True, blank=True)
    current_channel = models.ForeignKey(
        "voice.VoiceChannel",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="current_users",
    )
    roles = models.ManyToManyField("permissions.Role", blank=True, related_name="users")
    external_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)

    class Meta:
        indexes = [
            models.Index(fields=["minecraft_uuid"]),
            models.Index(fields=["is_online"]),
        ]
