from rest_framework import serializers

from core.users.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "external_id",
            "username",
            "display_name",
            "minecraft_uuid",
            "is_online",
            "last_seen_at",
            "current_channel",
        ]
