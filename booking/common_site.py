# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os

try:
    from cStringIO import StringIO
except ImportError:
    from _io import StringIO
from xhtml2pdf import pisa

from common.sites import SiteModel, CommonChangeList

from django.conf import settings
from django.conf.urls import url
from django.contrib import admin, messages
from django.contrib.admin.options import (csrf_protect_m,
                                          IS_POPUP_VAR,
                                          TO_FIELD_VAR)
from django.contrib.admin import TabularInline
from django.contrib.admin.checks import ModelAdminChecks
from django.contrib.admin.utils import quote, unquote
from django.core import checks
from django.core.exceptions import (FieldDoesNotExist,
                                    ValidationError,
                                    PermissionDenied)
from django.core.mail import EmailMessage
from django.db import router, transaction
from django.db.models.query_utils import Q
from django import forms
from django.forms import formset_factory
from django.forms.models import modelformset_factory
from django.http import HttpResponse
from django.shortcuts import render, redirect, reverse
from django.template.response import SimpleTemplateResponse, TemplateResponse
from django.template.loader import get_template
from django.utils.encoding import force_text
# from django.utils.translation import ugettext as _, ungettext
from django.utils.functional import curry
from django.utils.six import PY2
# from django_tables2 import RequestConfig

from finance.models import Office
from finance.top_filters import ProviderTopFilter, AgencyTopFilter

from booking.constants import (
    SERVICE_STATUS_PENDING, SERVICE_STATUS_COORDINATED, SERVICE_STATUS_CONFIRMED,
    SERVICE_STATUS_CANCELLED,
    BOOTSTRAP_STYLE_STATUS_MAPPING,
    BASE_BOOKING_SERVICE_CATEGORY_BOOKING_ALLOTMENT, BASE_BOOKING_SERVICE_CATEGORY_BOOKING_TRANSFER,
    BASE_BOOKING_SERVICE_CATEGORY_BOOKING_EXTRA, BASE_BOOKING_SERVICE_CATEGORY_BOOKING_PACKAGE,
    BASE_BOOKING_SERVICE_CATEGORY_PACKAGE_ALLOTMENT, BASE_BOOKING_SERVICE_CATEGORY_PACKAGE_TRANSFER,
    BASE_BOOKING_SERVICE_CATEGORY_PACKAGE_EXTRA
)
from booking.forms import (
    EmailPopupForm,
    PackageForm,
    PackageAllotmentInlineForm, PackageTransferInlineForm,
    PackageExtraInlineForm, PackageAllotmentForm,
    PackageTransferForm, PackageExtraForm,
    PackageProviderForm, AgencyPackageServiceForm,
    QuoteForm,
    QuoteAllotmentForm, QuoteTransferForm, QuoteExtraForm, QuotePackageForm,
    QuoteAllotmentInlineForm, QuoteTransferInlineForm,
    QuoteExtraInlineForm, QuotePackageInlineForm,
    QuotePackageAllotmentInlineForm, QuotePackageTransferInlineForm,
    QuotePackageExtraInlineForm, QuotePackageAllotmentForm,
    QuotePackageTransferForm, QuotePackageExtraForm,
    BookingForm, BookingServicePaxInlineForm,
    BookingAllotmentForm,
    BookingTransferForm,
    BookingExtraForm,
    BookingPackageForm,
    BookingPackageAllotmentForm,
    BookingPackageTransferForm,
    BookingPackageExtraForm,
    VouchersConfigForm,
    ProviderBookingPaymentForm,
    ProviderBookingPaymentServiceForm, ProviderBookingPaymentServiceReadonlyForm,
)
from booking.models import (
    BaseBookingService,
    Package, PackageAllotment, PackageTransfer, PackageExtra,
    AgencyPackageService, AgencyPackageDetail, PackageProvider,
    Quote, QuoteService,
    QuotePaxVariant, QuoteServicePaxVariant, QuotePackageServicePaxVariant,
    QuoteAllotment, QuoteTransfer, QuoteExtra, QuotePackage,
    QuotePackageAllotment, QuotePackageTransfer, QuotePackageExtra,
    Booking,
    BookingPax,
    BookingServicePax,
    BookingService,
    BookingAllotment, BookingTransfer, BookingExtra, BookingPackage,
    BookingPackageService, BookingPackageAllotment,
    BookingPackageTransfer, BookingPackageExtra,
    BookingInvoice, BookingInvoiceDetail, BookingInvoiceLine,
    BookingInvoicePartial,
    ProviderBookingPayment, ProviderBookingPaymentService,
    _get_child_objects, _get_quote_child_objects,
)
from booking.services import BookingServices
from booking.top_filters import (
    DateTopFilter, PackageTopFilter, CancelledTopFilter, InternalReferenceTopFilter,
    SellerTopFilter, PaidTopFilter)

from common.sites import CommonStackedInline, CommonTabularInline

from config.services import ConfigServices
from config.top_filters import LocationTopFilter

from finance.constants import STATUS_DRAFT, STATUS_READY, STATUS_CANCELLED

from reservas.admin import bookings_site


MENU_LABEL_CONFIG_BASIC = 'Configuration'
MENU_LABEL_PACKAGE = 'Package'
MENU_LABEL_QUOTE = 'Quote'
MENU_LABEL_BOOKING = 'Booking'
MENU_GROUP_LABEL_SERVICES = 'Services By Type'
MENU_GROUP_LABEL_PACKAGE_SERVICES = 'Package Services By Type'


# Starts Package Section

# # Utility method to get a list of
# # BookingService child objects from a BookingService list
# # TODO. remove this once we check everything goes fine
# def _get_child_objects(services):
#     TYPE_MODELS = {
#         'T': BookingTransfer,
#         'E': BookingExtra,
#         'A': BookingAllotment,
#         'P': BookingPackage,
#     }
#     objs = []
#     for service in services:
#         obj = TYPE_MODELS[service.service_type].objects.get(id=service.id)
#         objs.append(obj)
#     return objs


def _get_voucher_services(services):
    objs = []
    booking_services = _get_child_objects(services)
    for booking_service in booking_services:
        if isinstance(booking_service, BookingPackage) and booking_service.voucher_detail:
            PACKAGE_MODELS = {
                'T': BookingPackageTransfer,
                'E': BookingPackageExtra,
                'A': BookingPackageAllotment,
            }
            package_services = list(BookingPackageService.objects.filter(
                booking_package=booking_service).exclude(status=SERVICE_STATUS_CANCELLED))
            for package_service in package_services:
                service = PACKAGE_MODELS[package_service.service_type].objects.get(
                    id=package_service.id)
                objs.append(service)
        else:
            objs.append(booking_service)
    return objs

class PackageAllotmentInLine(CommonStackedInline):
    model = PackageAllotment
    extra = 0
    fields = [
        ('service', 'search_location'),
        ('room_type', 'board_type'),
        ('days_after', 'days_duration', 'provider')]
    ordering = ['days_after']
    form = PackageAllotmentInlineForm


class PackageTransferInLine(CommonStackedInline):
    model = PackageTransfer
    extra = 0
    fields = [
        ('service', 'search_location', 'time'),
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
        ('service', 'search_location', 'time'),
        ('service_addon', 'quantity', 'parameter'),
        ('days_after', 'days_duration', 'provider'),
        ('pickup_office', 'dropoff_office',)]
    ordering = ['days_after']
    form = PackageExtraInlineForm


class PackageSiteModel(SiteModel):
    model_order = 1010
    menu_label = MENU_LABEL_PACKAGE
    fields = (
        ('name', 'service_category', 'enabled'),
        ('location', 'amounts_type', 'pax_range'),
        'time', 'description'
    )
    list_display = (
        'name', 'service_category', 'location', 'amounts_type', 'pax_range', 'time', 'enabled')
    list_editable = ('enabled',)
    top_filters = ('name', ('location', LocationTopFilter), 'amounts_type', 'pax_range', 'enabled')
    ordering = ('enabled', 'name',)
    list_details_template = 'booking/package_details.html'
    change_details_template = 'booking/package_details.html'
    form = PackageForm
    inlines = [
        PackageAllotmentInLine, PackageTransferInLine, PackageExtraInLine]


class PackageServiceSiteModel(SiteModel):
    def response_post_delete(self, request, obj):
        if hasattr(obj, 'package') and obj.package:
            return redirect(reverse('common:booking_package_change', args=[obj.package.pk]))
        package = request.POST.get('package')
        if package:
            return redirect(reverse('common:booking_package_change', args=[package]))
        return super(PackageServiceSiteModel, self).response_post_delete(request, obj)

    def response_post_save_add(self, request, obj):
        if hasattr(obj, 'package') and obj.package:
            return redirect(reverse('common:booking_package_change', args=[obj.package.pk]))
        package = request.POST.get('package')
        if package:
            return redirect(reverse('common:booking_package_change', args=[package]))
        return super(PackageServiceSiteModel, self).response_post_save_add(request, obj)

    def response_post_save_change(self, request, obj):
        if hasattr(obj, 'package') and obj.package:
            return redirect(reverse('common:booking_package_change', args=[obj.package.pk]))
        package = request.POST.get('package')
        if package:
            return redirect(reverse('common:booking_package_change', args=[package]))
        return super(PackageServiceSiteModel, self).response_post_save_change(request, obj)


class PackageAllotmentSiteModel(PackageServiceSiteModel):
    model_order = 1020
    menu_label = MENU_LABEL_PACKAGE
    menu_group = MENU_GROUP_LABEL_SERVICES

    fields = (
        'package', ('service', 'search_location'),
        ('days_after', 'days_duration'),
        ('room_type', 'board_type'), 'provider', 'id')
    list_display = ('package', 'service', 'days_after', 'days_duration',)
    top_filters = ('package__name', 'service',)
    ordering = ('package__name', 'days_after', 'service__name',)
    form = PackageAllotmentForm


class PackageTransferSiteModel(PackageServiceSiteModel):
    model_order = 1030
    menu_label = MENU_LABEL_PACKAGE
    menu_group = MENU_GROUP_LABEL_SERVICES

    fields = (
        'package', ('service', 'search_location'),
        ('days_after', 'days_duration', 'time'),
        ('location_from', 'place_from'),
        ('pickup', 'schedule_from', 'schedule_time_from'),
        ('location_to', 'place_to'),
        ('dropoff', 'schedule_to', 'schedule_time_to'),
        'provider', 'id')
    list_display = ('package', 'service', 'days_after', 'time')
    top_filters = ('package__name', 'service',)
    ordering = ('package__name', 'days_after', 'service__name',)
    form = PackageTransferForm


class PackageExtraSiteModel(PackageServiceSiteModel):
    model_order = 1040
    menu_label = MENU_LABEL_PACKAGE
    menu_group = MENU_GROUP_LABEL_SERVICES

    fields = ['package', ('service', 'search_location'),
              ('days_after', 'days_duration', 'time'),
              ('service_addon', 'quantity', 'parameter'),
              ('pickup_office', 'dropoff_office',),
              'provider', 'id']
    list_display = ('package', 'service', 'service_addon', 'quantity', 'parameter',
                    'days_after', 'time',)
    top_filters = ('package__name', 'service',)
    ordering = ('package__name', 'days_after', 'service__name',)
    form = PackageExtraForm


# Starts Quote Section

class QuotePaxVariantInline(CommonStackedInline):
    model = QuotePaxVariant
    extra = 0
    fields = [
        ('pax_quantity', 'price_percent'),
        ('free_cost_single', 'free_price_single'),
        ('free_cost_double', 'free_price_double'),
        ('free_cost_triple', 'free_price_triple'),
        ('free_cost_qdrple', 'free_price_qdrple'),
        ('cost_single_amount', 'price_single_amount', 'utility_percent_single', 'utility_single', 'extra_single_amount'),
        ('cost_double_amount', 'price_double_amount', 'utility_percent_double', 'utility_double', 'extra_double_amount'),
        ('cost_triple_amount', 'price_triple_amount', 'utility_percent_triple', 'utility_triple', 'extra_triple_amount'),
        ('cost_qdrple_amount', 'price_qdrple_amount', 'utility_percent_qdrple', 'utility_qdrple', 'extra_qdrple_amount'),
    ]
    readonly_fields = [
        'cost_single_amount', 'price_single_amount', 'utility_percent_single', 'utility_single',
        'cost_double_amount', 'price_double_amount', 'utility_percent_double', 'utility_double',
        'cost_triple_amount', 'price_triple_amount', 'utility_percent_triple', 'utility_triple',
        'cost_qdrple_amount', 'price_qdrple_amount', 'utility_percent_qdrple', 'utility_qdrple',
    ]
    verbose_name_plural = 'Paxes Variants'


