# Generated by Django 3.2.4 on 2021-08-02 01:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sunsetRatingReciever', '0005_auto_20210801_1907'),
    ]

    operations = [
        migrations.CreateModel(
            name='Error',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(verbose_name='Date and Time of Recording')),
                ('type', models.CharField(max_length=100)),
                ('info', models.TextField()),
            ],
        ),
    ]