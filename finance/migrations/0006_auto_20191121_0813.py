# -*- coding: utf-8 -*-
# Generated by Django 1.11.23 on 2019-11-21 13:13
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0005_auto_20191120_2110'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='agencybillingcontact',
            options={'verbose_name': 'Agency Billing Contact', 'verbose_name_plural': 'Agency Billing Contacts'},
        ),
        migrations.AlterField(
            model_name='finantialdocument',
            name='document_type',
            field=models.CharField(choices=[('DEPOSIT', 'Deposit'), ('WITHDRAW', 'Withdraw'), ('TRANSFER', 'Transfer'), ('CURRENCY_EXCHANGE', 'Currency Exchange'), ('LOAN_ENTITY_DEPOSIT', 'Loan Entity Deposit'), ('LOAN_ENTITY_WITHDRAW', 'Loan Entity Withdraw'), ('LOAN_ACCOUNT_DEPOSIT', 'Loan Account Deposit'), ('LOAN_ACCOUNT_WITHDRAW', 'Loan Account Withdraw'), ('AGENCY_INVOICE', 'Agency Invoice'), ('AGENCY_PAYMENT', 'Agency Payment'), ('AGENCY_DEVOLUTION', 'Agency Devolution'), ('AGENCY_DISCOUNT', 'Agency Discount'), ('AGENCY_BKNG_INVOICE', 'Ag.Booking Invoice'), ('PROVIDER_INVOICE', 'Provider Invoice'), ('PROVIDER_PAYMENT', 'Provider Payment'), ('PROVIDER_DEVOLUTION', 'Provider Devolution'), ('PROVIDER_DISCOUNT', 'Provider Discount'), ('PROV.PAYM.WITHDRAW', 'Prov.Payment Withdraw')], max_length=50),
        ),
    ]
