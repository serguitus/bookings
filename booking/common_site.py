"""
bookings site models
"""
from django.conf.urls import url
from django.shortcuts import render

from common.sites import SiteModel
from booking.models import Booking
from reservas.admin import bookings_site

MENU_LABEL_BOOKINGS = 'Reservas'


class BookingSiteModel(SiteModel):
    menu_label = MENU_LABEL_BOOKINGS
    list_display = ['reference', 'date_from', 'date_to', 'status', 'agency']
    list_filter = ['agency', 'status']
    search_fields = ['reference']
    ordering = ['date_from', 'reference']

    def get_urls(self):
        urls = super(BookingSiteModel, self).get_urls()
        other_urls = [
            url(r'^bookinglist/$', self.booking_list),
        ]
        return other_urls + urls

    def booking_list(self, request):
        """ a list of bookings with their services """
        context = {}
        context.update(self.get_model_extra_context(request))
        bookings = Booking.objects.all()
        context.update({
            'bookings': bookings,
        })
        return render(request, 'booking/booking_list.html', context)


bookings_site.register(Booking, BookingSiteModel)
