from django.contrib import admin, messages
from django.contrib.admin.options import csrf_protect_m
from django.core.exceptions import ValidationError
from django.db import router, transaction

from reservas.admin import reservas_admin, ExtendedModelAdmin

from finance.models import (
    Agency, Provider, FinantialDocument,
    Deposit, Withdraw, CurrencyExchange, Transfer)
from finance.services import FinanceService


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


admin.site.register(Deposit)

# ### Registering in custom adminSite reservas_admin ###

class ExtendedDepositAdmin(ExtendedModelAdmin):
    actions_on_top = False
    fields = ('name', 'account', 'amount', 'date', 'status')
    list_display = ('name', 'account', 'amount', 'date', 'status')
    list_filter = ('currency', 'account', 'status', 'date')
    search_fields = ('name',)
    ordering = ['-date', 'currency', 'status']
    readonly_fields = ('name',)

    def save_model(self, request, obj, form, change):
        # overrides base class method
        return FinanceService.save_deposit(request.user, obj)

class ExtendedWithdrawAdmin(ExtendedDepositAdmin):
    def save_model(self, request, obj, form, change):
        # overrides base class method
        return FinanceService.save_withdraw(request.user, obj)

class ExtendedCurrencyExchangeAdmin(ExtendedModelAdmin):
    list_display = ('account', 'amount', 'date', 'status')

    def save_model(self, request, obj, form, change):
        # overrides base class method
        return FinanceService.save_currency_exchange(request.user, obj)

class ExtendedTransferAdmin(ExtendedModelAdmin):
    list_display = ('account', 'amount', 'date', 'status')

    def save_model(self, request, obj, form, change):
        # overrides base class method
        return FinanceService.save_transfer(request.user, obj)

reservas_admin.register(FinantialDocument)
reservas_admin.register(Provider, ProviderAdmin)
reservas_admin.register(Agency, AgencyAdmin)
reservas_admin.register(Deposit, ExtendedDepositAdmin)
reservas_admin.register(Withdraw, ExtendedWithdrawAdmin)
reservas_admin.register(CurrencyExchange, ExtendedCurrencyExchangeAdmin)
reservas_admin.register(Transfer, ExtendedTransferAdmin)
