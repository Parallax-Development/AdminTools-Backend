from rest_framework import serializers


class UserRecordSerializer(serializers.Serializer):
    id = serializers.CharField()
    external_id = serializers.CharField(allow_null=True)
    username = serializers.CharField()
    display_name = serializers.CharField(allow_blank=True)
    minecraft_uuid = serializers.CharField(allow_null=True)
    is_online = serializers.BooleanField()
    last_seen_at = serializers.DateTimeField(allow_null=True)
    current_channel = serializers.CharField(allow_null=True)


class VoiceChannelRecordSerializer(serializers.Serializer):
    id = serializers.CharField()
    server_id = serializers.CharField()
    external_id = serializers.CharField()
    name = serializers.CharField()
    is_active = serializers.BooleanField()
    metadata = serializers.JSONField()


class VoiceSessionRecordSerializer(serializers.Serializer):
    id = serializers.CharField()
    user = serializers.CharField()
    channel = serializers.CharField()
    server_id = serializers.CharField()
    started_at = serializers.DateTimeField()
    ended_at = serializers.DateTimeField(allow_null=True)
    metadata = serializers.JSONField()


class ModerationActionRecordSerializer(serializers.Serializer):
    id = serializers.CharField()
    target_user = serializers.CharField()
    actor_user = serializers.CharField(allow_null=True)
    server_id = serializers.CharField()
    action_type = serializers.CharField()
    reason = serializers.CharField(allow_blank=True)
    created_at = serializers.DateTimeField()
    expires_at = serializers.DateTimeField(allow_null=True)
    metadata = serializers.JSONField()


class TelemetryEventRecordSerializer(serializers.Serializer):
    id = serializers.CharField()
    event_id = serializers.CharField()
    event_type = serializers.CharField()
    server_id = serializers.CharField()
    user = serializers.CharField(allow_null=True)
    session = serializers.CharField(allow_null=True)
    payload = serializers.JSONField()
    occurred_at = serializers.DateTimeField()


class WidgetDefinitionRecordSerializer(serializers.Serializer):
    id = serializers.CharField()
    key = serializers.CharField()
    name = serializers.CharField()
    description = serializers.CharField(allow_blank=True)
    widget_type = serializers.CharField()
    schema = serializers.JSONField()
    is_active = serializers.BooleanField()
    required_permissions = serializers.ListField(child=serializers.CharField())
    allowed_roles = serializers.ListField(child=serializers.CharField())


class DashboardLayoutRecordSerializer(serializers.Serializer):
    id = serializers.CharField()
    user = serializers.CharField()
    name = serializers.CharField()
    layout = serializers.JSONField()
    is_default = serializers.BooleanField()
    updated_at = serializers.DateTimeField()
