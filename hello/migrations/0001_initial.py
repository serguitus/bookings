# -*- coding: utf-8 -*-
# Generated by Django 1.11.17 on 2019-10-05 12:01
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Hello1',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'verbose_name': 'Hello 1',
                'verbose_name_plural': 'Hellos 1s',
                'permissions': (('view', 'view'),),
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Hello2',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'verbose_name': 'Hello 2',
                'verbose_name_plural': 'Hellos 2s',
                'permissions': (('view', 'view'),),
                'managed': False,
            },
        ),
    ]
