from django.db import connection, models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.timezone import now

from accounting.constants import (
    CURRENCIES, CURRENCY_CUC, MOVEMENT_TYPES, MOVEMENT_TYPE_INPUT)


class Account(models.Model):
    class Meta:
        verbose_name = 'Account'
        verbose_name_plural = 'Accounts'
        unique_together = (('name', 'currency'),)
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=200, blank=True, null=True)
    currency = models.CharField(
        max_length=5, choices=CURRENCIES, default=CURRENCY_CUC)
    balance = models.DecimalField(default=0.0, max_digits=12, decimal_places=2)
    enabled = models.BooleanField(default=True)

    def __str__(self):
        return '%s (%s)' % (self.name, self.get_currency_display())

    def fix_balance(self):
        cursor = connection.cursor()
        try:
            cursor.execute(
                "UPDATE \
                    accounting_account a \
                SET \
                    a.balance = (\
                        SELECT \
                            SUM(CASE WHEN movement_type = %s THEN 1 ELSE -1 END * amount) \
                        FROM \
                            accounting_operationmovement \
                        WHERE \
                            account_id = a.id\
                    )\
                WHERE \
                    id = %s", [MOVEMENT_TYPE_INPUT, self.pk])
        finally:
            cursor.close()

    @classmethod
    def fix_balances(cls):
        cursor = connection.cursor()
        try:
            cursor.execute(
                "UPDATE \
                    accounting_account a \
                SET \
                    a.balance = (\
                        SELECT \
                            SUM(CASE WHEN movement_type = %s THEN 1 ELSE -1 END * amount) \
                        FROM \
                            accounting_operationmovement \
                        WHERE \
                            account_id = a.id\
                    )", MOVEMENT_TYPE_INPUT)
        finally:
            cursor.close()

class Operation(models.Model):
    class Meta:
        verbose_name = 'Operation'
        verbose_name_plural = 'Operations'
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        help_text='User who did the operation.',
    )
    datetime = models.DateTimeField(default=now)
    concept = models.CharField(max_length=50)
    detail = models.CharField(max_length=200)

    def __str__(self):
        return self.detail

    def delete(self, using=None, keep_parents=False):
        raise ValidationError(
            'Can not delete Operations')


class OperationMovement(models.Model):
    class Meta:
        verbose_name = 'Operation Movement'
        verbose_name_plural = 'Operations Movements'
    operation = models.ForeignKey(Operation)
    movement_type = models.CharField(max_length=2, choices=MOVEMENT_TYPES)
    account = models.ForeignKey(Account)
    amount = models.DecimalField(default=0.0, max_digits=9, decimal_places=2)

    def __str__(self):
        return  '%s on %s of %s' % (
            self.get_movement_type_display(), self.account, self.amount)

    def delete(self, using=None, keep_parents=False):
        raise ValidationError(
            'Can not delete Movements')
