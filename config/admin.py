"""
Config admin
"""
from config.models import (
    Service, Location, ServiceProvider,
    Extra, ExtraServiceProvider,
    Allotment, AllotmentRoomType, AllotmentBoardType, AllotmentServiceProvider,
    Transfer, TransferServiceProvider,
    PriceCatalogue)

from django.contrib import admin

from reservas.admin import reservas_admin, SelfTabularInline, ExtendedModelAdmin


class ExtendedLocationAdmin(ExtendedModelAdmin):
    actions_on_top = False
    search_fields = ('name',)


class ExtendedExtraAdmin(ExtendedModelAdmin):
    actions_on_top = False
    search_fields = ('name',)


class AllotmentRoomTypeInline(admin.TabularInline):
    model = AllotmentRoomType
    extra = 0


class AllotmentBoardTypeInline(admin.TabularInline):
    model = AllotmentBoardType
    extra = 0


class AllotmentProviderInline(admin.TabularInline):
    model = ServiceProvider
    extra = 0


class ExtendedServiceAdmin(ExtendedModelAdmin):
    readonly_model = True
    actions_on_top = False
    search_fields = ('name',)
    list_display = ('name', 'category', 'enabled')
    fields = ('name', 'category', 'enabled')


class ExtendedAllotmentAdmin(ExtendedModelAdmin):
    actions_on_top = False
    search_fields = ('name',)
    list_display = ('name', 'category', 'enabled', 'location', 'time_from', 'time_to')
    fields = ('name', 'category', 'enabled', 'location', 'time_from', 'time_to')
    readonly_fields = ('category',)
    inlines = [
        AllotmentRoomTypeInline, AllotmentBoardTypeInline, AllotmentProviderInline]


class ExtendedAllotmentRoomTypeAdmin(ExtendedModelAdmin):
    actions_on_top = False
    search_fields = ('name',)


class ExtendedAllotmentBoardTypeAdmin(ExtendedModelAdmin):
    actions_on_top = False
    search_fields = ('name',)


class ExtendedTransferAdmin(ExtendedModelAdmin):
    actions_on_top = False
    search_fields = ('name',)


class ExtendedPriceCatalogueAdmin(ExtendedModelAdmin):
    actions_on_top = False
    search_fields = ('name',)


class ExtendedServiceProviderAdmin(ExtendedModelAdmin):
    readonly_model = True
    actions_on_top = False
    search_fields = ('name',)


class ExtendedExtraServiceProviderAdmin(ExtendedModelAdmin):
    actions_on_top = False
    search_fields = ('name',)


class ExtendedAllotmentServiceProviderAdmin(ExtendedModelAdmin):
    actions_on_top = False
    search_fields = ('name',)


class ExtendedTransferServiceProviderAdmin(ExtendedModelAdmin):
    actions_on_top = False
    search_fields = ('name',)



reservas_admin.register(Service, ExtendedServiceAdmin)
reservas_admin.register(Location, ExtendedLocationAdmin)
reservas_admin.register(Extra, ExtendedExtraAdmin)
reservas_admin.register(Allotment, ExtendedAllotmentAdmin)
reservas_admin.register(Transfer, ExtendedTransferAdmin)

reservas_admin.register(ExtraServiceProvider, ExtendedExtraServiceProviderAdmin)
reservas_admin.register(AllotmentServiceProvider, ExtendedAllotmentServiceProviderAdmin)
reservas_admin.register(TransferServiceProvider, ExtendedTransferServiceProviderAdmin)
