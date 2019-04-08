# -*- coding: utf-8 -*-
from __future__ import unicode_literals
try:
    import cStringIO as StringIO
except ImportError:
    from _io import StringIO
from xhtml2pdf import pisa

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
from django.http import HttpResponse
from django.shortcuts import render, redirect, reverse
from django.template.response import SimpleTemplateResponse, TemplateResponse
from django.template.loader import get_template
from django.utils.encoding import force_text
# from django.utils.translation import ugettext as _, ungettext
from django.utils.functional import curry
# from django_tables2 import RequestConfig

from finance.top_filters import AgencyTopFilter

from booking.forms import (
    PackageAllotmentInlineForm, PackageTransferInlineForm, PackageExtraInlineForm,
    PackageAllotmentForm, PackageTransferForm, PackageExtraForm, AgencyPackageServiceForm,
    QuoteForm, QuoteAllotmentForm, QuoteTransferForm, QuoteExtraForm, QuotePackageForm,
    QuoteAllotmentInlineForm, QuoteTransferInlineForm,
    QuoteExtraInlineForm, QuotePackageInlineForm,
    QuotePackageAllotmentInlineForm, QuotePackageTransferInlineForm, QuotePackageExtraInlineForm,
    QuotePackageAllotmentForm, QuotePackageTransferForm, QuotePackageExtraForm,
    BookingForm,
    BookingServicePaxInlineForm,
    BookingAllotmentInlineForm, BookingAllotmentForm,
    BookingTransferInlineForm, BookingTransferForm,
    BookingExtraInlineForm, BookingExtraForm,
    BookingPackageInlineForm, BookingPackageForm,
    BookingPackageAllotmentInlineForm, BookingPackageAllotmentForm,
    BookingPackageTransferInlineForm, BookingPackageTransferForm,
    BookingPackageExtraInlineForm, BookingPackageExtraForm,
    VouchersConfigForm,
)
from booking.models import (
    Package, PackageAllotment, PackageTransfer, PackageExtra,
    AgencyPackageService, AgencyPackageDetail,
    Quote,
    QuotePaxVariant,
    QuoteAllotment, QuoteTransfer, QuoteExtra, QuotePackage,
    QuotePackageAllotment, QuotePackageTransfer, QuotePackageExtra,
    Booking,
    BookingPax,
    BookingServicePax,
    BookingService,
    BookingAllotment, BookingTransfer, BookingExtra, BookingPackage,
    BookingPackageAllotment, BookingPackageTransfer, BookingPackageExtra,
)
from booking.services import BookingServices
from booking.top_filters import DateTopFilter, PackageTopFilter, CancelledTopFilter

# from common.filters import TextFilter
from common.sites import CommonStackedInline, CommonTabularInline
# from functools import update_wrapper, partial

from reservas.admin import bookings_site


MENU_LABEL_CONFIG_BASIC = 'Configuration'
MENU_LABEL_PACKAGE = 'Package'
MENU_LABEL_QUOTE = 'Quote'
MENU_LABEL_BOOKING = 'Booking'
MENU_GROUP_LABEL_SERVICES = 'Services By Type'
MENU_GROUP_LABEL_PACKAGE_SERVICES = 'Package Services By Type'

# Starts Package Section


class PackageAllotmentInLine(CommonStackedInline):
    model = PackageAllotment
    extra = 0
    fields = [
        ('service', 'room_type', 'board_type'),
        ('days_after', 'days_duration', 'provider')]
    ordering = ['days_after']
    form = PackageAllotmentInlineForm


class PackageTransferInLine(CommonStackedInline):
    model = PackageTransfer
    extra = 0
    fields = [
        ('service', 'time'),
        ('location_from', 'pickup', 'schedule_from'),
        ('place_from'),
        ('location_to', 'dropoff', 'schedule_to'),
        ('place_to'),
        ('days_after', 'days_duration', 'provider')]
    ordering = ['days_after']
    form = PackageTransferInlineForm


class PackageExtraInLine(CommonStackedInline):
    model = PackageExtra
    extra = 0
    fields = [
        ('service', 'time'),
        ('addon', 'quantity', 'parameter'),
        ('days_after', 'days_duration', 'provider')]
    ordering = ['days_after']
    form = PackageExtraInlineForm


class PackageSiteModel(SiteModel):
    model_order = 1010
    menu_label = MENU_LABEL_PACKAGE
    fields = (
        ('name', 'enabled'), 
        ('amounts_type', 'has_pax_range'),
    )
    list_display = ('name', 'amounts_type', 'has_pax_range', 'enabled')
    list_editable = ('enabled',)
    top_filters = ('name', 'amounts_type', 'has_pax_range', 'enabled')
    ordering = ('enabled', 'name',)
    details_template = 'booking/package_details.html'
    inlines = [
        PackageAllotmentInLine, PackageTransferInLine, PackageExtraInLine]


