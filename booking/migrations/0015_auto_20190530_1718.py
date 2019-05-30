# -*- coding: utf-8 -*-
# Generated by Django 1.11.18 on 2019-05-30 21:18
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0014_auto_20190518_0920'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='bookingextra',
            options={'default_permissions': ('add', 'change'), 'verbose_name': 'Booking Extra', 'verbose_name_plural': 'Booking Extras'},
        ),
        migrations.AlterModelOptions(
            name='bookingservice',
            options={'default_permissions': ('add', 'change'), 'ordering': ['datetime_from'], 'verbose_name': 'Booking Service', 'verbose_name_plural': 'Booking Services'},
        ),
        migrations.AlterModelOptions(
            name='bookingtransfer',
            options={'default_permissions': ('add', 'change'), 'verbose_name': 'Booking Transfer', 'verbose_name_plural': 'Booking Transfers'},
        ),
        migrations.AlterField(
            model_name='bookingpackageservice',
            name='description',
            field=models.CharField(blank=True, max_length=1000, null=True),
        ),
        migrations.AlterField(
            model_name='bookingservice',
            name='description',
            field=models.CharField(blank=True, max_length=1000, null=True),
        ),
        migrations.AlterField(
            model_name='packageservice',
            name='description',
            field=models.CharField(blank=True, max_length=1000, null=True),
        ),
        migrations.AlterField(
            model_name='quotepackageservice',
            name='description',
            field=models.CharField(blank=True, max_length=1000, null=True),
        ),
        migrations.AlterField(
            model_name='quoteservice',
            name='description',
            field=models.CharField(blank=True, max_length=1000, null=True),
        ),
    ]
