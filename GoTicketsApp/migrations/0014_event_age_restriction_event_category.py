# Generated by Django 5.0.4 on 2024-07-29 09:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('GoTicketsApp', '0013_remove_event_location'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='age_restriction',
            field=models.CharField(choices=[('No', 'No'), ('12', '12+'), ('14', '14+'), ('16', '16+'), ('18', '18+'), ('21', '21+')], default='No', max_length=2),
        ),
        migrations.AddField(
            model_name='event',
            name='category',
            field=models.CharField(choices=[('Stand-up Comedy', 'Stand-up Comedy'), ('TH', 'Theatre'), ('SP', 'Sport'), ('CO', 'Concert')], default='Stand-up Comedy', max_length=20),
        ),
    ]