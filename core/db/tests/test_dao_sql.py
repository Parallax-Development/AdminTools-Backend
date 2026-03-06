import unittest

from django.test import TestCase
from django.utils import timezone

from core.db.config import get_domain_backend
from core.db.provider import get_dao_provider


class BaseSQLDAOTests(TestCase):
    def setUp(self):
        self.provider = get_dao_provider()

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

        updated = self.provider.users.update(user["id"], {"is_online": True})
        self.assertTrue(updated["is_online"])

        deleted = self.provider.voice_sessions.delete(session["id"])
        self.assertTrue(deleted)

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


@unittest.skipUnless(get_domain_backend() == "sqlite", "sqlite backend only")
class SQLiteDAOTests(BaseSQLDAOTests):
    pass


@unittest.skipUnless(get_domain_backend() == "postgres", "postgres backend only")
class PostgresDAOTests(BaseSQLDAOTests):
    pass


@unittest.skipUnless(get_domain_backend() == "mysql", "mysql backend only")
class MySQLDAOTests(BaseSQLDAOTests):
    pass


@unittest.skipUnless(get_domain_backend() == "oracle", "oracle backend only")
class OracleDAOTests(BaseSQLDAOTests):
    pass


@unittest.skipUnless(get_domain_backend() == "sqlserver", "sqlserver backend only")
class SQLServerDAOTests(BaseSQLDAOTests):
    pass
