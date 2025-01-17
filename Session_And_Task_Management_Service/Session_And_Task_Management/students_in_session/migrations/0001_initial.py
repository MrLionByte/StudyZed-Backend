# Generated by Django 5.1.2 on 2025-01-16 14:07

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('session_tutor', '0005_session_session_grade'),
    ]

    operations = [
        migrations.CreateModel(
            name='StudentsInSession',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('student_code', models.CharField(max_length=150)),
                ('is_allowded', models.BooleanField(default=False)),
                ('name_per_session', models.CharField(blank=True, max_length=250)),
                ('joined_on', models.DateField(auto_now_add=True)),
                ('updated_on', models.DateField(auto_now=True)),
                ('session', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='session_tutor.session')),
            ],
        ),
    ]
