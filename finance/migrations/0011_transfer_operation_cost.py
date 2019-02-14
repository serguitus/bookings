# -*- coding: utf-8 -*-
# Generated by Django 1.11.17 on 2019-02-13 21:34
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0010_agency_gain_percent'),
    ]

    operations = [
        migrations.AddField(
            model_name='transfer',
            name='operation_cost',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
    ]