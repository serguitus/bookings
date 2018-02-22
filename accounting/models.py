from __future__ import unicode_literals

from datetime import datetime
from django.db import models, transaction
from django.conf import settings
from django.core.exceptions import ValidationError
from accounting.constants import CURRENCIES, CURRENCY_CUC, ACCOUNT_NATURES, ACCOUNT_NATURE_DEBIT, ACCOUNT_NATURE_CREDIT, ACCOUNT_NATURE_BOTH, OPERATIONS, MANUAL_OPERATIONS
from accounting.exceptions import Error


class Account(models.Model):
    class Meta:
        verbose_name = 'Account'
        verbose_name_plural = 'Accounts'
        unique_together = (('name', 'currency'),) 

    name = models.CharField(max_length=50)
    description = models.CharField(max_length=200, blank=True, null=True)
    currency = models.CharField(max_length=5, choices=CURRENCIES, default=CURRENCY_CUC)
    balance = models.DecimalField(default=0.0, max_digits=12, decimal_places=2)
    allow_negative = models.BooleanField(default=True)

    def __str__(self):
        return '%s (%s)' % (self.name, self.balance)

    @classmethod
    def updateBalance(cls, account_id, amount, is_credit, date=datetime.now()):
        with transaction.atomic():
            account = (
                cls.objects.select_for_update().get(id=id)
            )
            if is_credit:
                account.balance += amount
            else:
                if account.allow_negative or account.balance >= amount:
                    account.balance -= amount
                else:
                    raise ValidationError('Non negativa balance allowed : extracting %s to %s' % (amount, account.balance))
            account.save()
        return account

class Movement(models.Model):
    class Meta:
        verbose_name = 'Movement'
        verbose_name_plural = 'Movements'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        help_text='User who performed the action.',
    )
    date = models.DateField()
    debit_account = models.ForeignKey(Account, related_name='debit_account')
    credit_account = models.ForeignKey(Account, related_name='credit_account')
    amount = models.IntegerField(default=0)
    concept = models.CharField(max_length=100)
    detail = models.CharField(max_length=500)

    def __str__(self):
        return '%s : %s' % (self.date, self.detail)

    CREDIT = True
    DEBIT = False

    @classmethod
    def create(cls, user, debit_account, credit_account, amount, concept, date=datetime.now(), detail=''):
        if user == None:
            raise ValidationError({
                'user': 'required for transaction',
            })
        if concept == None or concept.trim() == '':
            raise ValidationError({
                'concept': 'required for transaction',
            })
        if amount == None or amount <= 0:
            raise ValidationError({
                'amount': 'required for transaction',
            })

        with transaction.atomic():
            Account.updateBalance(
                account_id=debit_account.id,
                amount=amount,
                is_credit=Movement.DEBIT,
                date=date)
            Account.updateBalance(
                account_id=credit_account.id,
                amount=amount,
                is_credit=Movement.CREDIT,
                date=date)
            return cls.objects.create(
                user=user,
                date=date,
                debit_account=debit_account,
                credit_account=credit_account,
                amount=amount,
                concept=concept.trim(),
                detail=detail,
            )


class Operation(models.Model):
    class Meta:
        verbose_name = 'Operation'
        verbose_name_plural = 'Operations'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        help_text='User who performed the action.',
    )
    date = models.DateField()
    operation_type = models.CharField(max_length=50, choices=OPERATIONS)
    concept = models.CharField(max_length=100)
    detail = models.CharField(max_length=500)

    def __str__(self):
        return self.concept

    @classmethod
    def create(cls, user, src_debit_account, src_credit_account, src_amount, dest_debit_account, dest_credit_account, dest_amount, date=datetime.now()):
        assert src_amount > 0
        assert dest_amount > 0
        rate = dest_amount / src_amount

        concept = '%s : %s %s a %s %s' % (
            date, src_amount, src_debit_account.currency, dest_amount, dest_debit_account.currency)
        detail = '%s %s from %s to %s y %s %s from %s to %s' % (
            src_amount, src_debit_account.currency, src_debit_account.name, src_credit_account.name,
            dest_amount, dest_debit_account.currency, dest_debit_account.name, dest_credit_account.name)

        with transaction.atomic():
            src_currency_movement = Movement.create(
                user=user,
                debit_account=src_debit_account,
                credit_account=src_credit_account,
                amount=src_amount,
                concept='Conversion : %s : %s %s a %s %s' % (
                    date, src_amount, src_debit_account.currency, dest_amount, dest_debit_account.currency),
                detail='%s %s from %s to %s' % (
                    src_amount, src_debit_account.currency, src_debit_account.name, src_credit_account.name),
                date=date)
            dest_currency_movement = Movement.create(
                user=user,
                debit_account=dest_debit_account,
                credit_account=dest_credit_account,
                amount=dest_amount,
                concept='Conversion : %s : %s %s a %s %s' % (
                    date, src_amount, src_debit_account.currency, dest_amount, dest_debit_account.currency),
                detail='%s %s from %s to %s' % (
                    dest_amount, dest_debit_account.currency, dest_debit_account.name, dest_credit_account.name),
                date=date)

            return cls.objects.create(
                user=user,
                date=date,
                src_currency_movement=src_currency_movement,
                dest_currency_movement=dest_currency_movement,
                rate=rate,
                concept=concept,
                detail=detail)


class OperationMovement(models.Model):
    class Meta:
        verbose_name = 'Operation Movement'
        verbose_name_plural = 'Operations Movements'

    operation = models.ForeignKey(Operation, models.CASCADE)
    movement = models.ForeignKey(Movement, models.CASCADE)

    def __str__(self):
        return '%s - %s' % (self.operation.name, self.movement.name)


