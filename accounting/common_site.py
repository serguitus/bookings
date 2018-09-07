"""
accounting site models
"""
from accounting.models import Account, Operation, OperationMovement

from common.sites import SiteModel

from reservas.admin import bookings_site


MENU_LABEL_ACCOUNTING = 'Accounting'


class AccountSiteModel(SiteModel):
    model_order = 5010
    menu_label = MENU_LABEL_ACCOUNTING
    actions_on_top = True
    list_editable = ('enabled',)
    list_display = ('name', 'currency', 'enabled', 'balance')
    list_filter = ('name', 'currency', 'enabled', 'balance')
    search_fields = ('name',)
    ordering = ['enabled', 'currency', 'name']
    # inlines = [AccountMovementInline]
    readonly_fields = ('balance',)
    change_readonly_fields = ('currency',)


class OperationSiteModel(SiteModel):
    model_order = 5020
    menu_label = MENU_LABEL_ACCOUNTING
    readonly_model = True
    actions_on_top = False
    list_display = ('datetime', 'concept', 'detail',)
    list_filter = ('concept', 'datetime',)
    ordering = ['-datetime',]
    search_fields = ['concept', 'detail']


class OperationMovementSiteModel(SiteModel):
    model_order = 5030
    menu_label = MENU_LABEL_ACCOUNTING
    readonly_model = True
    actions_on_top = False
    list_display = ('operation', 'account', 'movement_type', 'amount',)
    list_filter = ('account', 'movement_type',)
    ordering = ['operation',]
    search_fields = ['account', 'amount']


bookings_site.register(Account, AccountSiteModel)
bookings_site.register(Operation, OperationSiteModel)
bookings_site.register(OperationMovement, OperationMovementSiteModel)
