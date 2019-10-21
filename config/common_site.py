# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from common.sites import SiteModel, CommonTabularInline, CommonStackedInline

from django.conf.urls import url
from django.contrib import admin, messages
from django.contrib.admin.options import csrf_protect_m, IS_POPUP_VAR, TO_FIELD_VAR
from django.contrib.admin import helpers
from django.contrib.admin.checks import ModelAdminChecks
from django.contrib.admin.utils import unquote
from django.core import checks
from django.core.exceptions import FieldDoesNotExist, ValidationError, PermissionDenied
from django.db import router, transaction
from django import forms
from django.forms.models import modelformset_factory
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.template.response import SimpleTemplateResponse, TemplateResponse
from django.utils.encoding import force_text
from django.utils.translation import ugettext as _, ungettext

from config.forms import (
    ProviderAllotmentServiceForm, ProviderTransferServiceForm, ProviderExtraServiceForm,
    ProviderAllotmentDetailInlineForm, ProviderTransferDetailInlineForm,
    ProviderExtraDetailInlineForm,
    AgencyAllotmentServiceForm, AgencyTransferServiceForm, AgencyExtraServiceForm,
    AgencyAllotmentDetailInlineForm, AgencyTransferDetailInlineForm,
    AgencyExtraDetailInlineForm,
    AllotmentRoomTypeInlineForm, ExtraAddonInlineForm,
    LocationTransferIntervalInlineForm, ServiceAddonInlineForm,
    PricesExportForm,
)
from config.models import (
    ServiceCategory, Location, Place, TransferInterval, Schedule, RoomType, Addon,
    Service,
    Allotment, AllotmentRoomType, AllotmentBoardType, AllotmentSupplement,
    Transfer, TransferSupplement,
    Extra, ExtraAddon, ExtraSupplement,
    AgencyAllotmentService, AgencyAllotmentDetail,
    AgencyTransferService, AgencyTransferDetail,
    AgencyExtraService, AgencyExtraDetail,
    ProviderAllotmentService, ProviderAllotmentDetail,
    ProviderTransferService, ProviderTransferDetail,
    ProviderExtraService, ProviderExtraDetail, ServiceAddon
)
from config.services import ConfigServices
from config.top_filters import (
    RoomTypeTopFilter, LocationTopFilter, ServiceCategoryTopFilter,
    AddonTopFilter,
    AllotmentTopFilter, TransferTopFilter, ExtraTopFilter,
    LocationForProviderTransferTopFilter, ExtraLocationForProviderTransferTopFilter,
    LocationForAgencyTransferTopFilter, ExtraLocationForAgencyTransferTopFilter,
    DateToTopFilter)
from config.views import render_prices_pdf

from finance.top_filters import ProviderTopFilter, AgencyTopFilter
from finance.models import Agency

from functools import update_wrapper, partial

from reservas.admin import bookings_site


MENU_LABEL_CONFIG_BASIC = 'Configuration'

class IncorrectLookupParameters(Exception):
    pass

class LocationPlaceInline(CommonStackedInline):
    model = Place
    extra = 0
    ordering = ['name',]


class LocationTransferIntervalInline(CommonStackedInline):
    model = TransferInterval
    fk_name = 'location'
    extra = 0
    fields = [('t_location_from', 'interval'),]
    ordering = ['t_location_from__name',]

    form = LocationTransferIntervalInlineForm


class LocationScheduleInline(CommonStackedInline):
    model = Schedule
    fk_name = 'location'
    extra = 0
    fields = [('is_arrival', 'number', 'time'),]
    ordering = ['is_arrival', 'number',]


class LocationSiteModel(SiteModel):
    model_order = 6010
    menu_label = MENU_LABEL_CONFIG_BASIC
    fields = ('name', 'enabled', 'short_name')
    list_display = ('name', 'enabled',)
    top_filters = ('name', 'enabled',)
    inlines = [LocationPlaceInline, LocationTransferIntervalInline, LocationScheduleInline]
    save_as = True


class ServiceAddonInline(CommonTabularInline):
    model = ServiceAddon
    extra = 0
    show_change_link = True

    form = ServiceAddonInlineForm


class ServiceCategorySiteModel(SiteModel):
    model_order = 6000
    menu_label = MENU_LABEL_CONFIG_BASIC
    fields = ('name',)
    list_display = ('name',)
    top_filters = ('name',)


