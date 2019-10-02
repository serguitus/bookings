
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models.signals import pre_save, post_save, pre_delete, post_delete
from django.dispatch import receiver

from booking.constants import SERVICE_CATEGORY_PACKAGE, SERVICE_STATUS_PENDING
from booking.models import (
    Quote, QuotePaxVariant,
    QuoteServicePaxVariant,
    QuoteAllotment, QuoteTransfer, QuoteExtra,
    QuotePackageServicePaxVariant,
    QuotePackage, QuotePackageAllotment, QuotePackageTransfer, QuotePackageExtra,
    Booking, BookingPax,
    BookingService, BookingServicePax,
    BookingAllotment, BookingTransfer, BookingExtra, BookingPackage,
    BookingPackageService, BookingPackageAllotment, BookingPackageTransfer, BookingPackageExtra)
from booking.services import BookingServices


# Quote

@receiver(post_save, sender=Quote)
def post_save_quote(sender, instance, **kwargs):
    if not hasattr(instance, 'code_updated') and not hasattr(instance, 'avoid_all'):
        with transaction.atomic(savepoint=False):
            BookingServices.sync_quote_paxvariants(instance)


@receiver(post_save, sender=QuotePaxVariant)
def post_save_quote_paxvariant(sender, instance, **kwargs):
    if not hasattr(instance, 'code_updated') and not hasattr(instance, 'avoid_all'):
        with transaction.atomic(savepoint=False):
            BookingServices.sync_quote_children_paxvariants(instance)


@receiver(pre_save, sender=QuoteServicePaxVariant)
def pre_save_quoteservice_paxvariant_setup_amounts(sender, instance, **kwargs):
    if not hasattr(instance, 'avoid_all'):
        BookingServices.setup_paxvariant_amounts(instance)


receiver(post_save, sender=QuoteServicePaxVariant)
def post_save_quoteservice_paxvariant(sender, instance, **kwargs):
    if not hasattr(instance, 'avoid_all'):
        with transaction.atomic(savepoint=False):
            BookingServices.sync_quotepackage_children_paxvariants(instance)
            BookingServices.update_quote_paxvariant_amounts(instance)


receiver(post_delete, sender=QuoteServicePaxVariant)
def post_delete_quoteservice_paxvariant(sender, instance, **kwargs):
    if not hasattr(instance, 'avoid_all'):
        with transaction.atomic(savepoint=False):
            BookingServices.update_quote_paxvariant_amounts(instance)


@receiver(post_save, sender=QuoteAllotment)
def post_save_quoteallotment(sender, instance, **kwargs):
    if not hasattr(instance, 'avoid_all'):
        with transaction.atomic(savepoint=False):
            BookingServices.update_quoteservice_paxvariants_amounts(instance)
            BookingServices.update_quote(instance)


@receiver(post_save, sender=QuoteTransfer)
def post_save_quotetransfer(sender, instance, **kwargs):
    if not hasattr(instance, 'avoid_all'):
        with transaction.atomic(savepoint=False):
            BookingServices.update_quoteservice_paxvariants_amounts(instance)
            BookingServices.update_quote(instance)


@receiver(post_save, sender=QuoteExtra)
def post_save_quoteextra(sender, instance, **kwargs):
    if not hasattr(instance, 'avoid_all'):
        with transaction.atomic(savepoint=False):
            BookingServices.update_quoteservice_paxvariants_amounts(instance)
            BookingServices.update_quote(instance)


@receiver(post_save, sender=QuotePackage)
def post_save_quotepackage(sender, instance, **kwargs):
    if not hasattr(instance, 'avoid_all'):
        with transaction.atomic(savepoint=False):
            BookingServices.update_quoteservice_paxvariants_amounts(instance)
            BookingServices.sync_quotepackage_services(instance)
            BookingServices.update_quote(instance)


@receiver(pre_save, sender=QuotePackageServicePaxVariant)
def pre_save_setup_amounts(sender, instance, **kwargs):
    if not hasattr(instance, 'avoid_all'):
        BookingServices.setup_paxvariant_amounts(instance)


