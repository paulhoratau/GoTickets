# Generated by Django 5.0.4 on 2024-05-08 20:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('GoTicketsApp', '0007_remove_purchase_is_confirmed'),
    ]

    operations = [
        migrations.CreateModel(
            name='card',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('card_number', models.CharField(max_length=16)),
                ('date', models.CharField(max_length=5)),
                ('cvv', models.CharField(max_length=3)),
            ],
        ),
    ]
