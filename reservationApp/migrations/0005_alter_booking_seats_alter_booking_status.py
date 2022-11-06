# Generated by Django 4.0.3 on 2022-11-05 14:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reservationApp', '0004_booking'),
    ]

    operations = [
        migrations.AlterField(
            model_name='booking',
            name='seats',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='booking',
            name='status',
            field=models.CharField(choices=[('1', 'Pending'), ('2', 'Paid')], default=1, max_length=2),
        ),
    ]