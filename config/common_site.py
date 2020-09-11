# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import messages
from django.contrib.admin.options import csrf_protect_m
from django.contrib.admin.utils import unquote, quote
from django.db import models
from django.forms.models import modelformset_factory
from django.http import HttpResponseRedirect
from django.shortcuts import render, reverse, redirect

from common.sites import SiteModel, CommonTabularInline, CommonStackedInline, CommonChangeList
from common.filters import DateFilter

from config.constants import (
    SERVICE_CATEGORY_ALLOTMENT, SERVICE_CATEGORY_TRANSFER, SERVICE_CATEGORY_EXTRA)

from config.forms import (
    ProviderAllotmentServiceForm, ProviderAllotmentDetailForm, ProviderAllotmentDetailInlineForm,
    ProviderTransferServiceForm, ProviderTransferDetailForm, ProviderTransferDetailInlineForm,
    ProviderExtraServiceForm, ProviderExtraDetailForm, ProviderExtraDetailInlineForm,
    AgencyAllotmentServiceForm, AgencyAllotmentDetailForm, AgencyAllotmentDetailInlineForm,
    AgencyTransferServiceForm, AgencyTransferDetailForm, AgencyTransferDetailInlineForm,
    AgencyExtraServiceForm, AgencyExtraDetailForm, AgencyExtraDetailInlineForm,
    AllotmentRoomTypeInlineForm, TransferZoneForm,
    LocationTransferIntervalInlineForm, ServiceAddonInlineForm,
    TransferPickupTimeInlineForm, PricesExportForm, ExtraForm,
    ServiceForm, ServiceBookDetailForm,
    ServiceBookDetailAllotmentForm, ServiceBookDetailTransferForm,
    ServiceBookDetailExtraForm, SearchServiceForm, ExtendCatalogForm
)
from config.models import (
    ServiceCategory, Location, Place, TransferInterval, Schedule,
    TransferZone, TransferPickupTime, AllotmentTransferZone, RoomType, Addon,
    Service,
    ServiceBookDetailAllotment, ServiceBookDetailTransfer, ServiceBookDetailExtra,
    Allotment, AllotmentRoomType, AllotmentBoardType,
    Transfer,
    Extra,
    AgencyAllotmentService, AgencyAllotmentDetail,
    AgencyTransferService, AgencyTransferDetail,
    AgencyExtraService, AgencyExtraDetail,
    ProviderAllotmentService, ProviderAllotmentDetail,
    ProviderTransferService, ProviderTransferDetail,
    ProviderExtraService, ProviderExtraDetail, ServiceAddon,
    CarRental, CarRentalOffice,
)
from config.services import ConfigServices
from config.top_filters import (
    RoomTypeTopFilter, LocationTopFilter, ServiceCategoryTopFilter,
    AddonTopFilter,
    AllotmentTopFilter, TransferTopFilter, ExtraTopFilter,
    ProviderTransferLocationTopFilter, ProviderTransferLocationAdditionalTopFilter,
    AgencyTransferLocationTopFilter, AgencyTransferLocationAdditionalTopFilter,
    DateTopFilter, AgencyTransferLocationTopFilter,
    ProviderDetailTransferTopFilter,
    ProviderTransferDetailLocationTopFilter, TransferDetailProviderTopFilter,
    PackageTopFilter,
)
from config.views import render_prices_pdf

from finance.top_filters import ProviderTopFilter, AgencyTopFilter
from finance.models import Agency

from reservas.admin import bookings_site


MENU_LABEL_CONFIG_BASIC = 'Configuration'
MENU_LABEL_CONFIG_GROUP = 'Configuration Services'
MENU_LABEL_PACKAGE = 'Package'
MENU_GROUP_LABEL_PACKAGE_SERVICES = 'Package Services By Type'


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
            return render_prices_pdf(
                request,
                {
                    'agency': Agency.objects.get(id=agency),
                    'date_from': date_from,
                    'date_to': date_to,
                    'services': Service.objects.filter(id__in=services).order_by('location__name')
                })
    context.update({'services': queryset})
    context.update({'form': PricesExportForm()})
    context.update({'site_title': 'Export Services'})
    context.update(extra_context or {})
    # context.update({'quote_id': id})
    return render(request, 'config/agency_prices_export.html', context=context)


def response_post_agency_service(request, obj, url):
    if hasattr(obj, 'agency_service') and obj.agency_service:
        return redirect(reverse(url, args=[obj.agency_service.pk]))
    agency_service = request.POST.get('agency_service')
    if agency_service:
        return redirect(reverse(url, args=[agency_service]))
    return None


def response_post_provider_service(request, obj, url):
    if hasattr(obj, 'provider_service') and obj.provider_service:
        return redirect(reverse(url, args=[obj.provider_service.pk]))
    provider_service = request.POST.get('provider_service')
    if provider_service:
        return redirect(reverse(url, args=[provider_service]))
    return None


class IncorrectLookupParameters(Exception):
    pass


class LocationPlaceInline(CommonStackedInline):
    model = Place
    extra = 0
    ordering = ['name']


class LocationTransferIntervalInline(CommonStackedInline):
    model = TransferInterval
    fk_name = 'location'
    extra = 0
    fields = [('t_location_from', 'interval')]
    ordering = ['t_location_from__name']

    form = LocationTransferIntervalInlineForm


class LocationScheduleInline(CommonStackedInline):
    model = Schedule
    fk_name = 'location'
    extra = 0
    fields = [('is_arrival', 'number', 'time')]
    ordering = ['is_arrival', 'number']


class LocationSiteModel(SiteModel):
    model_order = 6010
    menu_label = MENU_LABEL_CONFIG_BASIC
    fields = ('name', 'enabled', 'short_name')
    list_display = ('name', 'enabled',)
    top_filters = ('name', 'enabled',)
    inlines = [LocationPlaceInline, LocationTransferIntervalInline, LocationScheduleInline]
    save_as = True


class TransferPickupTimeInline(CommonTabularInline):
    model = TransferPickupTime
    fields = [('location', 'pickup_time'),]
    ordering = ['location',]
    extra = 0
    form = TransferPickupTimeInlineForm


class TransferZoneSiteModel(SiteModel):
    model_order = 6010
    menu_label = MENU_LABEL_CONFIG_BASIC
    fields = ('transfer', 'name',)
    list_display = ('transfer', 'name',)
    top_filters = ('transfer', 'name',)
    ordering = ('transfer', 'name',)
    form = TransferZoneForm
    inlines = [TransferPickupTimeInline]
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


