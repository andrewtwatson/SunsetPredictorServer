# Generated by Django 3.2.4 on 2021-08-08 21:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sunsetRatingReciever', '0006_error'),
    ]

    operations = [
        migrations.AddField(
            model_name='sunsetratingentry',
            name='air_pressure',
            field=models.IntegerField(default=None, null=True),
        ),
    ]
