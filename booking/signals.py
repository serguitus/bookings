
from django.db import transaction
from django.db.models.signals import post_save, post_delete

from django.dispatch import receiver

from booking.constants import SERVICE_CATEGORY_PACKAGE
from booking.models import (
    Quote, QuotePaxVariant,
    QuoteServicePaxVariant,
    QuoteAllotment, QuoteTransfer, QuoteExtra,
    QuotePackageServicePaxVariant,
    QuotePackage, QuotePackageAllotment, QuotePackageTransfer, QuotePackageExtra,
    Booking, BookingPax,
    BookingServicePax, BookingAllotment, BookingTransfer, BookingExtra,
    BookingPackage, BookingPackageAllotment, BookingPackageTransfer, BookingPackageExtra)
from booking.services import BookingServices


# Quote

@receiver(post_save, sender=Quote)
def update_quote(sender, instance, **kwargs):
    with transaction.atomic(savepoint=False):
        BookingServices.sync_pax_variants(instance)
        BookingServices.update_quote(instance)


@receiver((post_save), sender=QuotePaxVariant)
def sync_variant_quote(sender, instance, **kwargs):
    BookingServices.sync_pax_variants(instance)


@receiver((post_save), sender=QuoteServicePaxVariant)
def update_quote_pax_variant(sender, instance, **kwargs):
    BookingServices.update_quote_pax_variant_amounts(instance)


receiver((post_save), sender=QuotePackageServicePaxVariant)
def update_quotepackage_pax_variant(sender, instance, **kwargs):
    BookingServices.update_quotepackage_pax_variant_amounts(instance)


@receiver((post_save), sender=QuoteAllotment)
def update_allotment_pax_variants(sender, instance, **kwargs):
    with transaction.atomic(savepoint=False):
        BookingServices.update_service_pax_variants_amounts(instance)


@receiver((post_save, post_delete), sender=QuoteAllotment)
def update_allotment_quote(sender, instance, **kwargs):
    BookingServices.update_quote(instance)


@receiver((post_save), sender=QuoteTransfer)
def update_transfer_pax_variants(sender, instance, **kwargs):
    with transaction.atomic(savepoint=False):
        BookingServices.update_service_pax_variants_amounts(instance)


@receiver((post_save, post_delete), sender=QuoteTransfer)
def update_transfer_quote(sender, instance, **kwargs):
    BookingServices.update_quote(instance)


@receiver((post_save), sender=QuoteExtra)
def update_extra_pax_variants(sender, instance, **kwargs):
    with transaction.atomic(savepoint=False):
        BookingServices.update_service_pax_variants_amounts(instance)


@receiver((post_save, post_delete), sender=QuoteExtra)
def update_extra_quote(sender, instance, **kwargs):
    BookingServices.update_quote(instance)


@receiver(post_save, sender=QuotePackage)
def post_save_update_package_quote(sender, instance, **kwargs):
    with transaction.atomic(savepoint=False):
        BookingServices.update_service_pax_variants_amounts(instance)
        BookingServices.update_quote_package(instance)
        BookingServices.update_quote(instance)


@receiver(post_delete, sender=QuotePackage)
def post_delete_update_package_quote(sender, instance, **kwargs):
    with transaction.atomic(savepoint=False):
        BookingServices.update_quote(instance)


@receiver((post_save), sender=QuotePackageAllotment)
def update_package_allotment_pax_variants(sender, instance, **kwargs):
    with transaction.atomic(savepoint=False):
        BookingServices.update_quotepackage_service_pax_variants_amounts(instance)


@receiver((post_save, post_delete), sender=QuotePackageAllotment)
def update_package_allotment_package(sender, instance, **kwargs):
    BookingServices.update_quotepackage(instance)


@receiver((post_save), sender=QuotePackageTransfer)
def update_package_transfer_pax_variants(sender, instance, **kwargs):
    with transaction.atomic(savepoint=False):
        BookingServices.update_quotepackage_service_pax_variants_amounts(instance)


@receiver((post_save, post_delete), sender=QuotePackageTransfer)
def update_package_transfer_package(sender, instance, **kwargs):
    BookingServices.update_quotepackage(instance)


@receiver((post_save), sender=QuotePackageExtra)
def update_package_extra_pax_variants(sender, instance, **kwargs):
    with transaction.atomic(savepoint=False):
        BookingServices.update_quotepackage_service_pax_variants_amounts(instance)


@receiver((post_save, post_delete), sender=QuotePackageExtra)
def update_package_extra_package(sender, instance, **kwargs):
    BookingServices.update_quotepackage(instance)


# Booking

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


@receiver((post_save, post_delete), sender=BookingServicePax)
def update_booking_service(sender, instance, **kwargs):
    BookingServices.update_bookingservice_amounts(instance.booking_service)


@receiver(post_save, sender=BookingServicePax)
def update_booking_service_description(sender, instance, **kwargs):
    BookingServices.update_bookingservice_description(instance.booking_service)
