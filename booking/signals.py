
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
def post_save_quote(sender, instance, **kwargs):
    if not hasattr(instance, 'code_updated'):
        with transaction.atomic(savepoint=False):
            BookingServices.sync_quote_paxvariants(instance)


@receiver(post_save, sender=QuotePaxVariant)
def post_save_quote_paxvariant(sender, instance, **kwargs):
    if not hasattr(instance, 'code_updated'):
        with transaction.atomic(savepoint=False):
            BookingServices.sync_children_paxvariants(instance)


@receiver(pre_save, sender=QuoteServicePaxVariant)
def pre_save_quoteservice_paxvariant_setup_amounts(sender, instance, **kwargs):
    BookingServices.setup_paxvariant_amounts(instance)


receiver(post_save, sender=QuoteServicePaxVariant)
def post_save_quoteservice_paxvariant(sender, instance, **kwargs):
    with transaction.atomic(savepoint=False):
        BookingServices.update_quote_paxvariant_amounts(instance)


receiver(post_delete, sender=QuoteServicePaxVariant)
def post_delete_quoteservice_paxvariant(sender, instance, **kwargs):
    with transaction.atomic(savepoint=False):
        BookingServices.update_quote_paxvariant_amounts(instance)


@receiver(post_save, sender=QuoteAllotment)
def post_save_quoteallotment(sender, instance, **kwargs):
    with transaction.atomic(savepoint=False):
        BookingServices.update_quoteservice_paxvariants_amounts(instance)
        BookingServices.update_quote(instance)


@receiver(post_save, sender=QuoteTransfer)
def post_save_quotetransfer(sender, instance, **kwargs):
    with transaction.atomic(savepoint=False):
        BookingServices.update_quoteservice_paxvariants_amounts(instance)
        BookingServices.update_quote(instance)


@receiver(post_save, sender=QuoteExtra)
def post_save_quoteextra(sender, instance, **kwargs):
    with transaction.atomic(savepoint=False):
        BookingServices.update_quoteservice_paxvariants_amounts(instance)
        BookingServices.update_quote(instance)


@receiver(post_save, sender=QuotePackage)
def post_save_quotepackage(sender, instance, **kwargs):
    with transaction.atomic(savepoint=False):
        BookingServices.sync_quotepackage_services(instance)
        if not hasattr(instance, 'code_updated'):
            BookingServices.sync_quotepackage_paxvariants(instance)
        BookingServices.update_quote(instance)


@receiver(pre_save, sender=QuotePackageServicePaxVariant)
def pre_save_setup_amounts(sender, instance, **kwargs):
    BookingServices.setup_paxvariant_amounts(instance)


@receiver(post_save, sender=QuotePackageServicePaxVariant)
def post_save_quotepackage_service_paxvariant(sender, instance, **kwargs):
    if not hasattr(instance, 'code_updated'):
        with transaction.atomic(savepoint=False):
            BookingServices.update_quotepackage_paxvariant_amounts(instance)


@receiver(post_delete, sender=QuotePackageServicePaxVariant)
def post_delete_quotepackage_service_paxvariant(sender, instance, **kwargs):
    with transaction.atomic(savepoint=False):
        BookingServices.update_quotepackage_paxvariant_amounts(instance)


@receiver(post_save, sender=QuotePackageAllotment)
def post_save_quotepackage_allotment(sender, instance, **kwargs):
    with transaction.atomic(savepoint=False):
        BookingServices.update_quotepackageservice_paxvariants_amounts(instance)
        BookingServices.update_quotepackage(instance)


@receiver(post_save, sender=QuotePackageTransfer)
def post_save_quotepackage_transfer(sender, instance, **kwargs):
    with transaction.atomic(savepoint=False):
        BookingServices.update_quotepackageservice_paxvariants_amounts(instance)
        BookingServices.update_quotepackage(instance)


@receiver(post_save, sender=QuotePackageExtra)
def post_save_quotepackage_extra(sender, instance, **kwargs):
    with transaction.atomic(savepoint=False):
        BookingServices.update_quotepackageservice_paxvariants_amounts(instance)
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