class QuoteServicePaxVariantInline(CommonStackedInline):
    model = QuoteServicePaxVariant
    extra = 0
    fields = [
        ('quote_pax_variant'),
        ('free_cost_single', 'free_price_single'),
        ('free_cost_double', 'free_price_double'),
        ('free_cost_triple', 'free_price_triple'),
        ('free_cost_qdrple', 'free_price_qdrple'),
        ('manual_costs', 'manual_prices'),
        ('cost_single_amount', 'price_single_amount', 'utility_percent_single', 'utility_single'),
        ('cost_double_amount', 'price_double_amount', 'utility_percent_double', 'utility_double'),
        ('cost_triple_amount', 'price_triple_amount', 'utility_percent_triple', 'utility_triple'),
        ('cost_qdrple_amount', 'price_qdrple_amount', 'utility_percent_qdrple', 'utility_qdrple'),
    ]
    verbose_name_plural = 'Paxes Variants'
    can_delete = False

    readonly_fields = [
        'utility_percent_single', 'utility_percent_double',
        'utility_percent_triple', 'utility_percent_qdrple',
        'utility_single', 'utility_double', 'utility_triple', 'utility_qdrple']

    def has_add_permission(self,request):
        return False

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super(QuoteServicePaxVariantInline, self).get_readonly_fields(request, obj) or []

        if not request.user.has_perm("booking.change_amounts"):
            return readonly_fields + [
                'manual_costs', 'manual_prices',
                'cost_single_amount', 'price_single_amount', 'utility_percent_single', 'utility_single',
                'cost_double_amount', 'price_double_amount', 'utility_percent_double', 'utility_double',
                'cost_triple_amount', 'price_triple_amount', 'utility_percent_triple', 'utility_triple',
                'cost_qdrple_amount', 'price_qdrple_amount', 'utility_percent_qdrple', 'utility_qdrple',
            ]

        return readonly_fields


# Quote Package

class QuotePackageAllotmentInLine(CommonStackedInline):
    model = QuotePackageAllotment
    extra = 0
    fields = [
        ('service', 'search_location', 'status'), ('datetime_from', 'datetime_to'),
        ('room_type', 'board_type'), 'provider']
    ordering = ['datetime_from']
    form = QuotePackageAllotmentInlineForm


class QuotePackageTransferInLine(CommonStackedInline):
    model = QuotePackageTransfer
    extra = 0
    fields = [
        ('service', 'search_location', 'status'), ('datetime_from', 'datetime_to'),
        ('location_from', 'location_to'), 'provider']
    ordering = ['datetime_from']
    form = QuotePackageTransferInlineForm


class QuotePackageExtraInLine(CommonStackedInline):
    model = QuotePackageExtra
    extra = 0
    fields = [
        ('service', 'search_location', 'status'), ('datetime_from', 'datetime_to', 'time'),
        ('quantity', 'parameter'),
        ('pickup_office', 'dropoff_office',),
        'provider']
    ordering = ['datetime_from']
    form = QuotePackageExtraInlineForm


# Quote

class QuoteAllotmentInLine(CommonStackedInline):
    model = QuoteAllotment
    extra = 0
    fields = [
        ('service', 'search_location', 'status'), ('datetime_from', 'datetime_to'),
        ('room_type', 'board_type'), 'provider']
    ordering = ['datetime_from']
    form = QuoteAllotmentInlineForm


class QuoteTransferInLine(CommonStackedInline):
    model = QuoteTransfer
    extra = 0
    fields = [
        ('service', 'search_location', 'status'), ('datetime_from', 'datetime_to'),
        ('location_from', 'location_to'), 'provider']
    ordering = ['datetime_from']
    form = QuoteTransferInlineForm


class QuoteExtraInLine(CommonStackedInline):
    model = QuoteExtra
    extra = 0
    fields = [
        ('service', 'search_location', 'status'), ('datetime_from', 'datetime_to', 'time'),
        ('quantity', 'parameter'),
        ('pickup_office', 'dropoff_office',),
        'provider']
    ordering = ['datetime_from']
    form = QuoteExtraInlineForm


class QuotePackageInLine(CommonStackedInline):
    show_change_link = True
    model = QuotePackage
    extra = 0
    fields = [
        ('service', 'search_location', 'status'), ('datetime_from', 'datetime_to'),
        ('provider', 'price_by_package_catalogue'), 'quoteservice_ptr']
    ordering = ['datetime_from']
    form = QuotePackageInlineForm


class QuoteSiteModel(SiteModel):
    model_order = 510
    menu_label = MENU_LABEL_QUOTE

    recent_allowed = True
    fields = (
        ('reference', 'agency', 'seller'),
        ('status', 'currency'),
        ('date_from', 'date_to'), 'id',
        'mail_from', 'mail_to', 'mail_cc',
        'mail_bcc', 'mail_subject', 'mail_body', 'submit_action'
    )
    list_display = ('reference', 'agency', 'date_from',
                    'date_to', 'status', 'currency', 'seller')
    top_filters = ('reference', ('date_from', DateTopFilter),
                   'status', ('seller', SellerTopFilter),
                   'agency')
    ordering = ('date_from', 'reference',)
    readonly_fields = ('date_from', 'date_to', 'status')
    list_details_template = 'booking/quote_details.html'
    change_details_template = 'booking/quote_details.html'
    inlines = [QuotePaxVariantInline]
    form = QuoteForm
    add_form_template = 'booking/quote_change_form.html'
    change_form_template = 'booking/quote_change_form.html'
    save_as = True

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
            fields=['pax_name', 'pax_age', 'pax_group', 'is_price_free'],
            extra=1,
        )
        formset = None
        if request.method == 'POST':
            quote_id = request.POST.get('quote_id', None)
            if quote_id:
                formset = PaxFormSet(request.POST)
                if formset.is_valid():
                    booking, msg = BookingServices.build_booking_from_quote(
                        quote_id, formset.cleaned_data, request.user)
                    if booking:
                        return redirect(reverse('common:booking_booking_change',
                                                args=[booking.id]))
                    else:
                        self.message_user(request, msg, messages.ERROR)
                else: # Error de validacion del form. Repeat
                    self.message_user(request, 'Pax info missing', messages.ERROR)
            else:
                self.message_user(request, 'Quote Missing', messages.ERROR)

        if not formset:
            formset = PaxFormSet(queryset=BookingPax.objects.none())

        context = {}
        context.update(self.get_model_extra_context(request))
        context.update(extra_context or {})
        context.update({'title': 'Build Booking'})
        context.update({'quote_id': id})
        context.update({'formset': formset})
        return render(request, 'booking/quote_booking_build.html', context)

    def save_related(self, request, form, formsets, change):
        with transaction.atomic(savepoint=False):
            super(QuoteSiteModel, self).save_related(request, form, formsets, change)
            if not "_saveasnew" in request.POST:
                obj = self.save_form(request, form, change)
                BookingServices.sync_quote_paxvariants(obj)

    def response_add_saveasnew(
            self, request, obj, msg_dict, obj_url, preserved_filters, opts, post_url_continue=None):
        id = request.POST.get('id')
        if id and obj:
            BookingServices.clone_quote_services(id, obj)

        return super(QuoteSiteModel, self).response_add_saveasnew(
            request, obj, msg_dict, obj_url, preserved_filters, opts, post_url_continue)


    @csrf_protect_m
    def changeform_view(self, request, object_id=None,
                        form_url='', extra_context=None):
        if request.method == 'POST':
            if 'submit_action' in request.POST and request.POST['submit_action'] == '_send_mail':
                quote = Quote.objects.get(id=object_id)
                mail_from = request.POST.get('mail_from')
                to_list = _build_mail_address_list(request.POST.get('mail_to'))
                cc_list = _build_mail_address_list(request.POST.get('mail_cc'))
                bcc_list = _build_mail_address_list(request.POST.get('mail_bcc'))
                if not to_list or not mail_from:
                    messages.add_message(request=request,
                                         level=messages.ERROR,
                                         message='missing Remitent or Destination address',
                                         extra_tags='',
                                         fail_silently=False)
                    return redirect(reverse('common:booking_quote_change',
                                            args=[object_id]))
                email = EmailMessage(
                    from_email=mail_from,
                    to=to_list,
                    cc=cc_list,
                    bcc=bcc_list,
                    subject=request.POST.get('mail_subject'),
                    body=request.POST.get('mail_body'))

                email.content_subtype = "html"
                email.send()

                messages.add_message(
                    request=request, level=messages.SUCCESS,
                    message='Quote sent successfully.',
                    extra_tags='', fail_silently=False)
                return redirect(reverse('common:booking_quote_change',
                                        args=[object_id]))

            else:
                # default POST request. call Super
                return super(QuoteSiteModel, self).changeform_view(
                    request=request,
                    object_id=object_id,
                    form_url=form_url,
                    extra_context=extra_context)
        else:
            # GET request
            if not extra_context:
                extra_context = dict()
            if object_id:
                quote = Quote.objects.get(id=object_id)
                form = EmailPopupForm(
                    initial={'mail_from': default_requests_mail_from(request),
                             'mail_to': default_quote_mail_to(request, quote),
                             'mail_cc': '',
                             'mail_bcc': default_mail_bcc(request),
                             'mail_subject': default_quote_mail_subject(
                                 request, quote),
                             'mail_body': default_quote_mail_body(request,
                                                                  quote)})
            else:
                form = EmailPopupForm()
            extra_context.update({
                'modal_title': 'Send Quote Mail',
                'form': form,
            })
            return super(QuoteSiteModel, self).changeform_view(
                request=request,
                object_id=object_id,
                form_url=form_url,
                extra_context=extra_context)


class QuoteServiceSiteModel(SiteModel):
    def response_post_delete(self, request, obj):
        if hasattr(obj, 'quote') and obj.quote:
            return redirect(reverse('common:booking_quote_change', args=[obj.quote.pk]))
        quote = request.POST.get('quote')
        if quote:
            return redirect(reverse('common:booking_quote_change', args=[quote]))
        return super(QuoteServiceSiteModel, self).response_post_delete(request, obj)

    def response_post_save_add(self, request, obj):
        if hasattr(obj, 'quote') and obj.quote:
            return redirect(reverse('common:booking_quote_change', args=[obj.quote.pk]))
        quote = request.POST.get('quote')
        if quote:
            return redirect(reverse('common:booking_quote_change', args=[quote]))
        return super(QuoteServiceSiteModel, self).response_post_save_add(request, obj)

    def response_post_save_change(self, request, obj):
        if hasattr(obj, 'quote') and obj.quote:
            return redirect(reverse('common:booking_quote_change', args=[obj.quote.pk]))
        quote = request.POST.get('quote')
        if quote:
            return redirect(reverse('common:booking_quote_change', args=[quote]))
        return super(QuoteServiceSiteModel, self).response_post_save_change(request, obj)

    def delete_model(self, request, obj):
        with transaction.atomic(savepoint=False):
            super(QuoteServiceSiteModel, self).delete_model(request, obj)
            BookingServices.update_quote_paxvariants_amounts(obj)
            BookingServices.update_quote(obj)

    def save_related(self, request, form, formsets, change):
        with transaction.atomic(savepoint=False):
            super(QuoteServiceSiteModel, self).save_related(request, form, formsets, change)
            obj = self.save_form(request, form, change)
            BookingServices.update_quote_paxvariants_amounts(obj)


