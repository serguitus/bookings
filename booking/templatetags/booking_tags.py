from __future__ import unicode_literals
from django import template

from booking.models import (
    BookingTransfer,
    BookingAllotment,
    BookingExtra,
    BookingPackage)
from booking.tables import (
    PackageServiceTable,
    QuoteServiceTable, QuotePaxVariantTable,
    QuotePackageServiceTable,
    BookingServiceTable, BookingPaxTable,
    BookingVouchersTable,
    BookingServiceUpdateTable,
    BookingPackageServiceTable)
from booking.services import BookingServices

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
        order_by=('datetime_from', 'datetime_to'))
    return table


@register.simple_tag
def quoteservice_table(quote):
    table = QuoteServiceTable(
        quote.quote_services.all(),
        order_by=('datetime_from', 'datetime_to'))
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
        booking.booking_services.all(),
        order_by=('datetime_from', 'datetime_to'))
    return table
    # table = BookingServiceTable(bs)
    # return {'table': bs}


@register.simple_tag
def vouchers_table(booking):
    table = BookingVouchersTable(
        booking.booking_services.all(),
        order_by=('datetime_from', 'datetime_to'))
    return table


@register.simple_tag
def bookingservice_update_table(services):
    table = BookingServiceUpdateTable(
        services,
        order_by=('datetime_from', 'datetime_to'))
    return table


@register.simple_tag
def booking_pax_table(booking):
    """ Gives a table object with rooming list"""
    return BookingPaxTable(booking.rooming_list.all())


@register.simple_tag
def bookingpackage_table(bookingpackage):
    table = BookingPackageServiceTable(
        bookingpackage.booking_package_services.all(),
        order_by=('datetime_from', 'datetime_to'))
    return table


@register.inclusion_tag('booking/emails/provider_service.html')
def render_service(booking_service):
    """
    Renders some html into provider emails depending on
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
        booking_service=booking_service, service=booking_service.service, for_cost=True)
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
        '21': 'DBL+1Chld',
        '22': 'DBL+2Chld',
        '31': 'TPL+1Chld',
    }
    for room in rooms:
        room_count['%d%d' % (room[0], room[1])] += 1
    for k in room_count.keys():
        if room_count[k]:
            if dist:
                dist += ' + '
            dist += '%d %s' % (room_count[k], room_types[k])
    return dist
