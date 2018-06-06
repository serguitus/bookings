from django.db import models
from django.conf import settings
from django.db import connection

from accounting.constants import (
    CURRENCIES, CURRENCY_CUC, MOVEMENT_TYPES, MOVEMENT_TYPE_DEPOSIT, CONCEPTS)


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

    def update_balance(self):
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
                    id = %s", [MOVEMENT_TYPE_DEPOSIT, self.pk])
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
    date = models.DateTimeField()
    concept = models.CharField(max_length=50, choices=CONCEPTS)
    detail = models.CharField(max_length=200)

    def __str__(self):
        return self.detail


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
