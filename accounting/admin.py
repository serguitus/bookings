from django.contrib import admin

from accounting.models import Account, Operation, OperationMovement

from reservas.admin import reservas_admin, ExtendedModelAdmin


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    actions_on_top = True
    save_on_top = True
    list_editable = ('enabled',)
    list_display = ('name', 'currency', 'enabled', 'balance')
    list_filter = ('name', 'currency', 'enabled', 'balance')
    search_fields = ('name',)
    ordering = ['enabled', 'currency', 'name']


class ExtendedAccountAdmin(ExtendedModelAdmin):
    actions_on_top = True
    list_editable = ('enabled',)
    list_display = ('name', 'currency', 'enabled', 'balance')
    list_filter = ('name', 'currency', 'enabled', 'balance')
    search_fields = ('name',)
    ordering = ['enabled', 'currency', 'name']
    # inlines = [AccountMovementInline]
    readonly_fields = ('balance',)
    change_readonly_fields = ('currency',)


class ExtendedOperationAdmin(ExtendedModelAdmin):
    readonly_model = True
    actions_on_top = False
    list_display = ('datetime', 'concept', 'detail',)
    list_filter = ('concept', 'datetime',)
    ordering = ['-datetime',]


class ExtendedOperationMovementAdmin(ExtendedModelAdmin):
    readonly_model = True
    actions_on_top = False
    list_display = ('operation', 'account', 'movement_type', 'amount',)
    list_filter = ('account', 'movement_type',)
    ordering = ['operation',]


reservas_admin.register(Account, ExtendedAccountAdmin)
reservas_admin.register(Operation, ExtendedOperationAdmin)
reservas_admin.register(OperationMovement, ExtendedOperationMovementAdmin)

