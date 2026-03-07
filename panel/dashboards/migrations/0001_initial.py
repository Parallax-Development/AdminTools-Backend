from django.conf import settings
from django.contrib.postgres.indexes import GinIndex
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="DashboardLayout",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "user",
                    models.ForeignKey(on_delete=models.deletion.CASCADE, related_name="dashboards", to=settings.AUTH_USER_MODEL),
                ),
                ("name", models.CharField(max_length=128)),
                ("layout", models.JSONField(default=dict)),
                ("is_default", models.BooleanField(default=False)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "constraints": [
                    models.UniqueConstraint(fields=["user", "name"], name="uniq_dashboard_user_name")
                ],
                "indexes": [GinIndex(fields=["layout"], name="dashboard_layout_gin")],
            },
        ),
    ]
