# -*- coding: utf-8 -*-
# Generated by Django 1.11.23 on 2019-11-25 04:46
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0006_auto_20191121_0813'),
    ]

    operations = [
        migrations.AddField(
            model_name='finantialdocument',
            name='document_number',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]