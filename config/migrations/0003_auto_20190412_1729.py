# -*- coding: utf-8 -*-
# Generated by Django 1.11.17 on 2019-04-12 21:29
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('config', '0002_auto_20190411_1301'),
    ]

    operations = [
        migrations.AlterField(
            model_name='agencyextradetail',
            name='pax_range_max',
            field=models.SmallIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='agencyextradetail',
            name='pax_range_min',
            field=models.SmallIntegerField(default=0),
        ),
    ]