# -*- coding: utf-8 -*-
# Generated by Django 1.11.18 on 2019-04-11 13:21
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0016_auto_20190405_1314'),
    ]

    operations = [
        migrations.AddField(
            model_name='office',
            name='default_office',
            field=models.BooleanField(default=False),
        ),
    ]
