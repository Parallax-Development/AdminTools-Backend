from django.urls import include, path
from rest_framework.routers import DefaultRouter

from core.moderation.views import ModerationActionViewSet
from core.telemetry.views import TelemetryEventViewSet
from core.users.views import UserViewSet
from core.voice.views import VoiceChannelViewSet, VoiceSessionViewSet
from panel.dashboards.views import DashboardLayoutViewSet
from panel.widgets.views import WidgetDefinitionViewSet

router = DefaultRouter()
router.register("users", UserViewSet, basename="users")
router.register("voice-channels", VoiceChannelViewSet, basename="voice-channels")
router.register("voice-sessions", VoiceSessionViewSet, basename="voice-sessions")
router.register("moderation", ModerationActionViewSet, basename="moderation")
router.register("telemetry", TelemetryEventViewSet, basename="telemetry")
router.register("widgets", WidgetDefinitionViewSet, basename="widgets")
router.register("dashboards", DashboardLayoutViewSet, basename="dashboards")

urlpatterns = [
    path("api/", include(router.urls)),
]