class ServiceSiteModel(SiteModel):
    model_order = 6100
    menu_label = MENU_LABEL_CONFIG_BASIC
    menu_group = 'Configuration Services'
    fields = (('name', 'enabled'), ('service_category', 'category'),)
    list_display = ('name', 'service_category', 'category', 'enabled')
    top_filters = ('name', ('service_category', ServiceCategoryTopFilter), 'category', 'enabled')
    ordering = ['enabled', 'category', 'name']
    actions = ['export_prices']

    def export_prices(self, request, queryset, extra_context=None):
        """
        This allows exporting service prices for certain agency and dates
        """
        context = {}
        context.update(self.get_model_extra_context(request))
        context.update(extra_context or {})
        return export_prices(request, queryset, context)


class RoomTypeSiteModel(SiteModel):
    model_order = 6020
    menu_label = MENU_LABEL_CONFIG_BASIC
    fields = ('name', 'enabled',)
    list_display = ('name', 'enabled',)
    list_editable = ('enabled',)
    top_filters = ('name', 'enabled',)


class AddonSiteModel(SiteModel):
    model_order = 6030
    menu_label = MENU_LABEL_CONFIG_BASIC
    fields = ('name', 'enabled',)
    list_display = ('name', 'enabled',)
    list_editable = ('enabled',)
    top_filters = ('name', 'enabled',)


class AllotmentRoomTypeInline(CommonTabularInline):
    model = AllotmentRoomType
    extra = 0
    show_change_link = True

    form = AllotmentRoomTypeInlineForm


class AllotmentRoomTypeSiteModel(SiteModel):
    model_order = 8110
    menu_label = MENU_LABEL_CONFIG_BASIC
    menu_group = 'Configuration Testing'
    fields = ('allotment', 'room_type',)
    list_display = ('allotment', 'room_type',)
    top_filters = ('allotment__name', ('room_type', RoomTypeTopFilter),)
    ordering = ['allotment__name']


class AllotmentBoardTypeInline(CommonTabularInline):
    model = AllotmentBoardType
    extra = 0


class AllotmentBoardTypeSiteModel(SiteModel):
    model_order = 8120
    menu_label = MENU_LABEL_CONFIG_BASIC
    menu_group = 'Configuration Testing'
    fields = ('allotment', 'board_type',)
    list_display = ('allotment', 'board_type',)
    top_filters = ('allotment__name', 'board_type',)
    ordering = ['allotment__name']


class AllotmentSupplementInline(CommonTabularInline):
    model = AllotmentSupplement
    extra = 0


def export_prices(request, queryset, extra_context=None):
    """
    This allows exporting service prices for certain agency and dates
    """
    context = {}
    if 'apply' in request.POST:
        # The user clicked submit on the intermediate form.
        # render the pdf
        agency = request.POST.get('agency', None)

        from common.filters import parse_date

        date_from = parse_date(request.POST.get('start_date', None))
        date_to = parse_date(request.POST.get('end_date', None))

        services = request.POST.getlist('_selected_action', [])
        if agency and services:
            return render_prices_pdf({
                'agency': Agency.objects.get(id=agency),
                'date_from': date_from,
                'date_to': date_to,
                'services': Service.objects.filter(id__in=services)
            })
    context.update({'services': queryset})
    context.update({'form': PricesExportForm()})
    context.update({'site_title': 'Export Services'})
    context.update(extra_context or {})
    # context.update({'quote_id': id})
    return render(request, 'config/agency_prices_export.html', context=context)


class AllotmentSiteModel(SiteModel):
    model_order = 6110
    menu_label = MENU_LABEL_CONFIG_BASIC
    menu_group = 'Configuration Services'
    fields = (('name', 'location', 'is_shared_point'),
              ('service_category', 'cost_type'),
              ('phone', 'address'),
              ('time_from', 'time_to'),
              ('pax_range', 'enabled'),
              ('child_age', 'infant_age'))
    list_display = ('name', 'service_category', 'phone',
                    'location', 'is_shared_point', 'enabled',)
    top_filters = ('name', ('location', LocationTopFilter),
                   ('service_category', ServiceCategoryTopFilter),
                   'is_shared_point', 'enabled')
    ordering = ['enabled', 'name']
    inlines = [AllotmentRoomTypeInline, AllotmentBoardTypeInline,
               ServiceAddonInline]
    actions = ['export_prices']

    def export_prices(self, request, queryset, extra_context=None):
        """
        This allows exporting service prices for certain agency and dates
        """
        context = {}
        context.update(self.get_model_extra_context(request))
        context.update(extra_context or {})
        return export_prices(request, queryset, context)