class ServiceChangeList(CommonChangeList):
    def url_for_result(self, result):
        pk = getattr(result, self.pk_attname)
        category = getattr(result, 'category')
        if category == SERVICE_CATEGORY_ALLOTMENT:
            model_name = 'allotment'
        elif category == SERVICE_CATEGORY_TRANSFER:
            model_name = 'transfer'
        elif category == SERVICE_CATEGORY_EXTRA:
            model_name = 'extra'
        else:
            model_name = self.opts.app_label.model_name
        return reverse(
            '%s:%s_%s_change' % (
                self.model_admin.admin_site.site_namespace,
                self.opts.app_label,
                model_name),
            args=(quote(pk),),
            current_app=self.model_admin.admin_site.name)


class BaseServiceBookDetailSiteModel(SiteModel):
    def response_post_delete(self, request, obj):
        if hasattr(obj, 'service') and obj.service:
            if obj.service.category == 'A':
                return redirect(reverse('common:config_allotment_change',
                                        args=[obj.service.pk]))
            elif obj.service.category == 'T':
                return redirect(reverse('common:config_transfer_change',
                                        args=[obj.service.pk]))
            elif obj.service.category == 'E':
                return redirect(reverse('common:config_extra_change',
                                        args=[obj.service.pk]))
        service = request.POST.get('service')
        if service:
            service = Service.objects.get(id=service)
            if service.category == 'A':
                return redirect(reverse('common:config_allotment_change',
                                        args=[service.pk]))
            elif service.category == 'T':
                return redirect(reverse('common:config_transfer_change',
                                        args=[service.pk]))
            elif service.category == 'E':
                return redirect(reverse('common:config_extra_change',
                                        args=[service.pk]))
        return super(BaseServiceBookDetailSiteModel, self).response_post_delete(request, obj)

    def response_post_save_add(self, request, obj):
        if hasattr(obj, 'service') and obj.service:
            if obj.service.category == 'A':
                return redirect(reverse('common:config_allotment_change',
                                        args=[obj.service.pk]))
            elif obj.service.category == 'T':
                return redirect(reverse('common:config_transfer_change',
                                        args=[obj.service.pk]))
            elif obj.service.category == 'E':
                return redirect(reverse('common:config_extra_change',
                                        args=[obj.service.pk]))
        service = request.POST.get('service')
        if service:
            service = Service.objects.get(id=service)
            if service.category == 'A':
                return redirect(reverse('common:config_allotment_change',
                                        args=[service.pk]))
            elif service.category == 'T':
                return redirect(reverse('common:config_transfer_change',
                                        args=[service.pk]))
            elif service.category == 'E':
                return redirect(reverse('common:config_extra_change',
                                        args=[service.pk]))
        return super(BaseServiceBookDetailSiteModel, self).response_post_save_add(request, obj)

    def response_post_save_change(self, request, obj):
        if hasattr(obj, 'service') and obj.service:
            if obj.service.category == 'A':
                return redirect(reverse('common:config_allotment_change',
                                        args=[obj.service.pk]))
            elif obj.service.category == 'T':
                return redirect(reverse('common:config_transfer_change',
                                        args=[obj.service.pk]))
            elif obj.service.category == 'E':
                return redirect(reverse('common:config_extra_change',
                                        args=[obj.service.pk]))
        service = request.POST.get('service')
        if service:
            service = Service.objects.get(id=service)
            if service.category == 'A':
                return redirect(reverse('common:config_allotment_change',
                                        args=[service.pk]))
            elif service.category == 'T':
                return redirect(reverse('common:config_transfer_change',
                                        args=[service.pk]))
            elif service.category == 'E':
                return redirect(reverse('common:config_extra_change',
                                        args=[service.pk]))
        return super(BaseServiceBookDetailSiteModel, self).response_post_save_change(request, obj)


class ServiceBookDetailAllotmentSiteModel(BaseServiceBookDetailSiteModel):
    #model_order = 6150
    #menu_label = MENU_LABEL_CONFIG_BASIC
    #menu_group = MENU_LABEL_CONFIG_GROUP
    fields = [
        'service',
        ('book_service', 'search_location'),
        ('days_after', 'days_duration'),
        ('room_type', 'board_type'),
        'time',
        'service_addon',]
    list_display = (
        'service', 'book_service', 'days_after', 'days_duration',
        'room_type', 'board_type', 'service_addon',)
    top_filters = ('service',)
    ordering = ['service__name', 'days_after']
    form = ServiceBookDetailAllotmentForm


class ServiceBookDetailTransferSiteModel(BaseServiceBookDetailSiteModel):
    #model_order = 6160
    #menu_label = MENU_LABEL_CONFIG_BASIC
    #menu_group = MENU_LABEL_CONFIG_GROUP
    fields = [
        'service',
        ('book_service', 'search_location'),
        ('days_after', 'days_duration'),
        ('location_from', 'location_to'),
        ('pickup', 'dropoff'),
        ('place_from', 'place_to'),
        ('schedule_from', 'schedule_to'),
        ('schedule_time_from', 'schedule_time_to'),
        ('time', 'quantity'),
        'service_addon',]
    list_display = (
        'service', 'book_service', 'days_after', 'days_duration',
        'location_from', 'location_to', 'quantity', 'service_addon')
    top_filters = ('service',)
    ordering = ['service__name', 'days_after']
    form = ServiceBookDetailTransferForm


class ServiceBookDetailExtraSiteModel(BaseServiceBookDetailSiteModel):
    #model_order = 6170
    #menu_label = MENU_LABEL_CONFIG_BASIC
    #menu_group = MENU_LABEL_CONFIG_GROUP
    fields = [
        'service',
        ('book_service', 'search_location'),
        ('days_after', 'days_duration'),
        ('pickup_office', 'dropoff_office'),
        ('time', 'parameter', 'quantity'),
        'service_addon',]
    list_display = (
        'service', 'book_service', 'days_after', 'days_duration',
        'parameter', 'quantity', 'pickup_office', 'dropoff_office', 'service_addon')
    top_filters = ('service',)
    ordering = ['service__name', 'days_after']
    form = ServiceBookDetailExtraForm


