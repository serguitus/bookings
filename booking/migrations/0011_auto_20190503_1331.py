# -*- coding: utf-8 -*-
# Generated by Django 1.11.17 on 2019-05-03 17:31
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0010_auto_20190429_2021'),
    ]

    operations = [
        migrations.CreateModel(
            name='QuotePackageServicePaxVariant',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cost_single_amount', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Cost SGL')),
                ('cost_double_amount', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Cost DBL')),
                ('cost_triple_amount', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Cost TPL')),
                ('price_single_amount', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Price SGL')),
                ('price_double_amount', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Price DBL')),
                ('price_triple_amount', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Price TPL')),
                ('manual_costs', models.BooleanField(default=False, verbose_name='Manual Costs')),
                ('manual_prices', models.BooleanField(default=False, verbose_name='Manual Prices')),
                ('quote_package_service', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='quotepackageservice_paxvariants', to='booking.QuotePackageService')),
                ('quote_pax_variant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='booking.QuotePaxVariant', verbose_name='Pax Variant')),
            ],
            options={
                'verbose_name': 'Quote Package Service Pax Variant',
                'verbose_name_plural': 'Quotes Packages Services Paxes Variants',
            },
        ),
        migrations.AlterUniqueTogether(
            name='quotepackageservicepaxvariant',
            unique_together=set([('quote_pax_variant', 'quote_package_service')]),
        ),
    ]
