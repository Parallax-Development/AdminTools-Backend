from core.db.config import get_domain_backend
from core.db.dao import DjangoDAO, MongoDAO
from core.db.mappers import (
    map_dashboard_layout,
    map_moderation_action,
    map_telemetry_event,
    map_user,
    map_voice_channel,
    map_voice_session,
    map_widget_definition,
)


def is_mongodb_backend():
    return get_domain_backend() == "mongodb"


def _build_django_daos():
    from core.moderation.models import ModerationAction
    from core.telemetry.models import TelemetryEvent
    from core.users.models import User
    from core.voice.models import VoiceChannel, VoiceSession
    from panel.dashboards.models import DashboardLayout
    from panel.widgets.models import WidgetDefinition

    return {
        "users": DjangoDAO(User, map_user),
        "voice_channels": DjangoDAO(VoiceChannel, map_voice_channel),
        "voice_sessions": DjangoDAO(VoiceSession, map_voice_session),
        "moderation": DjangoDAO(ModerationAction, map_moderation_action),
        "telemetry": DjangoDAO(TelemetryEvent, map_telemetry_event),
        "widgets": DjangoDAO(WidgetDefinition, map_widget_definition),
        "dashboards": DjangoDAO(DashboardLayout, map_dashboard_layout),
    }


def _build_mongo_daos():
    return {
        "users": MongoDAO("users"),
        "voice_channels": MongoDAO("voice_channels"),
        "voice_sessions": MongoDAO("voice_sessions"),
        "moderation": MongoDAO("moderation_actions"),
        "telemetry": MongoDAO("telemetry_events"),
        "widgets": MongoDAO("widgets"),
        "dashboards": MongoDAO("dashboards"),
    }


class DAOProvider:
    def __init__(self):
        self.backend = get_domain_backend()
        self._daos = _build_mongo_daos() if self.backend == "mongodb" else _build_django_daos()

    @property
    def users(self):
        return self._daos["users"]

    @property
    def voice_channels(self):
        return self._daos["voice_channels"]

    @property
    def voice_sessions(self):
        return self._daos["voice_sessions"]

    @property
    def moderation(self):
        return self._daos["moderation"]

    @property
    def telemetry(self):
        return self._daos["telemetry"]

    @property
    def widgets(self):
        return self._daos["widgets"]

    @property
    def dashboards(self):
        return self._daos["dashboards"]


_provider = None


def get_dao_provider():
    global _provider
    if _provider is None:
        _provider = DAOProvider()
    return _provider