class PackageAllotmentSiteModel(SiteModel):
    model_order = 1020
    menu_label = MENU_LABEL_PACKAGE
    menu_group = MENU_GROUP_LABEL_SERVICES

    fields = (
        'package', ('service'),
        ('days_after', 'days_duration'),
        ('room_type', 'board_type'), 'provider', 'id')
    list_display = ('package', 'service', 'days_after', 'days_duration',)
    top_filters = ('package__name', 'service',)
    ordering = ('package__name', 'days_after', 'service__name',)
    form = PackageAllotmentForm

    def response_post_save_add(self, request, obj):
        return redirect(reverse('common:booking_package_change', args=[obj.package.pk]))

    def response_post_save_change(self, request, obj):
        return redirect(reverse('common:booking_package_change', args=[obj.package.pk]))


class PackageTransferSiteModel(SiteModel):
    model_order = 1030
    menu_label = MENU_LABEL_PACKAGE
    menu_group = MENU_GROUP_LABEL_SERVICES

    fields = (
        'package', ('service'),
        ('days_after', 'days_duration', 'time'),
        ('location_from', 'pickup', 'schedule_from'),
        ('place_from'),
        ('location_to', 'dropoff', 'schedule_to'),
        ('place_to'),
        'provider', 'id')
    list_display = ('package', 'service', 'days_after', 'time')
    top_filters = ('package__name', 'service',)
    ordering = ('package__name', 'days_after', 'service__name',)
    form = PackageTransferForm

    def response_post_save_add(self, request, obj):
        return redirect(reverse('common:booking_package_change', args=[obj.package.pk]))

    def response_post_save_change(self, request, obj):
        return redirect(reverse('common:booking_package_change', args=[obj.package.pk]))


class PackageExtraSiteModel(SiteModel):
    model_order = 1040
    menu_label = MENU_LABEL_PACKAGE
    menu_group = MENU_GROUP_LABEL_SERVICES

    fields = ['package', ('service'),
              ('days_after', 'days_duration', 'time'),
              ('addon', 'quantity', 'parameter'),
              'provider', 'id']
    list_display = ('package', 'service', 'addon', 'quantity', 'parameter',
                    'days_after', 'time',)
    top_filters = ('package__name', 'service',)
    ordering = ('package__name', 'days_after', 'service__name',)
    form = PackageExtraForm

    def response_post_save_add(self, request, obj):
        return redirect(reverse('common:booking_package_change', args=[obj.package.pk]))

    def response_post_save_change(self, request, obj):
        return redirect(reverse('common:booking_package_change', args=[obj.package.pk]))


# Starts Quote Section

class QuotePaxVariantInline(CommonStackedInline):
    model = QuotePaxVariant
    extra = 0
    fields = [
        ('pax_quantity', 'price_percent'),
        ('cost_single_amount', 'price_single_amount'),
        ('cost_double_amount', 'price_double_amount'),
        ('cost_triple_amount', 'price_triple_amount')]
    verbose_name_plural = 'Paxes Variants'


# Quote Package

class QuotePackageAllotmentInLine(CommonStackedInline):
    model = QuotePackageAllotment
    extra = 0
    fields = [
        ('service', 'status'), ('datetime_from', 'datetime_to'),
        ('room_type', 'board_type'), 'provider']
    ordering = ['datetime_from']
    form = QuotePackageAllotmentInlineForm


class QuotePackageAllotmentSiteModel(SiteModel):
    model_order = 560
    menu_label = MENU_LABEL_QUOTE
    menu_group = MENU_GROUP_LABEL_PACKAGE_SERVICES

    fields = ('quote_package', 'service', 'datetime_from', 'datetime_to', 'status',
              'room_type', 'board_type',
              'provider', 'id')
    list_display = ('quote_package', 'service', 'datetime_from', 'datetime_to',
                    'status',)
    top_filters = ('service', 'quote_package__quote__reference', ('datetime_from', DateTopFilter), 'status',)
    ordering = ('datetime_from', 'quote_package__quote__reference', 'service__name',)
    form = QuotePackageAllotmentForm


class QuotePackageTransferInLine(CommonStackedInline):
    model = QuotePackageTransfer
    extra = 0
    fields = [
        ('service', 'status'), ('datetime_from', 'datetime_to'),
        ('location_from', 'location_to'), 'provider']
    ordering = ['datetime_from']
    form = QuotePackageTransferInlineForm


