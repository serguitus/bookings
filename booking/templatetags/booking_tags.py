from django import template

from booking.models import (
    BookingTransfer,
    BookingAllotment,
    BookingExtra)
from booking.tables import (
    QuoteServiceTable, QuotePaxVariantTable, BookingServiceTable, BookingPaxTable)

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
        html = 'transfer_service.html'
        bs = BookingTransfer.objects.get(id=booking_service.id)
    elif booking_service.service_type == 'A':
        # Accomodation service
        html = 'allotment_service.html'
        bs = BookingAllotment.objects.get(id=booking_service.id)
    else:
        # Extra Service
        html = 'extra_service.html'
        bs = BookingExtra.objects.get(id=booking_service.id)

    return {
        'template': 'booking/emails/%s' % html,
        'bs': bs,
    }
