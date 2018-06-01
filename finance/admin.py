from django.contrib import admin
from reservas.admin import reservas_admin

from finance.models import (Agency, Provider, FinantialDocument,
                            Deposit)


@admin.register(Agency)
class AgencyAdmin(admin.ModelAdmin):
    list_display = ('name', 'currency', 'enabled')
    list_filter = ('name', 'currency', 'enabled')
    search_fields = ['name']
    ordering = ('enabled', 'currency', 'name')


@admin.register(Provider)
class ProviderAdmin(admin.ModelAdmin):
    list_display = ('name', 'currency', 'enabled')
    list_filter = ('name', 'currency', 'enabled')
    search_fields = ['name']
    ordering = ('enabled', 'currency', 'name')


admin.site.register(FinantialDocument)

# ### Registering in custom adminSite reservas_admin ###

reservas_admin.register(FinantialDocument)
reservas_admin.register(Provider, ProviderAdmin)
reservas_admin.register(Agency, AgencyAdmin)
reservas_admin.register(Deposit)
