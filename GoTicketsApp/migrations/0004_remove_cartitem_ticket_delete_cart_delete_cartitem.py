# Generated by Django 5.0.4 on 2024-04-23 16:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('GoTicketsApp', '0003_purchase'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cartitem',
            name='ticket',
        ),
        migrations.DeleteModel(
            name='Cart',
        ),
        migrations.DeleteModel(
            name='CartItem',
        ),
    ]
