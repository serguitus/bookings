"""
Config admin
"""
from config.models import (
    Location, Service, ServiceProvider, Cost,
    Extra, ExtraServiceProvider,
    Allotment, AllotmentRoomType, AllotmentBoardType, AllotmentServiceProvider,
    Transfer, TransferServiceProvider,
    PriceCatalogue)

from django.contrib import admin

from reservas.admin import reservas_admin, SelfTabularInline, ExtendedModelAdmin


class CostInline(admin.TabularInline):
    model = Cost
    extra = 0


class ExtendedLocationAdmin(ExtendedModelAdmin):
    actions_on_top = False
    search_fields = ('name',)

reservas_admin.register(Location, ExtendedLocationAdmin)


class ExtendedServiceAdmin(ExtendedModelAdmin):
    readonly_model = True
    actions_on_top = False
    search_fields = ('name',)
    list_display = ('name', 'category', 'enabled')
    fields = ('name', 'category', 'enabled')

reservas_admin.register(Service, ExtendedServiceAdmin)


class ExtendedServiceProviderAdmin(ExtendedModelAdmin):
    readonly_model = True
    actions_on_top = False
    search_fields = ('service', 'provider')
    list_display = ('service', 'provider')
    list_filter = ('service', 'provider')
    fields = ('service', 'provider')


reservas_admin.register(ServiceProvider, ExtendedServiceProviderAdmin)


#================
# Extra
#================

class ExtraProviderInline(admin.TabularInline):
    model = ExtraServiceProvider
    extra = 0


class ExtendedExtraAdmin(ExtendedModelAdmin):
    actions_on_top = False
    search_fields = ('name',)
    readonly_fields = ('category',)
    list_display = ('name', 'category', 'enabled')
    fields = ('name', 'category', 'enabled')
    inlines = [ExtraProviderInline]

reservas_admin.register(Extra, ExtendedExtraAdmin)


class ExtendedExtraServiceProviderAdmin(ExtendedModelAdmin):
    actions_on_top = False
    search_fields = ('service', 'provider')
    list_display = ('service', 'provider', 'cost_type')
    list_filter = ('service', 'provider', 'cost_type')
    fields = ('service', 'provider', 'cost_type')
    inlines = [CostInline]


reservas_admin.register(ExtraServiceProvider, ExtendedExtraServiceProviderAdmin)


#================
# Allotment
#================

class AllotmentRoomTypeInline(admin.TabularInline):
    model = AllotmentRoomType
    extra = 0


class AllotmentBoardTypeInline(admin.TabularInline):
    model = AllotmentBoardType
    extra = 0


class AllotmentProviderInline(admin.TabularInline):
    model = AllotmentServiceProvider
    extra = 0


class ExtendedAllotmentAdmin(ExtendedModelAdmin):
    actions_on_top = False
    search_fields = ('name',)
    list_display = ('name', 'category', 'enabled', 'location', 'time_from', 'time_to')
    fields = ('name', 'category', 'enabled', 'location', 'time_from', 'time_to')
    readonly_fields = ('category',)
    inlines = [
        AllotmentRoomTypeInline, AllotmentBoardTypeInline, AllotmentProviderInline]

reservas_admin.register(Allotment, ExtendedAllotmentAdmin)


class ExtendedAllotmentServiceProviderAdmin(ExtendedModelAdmin):
    actions_on_top = False
    search_fields = ('service', 'provider')
    list_display = ('service', 'provider', 'cost_type')
    list_filter = ('service', 'provider', 'cost_type')
    fields = ('service', 'provider', 'cost_type')
    inlines = [CostInline]

reservas_admin.register(AllotmentServiceProvider, ExtendedAllotmentServiceProviderAdmin)


#================
# Transfer
#================

class TransferProviderInline(admin.TabularInline):
    model = TransferServiceProvider
    extra = 0


class ExtendedTransferAdmin(ExtendedModelAdmin):
    actions_on_top = False
    search_fields = ('name',)
    list_display = ('name', 'category', 'enabled', 'location_from', 'location_to')
    fields = ('name', 'category', 'enabled', 'location_from', 'location_to')
    readonly_fields = ('category',)
    inlines = [
        TransferProviderInline]

reservas_admin.register(Transfer, ExtendedTransferAdmin)


class ExtendedTransferServiceProviderAdmin(ExtendedModelAdmin):
    actions_on_top = False
    search_fields = ('service', 'provider')
    list_display = ('service', 'provider', 'cost_type')
    list_filter = ('service', 'provider', 'cost_type')
    fields = ('service', 'provider', 'cost_type')
    inlines = [CostInline]

reservas_admin.register(TransferServiceProvider, ExtendedTransferServiceProviderAdmin)




class ExtendedPriceCatalogueAdmin(ExtendedModelAdmin):
    actions_on_top = False
    search_fields = ('name',)




