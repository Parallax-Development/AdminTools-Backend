from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.response import Response

from core.db.provider import get_dao_provider
from core.db.serializers import DashboardLayoutRecordSerializer


class DashboardLayoutViewSet(viewsets.ViewSet):
    serializer_class = DashboardLayoutRecordSerializer

    def list(self, request):
        provider = get_dao_provider()
        items = provider.dashboards.list(order_by="-updated_at")
        serializer = self.serializer_class(items, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        provider = get_dao_provider()
        item = provider.dashboards.get(id=pk)
        if not item:
            return Response({"detail": "not_found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(item)
        return Response(serializer.data)

    def create(self, request):
        provider = get_dao_provider()
        payload = {
            "user": request.data.get("user"),
            "name": request.data.get("name"),
            "layout": request.data.get("layout", {}),
            "is_default": bool(request.data.get("is_default", False)),
            "updated_at": timezone.now(),
        }
        item = provider.dashboards.create(payload)
        serializer = self.serializer_class(item)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        provider = get_dao_provider()
        payload = {
            "name": request.data.get("name"),
            "layout": request.data.get("layout"),
            "is_default": request.data.get("is_default"),
            "updated_at": timezone.now(),
        }
        cleaned = {key: value for key, value in payload.items() if value is not None}
        item = provider.dashboards.update(pk, cleaned)
        if not item:
            return Response({"detail": "not_found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(item)
        return Response(serializer.data)

    def destroy(self, request, pk=None):
        provider = get_dao_provider()
        deleted = provider.dashboards.delete(pk)
        if not deleted:
            return Response({"detail": "not_found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_204_NO_CONTENT)
