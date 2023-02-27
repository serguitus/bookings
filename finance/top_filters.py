# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db.models import Q

from common import filters

from finance.models import LoanEntity


class LoanEntityTopFilter(filters.ForeignKeyFilter):
    filter_title = 'Select Loan Entities'
    autocomplete_url = 'loanentity-autocomplete'


class LoanAccountTopFilter(filters.ForeignKeyFilter):
    filter_title = 'Select Loan Accounts'
    autocomplete_url = 'loanaccount-autocomplete'


class ProviderTopFilter(filters.ForeignKeyFilter):
    filter_title = 'Select Providers'
    autocomplete_url = 'provider-autocomplete'


class AgencyTopFilter(filters.ForeignKeyFilter):
    filter_title = 'Select Agencies'
    autocomplete_url = 'agency-autocomplete'


class EnabledTopFilter(filters.BooleanFilter):
    default_value = ["True"]
    filter_title = 'Enabled'
    filter_field_path = 'enabled'

    def queryset(self, request, queryset):
        search_option = self._values[0]
        if search_option == "True":
            # queryset = queryset.filter(status__exact=BOOKING_STATUS_CANCELLED)
            queryset = queryset.filter(enabled=True)
        if search_option == "False":
            # queryset = queryset.filter(status__exact=BOOKING_STATUS_CANCELLED)
            queryset = queryset.filter(enabled=False)

        queryset = queryset.distinct()
        return queryset