class QuoteAllotmentSiteModel(QuoteServiceSiteModel):
    model_order = 520
    menu_label = MENU_LABEL_QUOTE
    menu_group = MENU_GROUP_LABEL_SERVICES

    fields = (
        'quote', ('service', 'search_location', 'status'), ('datetime_from', 'nights', 'datetime_to'),
        'room_type', 'board_type', 'provider', 'id')
    list_display = ('quote', 'service', 'datetime_from', 'datetime_to', 'status',)
    top_filters = ('service', 'quote__reference', ('datetime_from', DateTopFilter), 'status',)
    ordering = ('datetime_from', 'quote__reference', 'service__name',)
    form = QuoteAllotmentForm
    add_form_template = 'booking/quoteallotment_change_form.html'
    change_form_template = 'booking/quoteallotment_change_form.html'
    inlines = [QuoteServicePaxVariantInline]


class QuoteTransferSiteModel(QuoteServiceSiteModel):
    model_order = 530
    menu_label = MENU_LABEL_QUOTE
    menu_group = MENU_GROUP_LABEL_SERVICES

    fields = (
        'quote', ('service', 'search_location', 'status'), ('datetime_from', 'datetime_to'),
        ('location_from', 'location_to'), 'service_addon',
        'provider', 'id')
    list_display = ('quote', 'name', 'service_addon', 'datetime_from', 'status',)
    top_filters = ('service', 'quote__reference', ('datetime_from', DateTopFilter), 'status',)
    ordering = ('datetime_from', 'quote__reference', 'service__name',)
    form = QuoteTransferForm
    add_form_template = 'booking/quotetransfer_change_form.html'
    change_form_template = 'booking/quotetransfer_change_form.html'
    inlines = [QuoteServicePaxVariantInline]


class QuoteExtraSiteModel(QuoteServiceSiteModel):
    model_order = 540
    menu_label = MENU_LABEL_QUOTE
    menu_group = MENU_GROUP_LABEL_SERVICES

    fields = (
        'quote',
        ('service', 'search_location', 'status'), ('datetime_from', 'datetime_to', 'time'),
        ('service_addon'), ('quantity', 'parameter'),
        ('pickup_office', 'dropoff_office',),
        'provider', 'description', 'id')
    list_display = (
        'quote', 'service', 'service_addon', 'quantity', 'parameter',
        'datetime_from', 'datetime_to', 'time', 'status',)
    top_filters = ('service', 'quote__reference', ('datetime_from', DateTopFilter), 'status',)
    ordering = ('datetime_from', 'quote__reference', 'service__name',)
    form = QuoteExtraForm
    add_form_template = 'booking/quoteextra_change_form.html'
    change_form_template = 'booking/quoteextra_change_form.html'
    inlines = [QuoteServicePaxVariantInline]


class QuotePackagePaxVariantInline(CommonStackedInline):
    model = QuoteServicePaxVariant
    extra = 0
    fields = [
        ('quote_pax_variant'),
        ('free_cost_single', 'free_price_single'),
        ('free_cost_double', 'free_price_double'),
        ('free_cost_triple', 'free_price_triple'),
        ('free_cost_qdrple', 'free_price_qdrple'),
        ('cost_single_amount', 'price_single_amount', 'utility_percent_single', 'utility_single'),
        ('cost_double_amount', 'price_double_amount', 'utility_percent_double', 'utility_double'),
        ('cost_triple_amount', 'price_triple_amount', 'utility_percent_triple', 'utility_triple'),
        ('cost_qdrple_amount', 'price_qdrple_amount', 'utility_percent_qdrple', 'utility_qdrple')
    ]
    readonly_fields = [
        'cost_single_amount', 'price_single_amount', 'utility_percent_single', 'utility_single',
        'cost_double_amount', 'price_double_amount', 'utility_percent_double', 'utility_double',
        'cost_triple_amount', 'price_triple_amount', 'utility_percent_triple', 'utility_triple',
        'cost_qdrple_amount', 'price_qdrple_amount', 'utility_percent_qdrple', 'utility_qdrple',
    ]
    verbose_name_plural = 'Paxes Variants'
    can_delete = False

    def has_add_permission(self,request):
        return False


class QuotePackageSiteModel(QuoteServiceSiteModel):
    model_order = 550
    menu_label = MENU_LABEL_QUOTE
    menu_group = MENU_GROUP_LABEL_SERVICES

    fields = (
        'quote',
        ('service', 'search_location', 'status'),
        ('datetime_from', 'datetime_to'),
        ('provider', 'price_by_package_catalogue'), 'id')
    list_display = (
        'quote', 'service', 'datetime_from', 'datetime_to', 'status',)
    top_filters = ('service', 'quote__reference',
                   ('datetime_from', DateTopFilter), 'status',)
    ordering = ('datetime_from', 'quote__reference', 'service__name',)
    form = QuotePackageForm
    add_form_template = 'booking/quotepackage_change_form.html'
    change_form_template = 'booking/quotepackage_change_form.html'
    readonly_fields = ['datetime_to', 'status']
    list_details_template = 'booking/quotepackage_details.html'
    change_details_template = 'booking/quotepackage_details.html'
    inlines = [QuotePackagePaxVariantInline]

    def delete_model(self, request, obj):
        BookingServices.delete_quotepackage_services(obj)
        super(QuotePackageSiteModel, self).delete_model(request, obj)

    def save_related(self, request, form, formsets, change):
        with transaction.atomic(savepoint=False):
            super(QuotePackageSiteModel, self).save_related(request, form, formsets, change)
            obj = self.save_form(request, form, change)
            BookingServices.sync_quotepackage_paxvariants(obj)


class QuotePackageServiceSiteModel(SiteModel):
    def response_post_delete(self, request, obj):
        if hasattr(obj, 'quote_package') and obj.quote_package:
            return redirect(
                reverse('common:booking_quotepackage_change', args=[obj.quote_package.pk]))
        quote_package = request.POST.get('quote_package')
        if quote_package:
            return redirect(
                reverse('common:booking_quotepackage_change', args=[quote_package]))
        return super(QuotePackageServiceSiteModel, self).response_post_delete(request, obj)

    def response_post_save_add(self, request, obj):
        if hasattr(obj, 'quote_package') and obj.quote_package:
            return redirect(
                reverse('common:booking_quotepackage_change', args=[obj.quote_package.pk]))
        quote_package = request.POST.get('quote_package')
        if quote_package:
            return redirect(
                reverse('common:booking_quotepackage_change', args=[quote_package]))
        return super(QuotePackageServiceSiteModel, self).response_post_save_add(request, obj)

    def response_post_save_change(self, request, obj):
        if hasattr(obj, 'quote_package') and obj.quote_package:
            return redirect(
                reverse('common:booking_quotepackage_change', args=[obj.quote_package.pk]))
        quote_package = request.POST.get('quote_package')
        if quote_package:
            return redirect(
                reverse('common:booking_quotepackage_change', args=[quote_package]))
        return super(QuotePackageServiceSiteModel, self).response_post_save_change(request, obj)

    def delete_model(self, request, obj):
        with transaction.atomic(savepoint=False):
            super(QuotePackageServiceSiteModel, self).delete_model(request, obj)
            BookingServices.update_quotepackage_paxvariants_amounts(obj)
            BookingServices.update_quotepackage(obj)

    def save_related(self, request, form, formsets, change):
        with transaction.atomic(savepoint=False):
            super(QuotePackageServiceSiteModel, self).save_related(request, form, formsets, change)
            obj = self.save_form(request, form, change)
            BookingServices.update_quotepackage_paxvariants_amounts(obj)


class QuotePackageServicePaxVariantInline(CommonStackedInline):
    model = QuotePackageServicePaxVariant
    extra = 0
    fields = [
        ('quotepackage_pax_variant'),
        ('manual_costs', 'manual_prices'),
        ('cost_single_amount', 'price_single_amount', 'utility_percent_single', 'utility_single'),
        ('cost_double_amount', 'price_double_amount', 'utility_percent_double', 'utility_double'),
        ('cost_triple_amount', 'price_triple_amount', 'utility_percent_triple', 'utility_triple'),
        ('cost_qdrple_amount', 'price_qdrple_amount', 'utility_percent_qdrple', 'utility_qdrple'),
    ]
    verbose_name_plural = 'Paxes Variants'
    can_delete = False

    readonly_fields = [
        'utility_percent_single', 'utility_percent_double',
        'utility_percent_triple', 'utility_percent_qdrple',
        'utility_single', 'utility_double', 'utility_triple', 'utility_qdrple']

    def has_add_permission(self, request):
        return False

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super(QuotePackageServicePaxVariantInline, self).get_readonly_fields(request, obj) or []

        if not request.user.has_perm("booking.change_amounts"):
            return readonly_fields + [
                'manual_costs', 'manual_prices',
                'cost_single_amount', 'price_single_amount', 'utility_percent_single', 'utility_single',
                'cost_double_amount', 'price_double_amount', 'utility_percent_double', 'utility_double',
                'cost_triple_amount', 'price_triple_amount', 'utility_percent_triple', 'utility_triple',
                'cost_qdrple_amount', 'price_qdrple_amount', 'utility_percent_qdrple', 'utility_qdrple',
            ]

        return readonly_fields


class QuotePackageAllotmentSiteModel(QuotePackageServiceSiteModel):
    model_order = 560
    menu_label = MENU_LABEL_QUOTE
    menu_group = MENU_GROUP_LABEL_PACKAGE_SERVICES

    fields = (
        'quote_package', ('service', 'search_location', 'status'), ('datetime_from', 'datetime_to'),
        'room_type', 'board_type', 'provider', 'id')
    list_display = ('quote_package', 'service', 'datetime_from', 'datetime_to', 'status',)
    top_filters = ('service', 'quote_package__quote__reference', ('datetime_from', DateTopFilter), 'status',)
    ordering = ('datetime_from', 'quote_package__quote__reference', 'service__name',)
    form = QuotePackageAllotmentForm
    add_form_template = 'booking/quotepackageallotment_change_form.html'
    change_form_template = 'booking/quotepackageallotment_change_form.html'
    inlines = [QuotePackageServicePaxVariantInline]


class QuotePackageTransferSiteModel(QuotePackageServiceSiteModel):
    model_order = 570
    menu_label = MENU_LABEL_QUOTE
    menu_group = MENU_GROUP_LABEL_PACKAGE_SERVICES

    fields = (
        'quote_package', ('service', 'search_location', 'status'), ('datetime_from', 'datetime_to'),
        ('location_from', 'location_to'), 'service_addon',
        'provider', 'id')
    list_display = ('quote_package', 'name', 'service_addon', 'datetime_from', 'status',)
    top_filters = ('service', 'quote_package__quote__reference', ('datetime_from', DateTopFilter), 'status',)
    ordering = ('datetime_from', 'quote_package__quote__reference', 'service__name',)
    form = QuotePackageTransferForm
    add_form_template = 'booking/quotepackagetransfer_change_form.html'
    change_form_template = 'booking/quotepackagetransfer_change_form.html'
    inlines = [QuotePackageServicePaxVariantInline]


class QuotePackageExtraSiteModel(QuotePackageServiceSiteModel):
    model_order = 580
    menu_label = MENU_LABEL_QUOTE
    menu_group = MENU_GROUP_LABEL_PACKAGE_SERVICES

    fields = (
        'quote_package',
        ('service', 'search_location', 'status'), ('datetime_from', 'datetime_to', 'time'),
        ('service_addon'), ('quantity', 'parameter'),
        ('pickup_office', 'dropoff_office',),
        'provider', 'id')
    list_display = (
        'quote_package', 'service', 'service_addon', 'quantity', 'parameter',
        'datetime_from', 'datetime_to', 'time', 'status',)
    top_filters = ('service', 'quote_package__quote__reference', ('datetime_from', DateTopFilter), 'status',)
    ordering = ('datetime_from', 'quote_package__quote__reference', 'service__name',)
    form = QuotePackageExtraForm
    add_form_template = 'booking/quotepackageextra_change_form.html'
    change_form_template = 'booking/quotepackageextra_change_form.html'
    inlines = [QuotePackageServicePaxVariantInline]


# Starts Booking Section

class BookingPaxInline(TabularInline):
    model = BookingPax
    fields = ['pax_name', 'pax_group', 'pax_age', 'is_price_free', 'version']
    verbose_name_plural = 'Rooming List'
    extra = 0
    ordering = ('pax_group', 'pax_name')

    def get_max_num(self, request, obj=None, **kwargs):
        adding = obj is None or obj.id is None
        if adding:
            return super(BookingPaxInline, self).get_max_num(request, obj, **kwargs)
        else:
            return 0


