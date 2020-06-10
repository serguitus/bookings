from __future__ import unicode_literals
from django import template

from booking.constants import SERVICE_STATUS_CANCELLED
from booking.models import (
    Booking,
    BaseBookingService,
    QuoteService,
    BookingProvidedTransfer,
    BookingProvidedAllotment,
    BookingProvidedExtra,
    BookingExtraPackage, ProviderBookingPayment,
    ProviderPaymentBookingProvided,
)
from booking.tables import (
    QuoteServiceTable, QuotePaxVariantTable,
    QuoteConfirmationTable,
    NewQuoteServiceBookDetailTable,
    BookingServiceTable,
    BookingExtraPackageServiceTable, BookingExtraPackageServiceSummaryTable,
    BookingConfirmationTable, BookingServiceSummaryTable, BookingPaxTable,
    BookingVouchersTable,
    BookingServiceUpdateTable,
    BookingBookDetailTable,
    AddPaxBookingServicesTable,
    ProviderBookingPaymentTable,
    ProviderPaymentBookingProvidedTable,
    ProviderBookingPaymentReportTable,
    AgencyPaymentTable,
)
from booking.services import BookingServices

from finance.models import AgencyPayment

register = template.Library()


@register.simple_tag
def quoteservice_table(quote):
    table = QuoteServiceTable(
        quote.quote_services.all(),
        order_by=('datetime_from', 'time', 'datetime_to'))
    return table


@register.simple_tag
def quotepaxvariant_table(quote):
    table = QuotePaxVariantTable(
        quote.quote_paxvariants.all(),
        order_by=('pax_quantity',))
    return table


@register.simple_tag
def bookingservice_table(booking):
    table = BookingServiceTable(
        BaseBookingService.objects.filter(booking=booking),
        order_by=('datetime_from', 'time', 'datetime_to'))
    return table


@register.simple_tag
def agencypayment_table(booking):
    if booking.invoice:
        qs = AgencyPayment.objects.filter(agencydocumentmatch__debit_document=booking.invoice)
    else:
        qs = AgencyPayment.objects.none()
    table = AgencyPaymentTable(qs, order_by=('date',),)
    return table


@register.simple_tag
def providerbookingpayment_table(service):
    table = ProviderBookingPaymentTable(
        ProviderBookingPayment.objects.filter(
            providerpaymentbookingprovided__provider_service=service),
        order_by=('date',),
    )
    return table


@register.simple_tag
def providerpaymentbookingprovided_table(payment):
    table = ProviderPaymentBookingProvidedTable(
        ProviderPaymentBookingProvided.objects.filter(provider_payment=payment),
        # TODO el parametro order_by no funciona aqui. al parecer el
        # orden del queryset es el que cuenta aqui
        order_by=('datetime_from', 'time', 'datetime_to'),
    )
    return table


@register.simple_tag
def providerbookingpaymentreport_table(payment):
    table = ProviderBookingPaymentReportTable(
        ProviderPaymentBookingProvided.objects.filter(
            provider_payment=payment).order_by(
                'provider_service__datetime_from',
                'provider_service__datetime_to'),
    )
    return table


@register.simple_tag
def bookingconfirmation_table(booking):
    table = BookingConfirmationTable(
        BaseBookingService.objects.filter(booking=booking),
        order_by=('datetime_from', 'time', 'datetime_to'))
    return table


@register.simple_tag
def quoteconfirmation_table(quote):
    table = QuoteConfirmationTable(
        QuoteService.objects.filter(quote=quote),
        order_by=('datetime_from', 'time', 'datetime_to'))
    return table


@register.simple_tag
def booking_services_summary_table(booking, request):
    b_id = request.GET.get('booking')
    if booking:
        table = BookingServiceSummaryTable(
            BaseBookingService.objects.filter(booking=booking),
            order_by=('datetime_from', 'time', 'datetime_to'))
    elif b_id:
        booking = Booking.objects.get(id=b_id)
        table = BookingServiceSummaryTable(
            BaseBookingService.objects.filter(booking=booking),
            order_by=('datetime_from', 'time', 'datetime_to'))
    else:
        table = BookingServiceSummaryTable(
            BaseBookingService.objects.none())
    return table


@register.simple_tag
def vouchers_table(booking):
    table = BookingVouchersTable(
        BaseBookingService.objects.filter(booking=booking).exclude(status=SERVICE_STATUS_CANCELLED),
        order_by=('datetime_from', 'time', 'datetime_to'))
    return table


@register.simple_tag
def bookingservice_update_table(services):
    table = BookingServiceUpdateTable(
        services,
        order_by=('datetime_from', 'time', 'datetime_to'))
    return table


