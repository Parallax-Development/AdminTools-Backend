from rest_framework import viewsets

from panel.dashboards.models import DashboardLayout
from panel.dashboards.serializers import DashboardLayoutSerializer


class DashboardLayoutViewSet(viewsets.ModelViewSet):
    queryset = DashboardLayout.objects.all().order_by("-updated_at")
    serializer_class = DashboardLayoutSerializer
