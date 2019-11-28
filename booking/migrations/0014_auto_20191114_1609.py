# -*- coding: utf-8 -*-
# Generated by Django 1.11.17 on 2019-11-14 21:09
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0013_auto_20191113_0650'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='booking',
            options={'default_permissions': ('add', 'change'), 'permissions': (('change_amounts', 'Can change amounts of Booking'), ('change_services_amounts', 'Can select services to change amounts')), 'verbose_name': 'Booking', 'verbose_name_plural': 'Bookings'},
        ),
        migrations.AlterModelOptions(
            name='bookingservice',
            options={'ordering': ['datetime_from', 'datetime_to'], 'verbose_name': 'Booking Service', 'verbose_name_plural': 'Booking Services'},
        ),
        migrations.AlterField(
            model_name='bookingservice',
            name='v_notes',
            field=models.CharField(blank=True, max_length=300, null=True, verbose_name='Voucher Notes'),
        ),
    ]