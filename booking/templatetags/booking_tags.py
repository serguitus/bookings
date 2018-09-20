from django import template

from booking.tables import BookingServiceTable

register = template.Library()


@register.simple_tag
def bookingservices_table(booking):
    return BookingServiceTable(booking.booking_services.all())
    # table = BookingServiceTable(bs)
    # return {'table': bs}
