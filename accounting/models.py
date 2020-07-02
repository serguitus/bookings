from django.db import connection, models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone

from accounting.constants import (
    CURRENCIES, CURRENCY_CUC, MOVEMENT_TYPES, MOVEMENT_TYPE_INPUT,
    MOVEMENT_TYPE_OUTPUT)


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
            cursor.execute("""
                UPDATE accounting_account a SET a.balance = (
                    SELECT COALESCE(
                        SUM(CASE WHEN movement_type = '%s' THEN 1 ELSE -1 END * amount),
                        0)
                    FROM accounting_operationmovement
                    WHERE account_id = a.id)
                WHERE id = %s
                """, [MOVEMENT_TYPE_INPUT, self.pk])
            self.refresh_from_db()
        finally:
            cursor.close()

    def check_balance(self):
        """
        Computes the balance of the account with the database movements
        To check the balance is correct
        """
        all_movs = OperationMovement.objects.filter(account_id=self.id)
        sum_in = all_movs.filter(
            movement_type=MOVEMENT_TYPE_INPUT).aggregate(
                models.Sum('amount'))
        sum_out = all_movs.filter(
            movement_type=MOVEMENT_TYPE_OUTPUT).aggregate(
                models.Sum('amount'))
        total_in = sum_in['amount__sum'] or 0
        total_out = sum_out['amount__sum'] or 0
        if self.balance == total_in - total_out:
            # everything is fine
            return True, self.balance
        return False, total_in - total_out

    def recalculate_balance(self):
        """ computes and updates self.balance if wrong
        returns:
        False: nothing changed.
        True: balance updated
        """
        status, balance = self.check_balance()
        if not status:
            self.balance = balance
            self.save()
            return 1
        return 0

    @classmethod
    def fix_balances(cls):
        cursor = connection.cursor()
        try:
            cursor.execute("""
                UPDATE accounting_account a SET a.balance = (
                    SELECT COALESCE(
                        SUM(CASE WHEN movement_type = '%s' THEN 1 ELSE -1 END * amount),
                        0)
                    FROM accounting_operationmovement
                    WHERE account_id = a.id)
            """, MOVEMENT_TYPE_INPUT)
        finally:
            cursor.close()


class Operation(models.Model):
    class Meta:
        verbose_name = 'Operation'
        verbose_name_plural = 'Operations'
        default_permissions = ('view',)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        help_text='User who did the operation.',
    )
    datetime = models.DateTimeField(default=timezone.now)
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
        default_permissions = ('view',)
        indexes = [
            models.Index(fields=['account']),
        ]
    operation = models.ForeignKey(Operation)
    movement_type = models.CharField(max_length=5, choices=MOVEMENT_TYPES)
    account = models.ForeignKey(Account)
    amount = models.DecimalField(default=0.0, max_digits=9, decimal_places=2)

    def __str__(self):
        return  '%s on %s of %s' % (
            self.get_movement_type_display(), self.account, self.amount)

    def delete(self, using=None, keep_parents=False):
        raise ValidationError(
            'Can not delete Movements')
