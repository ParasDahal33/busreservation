# Generated by Django 4.0.3 on 2022-11-06 02:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reservationApp', '0007_remove_bus_rem_seats_schedule_rem_seats_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='schedule',
            name='rem_seats',
            field=models.IntegerField(),
        ),
    ]