class BookingServicePaxInline(TabularInline):
    model = BookingServicePax
    fields = ['booking_pax', 'group', 'is_cost_free', 'is_price_free', 'force_adult', 'version']
    verbose_name_plural = 'Service Rooming List'
    extra = 0
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


class BookingSiteModel(SiteModel):
    model_order = 1110
    menu_label = MENU_LABEL_BOOKING

    recent_allowed = True
    fieldsets = (
        (None, {
            'fields': (
                ('seller', 'internal_reference', 'details'),
                ('name', 'reference', 'status'),
                ('agency', 'agency_contact'),
                ('date_from', 'date_to'),
                ('is_package_price',),
                ('package_sgl_price_amount', 'package_dbl_price_amount'),
                ('package_tpl_price_amount', 'package_qpl_price_amount'),
                ('cost_amount', 'price_amount', 'utility_percent', 'utility'),
                'id', 'version',
                'mail_from', 'mail_to', 'mail_cc', 'mail_bcc',
                'mail_subject', 'mail_body', 'submit_action')
        }),
        ('General Notes', {'fields': ('p_notes',),
                           'classes': ('collapse', 'wide')})
    )
    list_display = ('name', 'internal_reference', 'agency',
                    'reference', 'date_from',
                    'date_to', 'status', 'cost_amount',
                    'price_amount', 'utility_percent', 'utility',
                    'invoiced_amount', 'has_notes')
    top_filters = (('name', 'Booking Name'), 'reference', 'agency',
                   ('date_from', DateTopFilter), 'rooming_list__pax_name',
                   (InternalReferenceTopFilter),
                   (CancelledTopFilter), 'seller', 'invoice__document_number')
    list_per_page = 50
    ordering = ['date_from', 'date_to', 'reference']
    readonly_fields = ('date_from', 'date_to', 'status',
                       'cost_amount', 'price_amount', 'utility_percent', 'utility',
                       'internal_reference', 'details')
    list_details_template = 'booking/booking_details.html'
    change_details_template = 'booking/booking_details.html'
    inlines = [BookingPaxInline]
    form = BookingForm
    add_form_template = 'booking/booking_change_form.html'
    change_form_template = 'booking/booking_change_form.html'
    totalsum_list = ['cost_amount', 'price_amount']
    save_as = True

    def details(self, obj):
        return '[%s pax]' % obj.rooming_list.count()

    def get_changelist(self, request, **kwargs):
        """
        Returns the ChangeList class for use on the changelist page.
        """
        return StatusChangeList

    def get_urls(self):

        info = self.model._meta.app_label, self.model._meta.model_name
        urls = super(BookingSiteModel, self).get_urls()
        urlpatterns = [
            self.build_url(r'^voucher/(?P<id>\d+)/config/?',
                           self.config_vouchers,
                           '%s_%s_config_vouchers' % info),
            self.build_url(r'^(?P<id>\d+)/add_pax/?',
                           self.add_booking_pax,
                           '%s_%s_add_booking_pax' % info),
        ]
        return urlpatterns + urls

    def config_vouchers(self, request, id, extra_context=None):
        """ this handles configuration form to build vouchers"""

        def _add_initial_email_form(request, booking, context):
            """ helper method to add initial email form to context"""
            contact_email = ''
            if booking.agency_contact:
                contact_email = booking.agency_contact.email
            email_form = EmailPopupForm(
                initial={'mail_from': request.user.email,
                         'mail_to': contact_email,
                         'mail_cc': default_mail_cc(request, booking),
                         'mail_bcc': default_vouchers_mail_bcc(request),
                         'mail_subject': default_vouchers_mail_subject(
                             request, booking),
                         'mail_body': default_vouchers_mail_body(
                             request, booking)})
            context.update({
                'email_form': email_form,
            })
        context = {}
        context.update({'title': 'Vouchers Booking'})
        bk = Booking.objects.get(id=id)
        if request.method == 'GET':
            form = VouchersConfigForm()
            context.update(self.get_model_extra_context(request))
            context.update(extra_context or {})
            context.update({'current': bk})
            context.update({'form': form})
            _add_initial_email_form(request, bk, context)
            context.update({
                'modal_title': 'Vouchers Email',
            })
            return render(request, 'booking/voucher_config.html', context)
        else:
            ids = request.POST.getlist('pk', [])
            if not ids:
                messages.add_message(request, level=messages.ERROR,
                                     message='You havent choose any service')
            office = request.POST.get('office', None)
            if not office:
                messages.add_message(request, level=messages.ERROR,
                                     message='Please specify Office')
            if not office or not ids:
                form = VouchersConfigForm()
                context.update(self.get_model_extra_context(request))
                context.update(extra_context or {})
                context.update({'current': bk})
                context.update({'form': form})
                _add_initial_email_form(request, bk, context)
                return render(request, 'booking/voucher_config.html', context)

            context.update({
                'uid': request.user.pk,
                'office': Office.objects.get(id=office)
            })
            # use this two parameters to call methods to build pdf
            # it should return the pisa object to add it to the response object
            result, pdf = self._build_vouchers(id, ids, context)
            if result.err:
                # there was an error. show an error message
                messages.add_message(
                    request=request, level=messages.ERROR,
                    message='Error generating PDF - %s' % (result.err),
                    extra_tags='', fail_silently=False)
                form = VouchersConfigForm()
                context.update(self.get_model_extra_context(request))
                context.update(extra_context or {})
                context.update({'current': Booking.objects.get(id=id)})
                context.update({'form': form})
                return render(request, 'booking/voucher_config.html', context)
            submit_action = request.POST.get('submit_action')
            if submit_action == '_send_mail':
                mail_from = request.POST.get('mail_from')
                to_list = _build_mail_address_list(request.POST.get('mail_to'))
                cc_list = _build_mail_address_list(request.POST.get('mail_cc'))
                bcc_list = _build_mail_address_list(request.POST.get('mail_bcc'))
                email = EmailMessage(
                    from_email=mail_from,
                    to=to_list,
                    cc=cc_list,
                    bcc=bcc_list,
                    subject=request.POST.get('mail_subject'),
                    body=request.POST.get('mail_body'))

                email.attach('vouchers.pdf', pdf.getvalue(), 'application/pdf')
                email.content_subtype = "html"
                email.send()

                messages.add_message(
                    request=request, level=messages.SUCCESS,
                    message='Vouchers mail  sent successfully.',
                    extra_tags='', fail_silently=False)
                return redirect(reverse('common:booking_booking_change', args=[id]))
            return HttpResponse(pdf.getvalue(), content_type='application/pdf')

    def add_booking_pax(self, request, id, extra_context=None):
        """
        this will show a config form to add multiple pax to rooming
        of a booking and select services to update
        """
        PaxFormSet = modelformset_factory(
            model=BookingPax,
            fields=['pax_name', 'pax_age', 'pax_group', 'is_price_free'],
            extra=1,
        )
        if request.method == 'POST':
            formset = PaxFormSet(request.POST, prefix='form')
            bookingservices = BookingService.objects.filter(booking=id)
            current_rooming = BookingPax.objects.filter(booking=id)
            if formset.is_valid():
                booking = Booking.objects.get(pk=id)
                try:
                    BookingServices.add_paxes_to_booking(
                        booking,
                        formset.cleaned_data,
                        request.POST.getlist('pk'))
                    return redirect(reverse('common:booking_booking_change', args=[id]))
                except ValidationError as error:
                    messages.add_message(
                        request=request, level=messages.ERROR,
                        message=error.message)
            else:
                # some data missing. show error message
                messages.add_message(request, messages.ERROR,
                                     'Check new pax data')
        else:
            # GET request
            formset = PaxFormSet(prefix='form',
                                 queryset=BookingPax.objects.none())
            bookingservices = BookingService.objects.filter(booking=id)
            current_rooming = BookingPax.objects.filter(booking=id)

        context = {}
        context.update({'title': 'Add Pax to Rooming'})
        context.update(self.get_model_extra_context(request))
        context.update(extra_context or {})
        context.update({'booking_id': id})
        context.update({'formset': formset})
        context.update({'services': bookingservices or []})
        context.update({'rooming': current_rooming or []})
        return render(request, 'booking/booking_add_pax.html', context)

    def _build_vouchers(self, bk, service_ids, context):
        # This helper builds the PDF object with all vouchers
        template = get_template("booking/pdf/voucher.html")
        booking = Booking.objects.get(id=bk)
        services = BookingService.objects.filter(id__in=service_ids). \
                   order_by('datetime_from', 'time', 'datetime_to'). \
                   prefetch_related('rooming_list')
        objs = _get_voucher_services(services)
        context.update({'pagesize': 'Letter',
                        'booking': booking,
                        'services': objs})
        html = template.render(context)
        pdf = StringIO()
        if PY2:
            html = html.encode('UTF-8')
        result = pisa.pisaDocument(StringIO(html), dest=pdf,
                                   link_callback=_fetch_resources)
        return result, pdf

    def response_change(self, request, obj):
        bookingservices = BookingServices. \
                          find_bookingservices_with_different_amounts(obj)
        if bookingservices:
            # make a new GET request to show list of services to update
            redirect_url = reverse('bookingservice_update', args=[obj.id])
            if "_continue" in request.POST or "_saveasnew" in request.POST or "_addanother" in request.POST:
                redirect_url = '{}?{}'.format(redirect_url, 'stay_on_booking=1')
            return redirect(redirect_url)

        return super(BookingSiteModel, self).response_change(request, obj)

    # TODO remove this in favor of booking.views.BookingServiceUpdateView
    def select_bookingservices_view(self, request,
                                    booking, bookingservices=None):

        # for now do nothing here
        super(BookingSiteModel, self).response_change(request, booking)

        if request.method == 'POST' and 'service_selection' in request.POST:
            selected_bookingservices = list()
            BookingServices.update_bookingservices_amounts(selected_bookingservices)
            booking = selected_bookingservices[0].booking
            super(BookingSiteModel, self).response_change(request, booking)
        # show selection view

    def save_related(self, request, form, formsets, change):
        if "_saveasnew" in request.POST:
            for formset in formsets:
                formset.new_objects = []
                formset.changed_objects = []
                formset.deleted_objects = []
        else:
            with transaction.atomic(savepoint=False):
                super(BookingSiteModel, self).save_related(request, form, formsets, change)
                obj = self.save_form(request, form, change)
                BookingServices.update_booking_amounts(obj)

    @csrf_protect_m
    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        submit_action = request.POST.get('submit_action')
        if submit_action == '_send_mail':
            booking = Booking.objects.get(id=object_id)
            if not booking.invoice:
                messages.add_message(request, messages.ERROR , "Error Booking without Invoice")
                return redirect(reverse('common:booking_booking_change', args=[object_id]))

            invoice = booking.invoice
            result, pdf = self._build_invoice_pdf(invoice)
            if result.err:
                messages.add_message(request, messages.ERROR, "Failed Invoice PDF Generation - %s" % result.err)
                return redirect(reverse('common:booking_booking_change', args=[object_id]))
            mail_from = request.POST.get('mail_from')
            to_list = _build_mail_address_list(request.POST.get('mail_to'))
            cc_list = _build_mail_address_list(request.POST.get('mail_cc'))
            bcc_list = _build_mail_address_list(request.POST.get('mail_bcc'))
            email = EmailMessage(
                from_email=mail_from,
                to=to_list,
                cc=cc_list,
                bcc=bcc_list,
                subject=request.POST.get('mail_subject'),
                body=request.POST.get('mail_body'))

            email.attach('invoice.pdf', pdf.getvalue(), 'application/pdf')
            email.content_subtype = "html"
            email.send()

            messages.add_message(
                request=request, level=messages.SUCCESS,
                message='Invoice mail  sent successfully.',
                extra_tags='', fail_silently=False)
            return redirect(reverse('common:booking_booking_change', args=[object_id]))
        else:
            if not extra_context:
                extra_context = dict()
            if object_id:
                booking = Booking.objects.get(id=object_id)
                form = EmailPopupForm(
                    initial={'mail_from': default_requests_mail_from(request),
                             'mail_to': default_invoice_mail_to(request, booking),
                             'mail_cc': '',
                             'mail_bcc': default_invoice_mail_bcc(request),
                             'mail_subject': default_invoice_mail_subject(request, booking),
                             'mail_body': default_invoice_mail_body(request, booking),
                    })
            else:
                form = EmailPopupForm()
            extra_context.update({
                'modal_title': 'Provider Requests Mail',
                'form': form,
            })
            return super(BookingSiteModel, self).changeform_view(
                request=request,
                object_id=object_id,
                form_url=form_url,
                extra_context=extra_context)

    def _build_invoice_pdf(self, invoice):
        template = get_template("booking/pdf/invoice.html")
        details = BookingInvoiceDetail.objects.filter(invoice=invoice)
        lines = BookingInvoiceLine.objects.filter(invoice=invoice)
        partials = BookingInvoicePartial.objects.filter(invoice=invoice)
        context = {
            'pagesize': 'Letter',
            'invoice': invoice,
            'details': details,
            'lines': lines,
            'partials': partials,
        }
        html = template.render(context)
        if PY2:
            html = html.encode('UTF-8')
        pdf = StringIO()
        result = pisa.pisaDocument(StringIO(html), dest=pdf,
                                link_callback=_fetch_resources)
        return result, pdf

    def response_add_saveasnew(
            self, request, obj, msg_dict, obj_url, preserved_filters, opts, post_url_continue=None):
        id = request.POST.get('id')
        if id and obj:
            BookingServices.clone_booking_services(id, obj)

        return super(BookingSiteModel, self).response_add_saveasnew(
            request, obj, msg_dict, obj_url, preserved_filters, opts, post_url_continue)


