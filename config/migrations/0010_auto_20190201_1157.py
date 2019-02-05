# -*- coding: utf-8 -*-
# Generated by Django 1.11.18 on 2019-02-01 16:57
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('config', '0009_auto_20190128_2036'),
    ]

    operations = [
        migrations.AlterField(
            model_name='extra',
            name='parameter_type',
            field=models.CharField(choices=[(b'H', b'Hours'), (b'D', b'Days'), (b'N', b'Nights'), (b'S', b'Stay')], max_length=5),
        ),
        migrations.AlterUniqueTogether(
            name='providerextradetail',
            unique_together=set([('provider_service', 'pax_range_min', 'pax_range_max')]),
        ),
    ]