@register.simple_tag
def add_pax_bookingservices_table(services):
    table = AddPaxBookingServicesTable(
        services,
        order_by=('datetime_from', 'time', 'datetime_to'))
    return table


@register.simple_tag
def booking_pax_table(booking):
    """ Gives a table object with rooming list"""
    return BookingPaxTable(booking.rooming_list.all())


@register.simple_tag
def bookingextrapackage_services_summary_table(bookingpackage, request):
    bp_id = request.GET.get('booking_package')
    if bookingpackage:
        table = BookingExtraPackageServiceSummaryTable(
            bookingpackage.booking_package_services.all(),
            order_by=('datetime_from', 'time', 'datetime_to'))
    elif bp_id:
        bookingpackage = BookingExtraPackage.objects.get(id=bp_id)
        table = BookingExtraPackageServiceSummaryTable(
            bookingpackage.booking_package_services.all(),
            order_by=('datetime_from', 'time', 'datetime_to'))
    else:
        table = BookingServiceSummaryTable(
            BaseBookingService.objects.none())
    return table


@register.inclusion_tag('booking/emails/provider_service.html')
def render_service(booking_service, provider=None):
    """
    Renders some html into provider emails depending on
    booking_service type
    """
    bs = None
    c = {}
    if booking_service.service_type == 'T':
        # Transfer service
        if hasattr(booking_service, 'booking_package'):
            bs = BookingProvidedTransfer.objects.get(id=booking_service.id)
        else:
            bs = BookingProvidedTransfer.objects.get(id=booking_service.id)
    elif booking_service.service_type == 'A':
        # Accomodation service
        if hasattr(booking_service, 'booking_package'):
            bs = BookingProvidedAllotment.objects.get(id=booking_service.id)
        else:
            bs = BookingProvidedAllotment.objects.get(id=booking_service.id)
    elif booking_service.service_type == 'E':
        # Extra Service
        if hasattr(booking_service, 'booking_package'):
            bs = BookingProvidedExtra.objects.get(id=booking_service.id)
        else:
            bs = BookingProvidedExtra.objects.get(id=booking_service.id)
    elif booking_service.service_type == 'P':
        # Package Service
        bs = BookingExtraPackage.objects.get(id=booking_service.id)
    c.update({'bs': bs})
    if provider:
        c.update({'provider': provider})
    return c


@register.inclusion_tag('booking/emails/confirmation_service.html')
def render_confirmed_service(booking_service):
    """
    Renders some html into Confirmation emails depending on
    booking_service type
    """
    if booking_service.service_type == 'T':
        # Transfer service
        bs = BookingProvidedTransfer.objects.get(id=booking_service.id)
    elif booking_service.service_type == 'A':
        # Accomodation service
        bs = BookingProvidedAllotment.objects.get(id=booking_service.id)
    elif booking_service.service_type == 'E':
        # Extra Service
        bs = BookingProvidedExtra.objects.get(id=booking_service.id)
    elif booking_service.service_type == 'P':
        # Package Service
        bs = BookingExtraPackage.objects.get(id=booking_service.id)

    return {
        'bs': bs,
    }


@register.simple_tag
def get_distribution(booking_service):
    rooms = BookingServices.find_groups(
        booking_service=booking_service,
        service=booking_service.service,
        for_cost=True)
    dist = ''
    room_count = {
        '10': 0,  # SGL counter
        '20': 0,  # DBL counter
        '30': 0,  # TPL counter
        '21': 0,  # DBL+1Child
        '22': 0,  # DBL+2Child
        '31': 0,  # TPL+1Child
    }
    room_types = {
        '10': 'SGL',
        '20': 'DBL',
        '30': 'TPL',
        '21': 'DBL&1Chld',
        '22': 'DBL&2Chld',
        '31': 'TPL&1Chld',
    }
    for room in rooms:
        try:
            room_count['%d%d' % (room[0], room[1])] += 1
        except KeyError:
            # unknown room type. skip
            pass
    for k in room_count.keys():
        if room_count[k]:
            if dist:
                dist += ' + '
            dist += '%d %s' % (room_count[k], room_types[k])
    dist += ' ({} {})'.format(booking_service.room_type,
                              booking_service.board_type)
    return dist


@register.simple_tag
def quotebookdetail_table(quote_service):
    table = NewQuoteServiceBookDetailTable(
        quote_service.quotebookdetail_set.all(),
        order_by=('datetime_from', 'time'))
    return table


@register.simple_tag
def bookingbookdetail_table(booking_service):
    table = BookingBookDetailTable(
        booking_service.bookingbookdetail_booking_service.all(),
        order_by=('datetime_from', 'time'))
    return table
