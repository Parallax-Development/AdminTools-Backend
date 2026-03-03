from django.conf import settings
from django.db import models
from django.contrib.postgres.indexes import GinIndex


class DashboardLayout(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="dashboards")
    name = models.CharField(max_length=128)
    layout = models.JSONField(default=dict)
    is_default = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "name"], name="uniq_dashboard_user_name")
        ]
        indexes = [GinIndex(fields=["layout"], name="dashboard_layout_gin")]