def _build_mail_address_list(addresses):
    mail_address_list = addresses.replace(';', ' ').replace(',', ' ').split()
    mail_address_list = [mail_address for mail_address in mail_address_list if mail_address]
    return mail_address_list


class StatusChangeList(CommonChangeList):
    def row_classes_for_result(self, result):
        return BOOTSTRAP_STYLE_STATUS_MAPPING[result.status]


class ServiceChangeList(StatusChangeList):
    def url_for_result(self, result):
        pk = getattr(result, self.pk_attname)
        base_category = getattr(result, 'base_category')
        if base_category == BASE_BOOKING_SERVICE_CATEGORY_BOOKING_ALLOTMENT:
            model_name = 'bookingallotment'
        elif base_category == BASE_BOOKING_SERVICE_CATEGORY_BOOKING_TRANSFER:
            model_name = 'bookingtransfer'
        elif base_category == BASE_BOOKING_SERVICE_CATEGORY_BOOKING_EXTRA:
            model_name = 'bookingextra'
        elif base_category == BASE_BOOKING_SERVICE_CATEGORY_BOOKING_PACKAGE:
            model_name = 'bookingpackage'
        elif base_category == BASE_BOOKING_SERVICE_CATEGORY_PACKAGE_ALLOTMENT:
            model_name = 'bookingpackageallotment'
        elif base_category == BASE_BOOKING_SERVICE_CATEGORY_PACKAGE_TRANSFER:
            model_name = 'bookingpackagetransfer'
        elif base_category == BASE_BOOKING_SERVICE_CATEGORY_PACKAGE_EXTRA:
            model_name = 'bookingpackageextra'
        else:
            model_name = self.opts.app_label.model_name
        return reverse(
            '%s:%s_%s_change' % (
                self.model_admin.admin_site.site_namespace,
                self.opts.app_label,
                model_name),
            args=(quote(pk),),
            current_app=self.model_admin.admin_site.name)


class BaseServiceChangeList(ServiceChangeList):
    def get_queryset(self, request):
        # custom queryset to strip BookingPackageServices from list
        qs = super(BaseServiceChangeList, self).get_queryset(request)
        return qs.exclude(base_category=BASE_BOOKING_SERVICE_CATEGORY_BOOKING_PACKAGE)


class BookingBaseServiceSiteModel(SiteModel):
    model_order = 1260
    menu_label = MENU_LABEL_BOOKING
    menu_group = MENU_GROUP_LABEL_SERVICES

    readonly_fields = ['utility_percent', 'utility']

    fieldsets = (
        (None, {
            'fields': (
                ('name', 'status', 'conf_number'),
                ('service_addon'),
                ('manual_cost', 'provider'),
                'cost_amount', 'manual_price', 'price_amount',
                'utility_percent', 'utility')
        }),
        ('Notes', {'fields': ('p_notes', 'provider_notes'),
                   'classes': ('collapse', 'wide')})
    )

    list_display = ('name', 'datetime_from', 'datetime_to',
                    'service_provider', 'conf_number', 'full_booking_name',
                    'service_pax_count', 'booking_internal_reference',
                    'service_addon', 'cost_amount',
                    'price_amount', 'status', 'cost_amount_paid')
    top_filters = (('booking__name', 'Booking'),
                   ('name', 'Service'),
                   'booking__reference', 'conf_number',
                   ('booking__id', InternalReferenceTopFilter),
                   ('datetime_from', DateTopFilter), 'status', 'provider',
                   (CancelledTopFilter),
                   ('provider__is_private', 'Private'), PaidTopFilter)
    ordering = ('datetime_from', 'booking__reference', 'name',)
    list_details_template = 'booking/basebookingservice_details.html'
    change_details_template = 'booking/basebookingservice_details.html'

    def get_changelist(self, request, **kwargs):
        """
        Returns the ChangeList class for use on the changelist page.
        """
        return BaseServiceChangeList

    actions = ['coordinated_services', 'confirmed_services', ]

    def coordinated_services(self, request, queryset):
        services = list(queryset.all())
        BookingServices.set_services_status(services, SERVICE_STATUS_COORDINATED)

    coordinated_services.short_description = "Coordinated Services"

    def confirmed_services(self, request, queryset):
        services = list(queryset.all())
        BookingServices.set_services_status(services, SERVICE_STATUS_CONFIRMED)

    confirmed_services.short_description = "Confirmed Services"


class BookingServiceSiteModel(SiteModel):
    model_order = 1260
    menu_label = MENU_LABEL_BOOKING
    menu_group = MENU_GROUP_LABEL_SERVICES

    readonly_fields = ['utility_percent', 'utility']

    fieldsets = (
        (None, {
            'fields': (
                'booking', ('name', 'status', 'conf_number'),
                ('datetime_from', 'datetime_to', 'service_addon'),
                ('manual_cost', 'provider'),
                'cost_amount', 'manual_price', 'price_amount',
                'utility_percent', 'utility')
        }),
        ('Notes', {'fields': ('p_notes', 'v_notes', 'provider_notes'),
                   'classes': ('collapse', 'wide')})
    )

    list_display = ('name', 'datetime_from', 'datetime_to',
                    'service_provider', 'conf_number', 'booking_name',
                    'service_addon', 'cost_amount',
                    'price_amount', 'utility_percent', 'status',
                    'cost_amount_paid')
    top_filters = (('booking__name', 'Booking'),
                   ('name', 'Service'),
                   'booking__reference', 'conf_number',
                   ('booking__id', InternalReferenceTopFilter),
                   ('datetime_from', DateTopFilter), 'status', 'provider',
                   ('provider__is_private', 'Private'), CancelledTopFilter, PaidTopFilter)
    ordering = ('datetime_from', 'booking__reference', 'name',)
    list_details_template = 'booking/bookingservice_details.html'
    change_details_template = 'booking/bookingservice_details.html'

    def get_changelist(self, request, **kwargs):
        """
        Returns the ChangeList class for use on the changelist page.
        """
        return ServiceChangeList

    actions = ['coordinated_services', 'confirmed_services', ]

    def coordinated_services(self, request, queryset):
        services = list(queryset.all())
        BookingServices.set_services_status(services, SERVICE_STATUS_COORDINATED)

    coordinated_services.short_description = "Coordinated Services"

    def confirmed_services(self, request, queryset):
        services = list(queryset.all())
        BookingServices.set_services_status(services, SERVICE_STATUS_CONFIRMED)

    confirmed_services.short_description = "Confirmed Services"


class BaseBookingServiceSiteModel(SiteModel):

    custom_actions_template = 'booking/emails/email_button.html'

    def get_changelist(self, request, **kwargs):
        """
        Returns the ChangeList class for use on the changelist page.
        """
        return StatusChangeList

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super(BaseBookingServiceSiteModel, self).get_readonly_fields(request, obj) or []

        if not request.user.has_perm("booking.change_amounts"):
            return readonly_fields + ['manual_cost', 'cost_amount', 'manual_price', 'price_amount']

        return readonly_fields

    def response_post_delete(self, request, obj):
        if hasattr(obj, 'booking') and obj.booking:
            return redirect(reverse('common:booking_booking_change', args=[obj.booking.pk]))
        booking = request.POST.get('booking')
        if booking:
            return redirect(reverse('common:booking_booking_change', args=[booking]))
        return super(BaseBookingServiceSiteModel, self).response_post_delete(request, obj)

    def response_post_save_add(self, request, obj):
        if hasattr(obj, 'booking') and obj.booking:
            return redirect(reverse('common:booking_booking_change', args=[obj.booking.pk]))
        booking = request.POST.get('booking')
        if booking:
            return redirect(reverse('common:booking_booking_change', args=[booking]))
        return super(BaseBookingServiceSiteModel, self).response_post_save_add(request, obj)

    def response_post_save_change(self, request, obj):
        if hasattr(obj, 'booking') and obj.booking:
            return redirect(reverse('common:booking_booking_change', args=[obj.booking.pk]))
        booking = request.POST.get('booking')
        if booking:
            return redirect(reverse('common:booking_booking_change', args=[booking]))
        return super(BaseBookingServiceSiteModel, self).response_post_save_change(request, obj)

    def delete_model(self, request, obj):
        with transaction.atomic(savepoint=False):
            super(BaseBookingServiceSiteModel, self).delete_model(request, obj)
            BookingServices.update_booking_amounts(obj)
            BookingServices.update_booking(obj)

    def save_model(self, request, obj, form, change):
        # overrides base class method
        pax_list = self.build_inlines(request, obj)[0]
        BookingServices.setup_bookingservice_amounts(obj, pax_list)
        obj.save()

    def save_related(self, request, form, formsets, change):
        with transaction.atomic(savepoint=False):
            super(BaseBookingServiceSiteModel, self).save_related(request, form, formsets, change)
            obj = self.save_form(request, form, change)
            BookingServices.update_bookingservice_amounts(obj)
            BookingServices.update_bookingservice_description(obj)

    @csrf_protect_m
    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        submit_action = request.POST.get('submit_action')
        if submit_action == '_send_mail':
            mail_from = request.POST.get('mail_from')
            to_list = _build_mail_address_list(request.POST.get('mail_to'))
            cc_list = _build_mail_address_list(request.POST.get('mail_cc'))
            bcc_list = _build_mail_address_list(request.POST.get('mail_bcc'))
            email = EmailMessage(
                from_email=mail_from,
                to=to_list,
                cc=cc_list,
                bcc=bcc_list,
                subject=request.POST.get('mail_subject'),
                body=request.POST.get('mail_body'))
            email.send()
            messages.add_message(
                request=request, level=messages.SUCCESS,
                message='Requests mail  sent successfully.',
                extra_tags='', fail_silently=False)
            return redirect(reverse('common:booking_%s_change' % self.model._meta.model_name, args=[object_id]))
        else:
            if object_id:
                bs = BookingService.objects.get(pk=object_id)
                if not extra_context:
                    extra_context = dict()
                extra_context.update({
                    'modal_title': 'Provider Requests Mail',
                    'default_mail_from': default_requests_mail_from(request, bs.provider, bs.booking),
                    'default_mail_to': default_requests_mail_to(request, bs.provider, bs.booking),
                    'default_mail_cc': '',
                    'default_mail_bcc': default_requests_mail_bcc(request, bs.provider, bs.booking),
                    'default_mail_subject': default_requests_mail_subject(request, bs.provider, bs.booking),
                    'default_mail_body': default_requests_mail_body(request, bs.provider, bs.booking),
                })

            return super(BaseBookingServiceSiteModel, self).changeform_view(request, object_id, form_url, extra_context)

    @csrf_protect_m
    def delete_view(self, request, object_id, extra_context=None):
        bookingservice = BookingService.objects.get(pk=object_id)
        if bookingservice.status == SERVICE_STATUS_PENDING:
            return super(BaseBookingServiceSiteModel, self).delete_view(request, object_id, extra_context)
        messages.add_message(
            request=request, level=messages.ERROR,
            message='Only Pending Service can be Deleted. You can set Status to Cancelled.',
            extra_tags='', fail_silently=False)
        return redirect(reverse(
            'common:%s_%s_change' % (self.model._meta.app_label, self.model._meta.model_name),
            args=[object_id]))

    actions = ['coordinated_services', 'confirmed_services', ]

    def coordinated_services(self, request, queryset):
        services = list(queryset.all())
        BookingServices.set_services_status(services, SERVICE_STATUS_COORDINATED)

    coordinated_services.short_description = "Coordinated Services"

    def confirmed_services(self, request, queryset):
        services = list(queryset.all())
        BookingServices.set_services_status(services, SERVICE_STATUS_CONFIRMED)

    confirmed_services.short_description = "Confirmed Services"


