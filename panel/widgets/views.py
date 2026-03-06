from rest_framework import status, viewsets
from rest_framework.response import Response

from core.db.provider import get_dao_provider
from core.db.serializers import WidgetDefinitionRecordSerializer


class WidgetDefinitionViewSet(viewsets.ViewSet):
    serializer_class = WidgetDefinitionRecordSerializer

    def list(self, request):
        provider = get_dao_provider()
        items = provider.widgets.list(filters={"is_active": True}, order_by="id")
        serializer = self.serializer_class(items, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        provider = get_dao_provider()
        item = provider.widgets.get(id=pk)
        if not item:
            return Response({"detail": "not_found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(item)
        return Response(serializer.data)
