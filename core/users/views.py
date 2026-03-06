from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from core.db.provider import get_dao_provider
from core.db.serializers import UserRecordSerializer


class UserViewSet(viewsets.ViewSet):
    serializer_class = UserRecordSerializer

    def list(self, request):
        provider = get_dao_provider()
        items = provider.users.list(order_by="id")
        serializer = self.serializer_class(items, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        provider = get_dao_provider()
        item = provider.users.get(id=pk)
        if not item:
            return Response({"detail": "not_found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(item)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def active(self, request):
        provider = get_dao_provider()
        items = provider.users.list(filters={"is_online": True}, order_by="id")
        serializer = self.serializer_class(items, many=True)
        return Response({"count": len(items), "results": serializer.data, "timestamp": timezone.now()})
