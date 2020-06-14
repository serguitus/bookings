
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models.signals import pre_save, post_save, pre_delete, post_delete
from django.dispatch import receiver

from booking.constants import SERVICE_STATUS_PENDING
from booking.models import (
    Quote, QuotePaxVariant,
    QuoteServicePaxVariant,
    NewQuoteAllotment, NewQuoteTransfer, NewQuoteExtra,
    QuoteExtraPackage,
    Booking, BookingPax, BookingInvoice,
    BaseBookingService, BookingProvidedService, BaseBookingServicePax,
    BookingProvidedAllotment, BookingProvidedTransfer, BookingProvidedExtra, BookingExtraPackage,
    ProviderBookingPayment, ProviderPaymentBookingProvided,
)
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


@receiver(post_save, sender=QuoteServicePaxVariant)
def post_save_quoteservice_paxvariant(sender, instance, **kwargs):
    if not hasattr(instance, 'avoid_all'):
        with transaction.atomic(savepoint=False):
            BookingServices.sync_quotepackage_children_paxvariants(instance)
            BookingServices.update_quote_paxvariant_amounts(instance)


@receiver(post_delete, sender=QuoteServicePaxVariant)
def post_delete_quoteservice_paxvariant(sender, instance, **kwargs):
    if not hasattr(instance, 'avoid_all'):
        with transaction.atomic(savepoint=False):
            BookingServices.update_quote_paxvariant_amounts(instance)


@receiver(post_save, sender=NewQuoteAllotment)
def post_save_quoteallotment(sender, instance, **kwargs):
    if not hasattr(instance, 'avoid_all'):
        with transaction.atomic(savepoint=False):
            BookingServices.update_quoteservice_paxvariants_amounts(instance)
            BookingServices.update_quote(instance)


@receiver(post_save, sender=NewQuoteTransfer)
def post_save_quotetransfer(sender, instance, **kwargs):
    if not hasattr(instance, 'avoid_all'):
        with transaction.atomic(savepoint=False):
            BookingServices.update_quoteservice_paxvariants_amounts(instance)
            BookingServices.update_quote(instance)


@receiver(post_save, sender=NewQuoteExtra)
def post_save_quoteextra(sender, instance, **kwargs):
    if not hasattr(instance, 'avoid_all'):
        with transaction.atomic(savepoint=False):
            BookingServices.update_quoteservice_paxvariants_amounts(instance)
            BookingServices.update_quote(instance)


@receiver(post_save, sender=QuoteExtraPackage)
def post_save_quotepackage(sender, instance, **kwargs):
    if not hasattr(instance, 'avoid_all'):
        with transaction.atomic(savepoint=False):
            BookingServices.update_quoteservice_paxvariants_amounts(instance)
            BookingServices.sync_quotepackage_services(instance)
            BookingServices.update_quote(instance)


# Booking

@receiver((post_save, post_delete), sender=BaseBookingServicePax)
def post_save_post_delete_bookingservicepax(sender, instance, **kwargs):
    if not hasattr(instance, 'avoid_bookingservice_update'):
        with transaction.atomic(savepoint=False):
            BookingServices.update_bookingservice_amounts(instance.booking_service)


@receiver(pre_save, sender=BookingProvidedAllotment)
def pre_save_bookingallotment(sender, instance, **kwargs):
    if not hasattr(instance, 'avoid_all') and not hasattr(instance, 'avoid_update'):
        BookingServices.setup_bookingservice_amounts(instance)
    BookingServices.validate_basebookingservice(instance)


@receiver(pre_save, sender=BookingProvidedTransfer)
def pre_save_bookingtransfer(sender, instance, **kwargs):
    if not hasattr(instance, 'avoid_all') and not hasattr(instance, 'avoid_update'):
        BookingServices.setup_bookingservice_amounts(instance)
    BookingServices.validate_basebookingservice(instance)


@receiver(pre_save, sender=BookingProvidedExtra)
def pre_save_bookingextra(sender, instance, **kwargs):
    if not hasattr(instance, 'avoid_all') and not hasattr(instance, 'avoid_update'):
        BookingServices.setup_bookingservice_amounts(instance)
    BookingServices.validate_basebookingservice(instance)


@receiver(pre_delete, sender=BookingProvidedService)
def pre_delete_bookingservice(sender, instance, **kwargs):
    if instance.has_payment or instance.status != SERVICE_STATUS_PENDING:
        raise ValidationError('Can not delete Booking Services that are Not Pending')


@receiver(pre_delete, sender=BookingProvidedAllotment)
def pre_delete_bookingallotment(sender, instance, **kwargs):
    if instance.has_payment or instance.status != SERVICE_STATUS_PENDING:
        raise ValidationError('Can not delete Booking Services that are Not Pending')


@receiver(pre_delete, sender=BookingProvidedTransfer)
def pre_delete_bookingtransfer(sender, instance, **kwargs):
    if instance.has_payment or instance.status != SERVICE_STATUS_PENDING:
        raise ValidationError('Can not delete Booking Services that are Not Pending')


@receiver(pre_delete, sender=BookingProvidedExtra)
def pre_delete_bookingextra(sender, instance, **kwargs):
    if instance.has_payment or instance.status != SERVICE_STATUS_PENDING:
        raise ValidationError('Can not delete Booking Services that are Not Pending')


