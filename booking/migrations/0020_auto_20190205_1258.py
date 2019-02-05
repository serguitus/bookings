# -*- coding: utf-8 -*-
# Generated by Django 1.11.17 on 2019-02-05 17:58
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('config', '0013_auto_20190205_1258'),
        ('booking', '0019_auto_20190128_2038'),
    ]

    operations = [
        migrations.AddField(
            model_name='bookingextra',
            name='addon',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='config.Addon'),
        ),
        migrations.AddField(
            model_name='quoteextra',
            name='addon',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='config.Addon'),
        ),
    ]