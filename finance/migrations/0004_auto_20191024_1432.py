# -*- coding: utf-8 -*-
# Generated by Django 1.11.17 on 2019-10-24 18:32
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0003_auto_20191021_1246'),
    ]

    operations = [
        migrations.CreateModel(
            name='AgencyContact',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('email', models.EmailField(max_length=254)),
                ('agency', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='finance.Agency')),
            ],
            options={
                'verbose_name': 'Agency Contact',
                'verbose_name_plural': 'Agencies Contacts',
            },
        ),
        migrations.AlterUniqueTogether(
            name='agencycontact',
            unique_together=set([('agency', 'name')]),
        ),
    ]
