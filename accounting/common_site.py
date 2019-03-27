"""
accounting site models
"""
from accounting.models import Account, Operation, OperationMovement
from accounting.top_filters import AccountTopFilter

from common.sites import SiteModel

from reservas.admin import bookings_site


MENU_LABEL_ACCOUNTING = 'Accounting'
MENU_GROUP_LABEL_ACCOUNTING = 'Accounts'


class AccountSiteModel(SiteModel):
    model_order = 5010
    menu_label = MENU_LABEL_ACCOUNTING
    menu_group = MENU_GROUP_LABEL_ACCOUNTING
    actions_on_top = True
    list_editable = ('enabled',)
    list_display = ('name', 'currency', 'enabled', 'balance')
    top_filters = ('name', 'currency', 'enabled', 'balance')
    ordering = ['enabled', 'currency', 'name']
    # inlines = [AccountMovementInline]
    readonly_fields = ('balance',)
    change_readonly_fields = ('currency',)
    totalsum_list = ['balance']


class OperationSiteModel(SiteModel):
    model_order = 5020
    menu_label = MENU_LABEL_ACCOUNTING
    menu_group = MENU_GROUP_LABEL_ACCOUNTING
    readonly_model = True
    actions_on_top = False
    list_display = ('datetime', 'concept', 'detail',)
    top_filters = ('concept', 'detail', 'datetime',)
    ordering = ['-datetime',]


class OperationMovementSiteModel(SiteModel):
    model_order = 5030
    menu_label = MENU_LABEL_ACCOUNTING
    menu_group = MENU_GROUP_LABEL_ACCOUNTING
    readonly_model = True
    actions_on_top = False
    list_display = ('operation', 'account', 'movement_type', 'amount',)
    top_filters = (('account', AccountTopFilter), 'movement_type', 'amount',)
    ordering = ['operation',]


bookings_site.register(Account, AccountSiteModel)
bookings_site.register(Operation, OperationSiteModel)
bookings_site.register(OperationMovement, OperationMovementSiteModel)
