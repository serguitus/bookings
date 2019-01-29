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
    AgencyAllotmentServiceForm, AgencyTransferServiceForm, AgencyExtraServiceForm,
    AgencyAllotmentDetailInlineForm, AgencyTransferDetailInlineForm,
    AllotmentRoomTypeInlineForm,
)
from config.models import (
    Location, RoomType,
    Allotment, AllotmentRoomType, AllotmentBoardType, AllotmentSupplement,
    Transfer, TransferSupplement,
    Extra, ExtraSupplement,
    AgencyAllotmentService, AgencyAllotmentDetail,
    AgencyTransferService, AgencyTransferDetail,
    AgencyExtraService, AgencyExtraDetail,
    ProviderAllotmentService, ProviderAllotmentDetail,
    ProviderTransferService, ProviderTransferDetail,
    ProviderExtraService, ProviderExtraDetail,
)
from config.top_filters import (
    RoomTypeTopFilter, LocationTopFilter,
    AllotmentTopFilter, TransferTopFilter, ExtraTopFilter,
    LocationForProviderTransferTopFilter, ExtraLocationForProviderTransferTopFilter)

from finance.top_filters import ProviderTopFilter 

from functools import update_wrapper, partial

from reservas.admin import bookings_site


MENU_LABEL_CONFIG_BASIC = 'Configuration'

class IncorrectLookupParameters(Exception):
    pass

class LocationSiteModel(SiteModel):
    model_order = 6010
    menu_label = MENU_LABEL_CONFIG_BASIC
    fields = ('name', 'enabled', 'short_name')
    list_display = ('name', 'enabled',)
    top_filters = ('name', 'enabled',)


class RoomTypeSiteModel(SiteModel):
    model_order = 6020
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
    fields = ('allotment', 'room_type', 'room_capacity',)
    list_display = ('allotment', 'room_type', 'room_capacity',)
    top_filters = ('allotment__name', ('room_type', RoomTypeTopFilter),)
    ordering = ('allotment__name',)


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
    ordering = ('allotment__name',)


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
    ordering = ('enabled', 'name',)
    inlines = [AllotmentRoomTypeInline, AllotmentBoardTypeInline,
               AllotmentSupplementInline]


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
    ordering = ('enabled', 'name',)
    inlines = [TransferSupplementInline]


class ExtraSupplementInline(CommonTabularInline):
    model = ExtraSupplement
    extra = 0


class ExtraSiteModel(SiteModel):
    model_order = 6130
    menu_label = MENU_LABEL_CONFIG_BASIC
    menu_group = 'Configuration Services'
    fields = ('name', 'cost_type', 'parameter_type', 'enabled',)
    list_display = ('name', 'cost_type', 'parameter_type', 'enabled',)
    top_filters = ('name',)
    ordering = ('enabled', 'name',)
    inlines = [ExtraSupplementInline]


class ProviderAllotmentDetailInline(CommonStackedInline):
    model = ProviderAllotmentDetail
    extra = 0
    fields = (
        ('single_supplement', 'third_pax_discount'),
        ('room_type','board_type'),
        ('ad_1_amount','ch_1_ad_1_amount','ch_2_ad_1_amount',), # 'ch_3_ad_1_amount',),
        ('ad_2_amount','ch_1_ad_2_amount','ch_2_ad_2_amount',), # 'ch_3_ad_2_amount',),
        ('ad_3_amount','ch_1_ad_3_amount','ch_2_ad_3_amount',), # 'ch_3_ad_3_amount',),
    )
    form = ProviderAllotmentDetailInlineForm


class ProviderAllotmentServiceSiteModel(SiteModel):
    model_order = 7220
    menu_label = MENU_LABEL_CONFIG_BASIC
    menu_group = 'Provider Catalogue'
    recent_allowed = True
    fields = ('provider', 'service', 'date_from', 'date_to',)
    list_display = ('service', 'provider', 'date_from', 'date_to',)
    top_filters = (('provider', ProviderTopFilter), ('service', AllotmentTopFilter),)
    inlines = [ProviderAllotmentDetailInline]
    form = ProviderAllotmentServiceForm
    change_form_template = 'config/provider_allotment_change_form.html'
    add_form_template = 'config/provider_allotment_change_form.html'


class ProviderTransferDetailInline(CommonStackedInline):
    model = ProviderTransferDetail
    extra = 0
    fields = (
        ('p_location_from','p_location_to', 'ad_1_amount'),
    )
    form = ProviderTransferDetailInlineForm


