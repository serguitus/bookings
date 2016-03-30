from django import template

from booking.models import (
    BookingTransfer,
    BookingAllotment,
    BookingExtra)
from booking.tables import (
    QuoteServiceTable, QuotePaxVariantTable,
    BookingServiceTable, BookingPaxTable)
from booking.services import BookingService

register = template.Library()


@register.simple_tag
def quoteservices_table(quote):
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
def bookingservices_table(booking):
    table = BookingServiceTable(booking.booking_services.all(),
                                order_by=('datetime_from', 'datetime_to'))
    return table
    # table = BookingServiceTable(bs)
    # return {'table': bs}


@register.simple_tag
def booking_pax_table(booking):
    """ Gives a table object with rooming list"""
    return BookingPaxTable(booking.rooming_list.all())


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
    else:
        # Extra Service
        bs = BookingExtra.objects.get(id=booking_service.id)

    return {
        'bs': bs,
    }

@register.simple_tag
def get_distribution(booking_service):
    rooms = BookingService.find_groups(booking_service=booking_service,
                                      service=booking_service.service)
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
