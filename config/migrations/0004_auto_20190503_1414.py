# -*- coding: utf-8 -*-
# Generated by Django 1.11.17 on 2019-05-03 18:14
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('config', '0003_auto_20190412_1729'),
    ]

    operations = [
        migrations.AlterField(
            model_name='providerextradetail',
            name='pax_range_max',
            field=models.SmallIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='providerextradetail',
            name='pax_range_min',
            field=models.SmallIntegerField(default=0),
        ),
    ]