class BaseServiceSiteModel(SiteModel):
    change_form_template = 'config/service_change_form.html'
    change_list_template = 'config/service_change_list.html'
    list_details_template = 'config/service_list_details.html'
    change_details_template = 'config/service_change_details.html'

    @csrf_protect_m
    def changelist_view(self, request, extra_context=None):
        search_service_form = SearchServiceForm()
        context = dict(search_service_form=search_service_form)
        context.update(extra_context or {})
        return super(BaseServiceSiteModel, self).changelist_view(
            request, context)

    def changeform_context(
            self, request, form, obj, formsets, inline_instances,
            add, opts, object_id, to_field, form_validated=None, extra_context=None):
        search_service_form = SearchServiceForm()
        context = dict(search_service_form=search_service_form)
        context.update(extra_context or {})
        return super(BaseServiceSiteModel, self).changeform_context(
            request, form, obj, formsets, inline_instances,
            add, opts, object_id, to_field, form_validated, context)

    def export_prices(self, request, queryset, extra_context=None):
        """
        This allows exporting service prices for certain agency and dates
        """
        context = {}
        context.update(self.get_model_extra_context(request))
        context.update(extra_context or {})
        return export_prices(request, queryset, context)


class ServiceSiteModel(BaseServiceSiteModel):
    model_order = 6100
    menu_label = MENU_LABEL_CONFIG_BASIC
    menu_group = MENU_LABEL_CONFIG_GROUP
    fields = (('name', 'enabled'), ('service_category', 'category'),)
    list_display = ('name', 'location', 'service_category',
                    'category', 'enabled')
    list_editable = ('enabled',)
    top_filters = ('name', ('service_category', ServiceCategoryTopFilter),
                   'location', 'category', 'enabled')
    ordering = ['enabled', 'category', 'name']
    actions = ['export_prices']
    form = ServiceForm

    def get_changelist(self, request, **kwargs):
        """
        Returns the ChangeList class for use on the changelist page.
        """
        return ServiceChangeList


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


class AllotmentTransferZoneInline(CommonTabularInline):
    model = AllotmentTransferZone
    extra = 0


class AllotmentSiteModel(BaseServiceSiteModel):
    model_order = 6110
    menu_label = MENU_LABEL_CONFIG_BASIC
    menu_group = MENU_LABEL_CONFIG_GROUP
    fields = (('name', 'location'),
              ('service_category', 'cost_type', 'is_shared_point'),
              ('phone', 'address'),
              ('time_from', 'time_to'),
              ('pax_range', 'enabled'),
              ('child_discount_percent', 'child_age', 'infant_age'))
    list_display = ('name', 'service_category', 'phone',
                    'location', 'is_shared_point', 'enabled',)
    top_filters = ('name', ('service_category', ServiceCategoryTopFilter),
                   ('location', LocationTopFilter),
                   'is_shared_point', 'enabled')
    ordering = ['enabled', 'name']
    inlines = [AllotmentRoomTypeInline, AllotmentBoardTypeInline,
               ServiceAddonInline, AllotmentTransferZoneInline,]
    actions = ['export_prices']
    form = ServiceForm


class TransferSiteModel(BaseServiceSiteModel):
    model_order = 6120
    menu_label = MENU_LABEL_CONFIG_BASIC
    menu_group = MENU_LABEL_CONFIG_GROUP
    fields = (
        ('name', 'service_category'), ('cost_type', 'max_capacity', 'is_shared'),
        ('pax_range', 'has_pickup_time', 'is_ticket', 'is_internal'),
        ('child_discount_percent', 'child_age', 'infant_age'), 'enabled',)
    list_display = ('name', 'cost_type', 'max_capacity', 'is_shared', 'is_ticket', 'enabled',
                    'infant_age', 'child_age')
    top_filters = (
        'name', ('service_category', ServiceCategoryTopFilter),
        AgencyTransferLocationTopFilter, 'is_shared', 'enabled')
    ordering = ['enabled', 'name']
    inlines = [ServiceAddonInline]
    actions = ['export_prices']
    form = ServiceForm


class ExtraSiteModel(BaseServiceSiteModel):
    model_order = 6130
    menu_label = MENU_LABEL_CONFIG_BASIC
    menu_group = MENU_LABEL_CONFIG_GROUP
    fields = ('name', 'service_category', 'location',
              ('cost_type', 'parameter_type'), 'max_capacity',
              ('pax_range', 'is_internal', 'default_as_package'),
              ('child_discount_percent', 'child_age', 'infant_age'),
              ('car_rental', 'enabled'),
              'included_services',
              'description')
    list_display = ('name', 'service_category', 'location', 'cost_type',
                    'parameter_type', 'max_capacity', 'enabled',
                    'pax_range', 'has_pax_range',
                    'infant_age', 'child_age')
    top_filters = ('name', ('service_category', ServiceCategoryTopFilter),
                   ('location', LocationTopFilter))
    ordering = ['enabled', 'name']
    inlines = [ServiceAddonInline]
    actions = ['export_prices']
    form = ExtraForm


