from rest_framework import viewsets

from panel.widgets.models import WidgetDefinition
from panel.widgets.serializers import WidgetDefinitionSerializer


class WidgetDefinitionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = WidgetDefinition.objects.filter(is_active=True).order_by("id")
    serializer_class = WidgetDefinitionSerializer
