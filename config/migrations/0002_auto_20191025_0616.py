# -*- coding: utf-8 -*-
# Generated by Django 1.11.17 on 2019-10-25 10:16
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('config', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PickupTime',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pickup_time', models.TimeField()),
                ('location', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='config.Location', verbose_name='Dropoff Location')),
            ],
            options={
                'verbose_name': 'Transfer Interval',
                'verbose_name_plural': 'Transfers Intervals',
            },
        ),
        migrations.CreateModel(
            name='Zone',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
            ],
            options={
                'verbose_name': 'Zone',
                'verbose_name_plural': 'Zones',
            },
        ),
        migrations.AddField(
            model_name='transfer',
            name='has_pickup_time',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterUniqueTogether(
            name='zone',
            unique_together=set([('name',)]),
        ),
        migrations.AddField(
            model_name='pickuptime',
            name='zone',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='config.Zone', verbose_name='Pickup Zone'),
        ),
        migrations.AddField(
            model_name='allotment',
            name='zone',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='config.Zone'),
        ),
        migrations.AlterUniqueTogether(
            name='pickuptime',
            unique_together=set([('zone', 'location')]),
        ),
    ]
