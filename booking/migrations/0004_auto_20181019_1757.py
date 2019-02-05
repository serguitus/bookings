# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2018-10-19 21:57
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0003_auto_20181011_1750'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bookingservice',
            name='service_type',
            field=models.CharField(blank=True, choices=[('E', 'Extra'), ('A', 'Allotment'), ('T', 'Transfer')], max_length=5, null=True),
        ),
    ]