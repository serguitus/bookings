import django_tables2 as tables
from booking.models import Booking


class BookingTable(tables.Table):
    class Meta:
        model = Booking
        template_name = 'django_tables2/bootstrap.html'
        fields = ['reference', 'agency', 'date_from',
                  'date_to', 'cost_amount', 'price_amount']
