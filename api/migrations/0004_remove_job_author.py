# Generated by Django 5.0.6 on 2024-07-04 08:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_job_author_job_created_at'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='job',
            name='author',
        ),
    ]
