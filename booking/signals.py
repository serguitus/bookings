
from django.db import transaction
from django.db.models.signals import post_save

from django.dispatch import receiver

from booking.models import (
    QuoteAllotment, QuoteTransfer, QuoteExtra, QuotePackage,
    Booking, BookingPax, BookingAllotment, BookingTransfer, BookingExtra)
from booking.services import BookingServices


@receiver(post_save, sender=QuoteAllotment)
def update_allotment_quote(sender, instance, **kwargs):
    quote = instance.quote
    BookingServices.update_quote(quote)


@receiver(post_save, sender=QuoteTransfer)
def update_transfer_quote(sender, instance, **kwargs):
    quote = instance.quote
    BookingServices.update_quote(quote)


@receiver(post_save, sender=QuoteExtra)
def update_extra_quote(sender, instance, **kwargs):
    quote = instance.quote
    BookingServices.update_quote(quote)


@receiver(post_save, sender=QuotePackage)
def update_package_quote(sender, instance, **kwargs):
    with transaction.atomic(savepoint=False):
        BookingServices.update_quote_package(instance)
        quote = instance.quote
        BookingServices.update_quote(quote)


@receiver(post_save, sender=Booking)
def update_booking(sender, instance, **kwargs):
    booking = instance
    BookingServices.update_booking(booking)


@receiver(post_save, sender=BookingPax)
def update_pax_booking(sender, instance, **kwargs):
    booking = instance.booking
    BookingServices.update_booking(booking)


@receiver(post_save, sender=BookingAllotment)
def update_allotment_booking(sender, instance, **kwargs):
    booking = instance.booking
    BookingServices.update_booking(booking)


@receiver(post_save, sender=BookingTransfer)
def update_transfer_booking(sender, instance, **kwargs):
    booking = instance.booking
    BookingServices.update_booking(booking)


@receiver(post_save, sender=BookingExtra)
def update_extra_booking(sender, instance, **kwargs):
    booking = instance.booking
    BookingServices.update_booking(booking)
