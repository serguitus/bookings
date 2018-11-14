# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-11-14 19:43
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0012_auto_20181106_2032'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='bookingallotment',
            options={'verbose_name': 'Booking Accomodation', 'verbose_name_plural': 'Booking Accomodation'},
        ),
        migrations.AlterModelOptions(
            name='bookingextra',
            options={'verbose_name': 'Booking Extra', 'verbose_name_plural': 'Booking Extras'},
        ),
        migrations.AlterModelOptions(
            name='bookingpax',
            options={'verbose_name': 'Booking Pax', 'verbose_name_plural': 'Booking Rooming List'},
        ),
        migrations.AlterModelOptions(
            name='bookingservicepax',
            options={'verbose_name': 'Booking Service Pax', 'verbose_name_plural': 'Booking Service Rooming'},
        ),
        migrations.AlterModelOptions(
            name='bookingtransfer',
            options={'verbose_name': 'Booking Transfer', 'verbose_name_plural': 'Booking Transfers'},
        ),
        migrations.AlterModelOptions(
            name='bookingtransfersupplement',
            options={'verbose_name': 'Booking Transfer Line Supplement', 'verbose_name_plural': 'Booking Transfer Line Supplements'},
        ),
        migrations.AlterField(
            model_name='quotepaxvariant',
            name='cost_double_amount',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name=b'Cost DBL'),
        ),
        migrations.AlterField(
            model_name='quotepaxvariant',
            name='cost_single_amount',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name=b'Cost SGL'),
        ),
        migrations.AlterField(
            model_name='quotepaxvariant',
            name='cost_triple_amount',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name=b'Cost TPL'),
        ),
        migrations.AlterField(
            model_name='quotepaxvariant',
            name='price_double_amount',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name=b'Price DBL'),
        ),
        migrations.AlterField(
            model_name='quotepaxvariant',
            name='price_single_amount',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name=b'Price SGL'),
        ),
        migrations.AlterField(
            model_name='quotepaxvariant',
            name='price_triple_amount',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name=b'Price TPL'),
        ),
    ]