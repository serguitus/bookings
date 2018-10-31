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
from django.utils.functional import curry

from django_tables2 import RequestConfig

from booking.forms import (
    OrderForm, OrderAllotmentForm, OrderTransferForm, OrderExtraForm,
    OrderAllotmentInlineForm, OrderTransferInlineForm, OrderExtraInlineForm,
    BookingForm, BookingAllotmentForm, BookingTransferForm, BookingExtraForm,)
from booking.models import (
    Order,
    OrderPaxVariant,
    OrderAllotment, OrderTransfer, OrderExtra,
    Booking,
    BookingPax,
    BookingServicePax,
    BookingAllotment,
    BookingTransfer,
    BookingExtra,
)

from common.filters import TextFilter
from common.sites import CommonStackedInline, CommonTabularInline
from functools import update_wrapper, partial

from reservas.admin import bookings_site


MENU_LABEL_ORDER = 'Order'

MENU_LABEL_BOOKING = 'Booking'
MENU_LABEL_BOOKING_SERVICES = 'Services By Type'


# Starts Order Section

class OrderPaxVariantInline(CommonStackedInline):
    model = OrderPaxVariant
    extra = 1
    fields = ['pax_quantity',]
    verbose_name_plural = 'Paxes Variants'


class OrderAllotmentInLine(CommonStackedInline):
    model = OrderAllotment
    extra = 1
    fields = [
        ('service', 'status'), ('datetime_from', 'datetime_to'),
        ('room_type', 'board_type'), 'provider']
    form = OrderAllotmentInlineForm


class OrderTransferInLine(CommonStackedInline):
    model = OrderTransfer
    extra = 1
    fields = [
        ('service', 'status'), ('datetime_from', 'datetime_to'),
        ('location_from', 'location_to'), 'provider']
    form = OrderTransferInlineForm


class OrderExtraInLine(CommonStackedInline):
    model = OrderExtra
    extra = 1
    fields = [
        ('service', 'status'), ('datetime_from', 'datetime_to'),
        'parameter', 'provider']
    form = OrderExtraInlineForm


class OrderSiteModel(SiteModel):
    model_order = 510
    menu_label = MENU_LABEL_ORDER

    fields = ('reference', 'agency', 'date_from', 'date_to',
              'status', 'currency',)
    list_display = ('reference', 'agency', 'date_from',
                    'date_to', 'status', 'currency',)
    top_filters = ('reference', 'date_from', 'status')
    ordering = ('reference',)
    readonly_fields = ('date_from', 'date_to', 'status',)
    details_template = 'booking/order_details.html'
    inlines = [
        OrderPaxVariantInline, OrderAllotmentInLine, OrderTransferInLine, OrderExtraInLine]
    form = OrderForm


class OrderAllotmentSiteModel(SiteModel):
    model_order = 520
    menu_label = MENU_LABEL_ORDER

    fields = ('order', 'service', 'datetime_from', 'datetime_to', 'status',
              'cost_amount', 'price_amount', 'room_type', 'board_type',
              'provider', 'id')
    list_display = ('order', 'service', 'datetime_from', 'datetime_to',
                    'status',)
    list_filter = ('service', 'datetime_from', 'datetime_to', 'status',)
    search_fields = ['order__reference', ]
    ordering = ('order__reference', 'service__name',)
    form = OrderAllotmentForm


class OrderTransferSiteModel(SiteModel):
    model_order = 530
    menu_label = MENU_LABEL_ORDER

    fields = ('order', 'service',
              'location_from', 'location_to',
              'datetime_from', 'datetime_to', 'status',
              'cost_amount', 'price_amount', 'provider', 'id')
    list_display = ('order', 'name',
                    'datetime_from', 'datetime_to', 'status',)
    list_filter = ('service', 'datetime_from', 'datetime_to', 'status',)
    search_fields = ['order__reference',]
    ordering = ('order__reference', 'service__name',)
    form = OrderTransferForm


class OrderExtraSiteModel(SiteModel):
    model_order = 540
    menu_label = MENU_LABEL_ORDER

    fields = ('order', 'service', 'parameter',
              'datetime_from', 'datetime_to', 'status', 'provider', 'id')
    list_display = ('order', 'service', 'parameter', 'datetime_from', 'datetime_to', 'status',)
    list_filter = ('service', 'datetime_from', 'status',)
    search_fields = ('order__reference',)
    ordering = ('order__reference', 'service__name',)
    form = OrderExtraForm


# Starts Booking Section

