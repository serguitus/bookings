# -*- coding: utf-8 -*-
# Generated by Django 1.11.17 on 2019-10-28 20:44
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('config', '0003_auto_20191025_0642'),
    ]

    operations = [
        migrations.CreateModel(
            name='TransferZone',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('transfer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='config.Transfer')),
            ],
            options={
                'verbose_name': 'Transfer Zone',
                'verbose_name_plural': 'Transfers Zones',
            },
        ),
        migrations.CreateModel(
            name='AllotmentTransferZone',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('allotment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='config.Allotment')),
                ('transfer_zone', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='config.TransferZone')),
            ],
            options={
                'verbose_name': 'Allotment Transfer Zone',
                'verbose_name_plural': 'Allotments Transfers Zones',
            },
        ),
        migrations.CreateModel(
            name='TransferPickupTime',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('transfer_zone', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='config.TransferZone', verbose_name='Pickup Zone')),
                ('location', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='config.Location', verbose_name='Dropoff Location')),
                ('pickup_time', models.TimeField()),
            ],
            options={
                'verbose_name': 'Transfer Pickup Time',
                'verbose_name_plural': 'Transfer Pickups Times',
            },
        ),
        migrations.RemoveField(
            model_name='allotment',
            name='zone',
        ),
        migrations.DeleteModel(
            name='PickupTime',
        ),
        migrations.DeleteModel(
            name='Zone',
        ),
        migrations.AlterUniqueTogether(
            name='transferzone',
            unique_together=set([('transfer', 'name')]),
        ),
        migrations.AlterUniqueTogether(
            name='transferpickuptime',
            unique_together=set([('transfer_zone', 'location')]),
        ),
        migrations.AlterUniqueTogether(
            name='allotmenttransferzone',
            unique_together=set([('allotment', 'transfer_zone')]),
        ),
    ]
