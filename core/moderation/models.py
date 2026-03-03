from django.conf import settings
from django.db import models
from django.contrib.postgres.indexes import GinIndex


class ModerationAction(models.Model):
    ACTION_CHOICES = [
        ("mute", "mute"),
        ("kick", "kick"),
        ("ban", "ban"),
        ("unmute", "unmute"),
    ]

    target_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="moderation_actions"
    )
    actor_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="moderation_actions_issued",
    )
    server_id = models.CharField(max_length=64)
    action_type = models.CharField(max_length=16, choices=ACTION_CHOICES)
    reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["server_id"]),
            models.Index(fields=["action_type"]),
            models.Index(fields=["created_at"]),
            GinIndex(fields=["metadata"], name="moderation_metadata_gin"),
        ]
