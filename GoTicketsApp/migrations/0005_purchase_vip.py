# Generated by Django 5.0.4 on 2024-04-24 16:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('GoTicketsApp', '0004_remove_cartitem_ticket_delete_cart_delete_cartitem'),
    ]

    operations = [
        migrations.AddField(
            model_name='purchase',
            name='vip',
            field=models.BooleanField(default=False),
        ),
    ]