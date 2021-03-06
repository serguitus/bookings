# -*- coding: utf-8 -*-
# Generated by Django 1.11.23 on 2019-12-02 04:37
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0007_finantialdocument_document_number'),
    ]

    operations = [
        migrations.CreateModel(
            name='AgencyCopyContact',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('email', models.EmailField(max_length=254)),
                ('agency', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='finance.Agency')),
            ],
            options={
                'verbose_name': 'Agency Copy Contact',
                'verbose_name_plural': 'Agency CC Contacts',
            },
        ),
        migrations.AlterUniqueTogether(
            name='agencycopycontact',
            unique_together=set([('agency', 'name')]),
        ),
    ]
