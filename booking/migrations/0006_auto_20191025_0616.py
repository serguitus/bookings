# -*- coding: utf-8 -*-
# Generated by Django 1.11.17 on 2019-10-25 10:16
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0005_booking_agency_contact'),
    ]

    operations = [
        migrations.AlterField(
            model_name='booking',
            name='agency_contact',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='finance.AgencyContact', verbose_name='Contact'),
        ),
    ]
