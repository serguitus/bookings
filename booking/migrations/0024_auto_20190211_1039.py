# -*- coding: utf-8 -*-
# Generated by Django 1.11.17 on 2019-02-11 15:39
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0023_auto_20190205_1800'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bookingextra',
            name='parameter',
            field=models.SmallIntegerField(default=0, verbose_name='Hours'),
        ),
        migrations.AlterField(
            model_name='bookingpax',
            name='cost_amount',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Cost'),
        ),
        migrations.AlterField(
            model_name='bookingpax',
            name='pax_age',
            field=models.SmallIntegerField(blank=True, null=True, verbose_name='Age'),
        ),
        migrations.AlterField(
            model_name='bookingpax',
            name='pax_group',
            field=models.SmallIntegerField(verbose_name='Room'),
        ),
        migrations.AlterField(
            model_name='bookingpax',
            name='price_amount',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Price'),
        ),
        migrations.AlterField(
            model_name='bookingservicepax',
            name='cost_amount',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Cost'),
        ),
        migrations.AlterField(
            model_name='bookingservicepax',
            name='group',
            field=models.SmallIntegerField(verbose_name='Room'),
        ),
        migrations.AlterField(
            model_name='bookingservicepax',
            name='price_amount',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Price'),
        ),
        migrations.AlterField(
            model_name='quoteextra',
            name='parameter',
            field=models.SmallIntegerField(default=0, verbose_name='Hours'),
        ),
    ]