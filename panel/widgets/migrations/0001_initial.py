from django.contrib.postgres.indexes import GinIndex
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("permissions", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="WidgetDefinition",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("key", models.CharField(max_length=128, unique=True)),
                ("name", models.CharField(max_length=128)),
                ("description", models.TextField(blank=True)),
                (
                    "widget_type",
                    models.CharField(
                        choices=[
                            ("datatable", "datatable"),
                            ("chart", "chart"),
                            ("counter", "counter"),
                            ("button", "button"),
                            ("feed", "feed"),
                        ],
                        max_length=32,
                    ),
                ),
                ("schema", models.JSONField(default=dict)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "required_permissions",
                    models.ManyToManyField(blank=True, related_name="widgets", to="permissions.permission"),
                ),
                ("allowed_roles", models.ManyToManyField(blank=True, related_name="widgets", to="permissions.role")),
            ],
            options={
                "indexes": [
                    models.Index(fields=["widget_type"], name="widgets_widgetdefinition_widget_type_idx"),
                    GinIndex(fields=["schema"], name="widget_schema_gin"),
                ]
            },
        ),
    ]
