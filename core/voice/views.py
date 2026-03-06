from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from core.db.provider import get_dao_provider
from core.db.serializers import VoiceChannelRecordSerializer, VoiceSessionRecordSerializer


class VoiceChannelViewSet(viewsets.ViewSet):
    serializer_class = VoiceChannelRecordSerializer

    def list(self, request):
        provider = get_dao_provider()
        items = provider.voice_channels.list(order_by="id")
        serializer = self.serializer_class(items, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        provider = get_dao_provider()
        item = provider.voice_channels.get(id=pk)
        if not item:
            return Response({"detail": "not_found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(item)
        return Response(serializer.data)


class VoiceSessionViewSet(viewsets.ViewSet):
    serializer_class = VoiceSessionRecordSerializer

    def list(self, request):
        provider = get_dao_provider()
        items = provider.voice_sessions.list(order_by="-started_at")
        serializer = self.serializer_class(items, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        provider = get_dao_provider()
        item = provider.voice_sessions.get(id=pk)
        if not item:
            return Response({"detail": "not_found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(item)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def active(self, request):
        provider = get_dao_provider()
        items = provider.voice_sessions.list(filters={"ended_at__isnull": True}, order_by="-started_at")
        serializer = self.serializer_class(items, many=True)
        return Response({"count": len(items), "results": serializer.data})
