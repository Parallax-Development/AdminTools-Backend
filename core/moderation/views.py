from datetime import timedelta

from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from core.moderation.models import ModerationAction
from core.moderation.serializers import ModerationActionSerializer
from core.permissions.utils import user_has_permission
from core.users.models import User
from core.voice.services import send_plugin_command


class ModerationActionViewSet(viewsets.ModelViewSet):
    queryset = ModerationAction.objects.all().order_by("-created_at")
    serializer_class = ModerationActionSerializer

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

        target_user = User.objects.filter(id=target_user_id).first()
        if not target_user:
            return Response({"detail": "target_not_found"}, status=status.HTTP_404_NOT_FOUND)

        expires_at = None
        if duration_seconds > 0:
            expires_at = timezone.now() + timedelta(seconds=duration_seconds)

        action = ModerationAction.objects.create(
            target_user=target_user,
            actor_user=request.user if request.user.is_authenticated else None,
            server_id=server_id,
            action_type="mute",
            reason=reason,
            expires_at=expires_at,
            metadata={"duration_seconds": duration_seconds},
        )

        send_plugin_command(
            server_id,
            "moderation.mute",
            {
                "target_user_id": target_user.id,
                "minecraft_uuid": str(target_user.minecraft_uuid) if target_user.minecraft_uuid else None,
                "duration_seconds": duration_seconds,
                "reason": reason,
            },
        )

        return Response(ModerationActionSerializer(action).data, status=status.HTTP_201_CREATED)
