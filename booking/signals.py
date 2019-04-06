
from django.db import transaction
from django.db.models.signals import post_save, post_delete

from django.dispatch import receiver

from booking.models import (
    Quote, QuotePaxVariant, QuoteAllotment, QuoteTransfer, QuoteExtra,
    QuotePackage, QuotePackageAllotment, QuotePackageTransfer, QuotePackageExtra,
    Booking, BookingPax, BookingAllotment, BookingTransfer, BookingExtra,
    BookingPackage, BookingPackageAllotment, BookingPackageTransfer, BookingPackageExtra)
from booking.services import BookingServices


@receiver(post_save, sender=Quote)
def update_quote(sender, instance, **kwargs):
    BookingServices.update_quote(instance)


@receiver((post_save, post_delete), sender=QuotePaxVariant)
def update_variant_quote(sender, instance, **kwargs):
    BookingServices.update_quote(instance)


@receiver((post_save, post_delete), sender=QuoteAllotment)
def update_allotment_quote(sender, instance, **kwargs):
    BookingServices.update_quote(instance)


@receiver((post_save, post_delete), sender=QuoteTransfer)
def update_transfer_quote(sender, instance, **kwargs):
    BookingServices.update_quote(instance)


@receiver((post_save, post_delete), sender=QuoteExtra)
def update_extra_quote(sender, instance, **kwargs):
    BookingServices.update_quote(instance)


@receiver(post_save, sender=QuotePackage)
def post_save_update_package_quote(sender, instance, **kwargs):
    with transaction.atomic(savepoint=False):
        BookingServices.update_quote_package(instance)
        BookingServices.update_quote(instance)


@receiver(post_delete, sender=QuotePackage)
def post_delete_update_package_quote(sender, instance, **kwargs):
    with transaction.atomic(savepoint=False):
        BookingServices.update_quote(instance)


@receiver(post_save, sender=Booking)
def update_booking(sender, instance, **kwargs):
    BookingServices.update_booking(instance)


@receiver((post_save, post_delete), sender=BookingPax)
def update_pax_booking(sender, instance, **kwargs):
    BookingServices.update_booking(instance)


@receiver((post_save, post_delete), sender=BookingAllotment)
def update_allotment_booking(sender, instance, **kwargs):
    BookingServices.update_booking(instance)


@receiver((post_save, post_delete), sender=BookingTransfer)
def update_transfer_booking(sender, instance, **kwargs):
    BookingServices.update_booking(instance)

@receiver((post_save, post_delete), sender=BookingExtra)
def update_extra_booking(sender, instance, **kwargs):
    BookingServices.update_booking(instance)


@receiver(post_save, sender=BookingPackage)
def post_save_update_package_booking(sender, instance, **kwargs):
    with transaction.atomic(savepoint=False):
        BookingServices.update_booking_package(instance)
        BookingServices.update_booking(instance)


@receiver(post_delete, sender=BookingPackage)
def post_delete_update_package_booking(sender, instance, **kwargs):
    with transaction.atomic(savepoint=False):
        BookingServices.update_booking(instance)