class BookingPaxInline(TabularInline):
    model = BookingPax
    fields = ['pax_name', 'pax_group', 'pax_age']
    verbose_name_plural = 'Rooming List'
    extra = 0


class BookingServicePaxInline(TabularInline):
    model = BookingServicePax
    fields = ['booking_pax', 'group']
    verbose_name_plural = 'Service Rooming List'
    extra = 1

    def get_formset(self, request, obj=None, **kwargs):
        initial = []
        if request.method == "GET" and obj:
            saved = BookingServicePax.objects.filter(booking_service=obj.id)
            if not saved:
                for bp in BookingPax.objects.filter(booking=obj.booking):
                    new_pax = {'booking_pax': bp.id,
                               'group': bp.pax_group}
                    initial.append(new_pax)
        formset = super(BookingServicePaxInline, self).get_formset(request, obj, **kwargs)
        formset.__init__ = curry(formset.__init__, initial=initial)
        return formset

class BookingAllotmentInLine(CommonTabularInline):
    model = BookingAllotment
    extra = 0
    fields = [('service', 'status'), ('datetime_from', 'datetime_to'),
              ('room_type', 'board_type'), 'provider']


class BookingTransferInLine(CommonTabularInline):
    model = BookingTransfer
    extra = 0
    fields = [('service', 'status'), ('datetime_from', 'datetime_to'),
              ('location_from', 'location_to'),
              ('quantity', 'provider')]


class BookingExtraInLine(CommonTabularInline):
    model = BookingExtra
    extra = 0
    fields = [('service', 'status'), ('datetime_from', 'datetime_to'),
              ('quantity', 'parameter'), 'provider']


class BookingSiteModel(SiteModel):
    model_order = 1110
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
    model_order = 1210
    menu_label = MENU_LABEL_BOOKING
    menu_group = MENU_LABEL_BOOKING_SERVICES

    fields = ('booking', ('service', 'status'), ('datetime_from', 'datetime_to'),
              ('room_type', 'board_type'), 'cost_amount', 'price_amount',
              'provider', 'id')
    list_display = ('booking', 'service', 'datetime_from', 'datetime_to',
                    'status',)
    list_filter = ('service', 'datetime_from', 'datetime_to', 'status',)
    search_fields = ['booking__reference', ]
    ordering = ('booking__reference', 'service__name',)
    form = BookingAllotmentForm
    inlines = [BookingServicePaxInline]


class BookingTransferSiteModel(SiteModel):
    model_order = 1220
    menu_label = MENU_LABEL_BOOKING
    menu_group = MENU_LABEL_BOOKING_SERVICES

    fields = ('booking', ('service', 'status'),
              ('datetime_from', 'datetime_to'),
              ('location_from', 'location_to'),
              'cost_amount', 'price_amount', 'provider', 'id')
    list_display = ('booking', 'name',
                    'datetime_from', 'datetime_to', 'status',)
    list_filter = ('service', 'datetime_from', 'datetime_to', 'status',)
    search_fields = ['booking__reference',]
    ordering = ('booking__reference', 'service__name',)
    form = BookingTransferForm
    inlines = [BookingServicePaxInline]


class BookingExtraSiteModel(SiteModel):
    model_order = 1230
    menu_label = MENU_LABEL_BOOKING
    menu_group = MENU_LABEL_BOOKING_SERVICES

    fields = ('booking', ('service', 'status'),
              ('datetime_from', 'datetime_to'),
              ('quantity', 'parameter'),
              'cost_amount', 'price_amount', 'provider', 'id')
    list_display = ('booking', 'service', 'quantity', 'parameter', 'datetime_from', 'datetime_to', 'status',)
    list_filter = ('service', 'datetime_from', 'status',)
    search_fields = ('booking__reference',)
    ordering = ('booking__reference', 'service__name',)
    form = BookingExtraForm
    inlines = [BookingServicePaxInline]


# Starts Registration Section

bookings_site.register(Order, OrderSiteModel)

bookings_site.register(OrderAllotment, OrderAllotmentSiteModel)
bookings_site.register(OrderTransfer, OrderTransferSiteModel)
bookings_site.register(OrderExtra, OrderExtraSiteModel)

bookings_site.register(Booking, BookingSiteModel)

bookings_site.register(BookingAllotment, BookingAllotmentSiteModel)
bookings_site.register(BookingTransfer, BookingTransferSiteModel)
bookings_site.register(BookingExtra, BookingExtraSiteModel)
