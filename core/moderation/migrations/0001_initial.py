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
            name="ModerationAction",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "target_user",
                    models.ForeignKey(
                        on_delete=models.deletion.CASCADE,
                        related_name="moderation_actions",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "actor_user",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=models.deletion.SET_NULL,
                        related_name="moderation_actions_issued",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                ("server_id", models.CharField(max_length=64)),
                ("action_type", models.CharField(choices=[("mute", "mute"), ("kick", "kick"), ("ban", "ban"), ("unmute", "unmute")], max_length=16)),
                ("reason", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("expires_at", models.DateTimeField(blank=True, null=True)),
                ("metadata", models.JSONField(blank=True, default=dict)),
            ],
            options={
                "indexes": [
                    models.Index(fields=["server_id"], name="moderation_moderationaction_server_id_idx"),
                    models.Index(fields=["action_type"], name="moderation_moderationaction_action_type_idx"),
                    models.Index(fields=["created_at"], name="moderation_moderationaction_created_at_idx"),
                    GinIndex(fields=["metadata"], name="moderation_metadata_gin"),
                ]
            },
        ),
    ]
