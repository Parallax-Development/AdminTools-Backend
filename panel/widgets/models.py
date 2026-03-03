from django.db import models
from django.contrib.postgres.indexes import GinIndex


class WidgetDefinition(models.Model):
    WIDGET_TYPES = [
        ("datatable", "datatable"),
        ("chart", "chart"),
        ("counter", "counter"),
        ("button", "button"),
        ("feed", "feed"),
    ]

    key = models.CharField(max_length=128, unique=True)
    name = models.CharField(max_length=128)
    description = models.TextField(blank=True)
    widget_type = models.CharField(max_length=32, choices=WIDGET_TYPES)
    schema = models.JSONField(default=dict)
    is_active = models.BooleanField(default=True)
    required_permissions = models.ManyToManyField("permissions.Permission", blank=True, related_name="widgets")
    allowed_roles = models.ManyToManyField("permissions.Role", blank=True, related_name="widgets")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["widget_type"]),
            GinIndex(fields=["schema"], name="widget_schema_gin"),
        ]
