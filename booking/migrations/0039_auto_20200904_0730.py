# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2020-09-04 11:30
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('config', '0023_service_is_internal'),
        ('booking', '0038_auto_20200625_1322'),
    ]

    operations = [
        migrations.AddField(
            model_name='quoteprovidedservice',
            name='cost_by_catalog',
            field=models.BooleanField(default=True, verbose_name='Use Catalog Cost'),
        ),
        migrations.AddField(
            model_name='quoteprovidedservice',
            name='price_by_catalog',
            field=models.BooleanField(default=True, verbose_name='Use Catalog Price'),
        ),
        migrations.AlterField(
            model_name='quoteextrapackage',
            name='price_by_package_catalogue',
            field=models.BooleanField(default=True, verbose_name='Use Catalog Price'),
        ),
        migrations.RenameField(
            model_name='quoteextrapackage',
            old_name='price_by_package_catalogue',
            new_name='price_by_catalog',
        ),
        migrations.AddField(
            model_name='bookingprovidedservice',
            name='cost_by_catalog',
            field=models.BooleanField(default=True, verbose_name='Use Catalog Cost'),
        ),
        migrations.AddField(
            model_name='bookingprovidedservice',
            name='price_by_catalog',
            field=models.BooleanField(default=True, verbose_name='Use Catalog Price'),
        ),
        migrations.AlterField(
            model_name='bookingprovidedservice',
            name='booking_package',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='booking_package_services', to='booking.BookingExtraPackage'),
        ),
        migrations.AlterField(
            model_name='bookingextrapackage',
            name='price_by_package_catalogue',
            field=models.BooleanField(default=True, verbose_name='Use Catalog Price'),
        ),
        migrations.RenameField(
            model_name='bookingextrapackage',
            old_name='price_by_package_catalogue',
            new_name='price_by_catalog',
        ),
    ]
