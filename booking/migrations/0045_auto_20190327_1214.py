# -*- coding: utf-8 -*-
# Generated by Django 1.11.18 on 2019-03-27 16:14
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0044_auto_20190324_2015'),
    ]

    operations = [
        migrations.AlterField(
            model_name='booking',
            name='currency',
            field=models.CharField(choices=[(b'CUC', b'CUC'), (b'USD', b'USD'), (b'EUR', b'EUR'), (b'CUP', b'CUP')], default=b'CUC', max_length=5),
        ),
        migrations.AlterField(
            model_name='quote',
            name='currency',
            field=models.CharField(choices=[(b'CUC', b'CUC'), (b'USD', b'USD'), (b'EUR', b'EUR'), (b'CUP', b'CUP')], default=b'CUC', max_length=5),
        ),
    ]
