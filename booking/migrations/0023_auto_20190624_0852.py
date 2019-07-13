# -*- coding: utf-8 -*-
# Generated by Django 1.11.17 on 2019-06-24 12:52
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('config', '0008_auto_20190624_0852'),
        ('booking', '0022_auto_20190622_0755'),
    ]

    operations = [
        migrations.AddField(
            model_name='bookingpackageservice',
            name='service_addon',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='config.Addon'),
        ),
        migrations.AddField(
            model_name='bookingservice',
            name='service_addon',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='config.Addon'),
        ),
        migrations.AddField(
            model_name='packageservice',
            name='service_addon',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='config.Addon'),
        ),
        migrations.AddField(
            model_name='quotepackageservice',
            name='service_addon',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='config.Addon'),
        ),
        migrations.AddField(
            model_name='quoteservice',
            name='service_addon',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='config.Addon'),
        ),
    ]