# -*- coding: utf-8 -*-
# Generated by Django 1.11.18 on 2019-04-05 17:52
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0049_auto_20190404_1723'),
    ]

    operations = [
        migrations.AlterField(
            model_name='booking',
            name='reference',
            field=models.CharField(blank=True, max_length=25, null=True, verbose_name='TTOO Ref'),
        ),
    ]