class CatalogService(SiteModel):

    def get_details_model(self):
        return models.Model

    def build_details_formset(self):
        return modelformset_factory(
            model=self.get_details_model(),
            form=None,
            fields=None,
            extra=1,
        )

    def changeform_context(
            self, request, form, obj, formsets, inline_instances,
            add, opts, object_id, to_field, form_validated=None, extra_context=None):

        context = super(CatalogService, self).changeform_context(
            request, form, obj, formsets, inline_instances,
            add, opts, object_id, to_field, form_validated, extra_context)

        DetailsFormSet = self.build_details_formset()
        formset = DetailsFormSet(queryset=self.get_details_model().objects.none())
        context.update({'formset': formset})
        return context

    def save_related(self, request, form, formsets, change):
        super(CatalogService, self).save_related(request, form, formsets, change)
        DetailsFormSet = self.build_details_formset()
        formset = None
        catalog_service_id = form.instance.pk
        if catalog_service_id:
            formset = DetailsFormSet(request.POST)
            if formset.is_valid():
                for data in formset.cleaned_data:
                    try:
                        obj = self.get_details_model()(**data)
                        if isinstance(obj, (ProviderAllotmentDetail, ProviderTransferDetail, ProviderExtraDetail)):
                            obj.provider_service_id = catalog_service_id
                        elif isinstance(obj, (AgencyAllotmentDetail, AgencyTransferDetail, AgencyExtraDetail)):
                            obj.agency_service_id = catalog_service_id
                        else:
                            continue
                        obj.save()
                    except Exception:
                        continue

    # A base action to use in all children
    def extend_catalog_prices(self, request, queryset, title=None):
        form = None
        if 'apply' in request.POST:
            form = ExtendCatalogForm(request.POST)
            if form.is_valid():
                max_util = form.cleaned_data['max_util']
                min_util = form.cleaned_data['min_util']
                increase_percent = form.cleaned_data['diff_percent']
                increase_value = form.cleaned_data['diff_value']
                if (increase_percent is None or increase_percent == '') and (
                        increase_value is None or increase_value == ''):
                    # either increment should be specified!
                    messages.error(request,
                                   'Either Percent or Absolute increment'
                                   ' must be specified')
                    return HttpResponseRedirect(request.get_full_path())

                results = ConfigServices.next_year_catalog_amounts(
                    catalog_model=self.model,
                    catalog_service_ids=queryset.values_list('pk', flat=True),
                    diff_percent=increase_percent,
                    diff_amount=increase_value,
                    min_diff=min_util,
                    max_diff=max_util)
                for message in results['services_error_messages']:
                    messages.error(request, message)
                for message in results['details_error_messages']:
                    messages.error(request, message)
                if results['services_error_count']:
                    messages.error(request,
                    '{} services had problems while processing'.format(results['services_error_count']))
                if results['details_error_count']:
                    messages.error(request,
                    '{} Details had problems while processing'.format(results['details_error_count']))
                if results['services_success_count']:
                    self.message_user(request,
                                  "A total of {} Services and {} Details were successfully generated".format(results['services_success_count'],
                                                                                                            results['details_success_count']))
                return HttpResponseRedirect(request.get_full_path())
        if not form:
            form = ExtendCatalogForm(initial={
                '_selected_action': queryset.values_list('pk', flat=True)})
        context = {
            'form': form,
            'items': queryset,
            'title': title or 'Generate Provider costs for following year'}
        context.update(self.get_model_extra_context(request))
        return render(request, 'config/catalog_extend_dates.html', context)


class ProviderAllotmentDetailInline(CommonTabularInline):
    model = ProviderAllotmentDetail
    extra = 0
    fields = (
        ('single_supplement', 'third_pax_discount'),
        ('room_type', 'board_type'),
        ('pax_range_min', 'pax_range_max'),
        ('ad_1_amount', 'ch_1_ad_1_amount', 'ch_2_ad_1_amount',), # 'ch_3_ad_1_amount',),
        ('ad_2_amount', 'ch_1_ad_2_amount', 'ch_2_ad_2_amount',), # 'ch_3_ad_2_amount',),
        ('ad_3_amount', 'ch_1_ad_3_amount'), # 'ch_2_ad_3_amount', 'ch_3_ad_3_amount',),
        ('ad_4_amount',), # 'ch_1_ad_4_amount', 'ch_2_ad_3_amount', 'ch_3_ad_3_amount',),
    )
    ordering = ['id', 'room_type', 'board_type']
    form = ProviderAllotmentDetailInlineForm
    list_select_related = ('room_type', 'addon')
    template = 'config/edit_inline/catalog_tabular_inline.html'
    extra = 1

    def get_queryset(self, request):
        queryset = super(ProviderAllotmentDetailInline, self).get_queryset(request)
        queryset = queryset.none()
        return queryset


class ProviderAllotmentServiceSiteModel(CatalogService):
    model_order = 7220
    menu_label = MENU_LABEL_CONFIG_BASIC
    menu_group = 'Costs Catalogue'
    #recent_allowed = True
    fields = ('provider', 'service', 'date_from', 'date_to',)
    list_display = ('service', 'provider', 'date_from', 'date_to',)
    top_filters = (
        ('service', AllotmentTopFilter), ('provider', ProviderTopFilter),
        'service__service_category',
        ('date_to', DateTopFilter))
    inlines = [ProviderAllotmentDetailInline]
    ordering = ['service', 'provider', '-date_from']
    list_select_related = ('service', 'provider')
    form = ProviderAllotmentServiceForm
    add_form_template = 'config/catalog_service_change_form.html'
    change_form_template = 'config/catalog_service_change_form.html'
    save_as = True

    actions = ['rewrite_agency_amounts',
               'update_agency_amounts',
               'extend_catalog_prices']

    def rewrite_agency_amounts(self, request, queryset):
        ConfigServices.generate_agency_allotments_amounts_from_providers_allotments(
            list(queryset.all()), False)
    rewrite_agency_amounts.short_description = "Generate All Agency Prices"

    def update_agency_amounts(self, request, queryset):
        ConfigServices.generate_agency_allotments_amounts_from_providers_allotments(
            list(queryset.all()), True)
    update_agency_amounts.short_description = "Generate New Agency Prices"

    def extend_catalog_prices(self, request, queryset):
        return super(ProviderAllotmentServiceSiteModel, self).extend_catalog_prices(request, queryset)
    extend_catalog_prices.short_description = 'Extend selected Costs 1 year'

    def get_details_model(self):
        return ProviderAllotmentDetail

    def build_details_formset(self):
        return modelformset_factory(
            model=ProviderAllotmentDetail,
            form=ProviderAllotmentDetailInlineForm,
            fields=[
                'room_type', 'board_type', 'addon',
                'pax_range_min', 'pax_range_max',
                'ad_1_amount', 'ch_1_ad_1_amount', 'ch_2_ad_1_amount',
                'ad_2_amount', 'ch_1_ad_2_amount', 'ch_2_ad_2_amount',
                'ad_3_amount', 'ch_1_ad_3_amount', 'ch_2_ad_3_amount',
                'ad_4_amount', 'ch_1_ad_4_amount',],
            extra=1,
        )


