from rest_framework import serializers

from core.voice.models import VoiceChannel, VoiceSession


class VoiceChannelSerializer(serializers.ModelSerializer):
    class Meta:
        model = VoiceChannel
        fields = ["id", "server_id", "external_id", "name", "is_active", "metadata"]


class VoiceSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = VoiceSession
        fields = [
            "id",
            "user",
            "channel",
            "server_id",
            "started_at",
            "ended_at",
            "metadata",
        ]
