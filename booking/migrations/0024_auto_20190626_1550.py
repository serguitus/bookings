# -*- coding: utf-8 -*-
# Generated by Django 1.11.21 on 2019-06-26 19:50
from __future__ import unicode_literals

from django.db import migrations, IntegrityError, transaction


def update_existent_serviceAddon(apps, schema_editor):
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
        ('booking', '0023_auto_20190624_0852'),
        ('config', '0010_merge_20190626_1533'),
    ]

    operations = [
        migrations.RunPython(update_existent_serviceAddon,
                             backwards_function),
    ]