class QuotePackageTransferSiteModel(SiteModel):
    model_order = 570
    menu_label = MENU_LABEL_QUOTE
    menu_group = MENU_GROUP_LABEL_PACKAGE_SERVICES

    fields = ('quote_package', 'service',
              'location_from', 'location_to',
              'datetime_from', 'datetime_to', 'status',
              'provider', 'id')
    list_display = ('quote_package', 'name', 'datetime_from', 'status',)
    top_filters = ('service', 'quote_package__quote__reference', ('datetime_from', DateTopFilter), 'status',)
    ordering = ('datetime_from', 'quote_package__quote__reference', 'service__name',)
    form = QuotePackageTransferForm


class QuotePackageExtraInLine(CommonStackedInline):
    model = QuotePackageExtra
    extra = 0
    fields = [
        ('service', 'status'), ('datetime_from', 'datetime_to', 'time'),
        ('addon', 'quantity', 'parameter'),
        'provider']
    ordering = ['datetime_from']
    form = QuotePackageExtraInlineForm


class QuotePackageExtraSiteModel(SiteModel):
    model_order = 580
    menu_label = MENU_LABEL_QUOTE
    menu_group = MENU_GROUP_LABEL_PACKAGE_SERVICES

    fields = (
        'quote_package',
        ('service', 'status'),
        ('datetime_from', 'datetime_to', 'time'),
        ('addon', 'quantity', 'parameter'),
        'provider', 'id')
    list_display = (
        'quote_package', 'service', 'addon', 'quantity', 'parameter',
        'datetime_from', 'datetime_to', 'time', 'status',)
    top_filters = ('service', 'quote_package__quote__reference', ('datetime_from', DateTopFilter), 'status',)
    ordering = ('datetime_from', 'quote_package__quote__reference', 'service__name',)
    form = QuotePackageExtraForm


# Quote

class QuoteAllotmentInLine(CommonStackedInline):
    model = QuoteAllotment
    extra = 0
    fields = [
        ('service', 'status'), ('datetime_from', 'datetime_to'),
        ('room_type', 'board_type'), 'provider']
    ordering = ['datetime_from']
    form = QuoteAllotmentInlineForm


class QuoteTransferInLine(CommonStackedInline):
    model = QuoteTransfer
    extra = 0
    fields = [
        ('service', 'status'), ('datetime_from', 'datetime_to'),
        ('location_from', 'location_to'), 'provider']
    ordering = ['datetime_from']
    form = QuoteTransferInlineForm


class QuoteExtraInLine(CommonStackedInline):
    model = QuoteExtra
    extra = 0
    fields = [
        ('service', 'status'), ('datetime_from', 'datetime_to', 'time'),
        ('addon', 'quantity', 'parameter'),
        'provider']
    ordering = ['datetime_from']
    form = QuoteExtraInlineForm


class QuotePackageInLine(CommonStackedInline):
    show_change_link = True
    model = QuotePackage
    extra = 0
    fields = [
        ('service', 'status'), ('datetime_from', 'datetime_to'),
        ('provider', 'price_by_package_catalogue'), 'quoteservice_ptr']
    ordering = ['datetime_from']
    form = QuotePackageInlineForm


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
    top_filters = ('reference', ('date_from', DateTopFilter), 'status')
    ordering = ('date_from', 'reference',)
    readonly_fields = ('date_from', 'date_to',)
    details_template = 'booking/quote_details.html'
    inlines = [
        QuotePaxVariantInline, QuoteAllotmentInLine,
        QuoteTransferInLine, QuoteExtraInLine, QuotePackageInLine]
    form = QuoteForm
    change_form_template = 'booking/quote_change_form.html'

    def get_urls(self):
        info = self.model._meta.app_label, self.model._meta.model_name
        urls = super(QuoteSiteModel, self).get_urls()
        urlpatterns = [
            self.build_url(r'^(?P<id>\d+)/booking/build/?',
                           self.booking_build,
                           '%s_%s_booking_build' % info),
        ]
        return urlpatterns + urls

    def booking_build(self, request, id, extra_context=None):
        PaxFormSet = modelformset_factory(
            model=BookingPax,
            fields=['pax_name', 'pax_age', 'pax_group'],
            extra=1,
        )
        formset = None
        if request.method == 'POST':
            quote_id = request.POST.get('quote_id', None)
            if quote_id:
                formset = PaxFormSet(request.POST)
                formset.is_valid()
                booking, msg = BookingServices.build_booking(quote_id, formset.cleaned_data)
                if booking:
                    return redirect(reverse('common:booking_booking_change', args=[booking.id]))
                else:
                    self.message_user(request, msg, messages.ERROR)
            else:
                self.message_user(request, 'Quote Missing', messages.ERROR)

        if not formset:
            formset = PaxFormSet(queryset=BookingPax.objects.none())

        context = {}
        context.update(self.get_model_extra_context(request))
        context.update(extra_context or {})
        context.update({'quote_id': id})
        context.update({'formset': formset})
        return render(request, 'booking/quote_booking_build.html', context)


