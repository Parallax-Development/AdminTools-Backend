from rest_framework import serializers

from core.moderation.models import ModerationAction


class ModerationActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModerationAction
        fields = [
            "id",
            "target_user",
            "actor_user",
            "server_id",
            "action_type",
            "reason",
            "created_at",
            "expires_at",
            "metadata",
        ]
