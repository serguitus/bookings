
from django.db import transaction
from django.db.models.signals import pre_save, post_save, post_delete

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
    if not hasattr(instance, 'code_updated'):
        with transaction.atomic(savepoint=False):
            BookingServices.sync_quote_paxvariants(instance)


@receiver(post_save, sender=QuotePaxVariant)
def sync_variant_quote(sender, instance, **kwargs):
    if not hasattr(instance, 'code_updated'):
        with transaction.atomic(savepoint=False):
            BookingServices.sync_children_paxvariants(instance)


@receiver(pre_save, sender=QuoteServicePaxVariant)
def pre_save_quoteservice_paxvariant_setup_amounts(sender, instance, **kwargs):
    BookingServices.setup_paxvariant_amounts(instance)


receiver(post_save, sender=QuoteServicePaxVariant)
def post_save_update_quote_pax_variant(sender, instance, **kwargs):
    with transaction.atomic(savepoint=False):
        BookingServices.update_quote_paxvariant_amounts(instance)


@receiver(post_save, sender=QuoteAllotment)
def update_allotment_pax_variants(sender, instance, **kwargs):
    with transaction.atomic(savepoint=False):
        BookingServices.update_quoteservice_paxvariants_amounts(instance)


@receiver((post_save, post_delete), sender=QuoteAllotment)
def update_allotment_quote(sender, instance, **kwargs):
    with transaction.atomic(savepoint=False):
        BookingServices.update_quote(instance)


@receiver(post_save, sender=QuoteTransfer)
def update_transfer_pax_variants(sender, instance, **kwargs):
    with transaction.atomic(savepoint=False):
        BookingServices.update_quoteservice_paxvariants_amounts(instance)


@receiver((post_save, post_delete), sender=QuoteTransfer)
def update_transfer_quote(sender, instance, **kwargs):
    with transaction.atomic(savepoint=False):
        BookingServices.update_quote(instance)


@receiver(post_save, sender=QuoteExtra)
def update_extra_pax_variants(sender, instance, **kwargs):
    with transaction.atomic(savepoint=False):
        BookingServices.update_quoteservice_paxvariants_amounts(instance)


@receiver((post_save, post_delete), sender=QuoteExtra)
def update_extra_quote(sender, instance, **kwargs):
    with transaction.atomic(savepoint=False):
        BookingServices.update_quote(instance)


@receiver(post_save, sender=QuotePackage)
def post_save_update_package_quote(sender, instance, **kwargs):
    with transaction.atomic(savepoint=False):
        BookingServices.sync_quotepackage_services(instance)
        if not hasattr(instance, 'code_updated'):
            BookingServices.sync_quotepackage_paxvariants(instance)
        BookingServices.update_quote(instance)

@receiver(post_delete, sender=QuotePackage)
def post_delete_update_package_quote(sender, instance, **kwargs):
    with transaction.atomic(savepoint=False):
        BookingServices.update_quote(instance)


@receiver(pre_save, sender=QuotePackageServicePaxVariant)
def pre_save_setup_amounts(sender, instance, **kwargs):
    BookingServices.setup_paxvariant_amounts(instance)


@receiver(post_save, sender=QuotePackageServicePaxVariant)
def post_save_update_quotepackage_paxvariant(sender, instance, **kwargs):
    with transaction.atomic(savepoint=False):
        BookingServices.update_quotepackage_paxvariant_amounts(instance)


@receiver((post_save, post_delete), sender=QuotePackageAllotment)
def update_package_allotment_package(sender, instance, **kwargs):
    with transaction.atomic(savepoint=False):
        BookingServices.update_quotepackage(instance)


@receiver((post_save, post_delete), sender=QuotePackageTransfer)
def update_package_transfer_package(sender, instance, **kwargs):
    with transaction.atomic(savepoint=False):
        BookingServices.update_quotepackage(instance)


@receiver((post_save, post_delete), sender=QuotePackageExtra)
def update_package_extra_package(sender, instance, **kwargs):
    with transaction.atomic(savepoint=False):
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
