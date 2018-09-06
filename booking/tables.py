import django_tables2 as tables
from booking.models import Booking

class BookingTable(tables.Table):
    class Meta:
        model = Booking
        template_name = 'django_tables2/bootstrap.html'
