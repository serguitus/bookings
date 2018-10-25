from common.sites import SiteModel

from django.conf.urls import url
from django.contrib import admin, messages
from django.contrib.admin.options import (csrf_protect_m,
                                          IS_POPUP_VAR,
                                          TO_FIELD_VAR)
from django.contrib.admin import TabularInline
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

from booking.forms import BookingForm, BookingAllotmentForm, BookingTransferForm, BookingExtraForm
from booking.models import (
    Booking,
    BookingPax,
    BookingServicePax,
    BookingAllotment,
    BookingTransfer,
    BookingExtra,
)

from common.filters import TextFilter
from common.sites import CommonTabularInline
from functools import update_wrapper, partial

from reservas.admin import bookings_site


MENU_LABEL_BOOKING = 'Booking'
MENU_LABEL_BOOKING_SERVICES = 'Services By Type'


class BookingPaxInline(TabularInline):
    model = BookingPax
    fields = ['pax_name', 'pax_group', 'pax_age']
    verbose_name_plural = 'Rooming List'


class BookingServicePaxInline(TabularInline):
    model = BookingServicePax
    fields = ['booking_pax', 'group']
    verbose_name_plural = 'Service Rooming List'


class BookingAllotmentInLine(CommonTabularInline):
    model = BookingAllotment
    extra = 1
    fields = ['service', 'datetime_from', 'datetime_to',
              'provider', 'room_type', 'board_type', 'status']


class BookingTransferInLine(CommonTabularInline):
    model = BookingTransfer
    extra = 1
    fields = ['service', 'datetime_from', 'datetime_to',
              'location_from', 'location_to', 'quantity',
              'provider', 'status']


class BookingExtraInLine(CommonTabularInline):
    model = BookingExtra
    extra = 1
    fields = ['service', 'datetime_from', 'datetime_to',
              'provider', 'quantity', 'parameter', 'status']


class BookingSiteModel(SiteModel):
    model_order = 1010
    menu_label = MENU_LABEL_BOOKING

    fields = ('reference', 'agency', 'date_from', 'date_to',
              'status', 'currency', 'cost_amount',
              'price_amount',)
    list_display = ('reference', 'agency', 'date_from',
                    'date_to', 'status', 'currency', 'cost_amount',
                    'price_amount',)
    top_filters = ('reference','date_from',)
    ordering = ('reference',)
    readonly_fields = ('status',)
    details_template = 'booking/booking_details.html'
    inlines = [BookingPaxInline, BookingAllotmentInLine,
               BookingTransferInLine, BookingExtraInLine]
    form = BookingForm

    """
    @csrf_protect_m
    def changelist_view(self, request, extra_context=None):
        # a list of bookings with their services
        context = {}
        context.update(self.get_model_extra_context(request))
        # first get the filtered list of bookings to show
        # according to page filters
        qs = Booking.objects.all().prefetch_related('booking_services')
        bookings = BookingTable(qs)
        booking_services = {}
        for booking in bookings.rows:
            booking.services = BookingServiceTable(booking.booking_services.all())
        RequestConfig(request).configure(bookings)
        context.update({
            'bookings': bookings,
            'booking_services': booking_services,
        })
        return render(request, 'booking/booking_list.html', context)
    """

class BookingAllotmentSiteModel(SiteModel):
    model_order = 1110
    menu_label = MENU_LABEL_BOOKING
    menu_group = MENU_LABEL_BOOKING_SERVICES

    fields = ('booking', 'service', 'datetime_from', 'datetime_to', 'status',
              'cost_amount', 'price_amount', 'room_type', 'board_type',)
    list_display = ('booking', 'service', 'datetime_from', 'datetime_to',
                    'status',)
    list_filter = ('service', 'datetime_from', 'datetime_to', 'status',)
    search_fields = ['booking__reference', ]
    ordering = ('booking__reference', 'service__name',)
    form = BookingAllotmentForm
    inlines = [BookingServicePaxInline]


class BookingTransferSiteModel(SiteModel):
    model_order = 1120
    menu_label = MENU_LABEL_BOOKING
    menu_group = MENU_LABEL_BOOKING_SERVICES

    fields = ('booking', 'service',
              'location_from', 'location_to',
              'datetime_from', 'datetime_to', 'status',
              'cost_amount', 'price_amount', 'provider')
    list_display = ('booking', 'name',
                    'datetime_from', 'datetime_to', 'status',)
    list_filter = ('service', 'datetime_from', 'datetime_to', 'status',)
    search_fields = ['booking__reference',]
    ordering = ('booking__reference', 'service__name',)
    form = BookingTransferForm
    inlines = [BookingServicePaxInline]


class BookingExtraSiteModel(SiteModel):
    model_order = 1130
    menu_label = MENU_LABEL_BOOKING
    menu_group = MENU_LABEL_BOOKING_SERVICES

    fields = ('booking', 'service', 'quantity', 'parameter', 'datetime_from', 'datetime_to', 'status',
        'cost_amount', 'price_amount',)
    list_display = ('booking', 'service', 'quantity', 'parameter', 'datetime_from', 'datetime_to', 'status',)
    list_filter = ('service', 'datetime_from', 'status',)
    search_fields = ('booking__reference',)
    ordering = ('booking__reference', 'service__name',)
    form = BookingExtraForm
    inlines = [BookingServicePaxInline]


bookings_site.register(Booking, BookingSiteModel)

bookings_site.register(BookingAllotment, BookingAllotmentSiteModel)
bookings_site.register(BookingTransfer, BookingTransferSiteModel)
bookings_site.register(BookingExtra, BookingExtraSiteModel)
