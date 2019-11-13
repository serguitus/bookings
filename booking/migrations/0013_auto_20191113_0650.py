# -*- coding: utf-8 -*-
# Generated by Django 1.11.17 on 2019-11-13 11:50
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0012_auto_20191112_2125'),
    ]

    operations = [
        migrations.AddField(
            model_name='providerbookingpayment',
            name='currency_rate',
            field=models.DecimalField(decimal_places=4, default=1.0, max_digits=10),
        ),
        migrations.AddField(
            model_name='providerbookingpayment',
            name='services_amount',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
    ]
