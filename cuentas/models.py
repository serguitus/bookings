from __future__ import unicode_literals

from django.db import models
from django.conf import settings

# Create your models here.

class Caja(models.Model):
    """ Esto define una Caja en cierta moneda """
    currency = models.CharField(max_length=5, choices=settings.CURRENCIES)
    ammount = models.IntegerField(default=0)
    description = models.CharField(max_length=100)

    def __str__(self):
        """ Representation of a Caja """
        return "Caja %s" % self.currency


class Transaction(models.Model):
    """ This deals with money operations. deposits, extractions, loans and transferences """
    caja = models.ForeignKey(Caja, models.CASCADE)
    ammount = models.IntegerField(default=0)
    date = models.DateField()
    concept = models.CharField(max_length=100)
    detail = models.CharField(max_length=250)

    def __str__(self):
        return 'Transaccion: %s' % self.concept
