# Generated by Django 5.0.4 on 2024-07-30 11:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('GoTicketsApp', '0016_rename_friday_price_event_price_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='purchase',
            name='quantity',
            field=models.IntegerField(),
        ),
    ]