class ProviderAllotmentDetailSiteModel(SiteModel):
    recent_allowed = False
    fieldsets = (
        (None, {
            'fields':(
                'provider_service',
                ('room_type', 'board_type', 'addon'),
                ('pax_range_min', 'pax_range_max'),
                ('single_supplement', 'third_pax_discount'),
                ('ad_1_amount', 'ch_1_ad_1_amount', 'ch_2_ad_1_amount'), #, 'ch_3_ad_1_amount'
                ('ad_2_amount', 'ch_1_ad_2_amount', 'ch_2_ad_2_amount',), # 'ch_3_ad_2_amount'
                ('ad_3_amount', 'ch_1_ad_3_amount', 'ch_2_ad_3_amount',), # 'ch_3_ad_3_amount'
                ('ad_4_amount', 'ch_1_ad_4_amount',), # 'ch_2_ad_3_amount', 'ch_3_ad_3_amount',),
                # ('ch_1_ad_0_amount', 'ch_2_ad_0_amount', 'ch_3_ad_0_amount',),
                ),
            'classes': ('catalogue-detail',)
            }
        ),
    )
    list_display = (
        'provider_service', 'room_type', 'board_type', 'addon',
        'pax_range_min', 'pax_range_max',
        'ad_1_amount', 'ad_2_amount', 'ad_3_amount', 'ad_4_amount')
    #top_filters = (
    #    ('provider_service__service', AllotmentTopFilter), ('provider_service__provider', ProviderTopFilter),
    #    ('provider_service__date_to', DateTopFilter))
    ordering = [
        'provider_service__service', '-provider_service__date_from', 'provider_service__provider']
    form = ProviderAllotmentDetailForm

    def response_post_delete(self, request, obj):
        response = response_post_provider_service(
            request, obj, 'common:config_providerallotmentservice_change')
        if response:
            return response
        return super(ProviderAllotmentDetailSiteModel, self).response_post_delete(request, obj)

    def response_post_save_add(self, request, obj):
        response = response_post_provider_service(
            request, obj, 'common:config_providerallotmentservice_change')
        if response:
            return response
        return super(ProviderAllotmentDetailSiteModel, self).response_post_save_add(request, obj)

    def response_post_save_change(self, request, obj):
        response = response_post_provider_service(
            request, obj, 'common:config_providerallotmentservice_change')
        if response:
            return response
        return super(ProviderAllotmentDetailSiteModel, self).response_post_save_change(request, obj)


class ProviderTransferDetailInline(CommonTabularInline):
    model = ProviderTransferDetail
    extra = 0
    fields = (
        ('location_from', 'location_to', 'addon'),
        ('pax_range_min', 'pax_range_max'),
        ('ad_1_amount', 'ch_1_ad_1_amount'),
    )
    ordering = ['location_from', 'location_to']
    form = ProviderTransferDetailInlineForm
    list_select_related = ('location_from', 'location_to', 'addon')
    template = 'config/edit_inline/catalog_tabular_inline.html'

    def get_queryset(self, request):
        return super(ProviderTransferDetailInline, self).get_queryset(request).none()


class ProviderTransferServiceSiteModel(CatalogService):
    model_order = 7230
    menu_label = MENU_LABEL_CONFIG_BASIC
    menu_group = 'Costs Catalogue'
    #recent_allowed = True
    fields = ('provider', 'service', 'date_from', 'date_to',)
    list_display = ('service', 'provider', 'date_from', 'date_to',)
    top_filters = (
        ('service', TransferTopFilter), ('provider', ProviderTopFilter),
        'service__service_category',
        ('date_to', DateTopFilter),
        ProviderTransferLocationTopFilter, ProviderTransferLocationAdditionalTopFilter)
    inlines = [ProviderTransferDetailInline]
    ordering = ['service', 'provider', '-date_from']
    list_select_related = ('service', 'provider')
    form = ProviderTransferServiceForm
    add_form_template = 'config/catalog_service_change_form.html'
    change_form_template = 'config/catalog_service_change_form.html'
    save_as = True

    actions = ['rewrite_agency_amounts',
                'update_agency_amounts',
                'extend_catalog_prices']

    def rewrite_agency_amounts(self, request, queryset):
        ConfigServices.generate_agency_transfers_amounts_from_providers_transfers(
            list(queryset.all()), False)
    rewrite_agency_amounts.short_description = "Generate All Agency Prices"

    def update_agency_amounts(self, request, queryset):
        ConfigServices.generate_agency_transfers_amounts_from_providers_transfers(
            list(queryset.all()), True)
    update_agency_amounts.short_description = "Generate New Agency Prices"

    def extend_catalog_prices(self, request, queryset):
        return super(ProviderTransferServiceSiteModel, self).extend_catalog_prices(request, queryset)
    extend_catalog_prices.short_description = 'Extend selected Costs 1 year'

    def get_details_model(self):
        return ProviderTransferDetail

    def build_details_formset(self):
        return modelformset_factory(
            model=ProviderTransferDetail,
            form=ProviderTransferDetailInlineForm,
            fields=[
                'location_from', 'location_to', 'addon',
                'pax_range_min', 'pax_range_max',
                'ad_1_amount', 'ch_1_ad_1_amount',],
            extra=1,
        )


class ProviderTransferDetailSiteModel(SiteModel):
    recent_allowed = False
    fields = (
        ('location_from', 'location_to', 'addon'),
        ('pax_range_min', 'pax_range_max'),
        ('ad_1_amount', 'ch_1_ad_1_amount'),
    )
    list_display = (
        'location_from', 'location_to',
        'provider_service',
        'pax_range_min', 'pax_range_max',
        'cost_type', 'ad_1_amount', 'ch_1_ad_1_amount')
    top_filters = (
        ProviderTransferDetailLocationTopFilter,
        ProviderDetailTransferTopFilter, TransferDetailProviderTopFilter, ('provider_service__date_to', DateFilter))
    ordering = [
        'location_from', 'location_to',
        'provider_service__service', 'pax_range_max', 'ad_1_amount',]
    form = ProviderTransferDetailForm
    list_select_related = ('location_from', 'location_to', 'addon')

    def response_post_delete(self, request, obj):
        response = response_post_provider_service(
            request, obj, 'common:config_providertransferservice_change')
        if response:
            return response
        return super(ProviderTransferDetailSiteModel, self).response_post_delete(request, obj)

    def response_post_save_add(self, request, obj):
        response = response_post_provider_service(
            request, obj, 'common:config_providertransferservice_change')
        if response:
            return response
        return super(ProviderTransferDetailSiteModel, self).response_post_save_add(request, obj)

    def response_post_save_change(self, request, obj):
        response = response_post_provider_service(
            request, obj, 'common:config_providertransferservice_change')
        if response:
            return response
        return super(ProviderTransferDetailSiteModel, self).response_post_save_change(request, obj)