class TransferSupplementInline(CommonTabularInline):
    model = TransferSupplement
    extra = 0


class TransferSiteModel(SiteModel):
    model_order = 6120
    menu_label = MENU_LABEL_CONFIG_BASIC
    menu_group = 'Configuration Services'
    fields = ('name', 'service_category', 'cost_type', 'max_capacity', 'is_shared', 'pax_range', 'enabled',)
    list_display = ('name', 'cost_type', 'max_capacity', 'is_shared', 'enabled',)
    top_filters = ('name', ('service_category', ServiceCategoryTopFilter), 'is_shared', 'enabled',)
    ordering = ['enabled', 'name']
    inlines = [ServiceAddonInline]
    actions = ['export_prices']

    def export_prices(self, request, queryset, extra_context=None):
        """
        This allows exporting service prices for certain agency and dates
        """
        context = {}
        context.update(self.get_model_extra_context(request))
        context.update(extra_context or {})
        return export_prices(request, queryset, context)


# TODO deprecated class. To be removed with related elements
class ExtraAddonInline(CommonTabularInline):
    model = ExtraAddon
    extra = 0
    show_change_link = True

    form = ExtraAddonInlineForm


class ExtraAddonSiteModel(SiteModel):
    model_order = 8120
    menu_label = MENU_LABEL_CONFIG_BASIC
    menu_group = 'Configuration Testing'
    fields = ('extra', 'addon',)
    list_display = ('extra', 'addon',)
    top_filters = ('extra__name', ('addon', AddonTopFilter),)
    ordering = ['extra__name']


class ExtraSupplementInline(CommonTabularInline):
    model = ExtraSupplement
    extra = 0


class ExtraSiteModel(SiteModel):
    model_order = 6130
    menu_label = MENU_LABEL_CONFIG_BASIC
    menu_group = 'Configuration Services'
    fields = ('name', 'service_category', 'location', 'cost_type', 'parameter_type',
              'pax_range', 'enabled',)
    list_display = ('name', 'service_category', 'location', 'cost_type',
                    'parameter_type', 'enabled', 'pax_range', 'has_pax_range')
    top_filters = (('service_category', ServiceCategoryTopFilter), 'name',)
    ordering = ['enabled', 'name']
    inlines = [ServiceAddonInline]
    actions = ['export_prices']

    def export_prices(self, request, queryset, extra_context=None):
        """
        This allows exporting service prices for certain agency and dates
        """
        context = {}
        context.update(self.get_model_extra_context(request))
        context.update(extra_context or {})
        return export_prices(request, queryset, context)


class ProviderAllotmentDetailInline(CommonStackedInline):
    model = ProviderAllotmentDetail
    extra = 0
    fields = (
        ('single_supplement', 'third_pax_discount'),
        ('room_type', 'board_type', 'addon'),
        ('pax_range_min', 'pax_range_max'),
        ('ad_1_amount', 'ch_1_ad_1_amount', 'ch_2_ad_1_amount',), # 'ch_3_ad_1_amount',),
        ('ad_2_amount', 'ch_1_ad_2_amount', 'ch_2_ad_2_amount',), # 'ch_3_ad_2_amount',),
        ('ad_3_amount', 'ch_1_ad_3_amount', 'ch_2_ad_3_amount',), # 'ch_3_ad_3_amount',),
    )
    ordering = ['id', 'room_type', 'board_type']
    form = ProviderAllotmentDetailInlineForm


class ProviderAllotmentServiceSiteModel(SiteModel):
    model_order = 7220
    menu_label = MENU_LABEL_CONFIG_BASIC
    menu_group = 'Provider Catalogue'
    recent_allowed = True
    fields = ('provider', 'service', 'date_from', 'date_to',)
    list_display = ('service', 'provider', 'date_from', 'date_to',)
    top_filters = (
        ('service', AllotmentTopFilter), ('provider', ProviderTopFilter),
        ('date_to', DateToTopFilter))
    inlines = [ProviderAllotmentDetailInline]
    ordering = ['service', 'provider', '-date_from']
    form = ProviderAllotmentServiceForm
    change_form_template = 'config/provider_allotment_change_form.html'
    add_form_template = 'config/provider_allotment_change_form.html'
    save_as = True

    actions = ['rewrite_agency_amounts', 'update_agency_amounts']

    def rewrite_agency_amounts(self, request, queryset):
        ConfigServices.generate_agency_allotments_amounts_from_providers_allotments(
            list(queryset.all()), False)
    rewrite_agency_amounts.short_description = "Generate All Agency Prices"

    def update_agency_amounts(self, request, queryset):
        ConfigServices.generate_agency_allotments_amounts_from_providers_allotments(
            list(queryset.all()), True)
    update_agency_amounts.short_description = "Generate New Agency Prices"


