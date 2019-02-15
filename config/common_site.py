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
    AllotmentRoomTypeInlineForm, ExtraAddonInlineForm
)
from config.models import (
    Location, Place, RoomType, Addon,
    Allotment, AllotmentRoomType, AllotmentBoardType, AllotmentSupplement,
    Transfer, TransferSupplement,
    Extra, ExtraAddon, ExtraSupplement,
    AgencyAllotmentService, AgencyAllotmentDetail,
    AgencyTransferService, AgencyTransferDetail,
    AgencyExtraService, AgencyExtraDetail,
    ProviderAllotmentService, ProviderAllotmentDetail,
    ProviderTransferService, ProviderTransferDetail,
    ProviderExtraService, ProviderExtraDetail,
)
from config.top_filters import (
    RoomTypeTopFilter, LocationTopFilter,
    AddonTopFilter,
    AllotmentTopFilter, TransferTopFilter, ExtraTopFilter,
    LocationForProviderTransferTopFilter, ExtraLocationForProviderTransferTopFilter,
    LocationForAgencyTransferTopFilter, ExtraLocationForAgencyTransferTopFilter,
    DateToTopFilter)

from finance.top_filters import ProviderTopFilter, AgencyTopFilter 

from functools import update_wrapper, partial

from reservas.admin import bookings_site


MENU_LABEL_CONFIG_BASIC = 'Configuration'

class IncorrectLookupParameters(Exception):
    pass

class LocationPlaceInline(CommonTabularInline):
    model = Place
    extra = 0
    show_change_link = True


class LocationSiteModel(SiteModel):
    model_order = 6010
    menu_label = MENU_LABEL_CONFIG_BASIC
    fields = ('name', 'enabled', 'short_name')
    list_display = ('name', 'enabled',)
    top_filters = ('name', 'enabled',)
    inlines = [LocationPlaceInline]


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

class AllotmentSiteModel(SiteModel):
    model_order = 6110
    menu_label = MENU_LABEL_CONFIG_BASIC
    menu_group = 'Configuration Services'
    fields = (('name', 'location'),
              ('phone', 'address'),
              ('time_from', 'time_to'),
              'enabled',
              'child_age')
    list_display = ('name', 'phone', 'location',
                    'enabled',)
    top_filters = ('name', ('location', LocationTopFilter))
    ordering = ['enabled', 'name']
    inlines = [AllotmentRoomTypeInline, AllotmentBoardTypeInline,
               AllotmentSupplementInline]
    actions = ['generate_agency_amounts']

    def generate_agency_amounts(self, request, queryset):
        pass
    generate_agency_amounts.short_description = "Generate Agency Prices"


class TransferSupplementInline(CommonTabularInline):
    model = TransferSupplement
    extra = 0


class TransferSiteModel(SiteModel):
    model_order = 6120
    menu_label = MENU_LABEL_CONFIG_BASIC
    menu_group = 'Configuration Services'
    fields = ('name', 'cost_type', 'max_capacity', 'enabled',)
    list_display = ('name', 'cost_type', 'max_capacity', 'enabled',)
    top_filters = ('name', 'enabled',)
    ordering = ['enabled', 'name']
    inlines = [TransferSupplementInline]
    actions = ['generate_agency_amounts']

    def generate_agency_amounts(self, request, queryset):
        pass
    generate_agency_amounts.short_description = "Generate Agency Prices"


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
    fields = ('name', 'location', 'cost_type', 'parameter_type',
              'has_pax_range', 'enabled',)
    list_display = ('name', 'location', 'cost_type',
                    'parameter_type', 'enabled',)
    top_filters = ('name',)
    ordering = ['enabled', 'name']
    inlines = [ExtraAddonInline, ExtraSupplementInline]
    actions = ['generate_agency_amounts']

    def generate_agency_amounts(self, request, queryset):
        pass
    generate_agency_amounts.short_description = "Generate Agency Prices"


class ProviderAllotmentDetailInline(CommonStackedInline):
    model = ProviderAllotmentDetail
    extra = 0
    fields = (
        ('single_supplement', 'third_pax_discount'),
        ('room_type', 'board_type'),
        ('ad_1_amount', 'ch_1_ad_1_amount', 'ch_2_ad_1_amount',), # 'ch_3_ad_1_amount',),
        ('ad_2_amount', 'ch_1_ad_2_amount', 'ch_2_ad_2_amount',), # 'ch_3_ad_2_amount',),
        ('ad_3_amount', 'ch_1_ad_3_amount', 'ch_2_ad_3_amount',), # 'ch_3_ad_3_amount',),
    )
    ordering = ['room_type', 'board_type']
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


class ProviderTransferDetailInline(CommonStackedInline):
    model = ProviderTransferDetail
    extra = 0
    fields = (
        ('p_location_from', 'p_location_to', 'ad_1_amount'),
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


class ProviderExtraDetailInline(CommonStackedInline):
    model = ProviderExtraDetail
    extra = 0
    fields = (
        ('addon', 'ad_1_amount'), ('pax_range_min', 'pax_range_max'))
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


class AgencyAllotmentDetailInline(CommonStackedInline):
    model = AgencyAllotmentDetail
    extra = 0
    fields = (
        ('room_type', 'board_type',),
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


class AgencyTransferDetailInline(CommonStackedInline):
    model = AgencyTransferDetail
    extra = 0
    fields = (
        ('a_location_from', 'a_location_to', 'ad_1_amount'),
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


class AgencyExtraDetailInline(CommonStackedInline):
    model = AgencyExtraDetail
    extra = 0
    fields = (
        ('addon', 'ad_1_amount'), ('pax_range_min', 'pax_range_max'),)
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


bookings_site.register(Location, LocationSiteModel)
bookings_site.register(RoomType, RoomTypeSiteModel)
bookings_site.register(Addon, AddonSiteModel)

bookings_site.register(AllotmentRoomType, AllotmentRoomTypeSiteModel)
bookings_site.register(AllotmentBoardType, AllotmentBoardTypeSiteModel)
bookings_site.register(ExtraAddon, ExtraAddonSiteModel)

bookings_site.register(Allotment, AllotmentSiteModel)
bookings_site.register(Transfer, TransferSiteModel)
bookings_site.register(Extra, ExtraSiteModel)

bookings_site.register(AgencyAllotmentService, AgencyAllotmentServiceSiteModel)
bookings_site.register(AgencyTransferService, AgencyTransferServiceSiteModel)
bookings_site.register(AgencyExtraService, AgencyExtraServiceSiteModel)

bookings_site.register(ProviderAllotmentService, ProviderAllotmentServiceSiteModel)
bookings_site.register(ProviderTransferService, ProviderTransferServiceSiteModel)
bookings_site.register(ProviderExtraService, ProviderExtraServiceSiteModel)