class ProviderExtraDetailInline(CommonTabularInline):
    model = ProviderExtraDetail
    extra = 0
    fields = (
        ('pax_range_min', 'pax_range_max'),
        ('addon','ad_1_amount'))
    ordering = ['addon', 'pax_range_min', 'id']
    form = ProviderExtraDetailInlineForm
    template = 'config/edit_inline/catalog_tabular_inline.html'
    extra = 1

    def get_queryset(self, request):
        return super(ProviderExtraDetailInline, self).get_queryset(request).none()


class ProviderExtraServiceSiteModel(CatalogService):
    model_order = 7240
    menu_label = MENU_LABEL_CONFIG_BASIC
    menu_group = 'Costs Catalogue'
    #recent_allowed = True
    fields = ('provider', 'service', 'date_from', 'date_to',)
    list_display = ('service', 'provider', 'date_from', 'date_to',)
    top_filters = (
        ('service', ExtraTopFilter), ('provider', ProviderTopFilter),
        'service__service_category',
        ('date_to', DateTopFilter))
    inlines = [ProviderExtraDetailInline]
    ordering = ['service', 'provider', '-date_from']
    list_select_related = ('service', 'provider')
    form = ProviderExtraServiceForm
    add_form_template = 'config/catalog_service_change_form.html'
    change_form_template = 'config/catalog_service_change_form.html'
    save_as = True

    actions = ['rewrite_agency_amounts',
               'update_agency_amounts',
               'extend_catalog_prices']

    def rewrite_agency_amounts(self, request, queryset):
        ConfigServices.generate_agency_extras_amounts_from_providers_extras(
            list(queryset.all()), False)
    rewrite_agency_amounts.short_description = "Generate All Agency Prices"

    def update_agency_amounts(self, request, queryset):
        ConfigServices.generate_agency_extras_amounts_from_providers_extras(
            list(queryset.all()), True)
    update_agency_amounts.short_description = "Generate New Agency Prices"

    def extend_catalog_prices(self, request, queryset):
        return super(ProviderExtraServiceSiteModel, self).extend_catalog_prices(request, queryset)
    extend_catalog_prices.short_description = 'Extend selected Costs 1 year'

    def get_details_model(self):
        return ProviderExtraDetail

    def build_details_formset(self):
        return modelformset_factory(
            model=ProviderExtraDetail,
            form=ProviderExtraDetailInlineForm,
            fields=[
                'addon',
                'pax_range_min', 'pax_range_max',
                'ad_1_amount',],
            extra=1,
        )


class ProviderExtraDetailSiteModel(SiteModel):
    recent_allowed = False
    fields = (
        'provider_service',
        ('pax_range_min', 'pax_range_max'),
        ('addon', 'ad_1_amount'), )
    list_display = ('provider_service', 'pax_range_min', 'pax_range_max', 'addon', 'ad_1_amount')
    #top_filters = (
    #    ('provider_service__service', ExtraTopFilter), ('provider_service__provider', ProviderTopFilter),
    #    ('provider_service__date_to', DateTopFilter))
    ordering = [
        'provider_service__service', '-provider_service__date_from', 'provider_service__provider']
    form = ProviderExtraDetailForm

    def response_post_delete(self, request, obj):
        response = response_post_provider_service(
            request, obj, 'common:config_providerextraservice_change')
        if response:
            return response
        return super(ProviderExtraDetailSiteModel, self).response_post_delete(request, obj)

    def response_post_save_add(self, request, obj):
        response = response_post_provider_service(
            request, obj, 'common:config_providerextraservice_change')
        if response:
            return response
        return super(ProviderExtraDetailSiteModel, self).response_post_save_add(request, obj)

    def response_post_save_change(self, request, obj):
        response = response_post_provider_service(
            request, obj, 'common:config_providerextraservice_change')
        if response:
            return response
        return super(ProviderExtraDetailSiteModel, self).response_post_save_change(request, obj)


class AgencyAllotmentDetailInline(CommonTabularInline):
    model = AgencyAllotmentDetail
    extra = 0
    fields = (
        ('room_type', 'board_type'),
        ('pax_range_min', 'pax_range_max'),
        ('ad_1_amount', 'ch_1_ad_1_amount', 'ch_2_ad_1_amount'), #, 'ch_3_ad_1_amount',),
        ('ad_2_amount', 'ch_1_ad_2_amount', 'ch_2_ad_2_amount',), # 'ch_3_ad_2_amount',),
        ('ad_3_amount', 'ch_1_ad_3_amount'), #'ch_2_ad_3_amount',), 'ch_3_ad_3_amount',),
        ('ad_4_amount',), # 'ch_1_ad_4_amount'), 'ch_2_ad_3_amount',), 'ch_3_ad_3_amount',),
        # ('ch_1_ad_0_amount', 'ch_2_ad_0_amount', 'ch_3_ad_0_amount',),
    )
    ordering = ['room_type', 'board_type']
    form = AgencyAllotmentDetailInlineForm
    list_select_related = ('room_type', 'addon')
    template = 'config/edit_inline/catalog_tabular_inline.html'
    extra = 1

    def get_queryset(self, request):
        return super(AgencyAllotmentDetailInline, self).get_queryset(request).none()


class AgencyAllotmentServiceSiteModel(CatalogService):
    model_order = 7120
    menu_label = MENU_LABEL_CONFIG_BASIC
    menu_group = 'Selling Prices Catalogue'
    #recent_allowed = True
    fields = ('agency', 'service', 'date_from', 'date_to',)
    list_display = ('agency', 'service', 'date_from', 'date_to',)
    top_filters = (
        ('service', AllotmentTopFilter), ('agency', AgencyTopFilter),
        'service__service_category',
        ('date_to', DateTopFilter))
    inlines = [AgencyAllotmentDetailInline]
    ordering = ['service', 'agency', '-date_from']
    list_select_related = ('agency', 'service')
    form = AgencyAllotmentServiceForm
    add_form_template = 'config/catalog_service_change_form.html'
    change_form_template = 'config/catalog_service_change_form.html'
    save_as = True
    actions = ['extend_catalog_prices']

    def extend_catalog_prices(self, request, queryset):
        title = 'Generate Agency Prices for listed services on next year'
        return super(AgencyAllotmentServiceSiteModel, self).extend_catalog_prices(
            request,
            queryset,
            title)
    extend_catalog_prices.short_description = 'Extend selected Costs 1 year'

    def get_details_model(self):
        return AgencyAllotmentDetail

    def build_details_formset(self):
        return modelformset_factory(
            model=AgencyAllotmentDetail,
            form=AgencyAllotmentDetailInlineForm,
            fields=[
                'room_type', 'board_type', 'addon',
                'pax_range_min', 'pax_range_max',
                'ad_1_amount', 'ch_1_ad_1_amount', 'ch_2_ad_1_amount',
                'ad_2_amount', 'ch_1_ad_2_amount', 'ch_2_ad_2_amount',
                'ad_3_amount', 'ch_1_ad_3_amount', 'ch_2_ad_3_amount',
                'ad_4_amount', 'ch_1_ad_4_amount',],
            extra=1,
        )


