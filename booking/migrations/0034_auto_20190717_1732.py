# -*- coding: utf-8 -*-
# Generated by Django 1.11.17 on 2019-07-17 21:32
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0033_auto_20190716_1148'),
    ]

    operations = [
        migrations.AddField(
            model_name='bookingtransfer',
            name='schedule_time_from',
            field=models.TimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='bookingtransfer',
            name='schedule_time_to',
            field=models.TimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='packagetransfer',
            name='schedule_time_from',
            field=models.TimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='packagetransfer',
            name='schedule_time_to',
            field=models.TimeField(blank=True, null=True),
        ),
    ]
