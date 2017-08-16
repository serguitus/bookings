# -*- coding: utf-8 -*-

from django.db.models.signals import pre_save
from django.dispatch import receiver

from cuentas.models import Transaction

# @receiver(pre_save, sender=Transaction)
# def update_caja(sender, instance, **kwargs):
#     """ updates the Caja according to the ammount transfered """
#     if instance.pk:
#         # this transaction already exists, we are just updating it
#         original = sender.objects.get(pk=instance.pk)
#         if instance.caja == original.caja:
#             instance.caja.ammount -= original.ammount
#         else:
#             original.caja.ammount -= original.ammount
#             original.caja.save()
#     instance.caja.ammount += instance.ammount
#     instance.caja.save()
    
