# -*- coding: utf-8 -*-
# Generated by Django 1.11.18 on 2019-06-04 02:24
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0015_auto_20190530_1718'),
    ]

    operations = [
        migrations.AddField(
            model_name='bookingpackageservice',
            name='service_location',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='bookingservice',
            name='service_location',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='packageallotment',
            name='service_location',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='quotepackageservice',
            name='service_location',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='quoteservice',
            name='service_location',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]