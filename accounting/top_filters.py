from django.db.models import Q

from common import filters

from accounting.models import Account


class AccountTopFilter(filters.ForeignKeyFilter):
    filter_title = 'Select Accounts'
    autocomplete_url = 'account-autocomplete'

class AmountTopFilter(filters.TextFilter):
    filter_title = 'Amount'
