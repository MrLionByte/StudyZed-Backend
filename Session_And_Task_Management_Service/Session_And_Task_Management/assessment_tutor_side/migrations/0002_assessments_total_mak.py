# Generated by Django 5.1.2 on 2025-03-08 05:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assessment_tutor_side', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='assessments',
            name='total_mak',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
