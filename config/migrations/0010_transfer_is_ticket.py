# -*- coding: utf-8 -*-
# Generated by Django 1.11.23 on 2019-11-24 12:23
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('config', '0009_auto_20191122_1438'),
    ]

    operations = [
        migrations.AddField(
            model_name='transfer',
            name='is_ticket',
            field=models.BooleanField(default=False),
        ),
    ]