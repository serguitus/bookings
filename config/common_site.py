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
    AllotmentRoomTypeInlineForm, TransferForm,
)
from config.models import (
    Location, RoomType,
    Allotment, AllotmentRoomType, AllotmentBoardType, AllotmentSupplement,
    Transfer, TransferSupplement,
    Extra, ExtraSupplement,
)

from functools import update_wrapper, partial

from reservas.admin import bookings_site


MENU_LABEL_CONFIG_BASIC = 'Configuration'

class IncorrectLookupParameters(Exception):
    pass

class LocationSiteModel(SiteModel):
    model_order = 6010
    menu_label = MENU_LABEL_CONFIG_BASIC
    fields = ('name', 'enabled',)
    list_display = ('name', 'enabled',)
    list_filter = ('enabled',)
    search_fields = ('name',)


class RoomTypeSiteModel(SiteModel):
    model_order = 6020
    menu_label = MENU_LABEL_CONFIG_BASIC
    fields = ('name', 'enabled',)
    list_display = ('name', 'enabled',)
    list_filter = ('enabled',)
    search_fields = ('name',)


class AllotmentRoomTypeInline(CommonTabularInline):
    model = AllotmentRoomType
    extra = 0
    show_change_link = True

    form = AllotmentRoomTypeInlineForm


class AllotmentBoardTypeInline(CommonTabularInline):
    model = AllotmentBoardType
    extra = 0


class AllotmentSupplementInline(CommonTabularInline):
    model = AllotmentSupplement
    extra = 0


class AllotmentRoomTypeSiteModel(SiteModel):
    fields = ('allotment', 'room_type', 'room_capacity',)
    list_display = ('allotment', 'room_type', 'room_capacity',)
    list_filter = ('room_type', 'room_capacity',)
    search_fields = ('allotment__name',)
    ordering = ('allotment__name',)


class AllotmentSiteModel(SiteModel):
    model_order = 6110
    menu_label = MENU_LABEL_CONFIG_BASIC
    menu_group = 'Configuration Services'
    fields = ('name', 'location', 'time_from', 'time_to', 'enabled',)
    list_display = ('name', 'location', 'time_from', 'time_to', 'enabled',)
    list_filter = ('location', 'enabled',)
    search_fields = ('name', 'location__name',)
    ordering = ('enabled', 'name',)
    inlines = [AllotmentRoomTypeInline, AllotmentBoardTypeInline, AllotmentSupplementInline]


class TransferSupplementInline(admin.TabularInline):
    model = TransferSupplement
    extra = 0


class TransferSiteModel(SiteModel):
    model_order = 6120
    menu_label = MENU_LABEL_CONFIG_BASIC
    menu_group = 'Configuration Services'
    fields = ('name', 'location_from', 'location_to', 'enabled',)
    list_display = ('name', 'location_from', 'location_to', 'enabled',)
    list_filter = ('location_from', 'location_to', 'enabled',)
    search_fields = ('name', 'location_from__name, location_to__name',)
    ordering = ('enabled', 'name',)
    readonly_fields = ('name',)
    inlines = [TransferSupplementInline]

    form = TransferForm


class ExtraSupplementInline(admin.TabularInline):
    model = ExtraSupplement
    extra = 0


class ExtraSiteModel(SiteModel):
    model_order = 6130
    menu_label = MENU_LABEL_CONFIG_BASIC
    menu_group = 'Configuration Services'
    fields = ('name', 'enabled',)
    list_display = ('name', 'enabled',)
    list_filter = ('enabled',)
    search_fields = ('name',)
    ordering = ('enabled', 'name',)
    inlines = [ExtraSupplementInline]


bookings_site.register(Location, LocationSiteModel)
bookings_site.register(RoomType, RoomTypeSiteModel)

bookings_site.register(AllotmentRoomType, AllotmentRoomTypeSiteModel)

bookings_site.register(Allotment, AllotmentSiteModel)
bookings_site.register(Transfer, TransferSiteModel)
bookings_site.register(Extra, ExtraSiteModel)