class QuoteAllotmentSiteModel(SiteModel):
    model_order = 520
    menu_label = MENU_LABEL_QUOTE
    menu_group = MENU_GROUP_LABEL_SERVICES

    fields = ('quote', 'service', 'datetime_from', 'datetime_to', 'status',
              # 'cost_amount', 'price_amount',
              'room_type', 'board_type',
              'provider', 'id')
    list_display = ('quote', 'service', 'datetime_from', 'datetime_to',
                    'status',)
    top_filters = ('service', 'quote__reference', ('datetime_from', DateTopFilter), 'status',)
    ordering = ('datetime_from', 'quote__reference', 'service__name',)
    form = QuoteAllotmentForm


class QuoteTransferSiteModel(SiteModel):
    model_order = 530
    menu_label = MENU_LABEL_QUOTE
    menu_group = MENU_GROUP_LABEL_SERVICES

    fields = ('quote', 'service',
              'location_from', 'location_to',
              'datetime_from', 'datetime_to', 'status',
              'provider', 'id')
    list_display = ('quote', 'name', 'datetime_from', 'status',)
    top_filters = ('service', 'quote__reference', ('datetime_from', DateTopFilter), 'status',)
    ordering = ('datetime_from', 'quote__reference', 'service__name',)
    form = QuoteTransferForm


class QuoteExtraSiteModel(SiteModel):
    model_order = 540
    menu_label = MENU_LABEL_QUOTE
    menu_group = MENU_GROUP_LABEL_SERVICES

    fields = (
        'quote',
        ('service', 'status'),
        ('datetime_from', 'datetime_to', 'time'),
        ('addon', 'quantity', 'parameter'),
        'provider', 'id')
    list_display = (
        'quote', 'service', 'addon', 'quantity', 'parameter',
        'datetime_from', 'datetime_to', 'time', 'status',)
    top_filters = ('service', 'quote__reference', ('datetime_from', DateTopFilter), 'status',)
    ordering = ('datetime_from', 'quote__reference', 'service__name',)
    form = QuoteExtraForm


class QuotePackageSiteModel(SiteModel):
    model_order = 550
    menu_label = MENU_LABEL_QUOTE
    menu_group = MENU_GROUP_LABEL_SERVICES

    fields = (
        'quote',
        ('service', 'status'),
        ('datetime_from', 'datetime_to'),
        ('provider', 'price_by_package_catalogue'), 'id')
    list_display = (
        'quote', 'service', 'datetime_from', 'datetime_to', 'status',)
    top_filters = ('service', 'quote__reference', ('datetime_from', DateTopFilter), 'status',)
    ordering = ('datetime_from', 'quote__reference', 'service__name',)
    readonly_fields = ['datetime_to']
    details_template = 'booking/quotepackage_details.html'
    inlines = [
        QuotePackageAllotmentInLine, QuotePackageTransferInLine, QuotePackageExtraInLine]
    form = QuotePackageForm


# Starts Booking Section

class BookingPaxInline(TabularInline):
    model = BookingPax
    fields = ['pax_name', 'pax_group', 'pax_age']
    verbose_name_plural = 'Rooming List'
    extra = 0
    ordering = ('pax_group', 'pax_name')


class BookingServicePaxInline(TabularInline):
    model = BookingServicePax
    fields = ['booking_pax', 'group', 'is_cost_free', 'is_price_free']
    verbose_name_plural = 'Service Rooming List'
    form = BookingServicePaxInlineForm
    ordering = ('group', 'booking_pax__pax_name')

    def get_formset(self, request, obj=None, **kwargs):
        initial = []
        if request.method == "GET":
            saved = None
            if obj:
                saved = BookingServicePax.objects.filter(booking_service=obj.id)
            if not saved:
                booking = request.GET.get('booking')
                rooming = BookingPax.objects.filter(booking=booking).order_by('pax_group')
                self.extra = len(rooming)
                for bp in rooming:
                    new_pax = {'booking_pax': bp.id,
                               'group': bp.pax_group}
                    initial.append(new_pax)
        formset = super(BookingServicePaxInline, self).get_formset(request, obj, **kwargs)
        formset.__init__ = curry(formset.__init__, initial=initial)
        return formset