class BookingPackageServiceSiteModel(SiteModel):

    custom_actions_template = 'booking/emails/email_button.html'

    def get_changelist(self, request, **kwargs):
        """
        Returns the ChangeList class for use on the changelist page.
        """
        return StatusChangeList

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super(BookingPackageServiceSiteModel, self).get_readonly_fields(request, obj) or []

        if not request.user.has_perm("booking.change_amounts"):
            return readonly_fields + ['manual_cost', 'cost_amount', 'manual_price', 'price_amount']

        return readonly_fields

    def response_post_delete(self, request, obj):
        if hasattr(obj, 'booking_package') and obj.booking_package:
            return redirect(reverse('common:booking_bookingpackage_change', args=[obj.booking_package.pk]))
        booking_package = request.POST.get('booking_package')
        if booking_package:
            return redirect(reverse('common:booking_bookingpackage_change', args=[booking_package]))
        return super(BookingPackageServiceSiteModel, self).response_post_delete(request, obj)

    def response_post_save_add(self, request, obj):
        if hasattr(obj, 'booking_package') and obj.booking_package:
            return redirect(reverse('common:booking_bookingpackage_change', args=[obj.booking_package.pk]))
        booking_package = request.POST.get('booking_package')
        if booking_package:
            return redirect(reverse('common:booking_bookingpackage_change', args=[booking_package]))
        return super(BookingPackageServiceSiteModel, self).response_post_save_add(request, obj)

    def response_post_save_change(self, request, obj):
        if hasattr(obj, 'booking_package') and obj.booking_package:
            return redirect(reverse('common:booking_bookingpackage_change', args=[obj.booking_package.pk]))
        booking_package = request.POST.get('booking_package')
        if booking_package:
            return redirect(reverse('common:booking_bookingpackage_change', args=[booking_package]))
        return super(BookingPackageServiceSiteModel, self).response_post_save_change(request, obj)

    def delete_model(self, request, obj):
        with transaction.atomic(savepoint=False):
            super(BookingPackageServiceSiteModel, self).delete_model(request, obj)
            BookingServices.update_bookingpackage_amounts(obj)
            BookingServices.update_bookingpackage(obj)

    def save_model(self, request, obj, form, change):
        # overrides base class method
        BookingServices.setup_bookingservice_amounts(obj)
        obj.save()

    def save_related(self, request, form, formsets, change):
        with transaction.atomic(savepoint=False):
            super(BookingPackageServiceSiteModel, self).save_related(request, form, formsets, change)
            obj = self.save_form(request, form, change)
            BookingServices.update_bookingpackage_amounts(obj)

    actions = ['coordinated_services', 'confirmed_services', ]

    def coordinated_services(self, request, queryset):
        services = list(queryset.all())
        BookingServices.set_services_status(services, SERVICE_STATUS_COORDINATED)

    coordinated_services.short_description = "Coordinated Services"

    def confirmed_services(self, request, queryset):
        services = list(queryset.all())
        BookingServices.set_services_status(services, SERVICE_STATUS_CONFIRMED)

    confirmed_services.short_description = "Confirmed Services"


    @csrf_protect_m
    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        submit_action = request.POST.get('submit_action')
        if submit_action == '_send_mail':
            mail_from = request.POST.get('mail_from')
            to_list = _build_mail_address_list(request.POST.get('mail_to'))
            cc_list = _build_mail_address_list(request.POST.get('mail_cc'))
            bcc_list = _build_mail_address_list(request.POST.get('mail_bcc'))
            email = EmailMessage(
                from_email=mail_from,
                to=to_list,
                cc=cc_list,
                bcc=bcc_list,
                subject=request.POST.get('mail_subject'),
                body=request.POST.get('mail_body'))
            email.send()
            messages.add_message(
                request=request, level=messages.SUCCESS,
                message='Requests mail  sent successfully.',
                extra_tags='', fail_silently=False)
            return redirect(reverse('common:booking_%s_change' % self.model._meta.model_name, args=[object_id]))
        else:
            if object_id:
                bps = BookingPackageService.objects.get(pk=object_id)
                provider = bps.provider
                if not provider:
                    provider = bps.booking_package.provider
                if not extra_context:
                    extra_context = dict()
                extra_context.update(
                    {
                        'modal_title': 'Provider Requests Mail',
                        'default_mail_from': default_requests_mail_from(request, provider, bps.booking()),
                        'default_mail_to': default_requests_mail_to(request, provider, bps.booking()),
                        'default_mail_cc': '',
                        'default_mail_bcc': default_requests_mail_bcc(request, provider, bps.booking()),
                        'default_mail_subject': default_requests_mail_subject(request, provider, bps.booking()),
                        'default_mail_body': default_requests_mail_body(request, provider, bps.booking()),
                    })

            return super(BookingPackageServiceSiteModel, self).changeform_view(request, object_id, form_url, extra_context)

    @csrf_protect_m
    def delete_view(self, request, object_id, extra_context=None):
        bookingpackageservice = BookingPackageService.objects.get(pk=object_id)
        if bookingpackageservice.status == SERVICE_STATUS_PENDING:
            return super(BookingPackageServiceSiteModel, self).delete_view(request, object_id, extra_context)
        messages.add_message(
            request=request, level=messages.ERROR,
            message='Only Pending Service can be Deleted. You can set Status to Cancelled.',
            extra_tags='', fail_silently=False)
        return redirect(reverse(
            'common:%s_%s_change' % (self.model._meta.app_label,
                                     self.model._meta.model_name),
            args=[object_id]))


class BookingAllotmentSiteModel(BaseBookingServiceSiteModel):
    model_order = 1210
    menu_label = MENU_LABEL_BOOKING
    menu_group = MENU_GROUP_LABEL_SERVICES

    readonly_fields = ['utility_percent', 'utility', 'details']

    fieldsets = (
        (None, {
            'fields': (
                ('booking', 'details'),
                ('service', 'search_location'), ('status', 'conf_number'),
                ('datetime_from', 'nights', 'datetime_to'),
                ('room_type', 'board_type',),
                ('manual_cost', 'provider'),
                'cost_amount', 'manual_price', 'price_amount',
                'utility_percent', 'utility', 'id', 'version',
                'submit_action', 'mail_from', 'mail_to', 'mail_cc',
                'mail_bcc', 'mail_subject', 'mail_body')
        }),
        ('Notes', {'fields': ('p_notes', 'v_notes', 'provider_notes'),
                   'classes': ('collapse', 'wide')})
    )

    list_display = ('name', 'datetime_from', 'datetime_to', 'provider',
                    'booking', 'conf_number', 'cost_amount',
                    'price_amount',
                    'status', 'cost_amount_paid')
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
    list_details_template = 'booking/bookingallotment_details.html'
    change_details_template = 'booking/bookingallotment_details.html'

    def details(self, obj):
        if obj.description:
            return obj.description + ' [%s pax]' % obj.rooming_list.count()
        return ''


class BookingPackageAllotmentSiteModel(BookingPackageServiceSiteModel):
    model_order = 1310
    menu_label = MENU_LABEL_BOOKING
    menu_group = MENU_GROUP_LABEL_PACKAGE_SERVICES

    readonly_fields = ['utility_percent', 'utility']

    fieldsets = (
        (None, {
            'fields': (
                'booking_package', ('service', 'search_location'), ('status', 'conf_number'),
                ('datetime_from', 'datetime_to'),
                ('room_type', 'board_type'),
                ('manual_cost', 'provider'),
                'cost_amount', 'manual_price', 'price_amount', 'utility_percent', 'utility', 'id', 'version',
                'submit_action', 'mail_from', 'mail_to', 'mail_cc', 'mail_bcc', 'mail_subject', 'mail_body')
        }),
        ('Notes', {'fields': ('p_notes', 'provider_notes'),
                   'classes': ('collapse', 'wide')})
    )
    list_display = ('booking_package', 'name', 'datetime_from',
                    'datetime_to', 'cost_amount', 'manual_cost',
                    'price_amount', 'manual_price', 'utility_percent',
                    'utility', 'status', 'cost_amount_paid')
    top_filters = (('booking_package__booking__name', 'Booking'),
                   ('name', 'Service'),
                   'booking_package__booking__reference', 'conf_number',
                   ('datetime_from', DateTopFilter), 'status')
    ordering = ('datetime_from', 'booking_package', 'service__name',)
    form = BookingPackageAllotmentForm
    add_form_template = 'booking/bookingpackageallotment_change_form.html'
    change_form_template = 'booking/bookingpackageallotment_change_form.html'
    list_details_template = 'booking/bookingpackageallotment_details.html'
    change_details_template = 'booking/bookingpackageallotment_details.html'


class BookingTransferSiteModel(BaseBookingServiceSiteModel):
    model_order = 1220
    menu_label = MENU_LABEL_BOOKING
    menu_group = MENU_GROUP_LABEL_SERVICES

    readonly_fields = ['utility_percent', 'utility']

    fieldsets = (
        (None, {
            'fields': (
                'booking', ('service', 'search_location'), ('status', 'conf_number'),
                ('datetime_from', 'datetime_to', 'time'),
                ('location_from', 'place_from'),
                ('pickup', 'schedule_from', 'schedule_time_from'),
                ('location_to', 'place_to'),
                ('dropoff', 'schedule_to', 'schedule_time_to'),
                'service_addon',
                ('manual_cost', 'provider'),
                'cost_amount', 'manual_price', 'price_amount', 'utility_percent', 'utility', 'id', 'version',
                'submit_action', 'mail_from', 'mail_to', 'mail_cc', 'mail_bcc', 'mail_subject', 'mail_body')
        }),
        ('Notes', {'fields': ('p_notes', 'v_notes', 'provider_notes'),
                   'classes': ('collapse', 'wide')})
    )
    list_display = ('booking', 'name', 'service_addon',
                    'datetime_from', 'time', 'cost_amount', 'manual_cost',
                    'price_amount', 'manual_price', 'utility_percent', 'utility', 'status')
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
    list_details_template = 'booking/bookingtransfer_details.html'
    change_details_template = 'booking/bookingtransfer_details.html'


