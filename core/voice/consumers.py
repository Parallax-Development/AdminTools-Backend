import hashlib
import hmac
import time
from urllib.parse import parse_qs

from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.conf import settings
from django.utils import timezone

from core.db.provider import get_dao_provider, is_mongodb_backend
from core.users.models import User
from core.voice.redis import is_duplicate_event
from core.voice.services import get_or_create_channel, record_telemetry, set_user_offline, set_user_online


class PluginConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        query = parse_qs(self.scope.get("query_string", b"").decode())
        api_key = (query.get("api_key") or [""])[0]
        signature = (query.get("signature") or [""])[0]
        timestamp = (query.get("timestamp") or [""])[0]
        nonce = (query.get("nonce") or [""])[0]
        server_id = (query.get("server_id") or [""])[0]

        if not self.is_valid_signature(api_key, server_id, timestamp, nonce, signature):
            await self.close(code=4401)
            return

        self.server_id = server_id
        await self.channel_layer.group_add(f"plugin_{server_id}", self.channel_name)
        await self.accept()
        await self.send_json({"type": "ack", "server_id": server_id})

    async def disconnect(self, code):
        if hasattr(self, "server_id"):
            await self.channel_layer.group_discard(f"plugin_{self.server_id}", self.channel_name)

    async def receive_json(self, content, **kwargs):
        event_type = content.get("event_type")
        event_id = content.get("event_id")
        payload = content.get("payload") or {}

        if event_id and is_duplicate_event(event_id, settings.PLUGIN_EVENT_TTL_SECONDS):
            await self.send_json({"type": "ack", "event_id": event_id, "status": "duplicate"})
            return

        if event_type == "voice.user_connected":
            await self.handle_user_connected(payload)
        elif event_type == "voice.user_disconnected":
            await self.handle_user_disconnected(payload)
        elif event_type == "telemetry.event":
            await self.handle_telemetry(payload, event_id)

        await self.send_json({"type": "ack", "event_id": event_id, "status": "ok"})

    async def handle_user_connected(self, payload):
        minecraft_uuid = payload.get("minecraft_uuid")
        username = payload.get("username") or "unknown"
        display_name = payload.get("display_name") or username
        channel_id = payload.get("channel_id")
        channel_name = payload.get("channel_name")

        if is_mongodb_backend():
            provider = get_dao_provider()
            if minecraft_uuid:
                user = provider.users.get(minecraft_uuid=minecraft_uuid)
            else:
                user = provider.users.get(username=username)
            if not user:
                user = provider.users.create(
                    {
                        "minecraft_uuid": minecraft_uuid,
                        "username": username,
                        "display_name": display_name,
                        "is_online": False,
                        "last_seen_at": None,
                        "current_channel": None,
                        "external_id": None,
                    }
                )
            if display_name and user.get("display_name") != display_name:
                user = provider.users.update(user["id"], {"display_name": display_name})
            channel = get_or_create_channel(self.server_id, channel_id, channel_name)
            set_user_online(user, channel, self.server_id, payload)
            return

        if minecraft_uuid:
            user, _ = User.objects.get_or_create(minecraft_uuid=minecraft_uuid, defaults={"username": username})
        else:
            user, _ = User.objects.get_or_create(username=username)

        if display_name and user.display_name != display_name:
            user.display_name = display_name
            user.save(update_fields=["display_name"])

        channel = get_or_create_channel(self.server_id, channel_id, channel_name)
        set_user_online(user, channel, self.server_id, payload)

    async def handle_user_disconnected(self, payload):
        minecraft_uuid = payload.get("minecraft_uuid")
        username = payload.get("username")

        if is_mongodb_backend():
            provider = get_dao_provider()
            if minecraft_uuid:
                user = provider.users.get(minecraft_uuid=minecraft_uuid)
            else:
                user = provider.users.get(username=username)
            if user:
                set_user_offline(user, self.server_id, payload)
            return

        if minecraft_uuid:
            user = User.objects.filter(minecraft_uuid=minecraft_uuid).first()
        else:
            user = User.objects.filter(username=username).first()

        if user:
            set_user_offline(user, self.server_id, payload)

    async def handle_telemetry(self, payload, event_id):
        event_type = payload.get("type") or "generic"
        occurred_at = payload.get("occurred_at")
        parsed_time = timezone.now()
        if occurred_at:
            parsed_time = timezone.datetime.fromisoformat(occurred_at)
        record_telemetry(event_type, self.server_id, payload, event_id=event_id, occurred_at=parsed_time)

    async def plugin_command(self, event):
        await self.send_json({"type": "command", "command": event["command"], "payload": event["payload"]})

    def is_valid_signature(self, api_key, server_id, timestamp, nonce, signature):
        if not api_key or not signature or not timestamp or not nonce or not server_id:
            return False

        try:
            timestamp_value = int(timestamp)
        except ValueError:
            return False

        if abs(int(time.time()) - timestamp_value) > settings.PLUGIN_ALLOWED_DRIFT_SECONDS:
            return False

        secret = settings.PLUGIN_SHARED_SECRETS.get(api_key)
        if not secret:
            return False

        base_string = f"{api_key}.{server_id}.{timestamp}.{nonce}"
        expected = hmac.new(secret.encode(), base_string.encode(), hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected, signature)


class AdminConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("admin_updates", self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard("admin_updates", self.channel_name)

    async def admin_event(self, event):
        await self.send_json({"type": "event", "event": event["event"], "payload": event["payload"]})
