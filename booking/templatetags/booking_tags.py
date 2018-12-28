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
        0: 0,
        1: 0,
        2: 0,
        3: 0
    }
    for room in rooms:
        room_count[room[0]] += 1
    if room_count[1]:
        dist += '%d SGL' % room_count[1]
    if room_count[2]:
        if dist:
            dist += ' + '
        dist += '%d DBL' % room_count[2]
    if room_count[3]:
        if dist:
            dist += ' + '
        dist += '%d TPL' % room_count[3]
    if dist:
        dist += ' %s (%s)' % (booking_service.room_type,
                              booking_service.board_type)
    return dist