class AgencyAllotmentDetailSiteModel(SiteModel):
    recent_allowed = False
    fields = (
        'agency_service',
        ('room_type', 'board_type', 'addon'),
        ('pax_range_min', 'pax_range_max'),
        ('ad_1_amount', 'ch_1_ad_1_amount', 'ch_2_ad_1_amount'), #, 'ch_3_ad_1_amount',),
        ('ad_2_amount', 'ch_1_ad_2_amount', 'ch_2_ad_2_amount',), # 'ch_3_ad_2_amount',),
        ('ad_3_amount', 'ch_1_ad_3_amount', 'ch_2_ad_3_amount',), # 'ch_3_ad_3_amount',),
        ('ad_4_amount', 'ch_1_ad_4_amount',), # 'ch_2_ad_3_amount',), # 'ch_3_ad_3_amount',),
        # ('ch_1_ad_0_amount', 'ch_2_ad_0_amount', 'ch_3_ad_0_amount',),
    )
    list_display = (
        'agency_service', 'room_type', 'board_type', 'addon',
        'pax_range_min', 'pax_range_max',
        'ad_1_amount', 'ad_2_amount', 'ad_3_amount', 'ad_4_amount')
    #top_filters = (
    #    ('agency_service__service', AllotmentTopFilter), ('agency_service__agency', AgencyTopFilter),
    #    ('agency_service__date_to', DateTopFilter))
    ordering = [
        'agency_service__service', '-agency_service__date_from', 'agency_service__agency']
    form = AgencyAllotmentDetailForm

    def response_post_delete(self, request, obj):
        response = response_post_agency_service(
            request, obj, 'common:config_agencyallotmentservice_change')
        if response:
            return response
        return super(AgencyAllotmentDetailSiteModel, self).response_post_delete(request, obj)

    def response_post_save_add(self, request, obj):
        response = response_post_agency_service(
            request, obj, 'common:config_agencyallotmentservice_change')
        if response:
            return response
        return super(AgencyAllotmentDetailSiteModel, self).response_post_save_add(request, obj)

    def response_post_save_change(self, request, obj):
        response = response_post_agency_service(
            request, obj, 'common:config_agencyallotmentservice_change')
        if response:
            return response
        return super(AgencyAllotmentDetailSiteModel, self).response_post_save_change(request, obj)


class AgencyTransferDetailInline(CommonTabularInline):
    model = AgencyTransferDetail
    extra = 0
    fields = (
        ('location_from', 'location_to', 'not_reversible', 'addon'),
        ('pax_range_min', 'pax_range_max'),
        ('ad_1_amount', 'ch_1_ad_1_amount'),
    )
    ordering = ['location_from', 'location_to']
    form = AgencyTransferDetailInlineForm
    list_select_related = ('location_from', 'location_to', 'addon')

    def get_queryset(self, request):
        return super(AgencyTransferDetailInline, self).get_queryset(request).none()


class AgencyTransferServiceSiteModel(CatalogService):
    model_order = 7130
    menu_label = MENU_LABEL_CONFIG_BASIC
    menu_group = 'Selling Prices Catalogue'
    #recent_allowed = True
    fields = ('agency', 'service', 'date_from', 'date_to',)
    list_display = ('agency', 'service', 'date_from', 'date_to',)
    top_filters = (
        ('service', TransferTopFilter), ('agency', AgencyTopFilter),
        'service__service_category',
        ('date_to', DateTopFilter),
        AgencyTransferLocationTopFilter, AgencyTransferLocationAdditionalTopFilter)
    inlines = [AgencyTransferDetailInline]
    ordering = ['service', 'agency', '-date_from']
    list_select_related = ('service', 'agency')
    form = AgencyTransferServiceForm
    add_form_template = 'config/catalog_service_change_form.html'
    change_form_template = 'config/catalog_service_change_form.html'
    save_as = True
    actions = ['extend_catalog_prices']

    def extend_catalog_prices(self, request, queryset):
        title = 'Generate Agency Prices for listed services on next year'
        return super(AgencyTransferServiceSiteModel, self).extend_catalog_prices(
            request,
            queryset,
            title)
    extend_catalog_prices.short_description = 'Extend selected Costs 1 year'

    def get_details_model(self):
        return AgencyTransferDetail

    def build_details_formset(self):
        return modelformset_factory(
            model=AgencyTransferDetail,
            form=AgencyTransferDetailInlineForm,
            fields=[
                'location_from', 'location_to', 'addon',
                'pax_range_min', 'pax_range_max',
                'ad_1_amount', 'ch_1_ad_1_amount',],
            extra=1,
        )


class AgencyTransferDetailSiteModel(SiteModel):
    recent_allowed = False
    fields = (
        'agency_service',
        ('location_from', 'location_to', 'addon'),
        ('pax_range_min', 'pax_range_max', 'not_reversible'),
        ('ad_1_amount', 'ch_1_ad_1_amount'))
    list_display = (
        'agency_service', 'location_from', 'location_to', 'addon',
        'pax_range_min', 'pax_range_max', 'ad_1_amount', 'ch_1_ad_1_amount')
    #top_filters = (
    #    ('agency_service__service', TransferTopFilter), ('agency_service__agency', AgencyTopFilter),
    #    ('agency_service__date_to', DateTopFilter))
    ordering = [
        'agency_service__service', '-agency_service__date_from', 'agency_service__agency']
    form = AgencyTransferDetailForm

    def response_post_delete(self, request, obj):
        response = response_post_agency_service(
            request, obj, 'common:config_agencytransferservice_change')
        if response:
            return response
        return super(AgencyTransferDetailSiteModel, self).response_post_delete(request, obj)

    def response_post_save_add(self, request, obj):
        response = response_post_agency_service(
            request, obj, 'common:config_agencytransferservice_change')
        if response:
            return response
        return super(AgencyTransferDetailSiteModel, self).response_post_save_add(request, obj)

    def response_post_save_change(self, request, obj):
        response = response_post_agency_service(
            request, obj, 'common:config_agencytransferservice_change')
        if response:
            return response
        return super(AgencyTransferDetailSiteModel, self).response_post_save_change(request, obj)