class BookingPackageTransferSiteModel(BookingPackageServiceSiteModel):
    model_order = 1320
    menu_label = MENU_LABEL_BOOKING
    menu_group = MENU_GROUP_LABEL_PACKAGE_SERVICES

    readonly_fields = ['utility_percent', 'utility']

    fieldsets = (
        (None, {
            'fields': (
                'booking_package', ('service', 'search_location'), ('status', 'conf_number'),
                ('datetime_from', 'datetime_to', 'time'),
                ('location_from', 'place_from'),
                ('pickup', 'schedule_from', 'schedule_time_from'),
                ('location_to', 'place_to'),
                ('dropoff', 'schedule_to', 'schedule_time_to'),
                'service_addon',
                ('manual_cost', 'provider'),
                'cost_amount', 'manual_price', 'price_amount', 'utility_percent', 'utility', 'id', 'version',
                'submit_action', 'mail_from', 'mail_to', 'mail_cc', 'mail_bcc', 'mail_subject', 'mail_body')
        }),
        ('Notes', {'fields': ('p_notes', 'provider_notes'),
                   'classes': ('collapse', 'wide')})
    )
    list_display = ('booking_package', 'name', 'service_addon',
                    'datetime_from', 'time',
                    'cost_amount', 'manual_cost', 'price_amount',
                    'manual_price', 'utility_percent',
                    'utility', 'status', 'cost_amount_paid')
    top_filters = (
        ('booking_package__booking__name', 'Booking'),
        ('name', 'Service'),
        'booking_package__booking__reference', 'conf_number',
        ('datetime_from', DateTopFilter), 'status',)
    ordering = ('datetime_from', 'booking_package', 'service__name',)
    form = BookingPackageTransferForm
    add_form_template = 'booking/bookingpackagetransfer_change_form.html'
    change_form_template = 'booking/bookingpackagetransfer_change_form.html'
    list_details_template = 'booking/bookingpackagetransfer_details.html'
    change_details_template = 'booking/bookingpackagetransfer_details.html'


class BookingExtraSiteModel(BaseBookingServiceSiteModel):
    model_order = 1230
    menu_label = MENU_LABEL_BOOKING
    menu_group = MENU_GROUP_LABEL_SERVICES

    readonly_fields = ['utility_percent', 'utility']

    fieldsets = (
        (None, {
            'fields': (
                'booking', ('service', 'search_location'), ('status', 'conf_number'),
                ('datetime_from', 'nights', 'datetime_to', 'time'),
                'service_addon',
                ('quantity', 'parameter'),
                ('pickup_office', 'dropoff_office',),
                ('manual_cost', 'provider'),
                'cost_amount', 'manual_price', 'price_amount', 'utility_percent', 'utility', 'id', 'version',
                'submit_action', 'mail_from', 'mail_to', 'mail_cc', 'mail_bcc', 'mail_subject', 'mail_body')
        }),
        ('Notes', {'fields': ('p_notes', 'v_notes', 'provider_notes'),
                   'classes': ('collapse', 'wide')})
    )
    list_display = ('booking', 'name', 'service_addon', 'quantity', 'parameter',
                    'datetime_from', 'datetime_to', 'time',
                    'cost_amount', 'manual_cost', 'price_amount', 'manual_price', 'utility_percent', 'utility',
                    'status',)
    top_filters = ('booking__name', 'service', 'booking__reference',
                   ('datetime_from', DateTopFilter), 'status',)
    ordering = ('datetime_from', 'booking__reference', 'service__name',)
    form = BookingExtraForm
    add_form_template = 'booking/bookingextra_change_form.html'
    change_form_template = 'booking/bookingextra_change_form.html'
    inlines = [BookingServicePaxInline]
    list_details_template = 'booking/bookingextra_details.html'
    change_details_template = 'booking/bookingextra_details.html'


class BookingPackageExtraSiteModel(BookingPackageServiceSiteModel):
    model_order = 1330
    menu_label = MENU_LABEL_BOOKING
    menu_group = MENU_GROUP_LABEL_PACKAGE_SERVICES

    readonly_fields = ['utility_percent', 'utility']

    fieldsets = (
        (None, {
            'fields': (
                'booking_package', ('service', 'search_location'), ('status', 'conf_number'),
                ('datetime_from', 'datetime_to', 'time'),
                'service_addon',
                ('quantity', 'parameter'),
                ('pickup_office', 'dropoff_office',),
                ('manual_cost', 'provider'),
                'cost_amount', 'manual_price', 'price_amount', 'utility_percent', 'utility', 'id', 'version',
                'submit_action', 'mail_from', 'mail_to', 'mail_cc', 'mail_bcc', 'mail_subject', 'mail_body')
        }),
        ('Notes', {'fields': ('p_notes', 'provider_notes'),
                   'classes': ('collapse', 'wide')})
    )
    list_display = ('booking_package', 'name', 'service_addon',
                    'quantity', 'parameter',
                    'datetime_from', 'datetime_to', 'time',
                    'cost_amount', 'manual_cost',
                    'price_amount', 'manual_price',
                    'utility_percent', 'utility',
                    'status', 'cost_amount_paid')
    top_filters = (
        ('booking_package__booking__name', 'Booking'),
        ('name', 'Service'),
         'booking_package__booking__reference',
        ('datetime_from', DateTopFilter), 'status',)
    ordering = ('datetime_from', 'booking_package', 'service__name',)
    form = BookingPackageExtraForm
    add_form_template = 'booking/bookingpackageextra_change_form.html'
    change_form_template = 'booking/bookingpackageextra_change_form.html'
    list_details_template = 'booking/bookingpackageextra_details.html'
    change_details_template = 'booking/bookingpackageextra_details.html'


class BookingPackageSiteModel(BaseBookingServiceSiteModel):
    model_order = 1240
    menu_label = MENU_LABEL_BOOKING
    menu_group = MENU_GROUP_LABEL_SERVICES

    readonly_fields = ['status', 'utility_percent', 'utility'] 

    fieldsets = (
        (None, {
            'fields': (
                ('booking', 'voucher_detail'), ('service', 'search_location'), ('status', 'conf_number'),
                ('datetime_from', 'datetime_to', 'time'),
                ('provider'), 'cost_amount',
                ('manual_price', 'price_by_package_catalogue'),
                'price_amount', 'utility_percent', 'utility', 'id', 'version',
                'submit_action', 'mail_from', 'mail_to', 'mail_cc', 'mail_bcc', 'mail_subject', 'mail_body')
        }),
        ('Notes', {'fields': ('p_notes', 'v_notes', 'provider_notes'),
                   'classes': ('collapse', 'wide')})
    )
    list_display = ['booking', 'name', 'datetime_from', 'datetime_to',
            'cost_amount', 'price_amount', 'utility_percent', 'utility', 'status']
    top_filters = ['booking__name', 'service', 'booking__reference',
                   ('datetime_from', DateTopFilter), 'status']
    ordering = ['datetime_from', 'booking__reference', 'service__name']
    list_details_template = 'booking/bookingpackage_details.html'
    change_details_template = 'booking/bookingpackage_details.html'
    inlines = [BookingServicePaxInline]
    form = BookingPackageForm
    add_form_template = 'booking/bookingpackage_change_form.html'
    change_form_template = 'booking/bookingpackage_change_form.html'

    def save_related(self, request, form, formsets, change):
        with transaction.atomic(savepoint=False):
            super(BookingPackageSiteModel, self).save_related(request, form, formsets, change)
            obj = self.save_form(request, form, change)
            BookingServices.update_bookingpackageservices_amounts(obj)


class PackageProviderSiteModel(SiteModel):
    model_order = 7250
    menu_label = MENU_LABEL_CONFIG_BASIC
    menu_group = 'Provider Catalogue'
    fields = ('service', 'provider')
    list_display = ('service', 'provider')
    top_filters = (
        ('service', PackageTopFilter), ('provider', ProviderTopFilter))
    ordering = ['service', 'provider']
    form = PackageProviderForm
    save_as = True


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


class BookingInvoiceDetailInline(CommonTabularInline):
    model = BookingInvoiceDetail
    extra = 0
    fields = ['date_from', 'date_to', 'description', 'detail', 'price']


class BookingInvoiceLineInline(CommonTabularInline):
    model = BookingInvoiceLine
    extra = 0
    fields = ['date_from', 'date_to', 'bookingservice_name', 'price']


class BookingInvoicePartialInline(CommonTabularInline):
    model = BookingInvoicePartial
    extra = 0
    fields = ['pax_name', 'is_free', 'partial_amount',]


class BookingInvoiceSiteModel(SiteModel):
    delete_allowed = False
    recent_allowed = False

    fieldsets = (
        (None, {
            'fields': (
                ('booking_name', 'reference', 'document_number'),
                ('date_from', 'date_to'),
                ('issued_name', 'status',),
                ('booking_amount', 'currency', 'currency_rate'),
                ('amount', 'matched_amount', 'cash_amount', )
            )
        }),
        ('Configuration', {
            'fields': ('office', 'content_format', 'date_issued'),
        })
    )
    readonly_fields = ('booking_amount', 'currency_rate', 'matched_amount',
                       'document_number')

    change_form_template = 'booking/bookinginvoice_change_form.html'

    inlines = [BookingInvoiceDetailInline, BookingInvoiceLineInline,
               BookingInvoicePartialInline]
    list_details_template = 'booking/bookinginvoice_details.html'
    change_details_template = 'booking/bookinginvoice_details.html'

    def save_model(self, request, obj, form, change):
        BookingServices.save_booking_invoice(request, obj, form, change)

    def response_post_save_add(self, request, obj):
        if hasattr(obj, 'invoice_booking') and obj.invoice_booking:
            return redirect(reverse('common:booking_booking_change',
                                    args=[obj.invoice_booking.pk]))
        invoice_booking = request.POST.get('invoice_booking')
        if invoice_booking:
            return redirect(reverse('common:booking_booking_change',
                                    args=[invoice_booking]))
        return super(BookingInvoiceSiteModel, self).response_post_save_add(request, obj)

    def response_post_save_change(self, request, obj):
        if hasattr(obj, 'invoice_booking') and obj.invoice_booking:
            return redirect(reverse('common:booking_booking_change',
                                    args=[obj.invoice_booking.pk]))
        invoice_booking = request.POST.get('invoice_booking')
        if invoice_booking:
            return redirect(reverse('common:booking_booking_change',
                                    args=[invoice_booking]))
        return super(BookingInvoiceSiteModel, self).response_post_save_change(request, obj)


