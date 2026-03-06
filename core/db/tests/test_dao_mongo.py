import os
import unittest

from django.utils import timezone

from core.db.config import get_domain_backend
from core.db.mongo import get_mongo_database
from core.db.provider import get_dao_provider


@unittest.skipUnless(
    get_domain_backend() == "mongodb" and os.getenv("MONGO_URI"), "mongodb backend only"
)
class MongoDAOTests(unittest.TestCase):
    def setUp(self):
        self.provider = get_dao_provider()
        db = get_mongo_database()
        db.users.delete_many({})
        db.voice_channels.delete_many({})
        db.voice_sessions.delete_many({})
        db.telemetry_events.delete_many({})

    def test_user_channel_session_flow(self):
        user = self.provider.users.create(
            {
                "username": "tester",
                "display_name": "Tester",
                "minecraft_uuid": None,
                "is_online": False,
                "last_seen_at": None,
                "current_channel": None,
            }
        )
        fetched = self.provider.users.get(id=user["id"])
        self.assertIsNotNone(fetched)

        channel = self.provider.voice_channels.create(
            {
                "server_id": "srv",
                "external_id": "lobby",
                "name": "Lobby",
                "is_active": True,
                "metadata": {},
            }
        )
        session = self.provider.voice_sessions.create(
            {
                "user": user["id"],
                "channel": channel["id"],
                "server_id": "srv",
                "started_at": timezone.now(),
                "ended_at": None,
                "metadata": {},
            }
        )
        sessions = self.provider.voice_sessions.list(filters={"ended_at__isnull": True})
        self.assertTrue(any(item["id"] == session["id"] for item in sessions))

    def test_telemetry_crud(self):
        telemetry = self.provider.telemetry.create(
            {
                "event_id": "evt-1",
                "event_type": "packet_loss",
                "server_id": "srv",
                "payload": {"loss": 0.1},
                "user": None,
                "session": None,
                "occurred_at": timezone.now(),
            }
        )
        fetched = self.provider.telemetry.get(id=telemetry["id"])
        self.assertIsNotNone(fetched)
