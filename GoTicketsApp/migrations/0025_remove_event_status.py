# Generated by Django 5.0.4 on 2024-08-01 13:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('GoTicketsApp', '0024_event_status'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='event',
            name='status',
        ),
    ]