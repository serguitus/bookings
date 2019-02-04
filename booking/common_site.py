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
from django.shortcuts import render, redirect, reverse
from django.template.response import SimpleTemplateResponse, TemplateResponse
from django.utils.encoding import force_text
# from django.utils.translation import ugettext as _, ungettext
from django.utils.functional import curry
# from django_tables2 import RequestConfig
from booking.forms import (
    QuoteForm, QuoteAllotmentForm, QuoteTransferForm, QuoteExtraForm,
    QuoteAllotmentInlineForm, QuoteTransferInlineForm, QuoteExtraInlineForm,
    BookingForm,
    BookingServicePaxInlineForm,
    BookingAllotmentInlineForm, BookingAllotmentForm,
    BookingTransferInlineForm, BookingTransferForm,
    BookingExtraInlineForm, BookingExtraForm,
)
from booking.models import (
    Quote,
    QuotePaxVariant,
    QuoteAllotment, QuoteTransfer, QuoteExtra,
    Booking,
    BookingPax,
    BookingServicePax,
    BookingAllotment,
    BookingTransfer,
    BookingExtra,
)
# from common.filters import TextFilter
from common.sites import CommonStackedInline, CommonTabularInline
# from functools import update_wrapper, partial

from reservas.admin import bookings_site


MENU_LABEL_QUOTE = 'Quote'

MENU_LABEL_BOOKING = 'Booking'
MENU_LABEL_BOOKING_SERVICES = 'Services By Type'


# Starts Quote Section

class QuotePaxVariantInline(CommonStackedInline):
    model = QuotePaxVariant
    extra = 0
    fields = [
        'pax_quantity',
        ('cost_single_amount', 'price_single_amount'),
        ('cost_double_amount', 'price_double_amount'),
        ('cost_triple_amount', 'price_triple_amount')]
    verbose_name_plural = 'Paxes Variants'


class QuoteAllotmentInLine(CommonStackedInline):
    model = QuoteAllotment
    extra = 0
    fields = [
        ('service', 'status'), ('datetime_from', 'datetime_to'),
        ('room_type', 'board_type'), 'provider']
    form = QuoteAllotmentInlineForm
    template = 'booking/tabular.html'


class QuoteTransferInLine(CommonStackedInline):
    model = QuoteTransfer
    extra = 0
    fields = [
        ('service', 'status'), ('datetime_from', 'datetime_to'),
        ('location_from', 'location_to'), 'provider']
    form = QuoteTransferInlineForm


class QuoteExtraInLine(CommonStackedInline):
    model = QuoteExtra
    extra = 0
    fields = [
        ('service', 'status'), ('datetime_from', 'datetime_to'),
        'parameter', 'provider']
    form = QuoteExtraInlineForm


class QuoteSiteModel(SiteModel):
    model_order = 510
    menu_label = MENU_LABEL_QUOTE

    recent_allowed = True
    fields = (
        ('reference', 'agency'),
        ('status', 'currency'),
        ('date_from', 'date_to'),
    )
    list_display = ('reference', 'agency', 'date_from',
                    'date_to', 'status', 'currency',)
    top_filters = ('reference', 'date_from', 'status')
    ordering = ('reference',)
    readonly_fields = ('date_from', 'date_to',)
    details_template = 'booking/quote_details.html'
    inlines = [
        QuotePaxVariantInline, QuoteAllotmentInLine,
        QuoteTransferInLine, QuoteExtraInLine]
    form = QuoteForm
    change_form_template = 'booking/quote_change_form.html'


class QuoteAllotmentSiteModel(SiteModel):
    model_order = 520
    menu_label = MENU_LABEL_QUOTE

    fields = ('quote', 'service', 'datetime_from', 'datetime_to', 'status',
              # 'cost_amount', 'price_amount',
              'room_type', 'board_type',
              'provider', 'id')
    list_display = ('quote', 'service', 'datetime_from', 'datetime_to',
                    'status',)
    top_filters = ('service', 'quote__reference', 'datetime_from', 'status',)
    ordering = ('quote__reference', 'service__name',)
    form = QuoteAllotmentForm


class QuoteTransferSiteModel(SiteModel):
    model_order = 530
    menu_label = MENU_LABEL_QUOTE

    fields = ('quote', 'service',
              'location_from', 'location_to',
              'datetime_from', 'datetime_to', 'status',
              'cost_amount', 'price_amount', 'provider', 'id')
    list_display = ('quote', 'name',
                    'datetime_from', 'datetime_to', 'status',)
    top_filters = ('service', 'quote__reference', 'datetime_from', 'status',)
    ordering = ('quote__reference', 'service__name',)
    form = QuoteTransferForm


class QuoteExtraSiteModel(SiteModel):
    model_order = 540
    menu_label = MENU_LABEL_QUOTE

    fields = (
        'quote',
        ('service', 'status'),
        ('datetime_from', 'datetime_to'),
         'parameter', 'provider', 'id')
    list_display = ('quote', 'service', 'parameter', 'datetime_from', 'datetime_to', 'status',)
    top_filters = ('service', 'quote__reference', 'datetime_from', 'status',)
    ordering = ('quote__reference', 'service__name',)
    form = QuoteExtraForm


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
    form = BookingServicePaxInlineForm

    def get_formset(self, request, obj=None, **kwargs):
        initial = []
        if request.method == "GET" and obj:
            saved = BookingServicePax.objects.filter(booking_service=obj.id)
            if not saved:
                rooming = BookingPax.objects.filter(booking=obj.booking)
                self.extra = len(rooming)
                for bp in rooming:
                    new_pax = {'booking_pax': bp.id,
                               'group': bp.pax_group}
                    initial.append(new_pax)
        formset = super(BookingServicePaxInline, self).get_formset(request, obj, **kwargs)
        formset.__init__ = curry(formset.__init__, initial=initial)
        return formset


