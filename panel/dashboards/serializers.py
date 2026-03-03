from rest_framework import serializers

from panel.dashboards.models import DashboardLayout


class DashboardLayoutSerializer(serializers.ModelSerializer):
    class Meta:
        model = DashboardLayout
        fields = ["id", "user", "name", "layout", "is_default", "updated_at"]
