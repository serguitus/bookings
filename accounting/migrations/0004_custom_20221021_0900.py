# -*- coding: utf-8 -*-
# Generated by Django 1.11.23 on 2020-03-29 02:16
from __future__ import unicode_literals
from decimal import ROUND_HALF_EVEN, Decimal

from django.db import migrations, models
import django.db.models.deletion

from accounting.constants import MOVEMENT_TYPE_INPUT


def migrate_new_data(apps, schema_editor):

    Account = apps.get_model('accounting', 'Account')
    OperationMovement = apps.get_model('accounting', 'OperationMovement')

    # update final_account_balance on existing movements
    all_accounts = Account.objects.all()
    for account in all_accounts:
        all_movs = OperationMovement.objects.filter(account=account).order_by('id')
        initial_balance = Decimal()
        for movement in all_movs:
            if movement.movement_type == MOVEMENT_TYPE_INPUT:
                initial_balance = initial_balance + movement.amount
            else:
                initial_balance = initial_balance - movement.amount
            balance = initial_balance.quantize(Decimal('.01'), rounding=ROUND_HALF_EVEN)
            if movement.final_account_balance:
                saved_balance = movement.final_account_balance.quantize(Decimal('.01'), rounding=ROUND_HALF_EVEN)
                if balance != saved_balance:
                    movement.final_account_balance = initial_balance
                    movement.save(update_fields=['final_account_balance'])
            else:
                movement.final_account_balance = initial_balance
                movement.save(update_fields=['final_account_balance'])


def backwards_function(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0003_operationmovement_final_account_balance'),
    ]

    operations = [

        migrations.RunPython(migrate_new_data, backwards_function),

    ]
