from rest_framework import status, viewsets
from rest_framework.response import Response

from core.db.provider import get_dao_provider
from core.db.serializers import TelemetryEventRecordSerializer


class TelemetryEventViewSet(viewsets.ViewSet):
    serializer_class = TelemetryEventRecordSerializer

    def list(self, request):
        provider = get_dao_provider()
        items = provider.telemetry.list(order_by="-occurred_at")
        serializer = self.serializer_class(items, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        provider = get_dao_provider()
        item = provider.telemetry.get(id=pk)
        if not item:
            return Response({"detail": "not_found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(item)
        return Response(serializer.data)
