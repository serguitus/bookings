from django.db import connection, models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone

from accounting.constants import (
    CURRENCIES, CURRENCY_CUC, MOVEMENT_TYPES, MOVEMENT_TYPE_INPUT)


class Hello1(models.Model):
    class Meta:
        managed = False
        permissions = (('view', 'view'),)
        verbose_name = 'Hello 1'
        verbose_name_plural = 'Hellos 1s'


class Hello2(models.Model):
    class Meta:
        managed = False
        permissions = (('view', 'view'),)
        verbose_name = 'Hello 2'
        verbose_name_plural = 'Hellos 2s'
