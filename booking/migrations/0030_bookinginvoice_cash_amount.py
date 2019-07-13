# -*- coding: utf-8 -*-
# Generated by Django 1.11.17 on 2019-07-03 15:12
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0029_bookinginvoicepartial_is_free'),
    ]

    operations = [
        migrations.AddField(
            model_name='bookinginvoice',
            name='cash_amount',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=9),
        ),
    ]