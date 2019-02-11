# -*- coding: utf-8 -*-
# Generated by Django 1.11.17 on 2019-02-11 15:39
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('config', '0015_auto_20190205_1429'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='agencyallotmentdetail',
            options={'verbose_name': 'Accomodation Agency Detail', 'verbose_name_plural': 'Accomodation Agency Details'},
        ),
        migrations.AlterModelOptions(
            name='agencyallotmentservice',
            options={'verbose_name': 'Accomodation Service Agency', 'verbose_name_plural': 'Accomodation Service Agencies'},
        ),
        migrations.AlterModelOptions(
            name='agencytransferdetail',
            options={'verbose_name': 'Transfer Agency Detail', 'verbose_name_plural': 'Transfer Agency Details'},
        ),
        migrations.AlterModelOptions(
            name='agencytransferservice',
            options={'verbose_name': 'Transfer Service Agency', 'verbose_name_plural': 'Transfer Service Agencies'},
        ),
        migrations.AlterModelOptions(
            name='providertransferdetail',
            options={'verbose_name': 'Transfer Provider Detail', 'verbose_name_plural': 'Transfer Provider Details'},
        ),
        migrations.AlterModelOptions(
            name='providertransferservice',
            options={'verbose_name': 'Transfer Service Provider', 'verbose_name_plural': 'Transfer Service Providers'},
        ),
    ]