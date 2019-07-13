# -*- coding: utf-8 -*-
# Generated by Django 1.11.21 on 2019-06-26 03:03
from __future__ import unicode_literals

from django.db import migrations, IntegrityError, transaction


def migrate_ExtraAddon_to_ServiceAddon(apps, schema_editor):
    ExtraAddon = apps.get_model('config', 'ExtraAddon')
    ServiceAddon = apps.get_model('config', 'ServiceAddon')

    obs = ExtraAddon.objects.all()
    for obj in obs:
        s = ServiceAddon(addon=obj.addon, service=obj.extra)
        try:
            with transaction.atomic():
                s.save()
        except IntegrityError:
            continue


def backwards_function(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('config', '0008_auto_20190624_0852'),
    ]

    operations = [
        migrations.RunPython(migrate_ExtraAddon_to_ServiceAddon,
                             backwards_function),
    ]