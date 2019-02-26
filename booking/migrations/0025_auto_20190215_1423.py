# -*- coding: utf-8 -*-
# Generated by Django 1.11.17 on 2019-02-15 19:23
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('config', '0017_auto_20190215_1416'),
        ('booking', '0024_auto_20190211_1039'),
    ]

    operations = [
        migrations.AddField(
            model_name='bookingtransfer',
            name='place_from',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='place_from', to='config.Place'),
        ),
        migrations.AddField(
            model_name='bookingtransfer',
            name='place_to',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='place_to', to='config.Place'),
        ),
    ]