class BookingAllotmentInLine(CommonTabularInline):
    show_change_link = True
    model = BookingAllotment
    extra = 0
    fields = [('service', 'status', 'conf_number'),
              ('datetime_from', 'datetime_to'),
              ('room_type', 'board_type'), 'provider']
    ordering = ['datetime_from']
    form = BookingAllotmentInlineForm
    classes = ['collapse']


class BookingTransferInLine(CommonTabularInline):
    show_change_link = True
    model = BookingTransfer
    extra = 0
    fields = [('service', 'status', 'conf_number'),
              ('datetime_from', 'datetime_to', 'time'),
              ('location_from', 'location_to'),
              ('quantity', 'provider')]
    ordering = ['datetime_from']
    form = BookingTransferInlineForm
    classes = ['collapse']


class BookingExtraInLine(CommonTabularInline):
    show_change_link = True
    model = BookingExtra
    extra = 0
    fields = [('service', 'status', 'conf_number'),
              ('datetime_from', 'datetime_to', 'time'),
              ('quantity', 'parameter'), 'provider']
    ordering = ['datetime_from']
    form = BookingExtraInlineForm
    classes = ('collapse',)


class BookingPackageInLine(CommonTabularInline):
    show_change_link = True
    model = BookingPackage
    extra = 0
    fields = [('service', 'status', 'conf_number'), ('datetime_from', 'datetime_to'),
              ('provider', 'price_by_package_catalogue')]
    ordering = ['datetime_from']
    form = BookingPackageInlineForm
    classes = ('collapse',)


class BookingSiteModel(SiteModel):
    model_order = 1110
    menu_label = MENU_LABEL_BOOKING

    recent_allowed = True
    fieldsets = (
        (None, {
            'fields': (
                'internal_reference',
                ('name', 'reference', 'status'),
                ('agency', 'date_from', 'date_to'),
                ('is_package_price', 'price_amount', 'cost_amount'),
                ('package_sgl_price_amount', 'package_dbl_price_amount',
                 'package_tpl_price_amount'),)
        }),
        ('General Notes', {'fields': ('p_notes',),
                           'classes': ('collapse', 'wide')})
    )
    list_display = ('name', 'internal_reference', 'agency',
                    'reference', 'date_from',
                    'date_to', 'status', 'cost_amount',
                    'price_amount',)
    top_filters = (('name', 'Booking Name'), 'reference', 'agency',
                   ('date_from', DateTopFilter), 'rooming_list__pax_name',
                    (CancelledTopFilter))
    ordering = ['date_from', 'reference']
    readonly_fields = ('date_from', 'date_to', 'status',
                       'cost_amount', 'price_amount',
                       'internal_reference')
    details_template = 'booking/booking_details.html'
    inlines = [BookingPaxInline, BookingAllotmentInLine,
               BookingTransferInLine, BookingExtraInLine, BookingPackageInLine]
    form = BookingForm
    add_form_template = 'booking/booking_change_form.html'
    change_form_template = 'booking/booking_change_form.html'
    totalsum_list = ['cost_amount', 'price_amount']

    def get_urls(self):

        info = self.model._meta.app_label, self.model._meta.model_name
        urls = super(BookingSiteModel, self).get_urls()
        urlpatterns = [
            self.build_url(r'^invoices/(?P<id>\d+)/config/?',
                           self.config_invoice, 'config_invoice'),
            self.build_url(r'^voucher/(?P<id>\d+)/config/?',
                           self.config_vouchers,
                           '%s_%s_config_vouchers' % info),
        ]
        return urlpatterns + urls

    def config_invoice(self, request, id):
        # this handles configuration form to build invoices
        pass

    def config_vouchers(self, request, id, extra_context=None):
        # this handles configuration form to build vouchers
        context = {}
        if request.method == 'GET':
            form = VouchersConfigForm()
            context.update(self.get_model_extra_context(request))
            context.update(extra_context or {})
            context.update({'current': Booking.objects.get(id=id)})
            context.update({'form': form})
            return render(request, 'booking/voucher_config.html', context)
        else:
            # This is a POST. render vouchers
            ids = request.POST.getlist('pk', [])
            office = request.POST.get('office', None)
            # use this two parameters to call methods to build pdf
            # it should return the pisa object to add it to the response object
            pdf = self.build_vouchers(id, ids, office)
            if pdf:
                return HttpResponse(pdf.getvalue(),
                                    content_type='application/pdf')
            # there was an error. show an error message
            return redirect(reverse('common:booking_booking_change',
                                    args=[id]))

    def build_vouchers(self, bk, service_ids, office):
        # This helper builds the PDF object with all vouchers
        template = get_template("booking/pdf/voucher.html")
        booking = Booking.objects.get(id=bk)
        services = BookingService.objects.filter(pk__in=service_ids)
        context = {'pagesize': 'Letter',
                   'booking': booking,
                   'services': services}
        html = template.render(context)
        result = StringIO()
        pdf = pisa.pisaDocument(StringIO(html), dest=result)
        if pdf.err:
            return False
        return result


