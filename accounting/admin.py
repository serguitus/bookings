from django.contrib import admin

from accounting.models import Account, OperationMovement

from reservas.admin import reservas_admin, ExtendedModelAdmin


class AccountMovementInline(admin.TabularInline):
    model = OperationMovement
    extra = 0
    can_delete = False

    readonly_fields = ['operation', 'movement_type', 'amount']

    def has_add_permission(self, request):
        return False
    # def has_change_permission(self, request, obj=None):
    #     return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    actions_on_top = True
    save_on_top = True
    list_editable = ('enabled',)
    list_display = ('name', 'currency', 'enabled', 'balance')
    list_filter = ('name', 'currency', 'enabled', 'balance')
    search_fields = ('name',)
    ordering = ['enabled', 'currency', 'name']
    inlines = [AccountMovementInline]

    def get_readonly_fields(self, request, obj=None):
        """
        Hook for specifying custom readonly fields.
        """
        if obj is None:
            return ('balance',)

        return ('currency', 'balance',)

class ExtendedAccountAdmin(ExtendedModelAdmin):
    actions_on_top = True
    save_on_top = True
    list_editable = ('enabled',)
    list_display = ('name', 'currency', 'enabled', 'balance')
    list_filter = ('name', 'currency', 'enabled', 'balance')
    search_fields = ('name',)
    ordering = ['enabled', 'currency', 'name']
    # inlines = [AccountMovementInline]
    readonly_fields = ('balance',)
    change_readonly_fields = ('currency',)

reservas_admin.register(Account, ExtendedAccountAdmin)
