from django.contrib import admin

from accounting.models import Account


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_editable = ('enabled',)
    list_display = ('name', 'currency', 'enabled', 'balance')
    list_filter = ('name', 'currency', 'enabled', 'balance')
    search_fields = ('name',)
    ordering = ('enabled', 'currency', 'name')
    readonly_fields = ('balance',)

    def get_readonly_fields(self, request, obj=None):
        """
        Hook for specifying custom readonly fields.
        """
        if obj is None:
            return ('balance',)

        return ('currency', 'balance',)