class ProviderTransferServiceSiteModel(SiteModel):
    model_order = 7230
    menu_label = MENU_LABEL_CONFIG_BASIC
    menu_group = 'Provider Catalogue'
    recent_allowed = True
    fields = ('provider', 'service', 'date_from', 'date_to',)
    list_display = ('service',  'provider', 'date_from', 'date_to',)
    top_filters = (
        ('provider', ProviderTopFilter), ('service', TransferTopFilter),
        LocationForProviderTransferTopFilter, ExtraLocationForProviderTransferTopFilter)
    inlines = [ProviderTransferDetailInline]
    form = ProviderTransferServiceForm


class ProviderExtraDetailInline(CommonStackedInline):
    model = ProviderExtraDetail
    extra = 0
    fields = (
        'ad_1_amount',
    )


class ProviderExtraServiceSiteModel(SiteModel):
    model_order = 7240
    menu_label = MENU_LABEL_CONFIG_BASIC
    menu_group = 'Provider Catalogue'
    recent_allowed = True
    fields = ('provider', 'service', 'date_from', 'date_to',)
    list_display = ('service', 'provider', 'date_from', 'date_to',)
    top_filters = (('provider', ProviderTopFilter),
                   ('service', ExtraTopFilter),)
    inlines = [ProviderExtraDetailInline]
    form = ProviderExtraServiceForm


class AgencyAllotmentDetailInline(CommonStackedInline):
    model = AgencyAllotmentDetail
    extra = 0
    fields = (
        ('room_type','board_type',),
        ('ad_1_amount','ch_1_ad_1_amount','ch_2_ad_1_amount','ch_3_ad_1_amount',),
        ('ad_2_amount','ch_1_ad_2_amount','ch_2_ad_2_amount','ch_3_ad_2_amount',),
        ('ad_3_amount','ch_1_ad_3_amount','ch_2_ad_3_amount','ch_3_ad_3_amount',),
        ('ch_1_ad_0_amount','ch_2_ad_0_amount','ch_3_ad_0_amount',),
    )
    form = AgencyAllotmentDetailInlineForm


class AgencyAllotmentServiceSiteModel(SiteModel):
    model_order = 7120
    menu_label = MENU_LABEL_CONFIG_BASIC
    menu_group = 'Agency Catalogue'
    recent_allowed = True
    fields = ('agency', 'service', 'date_from', 'date_to',)
    list_display = ('agency', 'service', 'date_from', 'date_to',)
    top_filters = ('agency__name','service__name',)
    inlines = [AgencyAllotmentDetailInline]
    form = AgencyAllotmentServiceForm


class AgencyTransferDetailInline(CommonStackedInline):
    model = AgencyTransferDetail
    extra = 0
    fields = (
        ('a_location_from','a_location_to', 'ad_1_amount'),
    )
    form = AgencyTransferDetailInlineForm


class AgencyTransferServiceSiteModel(SiteModel):
    model_order = 7130
    menu_label = MENU_LABEL_CONFIG_BASIC
    menu_group = 'Agency Catalogue'
    recent_allowed = True
    fields = ('agency', 'service', 'date_from', 'date_to',)
    list_display = ('agency', 'service', 'date_from', 'date_to',)
    top_filters = ('agency__name','service__name',)
    inlines = [AgencyTransferDetailInline]
    form = AgencyTransferServiceForm


class AgencyExtraDetailInline(CommonStackedInline):
    model = AgencyExtraDetail
    extra = 0
    fields = (
        ('ad_1_amount', 'pax_range_min', 'pax_range_max',),
    )


class AgencyExtraServiceSiteModel(SiteModel):
    model_order = 7140
    menu_label = MENU_LABEL_CONFIG_BASIC
    menu_group = 'Agency Catalogue'
    recent_allowed = True
    fields = ('agency', 'service', 'date_from', 'date_to')
    list_display = ('agency', 'service', 'date_from', 'date_to',)
    top_filters = ('agency__name','service__name',)
    inlines = [AgencyExtraDetailInline]
    form = AgencyExtraServiceForm


bookings_site.register(Location, LocationSiteModel)
bookings_site.register(RoomType, RoomTypeSiteModel)

bookings_site.register(AllotmentRoomType, AllotmentRoomTypeSiteModel)
bookings_site.register(AllotmentBoardType, AllotmentBoardTypeSiteModel)

bookings_site.register(Allotment, AllotmentSiteModel)
bookings_site.register(Transfer, TransferSiteModel)
bookings_site.register(Extra, ExtraSiteModel)

bookings_site.register(AgencyAllotmentService, AgencyAllotmentServiceSiteModel)
bookings_site.register(AgencyTransferService, AgencyTransferServiceSiteModel)
bookings_site.register(AgencyExtraService, AgencyExtraServiceSiteModel)

bookings_site.register(ProviderAllotmentService, ProviderAllotmentServiceSiteModel)
bookings_site.register(ProviderTransferService, ProviderTransferServiceSiteModel)
bookings_site.register(ProviderExtraService, ProviderExtraServiceSiteModel)
