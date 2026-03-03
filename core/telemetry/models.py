from django.conf import settings
from django.db import models
from django.contrib.postgres.indexes import GinIndex


class TelemetryEvent(models.Model):
    event_id = models.CharField(max_length=128, unique=True)
    event_type = models.CharField(max_length=128)
    server_id = models.CharField(max_length=64)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    session = models.ForeignKey("voice.VoiceSession", null=True, blank=True, on_delete=models.SET_NULL)
    payload = models.JSONField(default=dict, blank=True)
    occurred_at = models.DateTimeField()

    class Meta:
        indexes = [
            models.Index(fields=["event_type"]),
            models.Index(fields=["server_id"]),
            models.Index(fields=["occurred_at"]),
            GinIndex(fields=["payload"], name="telemetry_payload_gin"),
        ]
