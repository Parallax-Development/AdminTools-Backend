from rest_framework import viewsets

from core.telemetry.models import TelemetryEvent
from core.telemetry.serializers import TelemetryEventSerializer


class TelemetryEventViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = TelemetryEvent.objects.all().order_by("-occurred_at")
    serializer_class = TelemetryEventSerializer
