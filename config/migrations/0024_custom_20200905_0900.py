# -*- coding: utf-8 -*-
# Generated by Django 1.11.23 on 2020-03-29 02:16
from __future__ import unicode_literals

from django.db import migrations


def fix_details_base_service(apps, schema_editor):

    ServiceBookDetailAllotment = apps.get_model('config', 'ServiceBookDetailAllotment')
    ServiceBookDetailTransfer = apps.get_model('config', 'ServiceBookDetailTransfer')
    ServiceBookDetailExtra = apps.get_model('config', 'ServiceBookDetailExtra')

    for detail_service in ServiceBookDetailAllotment.objects.all():
        detail_service.base_service_id = detail_service.book_service_id
        detail_service.save()
    for detail_service in ServiceBookDetailTransfer.objects.all():
        detail_service.base_service_id = detail_service.book_service_id
        detail_service.save()
    for detail_service in ServiceBookDetailExtra.objects.all():
        detail_service.base_service_id = detail_service.book_service_id
        detail_service.save()


def backwards_function(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('config', '0023_service_is_internal'),
    ]

    operations = [

        migrations.RunPython(fix_details_base_service, backwards_function),

    ]