from __future__ import unicode_literals

from datetime import datetime

from django.db import models, transaction
from django.conf import settings
from django.core.exceptions import ValidationError

from accounting.constants import CURRENCIES, CURRENCY_CUC, MOVEMENT_TYPES
from accounting.exceptions import Error


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
        return '%s (%s)' % (self.name, self.currency)


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
    concept = models.CharField(max_length=100)
    detail = models.CharField(max_length=500)

    def __str__(self):
        return '%s - %s' % (self.date, self.concept)


class OperationMovement(models.Model):
    class Meta:
        verbose_name = 'Operation Movement'
        verbose_name_plural = 'Operations Movements'
    operation = models.ForeignKey(Operation)
    movement_type = models.CharField(max_length=2, choices=MOVEMENT_TYPES)
    account = models.ForeignKey(Account)
    amount = models.DecimalField(default=0.0, max_digits=9, decimal_places=2)