class ProviderTransferDetailInline(CommonStackedInline):
    model = ProviderTransferDetail
    extra = 0
    fields = (
        ('p_location_from', 'p_location_to', 'addon'),
        ('pax_range_min', 'pax_range_max'),
        'ad_1_amount',
    )
    ordering = ['p_location_from', 'p_location_to']
    form = ProviderTransferDetailInlineForm


class ProviderTransferServiceSiteModel(SiteModel):
    model_order = 7230
    menu_label = MENU_LABEL_CONFIG_BASIC
    menu_group = 'Provider Catalogue'
    recent_allowed = True
    fields = ('provider', 'service', 'date_from', 'date_to',)
    list_display = ('service', 'provider', 'date_from', 'date_to',)
    top_filters = (
        ('service', TransferTopFilter), ('provider', ProviderTopFilter),
        ('date_to', DateToTopFilter),
        LocationForProviderTransferTopFilter, ExtraLocationForProviderTransferTopFilter)
    inlines = [ProviderTransferDetailInline]
    ordering = ['service', 'provider', '-date_from']
    form = ProviderTransferServiceForm
    save_as = True

    actions = ['rewrite_agency_amounts', 'update_agency_amounts']

    def rewrite_agency_amounts(self, request, queryset):
        ConfigServices.generate_agency_transfers_amounts_from_providers_transfers(
            list(queryset.all()), False)
    rewrite_agency_amounts.short_description = "Generate All Agency Prices"

    def update_agency_amounts(self, request, queryset):
        ConfigServices.generate_agency_transfers_amounts_from_providers_transfers(
            list(queryset.all()), True)
    update_agency_amounts.short_description = "Generate New Agency Prices"


class ProviderExtraDetailInline(CommonStackedInline):
    model = ProviderExtraDetail
    extra = 0
    fields = (
        ('pax_range_min', 'pax_range_max'),
        ('addon','ad_1_amount'))
    ordering = ['addon']
    form = ProviderExtraDetailInlineForm


class ProviderExtraServiceSiteModel(SiteModel):
    model_order = 7240
    menu_label = MENU_LABEL_CONFIG_BASIC
    menu_group = 'Provider Catalogue'
    recent_allowed = True
    fields = ('provider', 'service', 'date_from', 'date_to',)
    list_display = ('service', 'provider', 'date_from', 'date_to',)
    top_filters = (
        ('service', ExtraTopFilter), ('provider', ProviderTopFilter),
        ('date_to', DateToTopFilter))
    inlines = [ProviderExtraDetailInline]
    ordering = ['service', 'provider', '-date_from']
    form = ProviderExtraServiceForm
    save_as = True

    actions = ['rewrite_agency_amounts', 'update_agency_amounts']

    def rewrite_agency_amounts(self, request, queryset):
        ConfigServices.generate_agency_extras_amounts_from_providers_extras(
            list(queryset.all()), False)
    rewrite_agency_amounts.short_description = "Generate All Agency Prices"

    def update_agency_amounts(self, request, queryset):
        ConfigServices.generate_agency_extras_amounts_from_providers_extras(
            list(queryset.all()), True)
    update_agency_amounts.short_description = "Generate New Agency Prices"


class AgencyAllotmentDetailInline(CommonStackedInline):
    model = AgencyAllotmentDetail
    extra = 0
    fields = (
        ('room_type', 'board_type', 'addon'),
        ('pax_range_min', 'pax_range_max'),
        ('ad_1_amount', 'ch_1_ad_1_amount', 'ch_2_ad_1_amount', 'ch_3_ad_1_amount',),
        ('ad_2_amount', 'ch_1_ad_2_amount', 'ch_2_ad_2_amount', 'ch_3_ad_2_amount',),
        ('ad_3_amount', 'ch_1_ad_3_amount', 'ch_2_ad_3_amount', 'ch_3_ad_3_amount',),
        ('ch_1_ad_0_amount', 'ch_2_ad_0_amount', 'ch_3_ad_0_amount',),
    )
    ordering = ['room_type', 'board_type']
    form = AgencyAllotmentDetailInlineForm


