# -*- coding: utf-8 -*-
# Generated by Django 1.11.23 on 2020-01-05 20:48
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0020_auto_20191210_1423'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='bookingpackageservice',
            options={'ordering': ['datetime_from', 'time'], 'verbose_name': 'Booking Package Service', 'verbose_name_plural': 'Bookings Packages Services'},
        ),
        migrations.AlterModelOptions(
            name='bookingpax',
            options={'ordering': ['pax_group'], 'verbose_name': 'Booking Pax', 'verbose_name_plural': 'Booking Rooming List'},
        ),
        migrations.AlterModelOptions(
            name='bookingservice',
            options={'ordering': ['datetime_from', 'datetime_to', 'time'], 'verbose_name': 'Booking Service', 'verbose_name_plural': 'Booking Services'},
        ),
        migrations.AlterModelOptions(
            name='providerbookingpayment',
            options={'ordering': ['-date'], 'verbose_name': 'Provider Booking Payment', 'verbose_name_plural': 'Providers Bookings Payments'},
        ),
        migrations.AddField(
            model_name='bookingservicepax',
            name='force_adult',
            field=models.BooleanField(default=False),
        ),
    ]
