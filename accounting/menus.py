from django.contrib import admin

from common.sites import app_site
from reservas.admin import reservas_admin, ExtendedModelAdmin

from accounting.models import Account, OperationMovement


class AccountMovementMngInline(admin.TabularInline):
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


@admin.register(Account, site=app_site)
class AccountAdmin(admin.ModelAdmin):
    actions_on_top = True
    save_on_top = True
    list_editable = ('enabled',)
    list_display = ('name', 'currency', 'enabled', 'balance')
    list_filter = ('name', 'currency', 'enabled', 'balance')
    search_fields = ('name',)
    ordering = ('enabled', 'currency', 'name')
    inlines = [AccountMovementMngInline]

    def get_readonly_fields(self, request, obj=None):
        """
        Hook for specifying custom readonly fields.
        """
        if obj is None:
            return ('balance',)

        return ('currency', 'balance',)


# ### Registering in custom adminSite reservas_admin ###

class ExtendedAccountAdmin(ExtendedModelAdmin):
    site_actions = ['deposit']


reservas_admin.register(Account, ExtendedAccountAdmin)
