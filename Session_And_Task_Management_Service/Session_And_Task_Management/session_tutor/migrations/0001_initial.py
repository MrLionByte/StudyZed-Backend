# Generated by Django 5.1.2 on 2025-01-07 14:09

import cloudinary.models
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="session",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("tutor_code", models.CharField(max_length=150)),
                ("session_name", models.CharField(max_length=200)),
                ("session_duration", models.IntegerField()),
                ("session_discription", models.TextField()),
                ("session_code", models.CharField(max_length=150)),
                ("is_paid", models.BooleanField(default=False)),
                ("is_active", models.BooleanField(default=False)),
                (
                    "image",
                    cloudinary.models.CloudinaryField(
                        blank=True, max_length=255, verbose_name="image"
                    ),
                ),
                ("created_at", models.DateField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