@receiver(post_save, sender=QuotePackageServicePaxVariant)
def post_save_quotepackage_service_paxvariant(sender, instance, **kwargs):
    if not hasattr(instance, 'code_updated') and not hasattr(instance, 'avoid_all'):
        with transaction.atomic(savepoint=False):
            BookingServices.update_quotepackage_paxvariant_amounts(instance)


@receiver(post_delete, sender=QuotePackageServicePaxVariant)
def post_delete_quotepackage_service_paxvariant(sender, instance, **kwargs):
    if not hasattr(instance, 'avoid_all'):
        with transaction.atomic(savepoint=False):
            BookingServices.update_quotepackage_paxvariant_amounts(instance)


@receiver(post_save, sender=QuotePackageAllotment)
def post_save_quotepackage_allotment(sender, instance, **kwargs):
    if not hasattr(instance, 'avoid_all'):
        with transaction.atomic(savepoint=False):
            BookingServices.update_quotepackageservice_paxvariants_amounts(instance)
            BookingServices.update_quotepackage(instance)


@receiver(post_save, sender=QuotePackageTransfer)
def post_save_quotepackage_transfer(sender, instance, **kwargs):
    if not hasattr(instance, 'avoid_all'):
        with transaction.atomic(savepoint=False):
            BookingServices.update_quotepackageservice_paxvariants_amounts(instance)
            BookingServices.update_quotepackage(instance)


@receiver(post_save, sender=QuotePackageExtra)
def post_save_quotepackage_extra(sender, instance, **kwargs):
    if not hasattr(instance, 'avoid_all'):
        with transaction.atomic(savepoint=False):
            BookingServices.update_quotepackageservice_paxvariants_amounts(instance)
            BookingServices.update_quotepackage(instance)


# Booking

@receiver((post_save, post_delete), sender=BookingServicePax)
def post_save_post_delete_bookingservicepax(sender, instance, **kwargs):
    if not hasattr(instance, 'avoid_bookingservice_update'):
        with transaction.atomic(savepoint=False):
            BookingServices.update_bookingservice_amounts(instance.booking_service)


@receiver(pre_save, sender=BookingAllotment)
def pre_save_bookingallotment(sender, instance, **kwargs):
    if not hasattr(instance, 'avoid_all') and not hasattr(instance, 'avoid_update'):
        BookingServices.setup_bookingservice_amounts(instance)


@receiver(pre_save, sender=BookingTransfer)
def pre_save_bookingtransfer(sender, instance, **kwargs):
    if not hasattr(instance, 'avoid_all') and not hasattr(instance, 'avoid_update'):
        BookingServices.setup_bookingservice_amounts(instance)


@receiver(pre_save, sender=BookingExtra)
def pre_save_bookingextra(sender, instance, **kwargs):
    if not hasattr(instance, 'avoid_all') and not hasattr(instance, 'avoid_update'):
        BookingServices.setup_bookingservice_amounts(instance)


@receiver(pre_delete, sender=BookingService)
def pre_delete_bookingservice(sender, instance, **kwargs):
    if instance.status != SERVICE_STATUS_PENDING:
        raise ValidationError('Can not delete Booking Services that are Not Pending')


@receiver(pre_delete, sender=BookingAllotment)
def pre_delete_bookingallotment(sender, instance, **kwargs):
    if instance.status != SERVICE_STATUS_PENDING:
        raise ValidationError('Can not delete Booking Services that are Not Pending')


@receiver(pre_delete, sender=BookingTransfer)
def pre_delete_bookingtransfer(sender, instance, **kwargs):
    if instance.status != SERVICE_STATUS_PENDING:
        raise ValidationError('Can not delete Booking Services that are Not Pending')


@receiver(pre_delete, sender=BookingExtra)
def pre_delete_bookingextra(sender, instance, **kwargs):
    if instance.status != SERVICE_STATUS_PENDING:
        raise ValidationError('Can not delete Booking Services that are Not Pending')


@receiver(pre_delete, sender=BookingPackage)
def pre_delete_bookingpackage(sender, instance, **kwargs):
    if instance.status != SERVICE_STATUS_PENDING:
        raise ValidationError('Can not delete Booking Services that are Not Pending')


@receiver(pre_delete, sender=BookingPackageService)
def pre_delete_bookingpackageservice(sender, instance, **kwargs):
    if instance.status != SERVICE_STATUS_PENDING:
        raise ValidationError('Can not delete Booking Services that are Not Pending')


