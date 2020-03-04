# -*- coding: utf-8 -*-
# Generated by Django 1.11.23 on 2020-02-16 18:30
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('config', '0013_auto_20200216_1330'),
        ('booking', '0023_auto_20200128_1238'),
    ]

    operations = [
        migrations.CreateModel(
            name='BookingExtraComponent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('manual_cost', models.BooleanField(default=False)),
                ('manual_price', models.BooleanField(default=False)),
                ('cost_amount', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Cost')),
                ('price_amount', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Price')),
                ('booking_extra', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='booking.BookingExtra')),
                ('component', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='config.Extra')),
            ],
            options={
                'verbose_name': 'Booking Extra Component',
                'verbose_name_plural': 'Bookings Extras Components',
            },
        ),
        migrations.CreateModel(
            name='QuoteExtraComponent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('component', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='config.Extra')),
                ('quote_extra', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='booking.QuoteExtra')),
            ],
            options={
                'verbose_name': 'Quote Extra Component',
                'verbose_name_plural': 'Quotes Extras Components',
                'default_permissions': ('add', 'change'),
            },
        ),
        migrations.CreateModel(
            name='QuoteExtraComponentPaxVariant',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cost_single_amount', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Cost SGL')),
                ('cost_double_amount', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Cost DBL')),
                ('cost_triple_amount', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Cost TPL')),
                ('cost_qdrple_amount', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Cost QPL')),
                ('price_single_amount', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Price SGL')),
                ('price_double_amount', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Price DBL')),
                ('price_triple_amount', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Price TPL')),
                ('price_qdrple_amount', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Price QPL')),
                ('free_cost_single', models.SmallIntegerField(default=0)),
                ('free_cost_double', models.SmallIntegerField(default=0)),
                ('free_cost_triple', models.SmallIntegerField(default=0)),
                ('free_cost_qdrple', models.SmallIntegerField(default=0)),
                ('free_price_single', models.SmallIntegerField(default=0)),
                ('free_price_double', models.SmallIntegerField(default=0)),
                ('free_price_triple', models.SmallIntegerField(default=0)),
                ('free_price_qdrple', models.SmallIntegerField(default=0)),
                ('manual_costs', models.BooleanField(default=False, verbose_name='Manual Costs')),
                ('manual_prices', models.BooleanField(default=False, verbose_name='Manual Prices')),
                ('quote_extra_component', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='quoteextracomponent_paxvariants', to='booking.QuoteExtraComponent')),
            ],
            options={
                'verbose_name': 'Quote Extra Component Pax Variant',
                'verbose_name_plural': 'Quote Extras Components Pax Variants',
            },
        ),
        migrations.AlterModelOptions(
            name='quotepackageservicepaxvariant',
            options={'verbose_name': 'Quote Package Service Pax Variant', 'verbose_name_plural': 'Quote Package Services Pax Variants'},
        ),
        migrations.AlterModelOptions(
            name='quotepaxvariant',
            options={'verbose_name': 'Quote Pax', 'verbose_name_plural': 'Quotes Pax'},
        ),
        migrations.AlterModelOptions(
            name='quoteservicepaxvariant',
            options={'verbose_name': 'Quote Service Pax Variant', 'verbose_name_plural': 'Quote Services Pax Variants'},
        ),
        migrations.AddField(
            model_name='basebookingservice',
            name='base_location',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='config.Location'),
        ),
        migrations.AddField(
            model_name='basebookingservice',
            name='base_service',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='booking_base_service', to='config.Service'),
        ),
        migrations.AddField(
            model_name='packageservice',
            name='base_location',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='config.Location'),
        ),
        migrations.AddField(
            model_name='quotepackageservice',
            name='base_location',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='config.Location'),
        ),
        migrations.AddField(
            model_name='quotepackageservice',
            name='base_service',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='quotepackage_base_service', to='config.Service'),
        ),
        migrations.AddField(
            model_name='quoteservice',
            name='base_location',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='config.Location'),
        ),
        migrations.AddField(
            model_name='quoteservice',
            name='base_service',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='quote_base_service', to='config.Service'),
        ),
        migrations.AddField(
            model_name='quoteextracomponentpaxvariant',
            name='quote_service_pax_variant',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='booking.QuoteServicePaxVariant', verbose_name='Pax Variant'),
        ),
        migrations.AlterUniqueTogether(
            name='quoteextracomponentpaxvariant',
            unique_together=set([('quote_service_pax_variant', 'quote_extra_component')]),
        ),
        migrations.AlterUniqueTogether(
            name='quoteextracomponent',
            unique_together=set([('quote_extra', 'component')]),
        ),
        migrations.AlterUniqueTogether(
            name='bookingextracomponent',
            unique_together=set([('booking_extra', 'component')]),
        ),
    ]