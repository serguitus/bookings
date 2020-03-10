# -*- coding: utf-8 -*-
# Generated by Django 1.11.23 on 2020-03-10 15:15
from __future__ import unicode_literals

from django.db import migrations, models

def update_office_bank_details(apps, schema_editor):
    Office = apps.get_model('finance', 'Office')

    for reg in Office.objects.all():
        reg.bank_details = 'Beneficiary Name: LLOGO S.A.<br>' \
            + 'Beneficiary Account: 4021027875<br>' \
            + 'ADDRESS: CALLE 38, EDIF LOS CRISTALES, OFICINA 6-8, CIUDAD PANAMA<br>' \
            + 'Beneficiary Bank: CREDICORP BANK Panama, Rep. de Panama<br>' \
            + 'SWIFT: CRLDPAPA<br>' \
            + 'Address: Calle 50 Edif Plaza Credicorp Bank, Obarrio, CIUDAD PANAMA<br>' \
            + '<p>Please send transfer through our correspondent bank below.<br>' \
            + 'Intermediary Bank:<br>' \
            + 'WELLS FARGO BANK NA<br>' \
            + '375 Park Ave. NY 4080<br>' \
            + 'New York, N.Y. U.S.A.<br>' \
            + 'Fedwire : 026005092<br>' \
            + 'SWIFT: PNBPUS3NNYC<br>' \
            + 'Account with Intermediary Bank: 20001923715</p>'
        reg.save()

def backwards_function(apps, schema_editor):
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0009_provider_notes'),
    ]

    operations = [
        migrations.AddField(
            model_name='office',
            name='bank_details',
            field=models.CharField(blank=True, max_length=1000, null=True),
        ),
        migrations.RunPython(update_office_bank_details, backwards_function),
    ]
