"""
bookings site models
"""

from booking.models import Booking
from common.sites import SiteModel
from reservas.admin import bookings_site

MENU_LABEL_BOOKINGS = 'Reservas'


class BookingSiteModel(SiteModel):
    menu_label = MENU_LABEL_BOOKINGS
    list_display = ['reference', 'date_from', 'date_to', 'status', 'agency']
    list_filter = ['agency', 'status']
    search_fields = ['reference']
    ordering = ['date_from', 'reference']


bookings_site.register(Booking, BookingSiteModel)
