# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2018-11-23 20:57
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0007_auto_20181123_1539'),
    ]

    operations = [
        migrations.CreateModel(
            name='AgencyInvoiceLine',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('detail1', models.CharField(blank=True, max_length=100, null=True)),
                ('detail2', models.CharField(blank=True, max_length=100, null=True)),
                ('qtty', models.IntegerField(blank=True, null=True)),
                ('unit', models.CharField(blank=True, max_length=20, null=True)),
                ('unit_amount', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('line_amount', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('invoice', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='finance.AgencyInvoice')),
            ],
            options={
                'verbose_name': 'Agency Invoice Line',
                'verbose_name_plural': 'Agencies Invoices Lines',
            },
        ),
        migrations.CreateModel(
            name='AgencyInvoicePartial',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('detail1', models.CharField(blank=True, max_length=100, null=True)),
                ('detail2', models.CharField(blank=True, max_length=100, null=True)),
                ('partial_amount', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('invoice', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='finance.AgencyInvoice')),
            ],
            options={
                'verbose_name': 'Agency Invoice Partial',
                'verbose_name_plural': 'Agencies Invoices Partials',
            },
        ),
    ]
