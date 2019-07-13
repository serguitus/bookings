# -*- coding: utf-8 -*-
# Generated by Django 1.11.17 on 2019-07-02 15:43
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0026_bookingpax_is_price_free'),
    ]

    operations = [
        migrations.CreateModel(
            name='BookingInvoiceDetail',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(blank=True, max_length=100, null=True)),
                ('detail', models.CharField(blank=True, max_length=100, null=True)),
                ('date_from', models.DateField(blank=True, null=True)),
                ('date_to', models.DateField(blank=True, null=True)),
                ('price', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('invoice', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='booking.BookingInvoice')),
            ],
            options={
                'verbose_name': 'Booking Invoice Detail',
                'verbose_name_plural': 'Bookings Invoices Details',
            },
        ),
    ]