# Generated by Django 5.0.4 on 2024-04-29 20:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('GoTicketsApp', '0006_purchase_is_confirmed'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='purchase',
            name='is_confirmed',
        ),
    ]