# -*- coding: utf-8 -*-
# Generated by Django 1.11.17 on 2019-03-13 15:05
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0013_auto_20190219_1436'),
        ('config', '0019_auto_20190219_1026'),
    ]

    operations = [
        migrations.AlterField(
            model_name='extra',
            name='location',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='config.Location'),
        ),
        migrations.AlterUniqueTogether(
            name='agencyallotmentservice',
            unique_together=set([('agency', 'service', 'date_from', 'date_to')]),
        ),
        migrations.AlterUniqueTogether(
            name='agencyextraservice',
            unique_together=set([('agency', 'service', 'date_from', 'date_to')]),
        ),
        migrations.AlterUniqueTogether(
            name='agencytransferservice',
            unique_together=set([('agency', 'service', 'date_from', 'date_to')]),
        ),
        migrations.AlterUniqueTogether(
            name='providerallotmentservice',
            unique_together=set([('provider', 'service', 'date_from', 'date_to')]),
        ),
        migrations.AlterUniqueTogether(
            name='providerextraservice',
            unique_together=set([('provider', 'service', 'date_from', 'date_to')]),
        ),
        migrations.AlterUniqueTogether(
            name='providertransferservice',
            unique_together=set([('provider', 'service', 'date_from', 'date_to')]),
        ),
    ]