class AgencyAllotmentServiceSiteModel(SiteModel):
    model_order = 7120
    menu_label = MENU_LABEL_CONFIG_BASIC
    menu_group = 'Agency Catalogue'
    recent_allowed = True
    fields = ('agency', 'service', 'date_from', 'date_to',)
    list_display = ('agency', 'service', 'date_from', 'date_to',)
    top_filters = (
        ('service', AllotmentTopFilter), ('agency', AgencyTopFilter),
        ('date_to', DateToTopFilter))
    inlines = [AgencyAllotmentDetailInline]
    ordering = ['service', 'agency', '-date_from']
    form = AgencyAllotmentServiceForm
    save_as = True


class AgencyTransferDetailInline(CommonStackedInline):
    model = AgencyTransferDetail
    extra = 0
    fields = (
        ('a_location_from', 'a_location_to', 'addon'),
        ('pax_range_min', 'pax_range_max'),
        'ad_1_amount'
    )
    ordering = ['a_location_from', 'a_location_to']
    form = AgencyTransferDetailInlineForm


class AgencyTransferServiceSiteModel(SiteModel):
    model_order = 7130
    menu_label = MENU_LABEL_CONFIG_BASIC
    menu_group = 'Agency Catalogue'
    recent_allowed = True
    fields = ('agency', 'service', 'date_from', 'date_to',)
    list_display = ('agency', 'service', 'date_from', 'date_to',)
    top_filters = (
        ('service', TransferTopFilter), ('agency', AgencyTopFilter),
        ('date_to', DateToTopFilter),
        LocationForAgencyTransferTopFilter, ExtraLocationForAgencyTransferTopFilter)
    inlines = [AgencyTransferDetailInline]
    ordering = ['service', 'agency', '-date_from']
    form = AgencyTransferServiceForm
    save_as = True


class AgencyExtraDetailInline(CommonStackedInline):
    model = AgencyExtraDetail
    extra = 0
    fields = (
        ('pax_range_min', 'pax_range_max'),
        ('addon', 'ad_1_amount'), )
    ordering = ['addon']
    form = AgencyExtraDetailInlineForm


class AgencyExtraServiceSiteModel(SiteModel):
    model_order = 7140
    menu_label = MENU_LABEL_CONFIG_BASIC
    menu_group = 'Agency Catalogue'
    recent_allowed = True
    fields = ('agency', 'service', 'date_from', 'date_to')
    list_display = ('agency', 'service', 'date_from', 'date_to',)
    top_filters = (
        ('service', ExtraTopFilter), ('agency', AgencyTopFilter),
        ('date_to', DateToTopFilter))
    inlines = [AgencyExtraDetailInline]
    ordering = ['service', 'agency', '-date_from']
    form = AgencyExtraServiceForm
    save_as = True


bookings_site.register(ServiceCategory, ServiceCategorySiteModel)
bookings_site.register(Location, LocationSiteModel)
bookings_site.register(RoomType, RoomTypeSiteModel)
bookings_site.register(Addon, AddonSiteModel)

bookings_site.register(AllotmentRoomType, AllotmentRoomTypeSiteModel)
bookings_site.register(AllotmentBoardType, AllotmentBoardTypeSiteModel)
bookings_site.register(ExtraAddon, ExtraAddonSiteModel)

bookings_site.register(Service, ServiceSiteModel)
bookings_site.register(Allotment, AllotmentSiteModel)
bookings_site.register(Transfer, TransferSiteModel)
bookings_site.register(Extra, ExtraSiteModel)

bookings_site.register(AgencyAllotmentService, AgencyAllotmentServiceSiteModel)
bookings_site.register(AgencyTransferService, AgencyTransferServiceSiteModel)
bookings_site.register(AgencyExtraService, AgencyExtraServiceSiteModel)

bookings_site.register(ProviderAllotmentService, ProviderAllotmentServiceSiteModel)
bookings_site.register(ProviderTransferService, ProviderTransferServiceSiteModel)
bookings_site.register(ProviderExtraService, ProviderExtraServiceSiteModel)
