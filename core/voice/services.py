from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.utils import timezone

from core.telemetry.models import TelemetryEvent
from core.voice.models import VoiceChannel, VoiceSession
from core.voice.redis import add_active_user, remove_active_user


def set_user_online(user, channel, server_id, metadata):
    user.is_online = True
    user.current_channel = channel
    user.last_seen_at = timezone.now()
    user.save(update_fields=["is_online", "current_channel", "last_seen_at"])

    session = VoiceSession.objects.create(user=user, channel=channel, server_id=server_id, metadata=metadata or {})

    add_active_user(
        server_id,
        str(user.id),
        {
            "user_id": user.id,
            "username": user.username,
            "display_name": user.display_name,
            "channel_id": channel.id,
            "channel_name": channel.name,
            "started_at": session.started_at.isoformat(),
        },
    )

    publish_admin_event(
        "voice.user_connected",
        {
            "user_id": user.id,
            "session_id": session.id,
            "server_id": server_id,
            "channel_id": channel.id,
        },
    )

    return session


def set_user_offline(user, server_id, metadata):
    user.is_online = False
    user.current_channel = None
    user.last_seen_at = timezone.now()
    user.save(update_fields=["is_online", "current_channel", "last_seen_at"])

    active_session = (
        VoiceSession.objects.filter(user=user, ended_at__isnull=True).order_by("-started_at").first()
    )
    if active_session:
        active_session.ended_at = timezone.now()
        if metadata:
            active_session.metadata.update(metadata)
        active_session.save(update_fields=["ended_at", "metadata"])

    remove_active_user(server_id, str(user.id))

    publish_admin_event(
        "voice.user_disconnected",
        {
            "user_id": user.id,
            "session_id": active_session.id if active_session else None,
            "server_id": server_id,
        },
    )

    return active_session


def record_telemetry(event_type, server_id, payload, user=None, session=None, event_id=None, occurred_at=None):
    telemetry = TelemetryEvent.objects.create(
        event_id=event_id or f"auto-{timezone.now().timestamp()}",
        event_type=event_type,
        server_id=server_id,
        payload=payload or {},
        user=user,
        session=session,
        occurred_at=occurred_at or timezone.now(),
    )

    publish_admin_event(
        "telemetry.event",
        {
            "event_id": telemetry.event_id,
            "event_type": telemetry.event_type,
            "server_id": telemetry.server_id,
            "payload": telemetry.payload,
            "occurred_at": telemetry.occurred_at.isoformat(),
        },
    )

    return telemetry


def get_or_create_channel(server_id, external_id, name):
    channel, created = VoiceChannel.objects.get_or_create(
        server_id=server_id,
        external_id=external_id,
        defaults={"name": name or external_id},
    )
    if not created and name and channel.name != name:
        channel.name = name
        channel.save(update_fields=["name"])
    return channel


def publish_admin_event(event_type, payload):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "admin_updates",
        {"type": "admin.event", "event": event_type, "payload": payload},
    )


def send_plugin_command(server_id, command, payload):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"plugin_{server_id}",
        {"type": "plugin.command", "command": command, "payload": payload},
    )
