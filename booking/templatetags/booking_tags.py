from __future__ import unicode_literals
from django import template

from booking.models import (
    Booking,
    BookingService,
    BookingTransfer,
    BookingAllotment,
    BookingExtra,
    BookingPackage,
    BookingPackageTransfer,
    BookingPackageAllotment,
    BookingPackageExtra,
    BookingPackage, ProviderBookingPayment, ProviderBookingPaymentService,
)
from booking.tables import (
    PackageServiceTable,
    QuoteServiceTable, QuotePaxVariantTable,
    QuotePackageServiceTable,
    BookingServiceTable,
    BookingConfirmationTable, BookingServiceSummaryTable, BookingPaxTable,
    BookingVouchersTable,
    BookingServiceUpdateTable,
    BookingPackageServiceTable,
    BookingPackageServiceSummaryTable,
    AddPaxBookingServicesTable, ProviderBookingPaymentTable, ProviderBookingPaymentServiceTable,
    AgencyPaymentTable,
)
from booking.services import BookingServices

from finance.models import AgencyPayment

register = template.Library()


@register.simple_tag
def packageservice_table(package):
    table = PackageServiceTable(
        package.package_services.all(),
        order_by=('days_after', 'days_duration'))
    return table


@register.simple_tag
def quotepackage_table(quotepackage):
    table = QuotePackageServiceTable(
        quotepackage.quotepackage_services.all(),
        order_by=('datetime_from', 'time', 'datetime_to'))
    return table


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
        BookingService.objects.filter(booking=booking),
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
        ProviderBookingPayment.objects.filter(providerbookingpaymentservice__provider_service=service),
        order_by=('date',),
    )
    return table


@register.simple_tag
def providerbookingpaymentservice_table(payment):
    table = ProviderBookingPaymentServiceTable(
        ProviderBookingPaymentService.objects.filter(provider_payment=payment),
        order_by=('datetime_from', 'time','datetime_to',),
    )
    return table


@register.simple_tag
def bookingconfirmation_table(booking):
    table = BookingConfirmationTable(
        BookingService.objects.filter(booking=booking),
        order_by=('datetime_from', 'time', 'datetime_to'))
    return table


@register.simple_tag
def booking_services_summary_table(booking, request):
    b_id = request.GET.get('booking')
    if booking:
        table = BookingServiceSummaryTable(
            BookingService.objects.filter(booking=booking),
            order_by=('datetime_from', 'time', 'datetime_to'))
    elif b_id:
        booking = Booking.objects.get(id=b_id)
        table = BookingServiceSummaryTable(
            BookingService.objects.filter(booking=booking),
            order_by=('datetime_from', 'time', 'datetime_to'))
    else:
        table = BookingServiceSummaryTable(
            BookingService.objects.none())
    return table


@register.simple_tag
def vouchers_table(booking):
    table = BookingVouchersTable(
        BookingService.objects.filter(booking=booking),
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
def bookingpackage_table(bookingpackage):
    table = BookingPackageServiceTable(
        bookingpackage.booking_package_services.all(),
        order_by=('datetime_from', 'time', 'datetime_to'))
    return table


@register.simple_tag
def bookingpackage_services_summary_table(bookingpackage, request):
    bp_id = request.GET.get('booking_package')
    if bookingpackage:
        table = BookingPackageServiceSummaryTable(
            bookingpackage.booking_package_services.all(),
            order_by=('datetime_from', 'time', 'datetime_to'))
    elif bp_id:
        bookingpackage = BookingPackage.objects.get(id=bp_id)
        table = BookingPackageServiceSummaryTable(
            bookingpackage.booking_package_services.all(),
            order_by=('datetime_from', 'time', 'datetime_to'))
    else:
        table = BookingServiceSummaryTable(
            BookingService.objects.none())
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
            bs = BookingPackageTransfer.objects.get(id=booking_service.id)
        else:
            bs = BookingTransfer.objects.get(id=booking_service.id)
    elif booking_service.service_type == 'A':
        # Accomodation service
        if hasattr(booking_service, 'booking_package'):
            bs = BookingPackageAllotment.objects.get(id=booking_service.id)
        else:
            bs = BookingAllotment.objects.get(id=booking_service.id)
    elif booking_service.service_type == 'E':
        # Extra Service
        if hasattr(booking_service, 'booking_package'):
            bs = BookingPackageExtra.objects.get(id=booking_service.id)
        else:
            bs = BookingExtra.objects.get(id=booking_service.id)
    elif booking_service.service_type == 'P':
        # Package Service
        bs = BookingPackage.objects.get(id=booking_service.id)
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
        bs = BookingTransfer.objects.get(id=booking_service.id)
    elif booking_service.service_type == 'A':
        # Accomodation service
        bs = BookingAllotment.objects.get(id=booking_service.id)
    elif booking_service.service_type == 'E':
        # Extra Service
        bs = BookingExtra.objects.get(id=booking_service.id)
    elif booking_service.service_type == 'P':
        # Package Service
        bs = BookingPackage.objects.get(id=booking_service.id)

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
