# -*- coding: utf-8 -*-
# Generated by Django 1.11.18 on 2019-03-14 21:27
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0037_auto_20190309_0833'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='p_notes',
            field=models.CharField(blank=True, max_length=1000, null=True),
        ),
    ]
