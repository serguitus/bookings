# -*- coding: utf-8 -*-
# Generated by Django 1.11.21 on 2019-06-27 03:24
from __future__ import unicode_literals

from django.db import migrations, IntegrityError, transaction
from django.conf import settings


def update_existent_details(apps, schema_editor):
    AgencyAllotmentDetail = apps.get_model('config', 'AgencyAllotmentDetail')
    ProviderAllotmentDetail = apps.get_model('config',
                                             'ProviderAllotmentDetail')
    AgencyTransferDetail = apps.get_model('config', 'AgencyTransferDetail')
    ProviderTransferDetail = apps.get_model('config', 'ProviderTransferDetail')
    AgencyExtraDetail = apps.get_model('config', 'AgencyExtraDetail')
    ProviderExtraDetail = apps.get_model('config', 'ProviderExtraDetail')

    # first fix all none-extra Details.
    # They should all point to settings.ADDON_FOR_NO_ADDON
    for cls in [AgencyAllotmentDetail, ProviderAllotmentDetail,
                ProviderTransferDetail, AgencyTransferDetail]:
        for obj in cls.objects.all():
            obj.addon_id = settings.ADDON_FOR_NO_ADDON
            try:
                with transaction.atomic():
                    obj.save()
            except IntegrityError:
                continue
    # now the extraDetails
    # will only change those with id=1. this was a previous migration mistake
    # they should all point to settings.ADDON_FOR_NO_ADDON
    # afterwards we will need to manually set those that actually use id=1
    for cls in [AgencyExtraDetail, ProviderExtraDetail]:
        for obj in cls.objects.all():
            if obj.addon_id == 1:
                obj.addon_id = settings.ADDON_FOR_NO_ADDON
                try:
                    with transaction.atomic():
                        obj.save()
                except IntegrityError:
                    continue


def backwards_function(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('config', '0010_merge_20190626_1533'),
    ]

    operations = [
    ]