class BookingAllotmentSiteModel(SiteModel):
    model_order = 1210
    menu_label = MENU_LABEL_BOOKING
    menu_group = MENU_GROUP_LABEL_SERVICES

    fieldsets = (
        (None, {
            'fields': (
                'booking', ('service', 'status', 'conf_number'),
                ('datetime_from', 'datetime_to'),
                ('room_type', 'board_type'),
                'provider', 'cost_amount', 'price_amount', 'id')
        }),
        ('Notes', {'fields': ('p_notes', 'v_notes', 'provider_notes'),
                   'classes': ('collapse', 'wide')})
    )

    list_display = ('booking', 'name', 'datetime_from',
                    'datetime_to', 'status',)
    top_filters = (('booking__name', 'Booking'),
                   ('name', 'Service'),
                   'booking__reference', 'conf_number',
                   ('datetime_from', DateTopFilter), 'status')
    ordering = ('datetime_from', 'booking__reference', 'service__name',)
    save_as = True
    form = BookingAllotmentForm
    add_form_template = 'booking/bookingallotment_change_form.html'
    change_form_template = 'booking/bookingallotment_change_form.html'
    inlines = [BookingServicePaxInline]

    def response_post_save_add(self, request, obj):
        return redirect(reverse('common:booking_booking_change', args=[obj.booking.pk]))

    def response_post_save_change(self, request, obj):
        return redirect(reverse('common:booking_booking_change', args=[obj.booking.pk]))


class BookingTransferSiteModel(SiteModel):
    model_order = 1220
    menu_label = MENU_LABEL_BOOKING
    menu_group = MENU_GROUP_LABEL_SERVICES

    fieldsets = (
        (None, {
            'fields': (
                'booking', ('service', 'status', 'conf_number'),
                ('datetime_from', 'datetime_to', 'time'),
                ('location_from', 'pickup', 'schedule_from'),
                ('place_from'),
                ('location_to', 'dropoff', 'schedule_to'),
                ('place_to'),
                 'provider', 'cost_amount', 'price_amount','id')
        }),
        ('Notes', {'fields': ('p_notes', 'v_notes', 'provider_notes'),
                   'classes': ('collapse', 'wide')})
    )
    list_display = ('booking', 'name',
                    'datetime_from', 'time', 'status')
    top_filters = (
        ('booking__name', 'Booking'),
        ('name', 'Service'),
        'booking__reference', 'conf_number',
        ('datetime_from', DateTopFilter), 'status',)
    ordering = ('datetime_from', 'booking__reference', 'service__name',)
    form = BookingTransferForm
    add_form_template = 'booking/bookingtransfer_change_form.html'
    change_form_template = 'booking/bookingtransfer_change_form.html'
    inlines = [BookingServicePaxInline]

    def response_post_save_add(self, request, obj):
        return redirect(reverse('common:booking_booking_change', args=[obj.booking.pk]))

    def response_post_save_change(self, request, obj):
        return redirect(reverse('common:booking_booking_change', args=[obj.booking.pk]))


class BookingExtraSiteModel(SiteModel):
    model_order = 1230
    menu_label = MENU_LABEL_BOOKING
    menu_group = MENU_GROUP_LABEL_SERVICES

    fieldsets = (
        (None, {
            'fields': (
                'booking', ('service', 'status', 'conf_number'),
                ('datetime_from', 'datetime_to', 'time'),
                ('addon', 'quantity', 'parameter'),
                'provider', 'cost_amount', 'price_amount', 'id')
        }),
        ('Notes', {'fields': ('p_notes', 'v_notes', 'provider_notes'),
                   'classes': ('collapse', 'wide')})
    )
    list_display = ('booking', 'name', 'addon', 'quantity', 'parameter',
                    'datetime_from', 'datetime_to', 'time', 'status',)
    top_filters = ('booking__name', 'service', 'booking__reference',
                   ('datetime_from', DateTopFilter), 'status',)
    ordering = ('datetime_from', 'booking__reference', 'service__name',)
    form = BookingExtraForm
    add_form_template = 'booking/bookingextra_change_form.html'
    change_form_template = 'booking/bookingextra_change_form.html'
    inlines = [BookingServicePaxInline]

    def response_post_save_add(self, request, obj):
        return redirect(reverse('common:booking_booking_change', args=[obj.booking.pk]))

    def response_post_save_change(self, request, obj):
        return redirect(reverse('common:booking_booking_change', args=[obj.booking.pk]))


