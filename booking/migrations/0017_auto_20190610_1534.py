# -*- coding: utf-8 -*-
# Generated by Django 1.11.18 on 2019-06-10 19:34
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0016_auto_20190603_2224'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='packageallotment',
            name='service_location',
        ),
        migrations.AddField(
            model_name='packageservice',
            name='service_location',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Location'),
        ),
        migrations.AlterField(
            model_name='bookingpackageservice',
            name='service_location',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Location'),
        ),
        migrations.AlterField(
            model_name='bookingservice',
            name='service_location',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Location'),
        ),
        migrations.AlterField(
            model_name='quotepackageservice',
            name='service_location',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Location'),
        ),
        migrations.AlterField(
            model_name='quoteservice',
            name='service_location',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Location'),
        ),
    ]