class AgencyExtraDetailInline(CommonTabularInline):
    model = AgencyExtraDetail
    extra = 0
    fields = (
        ('pax_range_min', 'pax_range_max'),
        ('addon', 'ad_1_amount'), )
    ordering = ['addon', 'pax_range_min', 'pax_range_max']
    form = AgencyExtraDetailInlineForm
    list_select_related = ('addon')

    def get_queryset(self, request):
        return super(AgencyExtraDetailInline, self).get_queryset(request).none()


class AgencyExtraServiceSiteModel(CatalogService):
    model_order = 7140
    menu_label = MENU_LABEL_CONFIG_BASIC
    menu_group = 'Selling Prices Catalogue'
    #recent_allowed = True
    fields = ('agency', 'service', 'date_from', 'date_to')
    list_display = ('agency', 'service', 'date_from', 'date_to',)
    top_filters = (
        ('service', ExtraTopFilter), ('agency', AgencyTopFilter),
        'service__service_category',
        ('date_to', DateTopFilter))
    inlines = [AgencyExtraDetailInline]
    ordering = ['service', 'agency', '-date_from']
    list_select_related = ('service', 'agency')
    form = AgencyExtraServiceForm
    add_form_template = 'config/catalog_service_change_form.html'
    change_form_template = 'config/catalog_service_change_form.html'
    save_as = True
    actions = ['extend_catalog_prices']

    def extend_catalog_prices(self, request, queryset):
        title = 'Generate Agency Prices for listed services on next year'
        return super(AgencyExtraServiceSiteModel, self).extend_catalog_prices(
            request,
            queryset,
            title)
    extend_catalog_prices.short_description = 'Extend selected Costs 1 year'

    def get_details_model(self):
        return AgencyExtraDetail

    def build_details_formset(self):
        return modelformset_factory(
            model=AgencyExtraDetail,
            form=AgencyExtraDetailInlineForm,
            fields=[
                'addon',
                'pax_range_min', 'pax_range_max',
                'ad_1_amount'],
            extra=1,
        )


class AgencyExtraDetailSiteModel(SiteModel):
    recent_allowed = False
    fields = (
        'agency_service',
        ('pax_range_min', 'pax_range_max'),
        ('addon', 'ad_1_amount'), )
    list_display = ('agency_service', 'pax_range_min', 'pax_range_max', 'addon', 'ad_1_amount')
    #top_filters = (
    #    ('agency_service__service', ExtraTopFilter), ('agency_service__agency', AgencyTopFilter),
    #    ('agency_service__date_to', DateTopFilter))
    ordering = [
        'agency_service__service', '-agency_service__date_from', 'agency_service__agency']
    form = AgencyExtraDetailForm

    def response_post_delete(self, request, obj):
        response = response_post_agency_service(
            request, obj, 'common:config_agencyextraservice_change')
        if response:
            return response
        return super(AgencyExtraDetailSiteModel, self).response_post_delete(request, obj)

    def response_post_save_add(self, request, obj):
        response = response_post_agency_service(
            request, obj, 'common:config_agencyextraservice_change')
        if response:
            return response
        return super(AgencyExtraDetailSiteModel, self).response_post_save_add(request, obj)

    def response_post_save_change(self, request, obj):
        response = response_post_agency_service(
            request, obj, 'common:config_agencyextraservice_change')
        if response:
            return response
        return super(AgencyExtraDetailSiteModel, self).response_post_save_change(request, obj)


class CarRentalOfficeInline(CommonStackedInline):
    model = CarRentalOffice
    extra = 0
    fields = ('office',)
    ordering = ['office']


class CarRentalSiteModel(SiteModel):
    model_order = 6050
    menu_label = MENU_LABEL_CONFIG_BASIC
    fields = ('name',)
    list_display = ('name',)
    top_filters = ('name',)
    inlines = [CarRentalOfficeInline]
    ordering = ['name',]


bookings_site.register(ServiceCategory, ServiceCategorySiteModel)
bookings_site.register(Location, LocationSiteModel)
bookings_site.register(TransferZone, TransferZoneSiteModel)
bookings_site.register(RoomType, RoomTypeSiteModel)
bookings_site.register(Addon, AddonSiteModel)
bookings_site.register(CarRental, CarRentalSiteModel)

bookings_site.register(AllotmentRoomType, AllotmentRoomTypeSiteModel)
bookings_site.register(AllotmentBoardType, AllotmentBoardTypeSiteModel)

bookings_site.register(Service, ServiceSiteModel)
bookings_site.register(Allotment, AllotmentSiteModel)
bookings_site.register(Transfer, TransferSiteModel)
bookings_site.register(Extra, ExtraSiteModel)
bookings_site.register(ServiceBookDetailAllotment, ServiceBookDetailAllotmentSiteModel)
bookings_site.register(ServiceBookDetailTransfer, ServiceBookDetailTransferSiteModel)
bookings_site.register(ServiceBookDetailExtra, ServiceBookDetailExtraSiteModel)

bookings_site.register(AgencyAllotmentService, AgencyAllotmentServiceSiteModel)
bookings_site.register(AgencyAllotmentDetail, AgencyAllotmentDetailSiteModel)
bookings_site.register(AgencyTransferService, AgencyTransferServiceSiteModel)
bookings_site.register(AgencyTransferDetail, AgencyTransferDetailSiteModel)
bookings_site.register(AgencyExtraService, AgencyExtraServiceSiteModel)
bookings_site.register(AgencyExtraDetail, AgencyExtraDetailSiteModel)

bookings_site.register(ProviderAllotmentService, ProviderAllotmentServiceSiteModel)
bookings_site.register(ProviderAllotmentDetail, ProviderAllotmentDetailSiteModel)
bookings_site.register(ProviderTransferService, ProviderTransferServiceSiteModel)
bookings_site.register(ProviderTransferDetail, ProviderTransferDetailSiteModel)
bookings_site.register(ProviderExtraService, ProviderExtraServiceSiteModel)
bookings_site.register(ProviderExtraDetail, ProviderExtraDetailSiteModel)