class ProviderBookingPaymentSiteModel(SiteModel):

    from finance.common_site import MENU_LABEL_FINANCE_ADVANCED

    model_order = 4130
    menu_label = MENU_LABEL_FINANCE_ADVANCED

    fieldsets = (
        (None, {
            'fields': (
                ('provider', 'name'),
                ('date', 'status'),
                ('account', 'services_amount'),
                ('currency_rate', 'amount'),
                ('details',),
                'mail_from', 'mail_to', 'mail_cc', 'mail_bcc', 'mail_subject', 'mail_body',
                'submit_action',
            )
        }),
    )
    list_display = ('provider', 'details', 'account', 'services_amount',
                    'amount', 'date', 'status')
    readonly_fields = ['services_amount']
    add_readonly_fields = ['status']

    top_filters = ('provider', 'details', 'account', 'status', 'date',)

    recent_allowed = True
    form = ProviderBookingPaymentForm
    change_form_template = 'booking/providerbookingpayment_change_form.html'
    list_details_template = 'booking/providerbookingpayment_details.html'

    custom_actions_template = 'booking/include/providerpayment_actions.html'

    def get_changelist(self, request, **kwargs):
        """
        Returns the ChangeList class for use on the changelist page.
        """
        return StatusChangeList

    def is_readonly_model(self, request, obj=None):
        return obj and obj.status == STATUS_CANCELLED

    def has_delete_permission(self, request, obj=None):
        if obj is not None and obj.status != STATUS_DRAFT:
            return False
        return super(ProviderBookingPaymentSiteModel, self).has_delete_permission(request, obj)

    def get_change_readonly_fields(self, request, obj=None):
        if obj is not None:
            if obj.status == STATUS_CANCELLED:
                return ['provider', 'name', 'date', 'services_amount',
                        'currency_rate', 'status', 'account', 'amount']
            elif obj.status == STATUS_READY:
                return ['provider', 'name', 'date', 'services_amount',
                        'currency_rate', 'account', 'amount']
            else:
                return ['provider']
        return []

    def custom_context(
            self, request, form=None, obj=None, formsets=None, inline_instances=None,
            add=None, opts=None, object_id=None, to_field=None):
        if object_id:
            formset_services = BookingServices.booking_provider_payment_services(request, form, object_id)
            return dict(formset_services=formset_services)

        return {}

    def changeform_context(
            self, request, form, obj, formsets, inline_instances,
            add, opts, object_id, to_field, form_validated=None, extra_context=None):

        context = super(ProviderBookingPaymentSiteModel, self).changeform_context(
            request, form, obj, formsets, inline_instances, add, opts, object_id, to_field,
            form_validated, extra_context)

        if object_id:
            if 'formset_services' not in context:
                context['formset_services'] = BookingServices.booking_provider_payment_services(request, form, object_id)
            if obj.status == STATUS_DRAFT:
                ServicesFormSet = formset_factory(ProviderBookingPaymentServiceForm, extra=0)
            else:
                ServicesFormSet = formset_factory(ProviderBookingPaymentServiceReadonlyForm, extra=0)
            services_formset = ServicesFormSet(initial=list(context['formset_services']))

            context.update(dict(services_formset=services_formset))

        return context

    def save_model(self, request, obj, form, change):
        if obj. pk:
            # disable save of agencyinvoice object
            ServicesFormSet = formset_factory(ProviderBookingPaymentServiceForm)
            services_formset = ServicesFormSet(request.POST)
            if services_formset.is_valid():
                BookingServices.save_payment(
                    request.user, obj, services_formset.cleaned_data)
            else:
                raise ValidationError('Invalid Services Payments Data')
        else:
            super(ProviderBookingPaymentSiteModel, self).save_model(request, obj, form, change)

    @csrf_protect_m
    def changeform_view(self, request, object_id=None,
                        form_url='', extra_context=None):
        if request.method == 'POST':
            if '_pdf' in request.POST:
                payment = ProviderBookingPayment.objects.get(id=object_id)
                result, pdf = self._build_provider_payment_pdf(payment)
                if result.err:
                    messages.add_message(request, messages.ERROR, "Failed Provider Payment PDF Generation - %s" % result.err)
                    return redirect(reverse('common:booking_providerbookingpayment_change', args=[object_id]))
                return HttpResponse(pdf.getvalue(), content_type='application/pdf')
            elif 'submit_action' in request.POST and request.POST['submit_action'] == '_send_mail':
                payment = ProviderBookingPayment.objects.get(id=object_id)


                result, pdf = self._build_provider_payment_pdf(payment)
                if result.err:
                    messages.add_message(request, messages.ERROR, "Failed Provider Payment PDF Generation - %s" % result.err)
                    return redirect(reverse('common:booking_providerbookingpayment_change', args=[object_id]))
                mail_from = request.POST.get('mail_from')
                to_list = _build_mail_address_list(request.POST.get('mail_to'))
                cc_list = _build_mail_address_list(request.POST.get('mail_cc'))
                bcc_list = _build_mail_address_list(request.POST.get('mail_bcc'))

                if not to_list or not mail_from:
                    messages.add_message(request=request,
                                         level=messages.ERROR,
                                         message='missing Remitent or Destination address',
                                         extra_tags='',
                                         fail_silently=False)
                    return redirect(reverse('common:booking_providerbookingpayment_change',
                                            args=[object_id]))
                email = EmailMessage(
                    from_email=mail_from,
                    to=to_list,
                    cc=cc_list,
                    bcc=bcc_list,
                    subject=request.POST.get('mail_subject'),
                    body=request.POST.get('mail_body'))

                email.attach('provider_payment.pdf', pdf.getvalue(), 'application/pdf')
                email.content_subtype = "html"
                email.send()

                messages.add_message(
                    request=request, level=messages.SUCCESS,
                    message='Payment sent successfully.',
                    extra_tags='', fail_silently=False)
                return redirect(reverse('common:booking_providerbookingpayment_change',
                                        args=[object_id]))
            else:
                # default POST request. call Super
                return super(ProviderBookingPaymentSiteModel, self).changeform_view(
                    request=request,
                    object_id=object_id,
                    form_url=form_url,
                    extra_context=extra_context)
        else:
            # GET request
            if not extra_context:
                extra_context = dict()
            if object_id and object_id.isnumeric():
                payment = ProviderBookingPayment.objects.get(id=object_id)
                form = EmailPopupForm(
                    initial={'mail_from': default_requests_mail_from(request),
                             'mail_to': default_requests_mail_to(request, payment.provider),
                             'mail_cc': '',
                             'mail_bcc': default_mail_bcc(request),
                             'mail_subject': default_provider_payment_mail_subject(
                                 request, payment),
                             'mail_body': default_provider_payment_mail_body(request, payment)})
            else:
                form = EmailPopupForm()
            extra_context.update({
                'modal_title': 'Provider Payment E-mail',
                'form': form,
            })
            return super(ProviderBookingPaymentSiteModel, self).changeform_view(
                request=request,
                object_id=object_id,
                form_url=form_url,
                extra_context=extra_context)

    def _build_provider_payment_pdf(self, payment):
        template = get_template("booking/pdf/provider_payment.html")
        # services = ProviderBookingPaymentService.objects.filter(provider_payment=payment)
        context = {
            # 'pagesize': 'Letter',
            'payment': payment,
            # 'services': services,
        }
        html = template.render(context)
        if PY2:
            html = html.encode('UTF-8')
        pdf = StringIO()
        result = pisa.pisaDocument(StringIO(html), dest=pdf,
                                link_callback=_fetch_resources)
        return result, pdf


def default_requests_mail_from(request, provider=None, booking=None):
    if provider and not provider.is_private:
        return settings.FORMAL_COMPANY_EMAIL
    return request.user.email or None


def default_requests_mail_to(request, provider=None, booking=None):
    if provider:
        return provider.email
    return None


def default_requests_mail_bcc(request, provider=None, booking=None):
    return request.user.email or None


def default_requests_mail_subject(request, provider=None, booking=None):
    subject_ref = ''
    if booking:
        subject_ref = booking.name or ''
        if booking.reference:
            subject_ref += ' (%s)' % booking.reference
    return 'Solicitud de Reserva %s' % subject_ref


def default_requests_mail_body(request, provider=None, booking=None):
    if provider:
        services = list(BookingService.objects.filter(
            booking=booking,
            provider=provider).exclude(status='CN').all())
        package_services = list(BookingPackageService.objects.filter(
            Q(booking_package__booking=booking)
            & (
                Q(provider=provider)
                | (
                    Q(booking_package__provider=provider) & Q(provider__isnull=True)
                )
            )).all())
        services.extend(package_services)
        try:
            services.sort(key=lambda x: x.datetime_from)
        except TypeError:
            # probably a date missing. ignore ordering
            # this bookingService has to be fixed by user
            pass
    else:
        services = []
    #rooming = bs.rooming_list.all()
    initial = {
        'user': request.user,
        'booking': booking,
        'provider': provider,
        'services': services,
    }
    return get_template('booking/emails/provider_email.html').render(initial)


def default_invoice_mail_to(request, booking=None):
    email_list = ''
    if booking and booking.agency:
        for invoice_contact in booking.agency.agencybillingcontact_set.all():
            email_list += '{}, '.format(invoice_contact.email)
    if not email_list:
        # there is no billing_contacts for this agency.
        # sending to agency_contact
        if booking and booking.agency_contact:
            email_list += '{}'.format(booking.agency_contact.email)
    return email_list


def default_invoice_mail_bcc(request, booking=None):
    return default_mail_bcc(request)


def default_invoice_mail_subject(request, booking=None):
    subject_ref = ''
    if booking:
        subject_ref = booking.name or ''
        if booking.reference:
            subject_ref += ' (%s)' % booking.reference
    return 'Invoice for %s' % subject_ref


def default_invoice_mail_body(request, booking=None):
    dest = 'Customer'
    if booking and booking.agency_contact:
        dest = booking.agency_contact.name
    context = {
        'user': request.user,
        'client': dest,
    }
    return get_template('booking/emails/invoice_email.html').render(context)


def default_mail_cc(request, booking):
    if booking.agency:
        cc_list = ''
        for contact in booking.agency.agencycopycontact_set.all():
            name, domain = contact.email.split('@')
            if name in [f.name for f in Booking._meta.get_fields()]:
                attr = getattr(booking, name)
                if attr:
                    cc_list += '%s@%s, ' % (attr, domain)
            else:
                cc_list += '%s, ' % contact.email
        return cc_list


def default_vouchers_mail_bcc(request):
    return default_mail_bcc(request)


def default_mail_bcc(request):
    if request.user.email == settings.DEFAULT_BCC:
        return settings.DEFAULT_BCC
    else:
        return '%s, %s' % (request.user.email, settings.DEFAULT_BCC)


def default_vouchers_mail_subject(request, booking):
    ref = ''
    if booking.reference:
        ref = '(%s)' % booking.reference
    return 'Vouchers for %s x%s %s' % (booking.name,
                                       booking.rooming_list.count(),
                                       ref)


def default_vouchers_mail_body(request, booking=None):
    dest = 'Customer'
    if booking and booking.agency_contact:
        dest = booking.agency_contact.name
    context = {
            'user': request.user,
            'client': dest,
    }
    return get_template('booking/emails/vouchers_email.html').render(context)


def default_quote_mail_to(request, quote=None):
    email_list = ''
    # add here any logic to set default quote client email
    return email_list


def default_quote_mail_subject(request, quote=None):
    subject_ref = ''
    if quote:
        subject_ref = quote.reference or ''

    return 'Quote for %s' % subject_ref


def default_quote_mail_body(request, quote=None):
    dest = 'Customer'
    # quote_services = QuoteService.objects.filter(id=quote.id)
    # child_services = _get_quote_child_objects(quote_services)
    pax_minimums = quote.quote_paxvariants.all()
    context = {
        'user': request.user,
        'client': dest,
        'quote': quote,
        'minimums': pax_minimums,
        # 'quote_services': child_services,
    }
    return get_template('booking/emails/quote_email.html').render(context)


def default_provider_payment_mail_subject(request, payment=None):
    subject_ref = ''
    if payment:
        subject_ref = '%s - %s %s' % (payment.date, payment.amount, payment.currency)

    return 'Payment details %s' % (subject_ref)


def default_provider_payment_mail_body(request, payment=None):
    if payment:
        provider = payment.provider
        services = list(ProviderBookingPaymentService.objects.filter(
            provider_payment=payment).order_by('provider_service__datetime_from'))
    else:
        services = []
    initial = {
        'user': request.user,
        'payment': payment,
        'provider': provider,
        'services': services,
    }
    return get_template('booking/emails/provider_payment_email.html').render(initial)


def _fetch_resources(uri, rel):
    path = os.path.join(settings.MEDIA_ROOT,
                        uri.replace(settings.MEDIA_URL, ""))
    return path



# Starts Registration Section

bookings_site.register(Package, PackageSiteModel)

bookings_site.register(PackageAllotment, PackageAllotmentSiteModel)
bookings_site.register(PackageTransfer, PackageTransferSiteModel)
bookings_site.register(PackageExtra, PackageExtraSiteModel)

bookings_site.register(AgencyPackageService, AgencyPackageServiceSiteModel)
bookings_site.register(PackageProvider, PackageProviderSiteModel)

bookings_site.register(Quote, QuoteSiteModel)

bookings_site.register(QuoteAllotment, QuoteAllotmentSiteModel)
bookings_site.register(QuoteTransfer, QuoteTransferSiteModel)
bookings_site.register(QuoteExtra, QuoteExtraSiteModel)
bookings_site.register(QuotePackage, QuotePackageSiteModel)
bookings_site.register(QuotePackageAllotment, QuotePackageAllotmentSiteModel)
bookings_site.register(QuotePackageTransfer, QuotePackageTransferSiteModel)
bookings_site.register(QuotePackageExtra, QuotePackageExtraSiteModel)


bookings_site.register(Booking, BookingSiteModel)

bookings_site.register(BaseBookingService, BookingBaseServiceSiteModel)

bookings_site.register(BookingService, BookingServiceSiteModel)

bookings_site.register(BookingAllotment, BookingAllotmentSiteModel)
bookings_site.register(BookingTransfer, BookingTransferSiteModel)
bookings_site.register(BookingExtra, BookingExtraSiteModel)
bookings_site.register(BookingPackage, BookingPackageSiteModel)
bookings_site.register(BookingPackageAllotment, BookingPackageAllotmentSiteModel)
bookings_site.register(BookingPackageTransfer, BookingPackageTransferSiteModel)
bookings_site.register(BookingPackageExtra, BookingPackageExtraSiteModel)

bookings_site.register(BookingInvoice, BookingInvoiceSiteModel)

bookings_site.register(ProviderBookingPayment, ProviderBookingPaymentSiteModel)
