from django.conf import settings
from django.contrib.postgres.indexes import GinIndex
from django.db import migrations, models
from django.db.models import Q


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="VoiceChannel",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("server_id", models.CharField(max_length=64)),
                ("external_id", models.CharField(max_length=128)),
                ("name", models.CharField(max_length=128)),
                ("is_active", models.BooleanField(default=True)),
                ("metadata", models.JSONField(blank=True, default=dict)),
            ],
            options={
                "constraints": [
                    models.UniqueConstraint(fields=["server_id", "external_id"], name="uniq_channel_server_external")
                ],
                "indexes": [
                    models.Index(fields=["server_id"], name="voice_voicechannel_server_id_idx"),
                    models.Index(fields=["external_id"], name="voice_voicechannel_external_id_idx"),
                    models.Index(fields=["name"], name="voice_voicechannel_name_idx"),
                    GinIndex(fields=["metadata"], name="voice_channel_metadata_gin"),
                ],
            },
        ),
        migrations.CreateModel(
            name="VoiceSession",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "user",
                    models.ForeignKey(on_delete=models.deletion.CASCADE, related_name="voice_sessions", to=settings.AUTH_USER_MODEL),
                ),
                (
                    "channel",
                    models.ForeignKey(on_delete=models.deletion.PROTECT, related_name="sessions", to="voice.voicechannel"),
                ),
                ("server_id", models.CharField(max_length=64)),
                ("started_at", models.DateTimeField(auto_now_add=True)),
                ("ended_at", models.DateTimeField(blank=True, null=True)),
                ("metadata", models.JSONField(blank=True, default=dict)),
            ],
            options={
                "indexes": [
                    models.Index(fields=["server_id"], name="voice_voicesession_server_id_idx"),
                    models.Index(fields=["started_at"], name="voice_voicesession_started_at_idx"),
                    models.Index(fields=["ended_at"], name="voice_voicesession_ended_at_idx"),
                    GinIndex(fields=["metadata"], name="voice_session_metadata_gin"),
                ],
                "constraints": [
                    models.UniqueConstraint(
                        fields=["user"],
                        condition=Q(ended_at__isnull=True),
                        name="uniq_active_session_user",
                    )
                ],
            },
        ),
    ]
