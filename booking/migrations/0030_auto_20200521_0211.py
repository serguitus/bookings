# -*- coding: utf-8 -*-
# Generated by Django 1.11.28 on 2020-05-21 06:11
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0029_auto_20200405_1924'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='providerbookingpayment',
            options={'ordering': ['-date'], 'verbose_name': 'Payment to Provider', 'verbose_name_plural': 'Payments to Providers'},
        ),
    ]
