# -*- coding: utf-8 -*-
# Generated by Django 1.11.17 on 2019-03-22 18:19
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0039_auto_20190315_0003'),
    ]

    operations = [
        migrations.AddField(
            model_name='bookingservicepax',
            name='is_cost_free',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='bookingservicepax',
            name='is_price_free',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='booking',
            name='p_notes',
            field=models.CharField(blank=True, max_length=1000, null=True, verbose_name='Private Notes'),
        ),
        migrations.AlterField(
            model_name='bookingservice',
            name='p_notes',
            field=models.CharField(blank=True, max_length=1000, null=True, verbose_name='Private Notes'),
        ),
        migrations.AlterField(
            model_name='bookingservice',
            name='provider_notes',
            field=models.CharField(blank=True, max_length=1000, null=True, verbose_name='Provider Notes'),
        ),
        migrations.AlterField(
            model_name='bookingservice',
            name='v_notes',
            field=models.CharField(blank=True, max_length=1000, null=True, verbose_name='Voucher Notes'),
        ),
    ]
