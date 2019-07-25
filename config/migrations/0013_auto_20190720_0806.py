# -*- coding: utf-8 -*-
# Generated by Django 1.11.17 on 2019-07-20 12:06
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('config', '0012_auto_20190717_1732'),
    ]

    operations = [
        migrations.AlterField(
            model_name='service',
            name='service_category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='config.ServiceCategory', verbose_name='Category'),
        ),
    ]