class BookingPackageAllotmentInLine(CommonStackedInline):
    model = BookingPackageAllotment
    extra = 0
    fields = [('service', 'status', 'conf_number'), ('datetime_from', 'datetime_to'),
              ('room_type', 'board_type'), 'provider']
    ordering = ['datetime_from']
    form = BookingPackageAllotmentInlineForm
    classes = ['collapse']


class BookingPackageAllotmentSiteModel(SiteModel):
    model_order = 1310
    menu_label = MENU_LABEL_BOOKING
    menu_group = MENU_GROUP_LABEL_PACKAGE_SERVICES

    fields = ['booking_package', ('service', 'status', 'conf_number'),
                ('datetime_from', 'datetime_to'),
                ('room_type', 'board_type'),
                'provider', 'id']
    list_display = ('booking_package', 'name', 'datetime_from',
                    'datetime_to', 'status',)
    top_filters = (('booking_package__booking__name', 'booking_package__Booking'),
                   ('name', 'Service'),
                   'booking_package__booking__reference', 'conf_number',
                   ('datetime_from', DateTopFilter), 'status')
    ordering = ('datetime_from', 'booking_package', 'service__name',)
    form = BookingPackageAllotmentForm

    def response_post_save_add(self, request, obj):
        return redirect(
            reverse('common:booking_bookingpackage_change', args=[obj.booking_package.pk]))

    def response_post_save_change(self, request, obj):
        return redirect(
            reverse('common:booking_bookingpackage_change', args=[obj.booking_package.pk]))


class BookingPackageTransferInLine(CommonStackedInline):
    model = BookingPackageTransfer
    extra = 0
    fields = [
        ('service', 'status', 'conf_number'), ('datetime_from', 'datetime_to', 'time'),
        ('location_from', 'pickup', 'schedule_from'),
        ('place_from'),
        ('location_to', 'dropoff', 'schedule_to'),
        ('place_to'),
        ('quantity', 'provider')]
    ordering = ['datetime_from']
    form = BookingPackageTransferInlineForm
    classes = ['collapse']


class BookingPackageTransferSiteModel(SiteModel):
    model_order = 1320
    menu_label = MENU_LABEL_BOOKING
    menu_group = MENU_GROUP_LABEL_PACKAGE_SERVICES

    fields = [
        'booking_package', ('service', 'status', 'conf_number'),
        ('datetime_from', 'datetime_to', 'time'),
        ('location_from', 'pickup', 'schedule_from'),
        ('place_from'),
        ('location_to', 'dropoff', 'schedule_to'),
        ('place_to'),
        'provider', 'id']
    list_display = ('booking_package', 'name', 'datetime_from', 'time', 'status')
    top_filters = (
        ('booking_package__booking__name', 'Booking_package'),
        ('name', 'Service'),
        'booking_package__booking__reference', 'conf_number',
        ('datetime_from', DateTopFilter), 'status',)
    ordering = ('datetime_from', 'booking_package', 'service__name',)
    form = BookingPackageTransferForm

    def response_post_save_add(self, request, obj):
        return redirect(
            reverse('common:booking_bookingpackage_change', args=[obj.booking_package.pk]))

    def response_post_save_change(self, request, obj):
        return redirect(
            reverse('common:booking_bookingpackage_change', args=[obj.booking_package.pk]))


class BookingPackageExtraInLine(CommonStackedInline):
    model = BookingPackageExtra
    extra = 0
    fields = [('service', 'status', 'conf_number'), ('datetime_from', 'datetime_to', 'time'),
              ('addon', 'quantity', 'parameter'), 'provider']
    ordering = ['datetime_from']
    form = BookingPackageExtraInlineForm
    classes = ('collapse',)


