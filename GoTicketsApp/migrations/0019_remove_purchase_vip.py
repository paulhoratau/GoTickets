# Generated by Django 5.0.4 on 2024-07-30 12:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('GoTicketsApp', '0018_alter_purchase_quantity'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='purchase',
            name='vip',
        ),
    ]
