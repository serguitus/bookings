# -*- coding: utf-8 -*-
# Generated by Django 1.11.17 on 2019-08-05 20:10
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0035_auto_20190720_0806'),
    ]

    operations = [
        migrations.AddField(
            model_name='bookingpackage',
            name='time',
            field=models.TimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='bookingpackage',
            name='voucher_detail',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='package',
            name='time',
            field=models.TimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='quotepackage',
            name='time',
            field=models.TimeField(blank=True, null=True),
        ),
    ]
