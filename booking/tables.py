import django_tables2 as tables

from django.utils.html import format_html
from booking.models import Booking, BookingService, BookingPax


class BookingTable(tables.Table):
    class Meta:
        model = Booking
        template_name = 'django_tables2/bootstrap.html'
        fields = ['id', 'reference', 'agency', 'date_from',
                  'date_to', 'cost_amount', 'price_amount']

    def render_reference(self, value, record):
        return format_html('<a href="#services-list-%s" data-toggle="collapse">%s</a>' % (record.id, value))

    def before_render(self, request):
        self.columns.hide('id')


class BookingServiceTable(tables.Table):
    class Meta:
        model = BookingService
        template_name = 'booking/bookingservices_list.html'
        fields = ['name', 'datetime_from', 'datetime_to', 'cost_amount',
                  'price_amount']


class BookingPaxTable(tables.Table):
    class Meta:
        model = BookingPax
        template_name = 'booking/bookingservices_list.html'
        fields = ['pax_name', 'pax_age']
