from django.conf import settings
from django.contrib.postgres.indexes import GinIndex
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("voice", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="TelemetryEvent",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("event_id", models.CharField(max_length=128, unique=True)),
                ("event_type", models.CharField(max_length=128)),
                ("server_id", models.CharField(max_length=64)),
                (
                    "user",
                    models.ForeignKey(blank=True, null=True, on_delete=models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
                ),
                (
                    "session",
                    models.ForeignKey(blank=True, null=True, on_delete=models.deletion.SET_NULL, to="voice.voicesession"),
                ),
                ("payload", models.JSONField(blank=True, default=dict)),
                ("occurred_at", models.DateTimeField()),
            ],
            options={
                "indexes": [
                    models.Index(fields=["event_type"], name="telemetry_telemetryevent_event_type_idx"),
                    models.Index(fields=["server_id"], name="telemetry_telemetryevent_server_id_idx"),
                    models.Index(fields=["occurred_at"], name="telemetry_telemetryevent_occurred_at_idx"),
                    GinIndex(fields=["payload"], name="telemetry_payload_gin"),
                ]
            },
        ),
    ]
