# -*- coding: utf-8 -*-
# Generated by Django 1.11.23 on 2020-03-29 02:16
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


def migrate_new_data(apps, schema_editor):

    ProviderBookingPaymentService = apps.get_model('booking', 'ProviderBookingPaymentService')
    ProviderPaymentBookingProvided = apps.get_model('booking', 'ProviderPaymentBookingProvided')

    # provider payments for packages are excluded here. migrated on config 0018_custom.
    for pay_service in ProviderBookingPaymentService.objects.exclude(provider_service__base_category='BP'):
        new_pay_service = ProviderPaymentBookingProvided()
        new_pay_service.provider_payment_id = pay_service.provider_payment_id
        new_pay_service.provider_service_id = pay_service.provider_service_id
        new_pay_service.amount_paid = pay_service.amount_paid
        new_pay_service.service_cost_amount_to_pay = pay_service.service_cost_amount_to_pay
        new_pay_service.service_cost_amount_paid = pay_service.service_cost_amount_paid
        new_pay_service.save()


def backwards_function(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0033_custom_20200530_0900'),
    ]

    operations = [

        migrations.RunPython(migrate_new_data, backwards_function),

    ]
