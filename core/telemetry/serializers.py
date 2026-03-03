from rest_framework import serializers

from core.telemetry.models import TelemetryEvent


class TelemetryEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = TelemetryEvent
        fields = ["id", "event_id", "event_type", "server_id", "user", "session", "payload", "occurred_at"]