class BookingAllotmentInLine(CommonTabularInline):
    model = BookingAllotment
    extra = 0
    fields = [('service', 'status', 'conf_number'), ('datetime_from', 'datetime_to'),
              ('room_type', 'board_type'), 'provider']
    form = BookingAllotmentInlineForm


class BookingTransferInLine(CommonTabularInline):
    model = BookingTransfer
    extra = 0
    fields = [('service', 'status', 'conf_number'), ('datetime_from', 'datetime_to', 'time'),
              ('location_from', 'location_to'),
              ('quantity', 'provider')]
    form = BookingTransferInlineForm


class BookingExtraInLine(CommonTabularInline):
    model = BookingExtra
    extra = 0
    fields = [('service', 'status', 'conf_number'), ('datetime_from', 'datetime_to', 'time'),
              ('quantity', 'parameter'), 'provider']
    form = BookingExtraInlineForm


class BookingSiteModel(SiteModel):
    model_order = 1110
    menu_label = MENU_LABEL_BOOKING

    recent_allowed = True
    fields = (('name', 'reference'), 'agency', 'status')
    list_display = ('name', 'reference', 'agency', 'date_from',
                    'date_to', 'status', 'currency', 'cost_amount',
                    'price_amount',)
    top_filters = (('name', 'Booking Name'), 'reference', 'date_from', )
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

    fields = ('booking', ('service', 'status', 'conf_number'),
              ('datetime_from', 'datetime_to'),
              ('room_type', 'board_type'),
              'cost_amount', 'price_amount', 'provider', 'id')
    list_display = ('booking', 'service', 'datetime_from',
                    'datetime_to', 'status',)
    top_filters = (('booking__name', 'Booking'),
                   ('name', 'Service'),
                   'booking__reference', 'conf_number',
                   'datetime_from', 'status')
    ordering = ('booking__reference', 'service__name',)
    form = BookingAllotmentForm
    change_form_template = 'booking/bookingservices_change_form.html'
    inlines = [BookingServicePaxInline]

    def response_add(self, request, obj, post_url_continue=None):
        return redirect(reverse('common:booking_booking_change',
                                args=[obj.booking.pk]))

    def response_change(self, request, obj, post_url_continue=None):
        return redirect(reverse('common:booking_booking_change',
                                args=[obj.booking.pk]))


class BookingTransferSiteModel(SiteModel):
    model_order = 1220
    menu_label = MENU_LABEL_BOOKING
    menu_group = MENU_LABEL_BOOKING_SERVICES

    fields = ('booking', ('service', 'status', 'conf_number'),
              ('datetime_from', 'datetime_to', 'time'),
              ('location_from', 'pickup'),
              ('location_to', 'dropoff'),
              'cost_amount', 'price_amount', 'provider', 'id')
    list_display = ('booking', 'name',
                    'datetime_from', 'datetime_to', 'time', 'status')
    top_filters = ('booking__name', 'service', 'booking__reference',
                   'datetime_from', 'status',)
    ordering = ('booking__reference', 'service__name',)
    form = BookingTransferForm
    change_form_template = 'booking/bookingservices_change_form.html'
    inlines = [BookingServicePaxInline]

    def response_add(self, request, obj, post_url_continue=None):
        return redirect(reverse('common:booking_booking_change', args=[1]))

    def response_change(self, request, obj, post_url_continue=None):
        return redirect(reverse('common:booking_booking_change', args=[1]))


class BookingExtraSiteModel(SiteModel):
    model_order = 1230
    menu_label = MENU_LABEL_BOOKING
    menu_group = MENU_LABEL_BOOKING_SERVICES

    fields = ['booking', ('service', 'status', 'conf_number'),
              ('datetime_from', 'datetime_to', 'time'),
              ('quantity', 'parameter'),
              'cost_amount', 'price_amount', 'provider', 'id']
    list_display = ('booking', 'name', 'quantity', 'parameter',
                    'datetime_from', 'datetime_to', 'time', 'status',)
    top_filters = ('booking__name', 'service', 'booking__reference',
                   'datetime_from','status',)
    ordering = ('booking__reference', 'service__name',)
    form = BookingExtraForm
    change_form_template = 'booking/bookingservices_change_form.html'
    inlines = [BookingServicePaxInline]

    def response_add(self, request, obj, post_url_continue=None):
        return redirect(reverse('common:booking_booking_change', args=[1]))

    def response_change(self, request, obj, post_url_continue=None):
        return redirect(reverse('common:booking_booking_change', args=[1]))


# Starts Registration Section

bookings_site.register(Quote, QuoteSiteModel)

bookings_site.register(QuoteAllotment, QuoteAllotmentSiteModel)
bookings_site.register(QuoteTransfer, QuoteTransferSiteModel)
bookings_site.register(QuoteExtra, QuoteExtraSiteModel)

bookings_site.register(Booking, BookingSiteModel)

bookings_site.register(BookingAllotment, BookingAllotmentSiteModel)
bookings_site.register(BookingTransfer, BookingTransferSiteModel)
bookings_site.register(BookingExtra, BookingExtraSiteModel)
