# Generated by Django 3.2.4 on 2021-07-10 19:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sunsetRatingReciever', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='user_id',
            field=models.BigAutoField(primary_key=True, serialize=False),
        ),
    ]
