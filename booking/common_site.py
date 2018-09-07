from common.sites import SiteModel

from django.conf.urls import url
from django.contrib import admin, messages
from django.contrib.admin.options import (csrf_protect_m,
                                          IS_POPUP_VAR,
                                          TO_FIELD_VAR)
from django.contrib.admin import helpers
from django.contrib.admin.checks import ModelAdminChecks
from django.contrib.admin.utils import unquote
from django.core import checks
from django.core.exceptions import (FieldDoesNotExist,
                                    ValidationError,
                                    PermissionDenied)
from django.db import router, transaction
from django import forms
from django.forms.models import modelformset_factory
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.template.response import SimpleTemplateResponse, TemplateResponse
from django.utils.encoding import force_text
from django.utils.translation import ugettext as _, ungettext

from django_tables2 import RequestConfig

from booking.models import (
    Booking,
    BookingAllotment,
    BookingTransfer,
    BookingExtra,
)
from booking.tables import BookingTable

from functools import update_wrapper, partial

from reservas.admin import bookings_site


MENU_LABEL_BOOKING = 'Booking'
MENU_LABEL_BOOKING_SERVICES = 'Services By Type'


class BookingSiteModel(SiteModel):
    model_order = 1010
    menu_label = MENU_LABEL_BOOKING

    fields = ('reference',)
    list_display = ('reference',)
    list_filter = ('reference',)
    search_fields = ['reference', ]
    ordering = ('reference',)

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
        bookings = BookingTable(Booking.objects.all())
        RequestConfig(request).configure(bookings)
        context.update({
            'bookings': bookings,
        })
        return render(request, 'booking/booking_list.html', context)


class BookingAllotmentSiteModel(SiteModel):
    model_order = 1110
    menu_label = MENU_LABEL_BOOKING
    menu_group = MENU_LABEL_BOOKING_SERVICES

    fields = ('booking',)
    list_display = ('booking',)
    list_filter = ('booking',)
    search_fields = ['booking__reference', ]
    ordering = ('booking__reference', 'service__name',)


class BookingTransferSiteModel(SiteModel):
    model_order = 1120
    menu_label = MENU_LABEL_BOOKING
    menu_group = MENU_LABEL_BOOKING_SERVICES

    fields = ('booking',)
    list_display = ('booking',)
    list_filter = ('booking',)
    search_fields = ['booking__reference', ]
    ordering = ('booking__reference', 'service__name',)


class BookingExtraSiteModel(SiteModel):
    model_order = 1130
    menu_label = MENU_LABEL_BOOKING
    menu_group = MENU_LABEL_BOOKING_SERVICES

    fields = ('booking',)
    list_display = ('booking',)
    list_filter = ('booking',)
    search_fields = ['booking__reference', ]
    ordering = ('booking__reference', 'service__name',)


bookings_site.register(Booking, BookingSiteModel)

bookings_site.register(BookingAllotment, BookingAllotmentSiteModel)
bookings_site.register(BookingTransfer, BookingTransferSiteModel)
bookings_site.register(BookingExtra, BookingExtraSiteModel)