@receiver(pre_delete, sender=BookingExtraPackage)
def pre_delete_bookingpackage(sender, instance, **kwargs):
    if instance.has_payment or instance.status != SERVICE_STATUS_PENDING:
        raise ValidationError('Can not delete Booking Services that are Not Pending')


@receiver(pre_delete, sender=BookingProvidedService)
def pre_delete_bookingpackageservice(sender, instance, **kwargs):
    if instance.has_payment or instance.status != SERVICE_STATUS_PENDING:
        raise ValidationError('Can not delete Booking Services that are Not Pending')


@receiver(pre_delete, sender=BookingProvidedAllotment)
def pre_delete_bookingpackageallotment(sender, instance, **kwargs):
    if instance.has_payment or instance.status != SERVICE_STATUS_PENDING:
        raise ValidationError('Can not delete Booking Services that are Not Pending')


@receiver(pre_delete, sender=BookingProvidedTransfer)
def pre_delete_bookingpackagetransfer(sender, instance, **kwargs):
    if instance.has_payment or instance.status != SERVICE_STATUS_PENDING:
        raise ValidationError('Can not delete Booking Services that are Not Pending')


@receiver(pre_delete, sender=BookingProvidedExtra)
def pre_delete_bookingpackageextra(sender, instance, **kwargs):
    if instance.has_payment or instance.status != SERVICE_STATUS_PENDING:
        raise ValidationError('Can not delete Booking Services that are Not Pending')


@receiver((post_save, post_delete), sender=BookingProvidedAllotment)
def post_save_post_delete_bookingallotment(sender, instance, **kwargs):
    if not hasattr(instance, 'avoid_all') and not hasattr(instance, 'avoid_booking_update'):
        with transaction.atomic(savepoint=False):
            BookingServices.update_booking(instance)


@receiver((post_save, post_delete), sender=BookingProvidedTransfer)
def post_save_post_delete_bookingtransfer(sender, instance, **kwargs):
    if not hasattr(instance, 'avoid_all') and not hasattr(instance, 'avoid_booking_update'):
        with transaction.atomic(savepoint=False):
            BookingServices.update_booking(instance)


@receiver((post_save, post_delete), sender=BookingProvidedExtra)
def post_save_post_delete_bookingextra(sender, instance, **kwargs):
    if not hasattr(instance, 'avoid_all') and not hasattr(instance, 'avoid_booking_update'):
        with transaction.atomic(savepoint=False):
            BookingServices.update_booking(instance)


@receiver((post_save, post_delete), sender=BookingExtraPackage)
def post_save_post_delete_bookingpackage(sender, instance, **kwargs):
    if not hasattr(instance, 'avoid_all') and not hasattr(instance, 'avoid_booking_update'):
        with transaction.atomic(savepoint=False):
            BookingServices.update_booking(instance)


@receiver(pre_save, sender=BookingProvidedAllotment)
def pre_save_bookingpackageallotment(sender, instance, **kwargs):
    if not hasattr(instance, 'avoid_all') and not hasattr(instance, 'avoid_update'):
        BookingServices.setup_bookingservice_amounts(instance)
    BookingServices.validate_basebookingservice(instance)


@receiver(pre_save, sender=BookingProvidedTransfer)
def pre_save_bookingpackagetransfer(sender, instance, **kwargs):
    if not hasattr(instance, 'avoid_all') and not hasattr(instance, 'avoid_update'):
        BookingServices.setup_bookingservice_amounts(instance)
    BookingServices.validate_basebookingservice(instance)


@receiver(pre_save, sender=BookingProvidedExtra)
def pre_save_bookingpackageextra(sender, instance, **kwargs):
    if not hasattr(instance, 'avoid_all') and not hasattr(instance, 'avoid_update'):
        BookingServices.setup_bookingservice_amounts(instance)
    BookingServices.validate_basebookingservice(instance)


@receiver((post_save, post_delete), sender=BookingProvidedAllotment)
def post_save_post_delete_bookingpackageallotment(sender, instance, **kwargs):
    if not hasattr(instance, 'avoid_all') and not hasattr(instance, 'avoid_bookingpackage_update'):
        with transaction.atomic(savepoint=False):
            BookingServices.update_bookingpackage(instance)


@receiver((post_save, post_delete), sender=BookingProvidedTransfer)
def post_save_post_delete_bookingpackagetransfer(sender, instance, **kwargs):
    if not hasattr(instance, 'avoid_all') and not hasattr(instance, 'avoid_bookingpackage_update'):
        with transaction.atomic(savepoint=False):
            BookingServices.update_bookingpackage(instance)


@receiver((post_save, post_delete), sender=BookingProvidedExtra)
def post_save_post_delete_bookingpackageextra(sender, instance, **kwargs):
    if not hasattr(instance, 'avoid_all') and not hasattr(instance, 'avoid_bookingpackage_update'):
        with transaction.atomic(savepoint=False):
            BookingServices.update_bookingpackage(instance)


@receiver((post_save), sender=BookingInvoice)
def post_save_bookinginvoice(sender, instance, **kwargs):
    if not instance.document_number:
        instance.document_number = '{}-{}'.format(instance.invoice_booking.id,
                                                  instance.id)
        instance.save()
