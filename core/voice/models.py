from django.conf import settings
from django.db import models
from django.db.models import Q
from django.contrib.postgres.indexes import GinIndex


class VoiceChannel(models.Model):
    server_id = models.CharField(max_length=64)
    external_id = models.CharField(max_length=128)
    name = models.CharField(max_length=128)
    is_active = models.BooleanField(default=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["server_id", "external_id"], name="uniq_channel_server_external")
        ]
        indexes = [
            models.Index(fields=["server_id"]),
            models.Index(fields=["external_id"]),
            models.Index(fields=["name"]),
            GinIndex(fields=["metadata"], name="voice_channel_metadata_gin"),
        ]


class VoiceSession(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="voice_sessions")
    channel = models.ForeignKey(VoiceChannel, on_delete=models.PROTECT, related_name="sessions")
    server_id = models.CharField(max_length=64)
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["server_id"]),
            models.Index(fields=["started_at"]),
            models.Index(fields=["ended_at"]),
            GinIndex(fields=["metadata"], name="voice_session_metadata_gin"),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["user"],
                condition=Q(ended_at__isnull=True),
                name="uniq_active_session_user",
            )
        ]
