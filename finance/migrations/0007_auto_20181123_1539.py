# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2018-11-23 20:39
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0006_auto_20181123_1531'),
    ]

    operations = [
        migrations.AlterField(
            model_name='office',
            name='detail1',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='office',
            name='detail2',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]