class BookingPackageExtraSiteModel(SiteModel):
    model_order = 1330
    menu_label = MENU_LABEL_BOOKING
    menu_group = MENU_GROUP_LABEL_PACKAGE_SERVICES

    fields = ['booking_package', ('service', 'status', 'conf_number'),
              ('datetime_from', 'datetime_to', 'time'),
              ('addon', 'quantity', 'parameter'),
              'provider', 'id']
    list_display = ('booking_package', 'name', 'addon', 'quantity', 'parameter',
                    'datetime_from', 'datetime_to', 'time', 'status',)
    top_filters = (
        'booking_package__booking__name', 'service', 'booking_package__booking__reference',
        ('datetime_from', DateTopFilter), 'status',)
    ordering = ('datetime_from', 'booking_package', 'service__name',)
    form = BookingPackageExtraForm

    def response_post_save_add(self, request, obj):
        return redirect(
            reverse('common:booking_bookingpackage_change', args=[obj.booking_package.pk]))

    def response_post_save_change(self, request, obj):
        return redirect(
            reverse('common:booking_bookingpackage_change', args=[obj.booking_package.pk]))


class BookingPackageSiteModel(SiteModel):
    model_order = 1240
    menu_label = MENU_LABEL_BOOKING
    menu_group = MENU_GROUP_LABEL_SERVICES

    fields = [
        'booking', ('service', 'status', 'conf_number'),
        ('datetime_from', 'datetime_to'),
        'provider', 'cost_amount', 'price_by_package_catalogue', 'price_amount', 'id']
    list_display = ['booking', 'name', 'datetime_from', 'datetime_to', 'status']
    top_filters = ['booking__name', 'service', 'booking__reference',
                   ('datetime_from', DateTopFilter), 'status']
    ordering = ['datetime_from', 'booking__reference', 'service__name']
    readonly_fields = ['datetime_from', 'datetime_to', 'status']
    details_template = 'booking/bookingpackage_details.html'
    inlines = [BookingServicePaxInline, BookingPackageAllotmentInLine,
               BookingPackageTransferInLine, BookingPackageExtraInLine]
    form = BookingPackageForm
    add_form_template = 'booking/bookingpackage_change_form.html'
    change_form_template = 'booking/bookingpackage_change_form.html'

    def response_post_save_add(self, request, obj):
        return redirect(reverse('common:booking_booking_change', args=[obj.booking.pk]))

    def response_post_save_change(self, request, obj):
        return redirect(reverse('common:booking_booking_change', args=[obj.booking.pk]))


class AgencyPackageDetailInline(CommonStackedInline):
    model = AgencyPackageDetail
    extra = 0
    fields = (('ad_1_amount', 'pax_range_min', 'pax_range_max'),)


class AgencyPackageServiceSiteModel(SiteModel):
    model_order = 7140
    menu_label = MENU_LABEL_CONFIG_BASIC
    menu_group = 'Agency Catalogue'
    recent_allowed = True
    fields = ('agency', 'service', 'date_from', 'date_to')
    list_display = ('agency', 'service', 'date_from', 'date_to',)
    top_filters = (
        ('service', PackageTopFilter), ('agency', AgencyTopFilter),
        ('date_to', DateTopFilter))
    inlines = [AgencyPackageDetailInline]
    ordering = ['service', 'agency', '-date_from']
    form = AgencyPackageServiceForm
    save_as = True


# Starts Registration Section

bookings_site.register(Package, PackageSiteModel)

bookings_site.register(PackageAllotment, PackageAllotmentSiteModel)
bookings_site.register(PackageTransfer, PackageTransferSiteModel)
bookings_site.register(PackageExtra, PackageExtraSiteModel)

bookings_site.register(AgencyPackageService, AgencyPackageServiceSiteModel)

bookings_site.register(Quote, QuoteSiteModel)

bookings_site.register(QuoteAllotment, QuoteAllotmentSiteModel)
bookings_site.register(QuoteTransfer, QuoteTransferSiteModel)
bookings_site.register(QuoteExtra, QuoteExtraSiteModel)
bookings_site.register(QuotePackage, QuotePackageSiteModel)
bookings_site.register(QuotePackageAllotment, QuotePackageAllotmentSiteModel)
bookings_site.register(QuotePackageTransfer, QuotePackageTransferSiteModel)
bookings_site.register(QuotePackageExtra, QuotePackageExtraSiteModel)


bookings_site.register(Booking, BookingSiteModel)

bookings_site.register(BookingAllotment, BookingAllotmentSiteModel)
bookings_site.register(BookingTransfer, BookingTransferSiteModel)
bookings_site.register(BookingExtra, BookingExtraSiteModel)
bookings_site.register(BookingPackage, BookingPackageSiteModel)
bookings_site.register(BookingPackageAllotment, BookingPackageAllotmentSiteModel)
bookings_site.register(BookingPackageTransfer, BookingPackageTransferSiteModel)
bookings_site.register(BookingPackageExtra, BookingPackageExtraSiteModel)
