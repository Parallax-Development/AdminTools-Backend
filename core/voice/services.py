from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.utils import timezone

from core.db.provider import get_dao_provider, is_mongodb_backend
from core.telemetry.models import TelemetryEvent
from core.voice.models import VoiceChannel, VoiceSession
from core.voice.redis import add_active_user, remove_active_user


def set_user_online(user, channel, server_id, metadata):
    if is_mongodb_backend():
        provider = get_dao_provider()
        now = timezone.now()
        provider.users.update(user["id"], {"is_online": True, "current_channel": channel["id"], "last_seen_at": now})
        session = provider.voice_sessions.create(
            {
                "user": user["id"],
                "channel": channel["id"],
                "server_id": server_id,
                "started_at": now,
                "ended_at": None,
                "metadata": metadata or {},
            }
        )
        add_active_user(
            server_id,
            str(user["id"]),
            {
                "user_id": user["id"],
                "username": user["username"],
                "display_name": user.get("display_name") or user["username"],
                "channel_id": channel["id"],
                "channel_name": channel["name"],
                "started_at": session["started_at"].isoformat(),
            },
        )
        publish_admin_event(
            "voice.user_connected",
            {
                "user_id": user["id"],
                "session_id": session["id"],
                "server_id": server_id,
                "channel_id": channel["id"],
            },
        )
        return session

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
    if is_mongodb_backend():
        provider = get_dao_provider()
        now = timezone.now()
        provider.users.update(user["id"], {"is_online": False, "current_channel": None, "last_seen_at": now})
        active_sessions = provider.voice_sessions.list(
            filters={"user": user["id"], "ended_at__isnull": True}, order_by="-started_at", limit=1
        )
        active_session = active_sessions[0] if active_sessions else None
        if active_session:
            payload = {"ended_at": now}
            if metadata:
                payload["metadata"] = {**(active_session.get("metadata") or {}), **metadata}
            provider.voice_sessions.update(active_session["id"], payload)
        remove_active_user(server_id, str(user["id"]))
        publish_admin_event(
            "voice.user_disconnected",
            {
                "user_id": user["id"],
                "session_id": active_session["id"] if active_session else None,
                "server_id": server_id,
            },
        )
        return active_session

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
    if is_mongodb_backend():
        provider = get_dao_provider()
        telemetry = provider.telemetry.create(
            {
                "event_id": event_id or f"auto-{timezone.now().timestamp()}",
                "event_type": event_type,
                "server_id": server_id,
                "payload": payload or {},
                "user": user["id"] if isinstance(user, dict) else None,
                "session": session["id"] if isinstance(session, dict) else None,
                "occurred_at": occurred_at or timezone.now(),
            }
        )
        publish_admin_event(
            "telemetry.event",
            {
                "event_id": telemetry["event_id"],
                "event_type": telemetry["event_type"],
                "server_id": telemetry["server_id"],
                "payload": telemetry["payload"],
                "occurred_at": telemetry["occurred_at"].isoformat(),
            },
        )
        return telemetry

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
    if is_mongodb_backend():
        provider = get_dao_provider()
        channel = provider.voice_channels.get(server_id=server_id, external_id=external_id)
        if channel:
            if name and channel["name"] != name:
                channel = provider.voice_channels.update(channel["id"], {"name": name})
            return channel
        return provider.voice_channels.create(
            {
                "server_id": server_id,
                "external_id": external_id,
                "name": name or external_id,
                "is_active": True,
                "metadata": {},
            }
        )

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
