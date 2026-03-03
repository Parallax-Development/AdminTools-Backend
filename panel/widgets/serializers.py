from rest_framework import serializers

from panel.widgets.models import WidgetDefinition


class WidgetDefinitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = WidgetDefinition
        fields = [
            "id",
            "key",
            "name",
            "description",
            "widget_type",
            "schema",
            "is_active",
            "required_permissions",
            "allowed_roles",
        ]
