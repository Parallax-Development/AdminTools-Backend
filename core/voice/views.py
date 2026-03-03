from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from core.voice.models import VoiceChannel, VoiceSession
from core.voice.serializers import VoiceChannelSerializer, VoiceSessionSerializer


class VoiceChannelViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = VoiceChannel.objects.all().order_by("id")
    serializer_class = VoiceChannelSerializer


class VoiceSessionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = VoiceSession.objects.all().order_by("-started_at")
    serializer_class = VoiceSessionSerializer

    @action(detail=False, methods=["get"])
    def active(self, request):
        queryset = self.get_queryset().filter(ended_at__isnull=True)
        serializer = self.get_serializer(queryset, many=True)
        return Response({"count": queryset.count(), "results": serializer.data})
