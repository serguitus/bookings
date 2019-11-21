# -*- coding: utf-8 -*-
# Generated by Django 1.11.23 on 2019-11-21 13:13
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0014_auto_20191114_1609'),
    ]

    operations = [
        migrations.AlterField(
            model_name='basebookingservice',
            name='booking',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='base_booking_services', to='booking.Booking'),
        ),
        migrations.AlterField(
            model_name='basebookingservice',
            name='cost_amount',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Cost'),
        ),
        migrations.AlterField(
            model_name='basebookingservice',
            name='datetime_from',
            field=models.DateField(blank=True, null=True, verbose_name='From'),
        ),
        migrations.AlterField(
            model_name='basebookingservice',
            name='datetime_to',
            field=models.DateField(blank=True, null=True, verbose_name='To'),
        ),
        migrations.AlterField(
            model_name='basebookingservice',
            name='price_amount',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Price'),
        ),
        migrations.AlterField(
            model_name='basebookingservice',
            name='service_addon',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='config.Addon', verbose_name='Addon'),
        ),
        migrations.AlterField(
            model_name='booking',
            name='cost_amount',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Cost'),
        ),
        migrations.AlterField(
            model_name='booking',
            name='price_amount',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Price'),
        ),
        migrations.AlterField(
            model_name='bookingservice',
            name='v_notes',
            field=models.CharField(blank=True, max_length=200, null=True, verbose_name='Voucher Notes'),
        ),
        migrations.AlterField(
            model_name='packageservice',
            name='service_addon',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='config.Addon', verbose_name='Addon'),
        ),
        migrations.AlterField(
            model_name='quotepackageservice',
            name='datetime_from',
            field=models.DateField(blank=True, null=True, verbose_name='From'),
        ),
        migrations.AlterField(
            model_name='quotepackageservice',
            name='datetime_to',
            field=models.DateField(blank=True, null=True, verbose_name='To'),
        ),
        migrations.AlterField(
            model_name='quotepackageservice',
            name='service_addon',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='config.Addon', verbose_name='Addon'),
        ),
        migrations.AlterField(
            model_name='quoteservice',
            name='datetime_from',
            field=models.DateField(blank=True, null=True, verbose_name='From'),
        ),
        migrations.AlterField(
            model_name='quoteservice',
            name='datetime_to',
            field=models.DateField(blank=True, null=True, verbose_name='To'),
        ),
        migrations.AlterField(
            model_name='quoteservice',
            name='service_addon',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='config.Addon', verbose_name='Addon'),
        ),
    ]