@receiver(pre_delete, sender=BookingPackageAllotment)
def pre_delete_bookingpackageallotment(sender, instance, **kwargs):
    if instance.status != SERVICE_STATUS_PENDING:
        raise ValidationError('Can not delete Booking Services that are Not Pending')


@receiver(pre_delete, sender=BookingPackageTransfer)
def pre_delete_bookingpackagetransfer(sender, instance, **kwargs):
    if instance.status != SERVICE_STATUS_PENDING:
        raise ValidationError('Can not delete Booking Services that are Not Pending')


@receiver(pre_delete, sender=BookingPackageExtra)
def pre_delete_bookingpackageextra(sender, instance, **kwargs):
    if instance.status != SERVICE_STATUS_PENDING:
        raise ValidationError('Can not delete Booking Services that are Not Pending')


@receiver((post_save, post_delete), sender=BookingAllotment)
def post_save_post_delete_bookingallotment(sender, instance, **kwargs):
    if not hasattr(instance, 'avoid_all') and not hasattr(instance, 'avoid_booking_update'):
        with transaction.atomic(savepoint=False):
            BookingServices.update_booking(instance)


@receiver((post_save, post_delete), sender=BookingTransfer)
def post_save_post_delete_bookingtransfer(sender, instance, **kwargs):
    if not hasattr(instance, 'avoid_all') and not hasattr(instance, 'avoid_booking_update'):
        with transaction.atomic(savepoint=False):
            BookingServices.update_booking(instance)


@receiver((post_save, post_delete), sender=BookingExtra)
def post_save_post_delete_bookingextra(sender, instance, **kwargs):
    if not hasattr(instance, 'avoid_all') and not hasattr(instance, 'avoid_booking_update'):
        with transaction.atomic(savepoint=False):
            BookingServices.update_booking(instance)


@receiver((post_save, post_delete), sender=BookingPackage)
def post_save_post_delete_bookingpackage(sender, instance, **kwargs):
    if not hasattr(instance, 'avoid_all') and not hasattr(instance, 'avoid_booking_update'):
        with transaction.atomic(savepoint=False):
            BookingServices.update_booking(instance)


@receiver(pre_save, sender=BookingPackageAllotment)
def pre_save_bookingpackageallotment(sender, instance, **kwargs):
    if not hasattr(instance, 'avoid_all') and not hasattr(instance, 'avoid_update'):
        BookingServices.setup_bookingservice_amounts(instance)


@receiver(pre_save, sender=BookingPackageTransfer)
def pre_save_bookingpackagetransfer(sender, instance, **kwargs):
    if not hasattr(instance, 'avoid_all') and not hasattr(instance, 'avoid_update'):
        BookingServices.setup_bookingservice_amounts(instance)


@receiver(pre_save, sender=BookingPackageExtra)
def pre_save_bookingpackageextra(sender, instance, **kwargs):
    if not hasattr(instance, 'avoid_all') and not hasattr(instance, 'avoid_update'):
        BookingServices.setup_bookingservice_amounts(instance)


@receiver((post_save, post_delete), sender=BookingPackageAllotment)
def post_save_post_delete_bookingpackageallotment(sender, instance, **kwargs):
    if not hasattr(instance, 'avoid_all') and not hasattr(instance, 'avoid_bookingpackage_update'):
        with transaction.atomic(savepoint=False):
            BookingServices.update_bookingpackage(instance)


@receiver((post_save, post_delete), sender=BookingPackageTransfer)
def post_save_post_delete_bookingpackagetransfer(sender, instance, **kwargs):
    if not hasattr(instance, 'avoid_all') and not hasattr(instance, 'avoid_bookingpackage_update'):
        with transaction.atomic(savepoint=False):
            BookingServices.update_bookingpackage(instance)

@receiver((post_save, post_delete), sender=BookingPackageExtra)
def post_save_post_delete_bookingpackageextra(sender, instance, **kwargs):
    if not hasattr(instance, 'avoid_all') and not hasattr(instance, 'avoid_bookingpackage_update'):
        with transaction.atomic(savepoint=False):
            BookingServices.update_bookingpackage(instance)
