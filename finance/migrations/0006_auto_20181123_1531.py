# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2018-11-23 20:31
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0005_auto_20181120_1505'),
    ]

    operations = [
        migrations.CreateModel(
            name='Office',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('logo', models.ImageField(blank=True, null=True, upload_to='')),
                ('address', models.CharField(max_length=100)),
                ('detail1', models.CharField(max_length=100)),
                ('detail2', models.CharField(max_length=100)),
            ],
            options={
                'verbose_name': 'Office',
                'verbose_name_plural': 'Offices',
            },
        ),
        migrations.AlterUniqueTogether(
            name='office',
            unique_together=set([('name',)]),
        ),
    ]