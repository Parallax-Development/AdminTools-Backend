from datetime import timedelta

from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from core.db.provider import get_dao_provider
from core.db.serializers import ModerationActionRecordSerializer
from core.permissions.utils import user_has_permission
from core.voice.services import send_plugin_command


class ModerationActionViewSet(viewsets.ViewSet):
    serializer_class = ModerationActionRecordSerializer

    @action(detail=False, methods=["post"])
    def mute(self, request):
        if not user_has_permission(request.user, "moderation.mute"):
            return Response({"detail": "permission_denied"}, status=status.HTTP_403_FORBIDDEN)

        target_user_id = request.data.get("target_user_id")
        server_id = request.data.get("server_id")
        reason = request.data.get("reason", "")
        duration_seconds = int(request.data.get("duration_seconds", 0))

        if not target_user_id or not server_id:
            return Response({"detail": "missing_target_or_server"}, status=status.HTTP_400_BAD_REQUEST)

        provider = get_dao_provider()
        target_user = provider.users.get(id=target_user_id)
        if not target_user:
            return Response({"detail": "target_not_found"}, status=status.HTTP_404_NOT_FOUND)

        expires_at = None
        if duration_seconds > 0:
            expires_at = timezone.now() + timedelta(seconds=duration_seconds)

        action = provider.moderation.create(
            {
                "target_user": target_user["id"],
                "actor_user": str(request.user.id) if request.user.is_authenticated else None,
                "server_id": server_id,
                "action_type": "mute",
                "reason": reason,
                "created_at": timezone.now(),
                "expires_at": expires_at,
                "metadata": {"duration_seconds": duration_seconds},
            }
        )

        send_plugin_command(
            server_id,
            "moderation.mute",
            {
                "target_user_id": target_user["id"],
                "minecraft_uuid": target_user.get("minecraft_uuid"),
                "duration_seconds": duration_seconds,
                "reason": reason,
            },
        )

        return Response(self.serializer_class(action).data, status=status.HTTP_201_CREATED)
