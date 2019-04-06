from __future__ import unicode_literals
from datetime import date, timedelta
from common import filters
from booking.constants import BOOKING_STATUS_CANCELLED

class DateTopFilter(filters.DateFilter):
    default_value = [date.today() - timedelta(days=30), None]


class PackageTopFilter(filters.ForeignKeyFilter):
    filter_title = 'Select Packages'
    autocomplete_url = 'package-autocomplete'

class CancelledTopFilter(filters.BooleanFilter):
    default_value = ["False"]
    filter_title = 'Cancelled'

    def queryset(self, request, queryset):
        search_option = self._values[0]
        if search_option == "True":
            queryset = queryset.filter(status__exact=BOOKING_STATUS_CANCELLED)
        if search_option == "False":
            queryset = queryset.exclude(status__exact=BOOKING_STATUS_CANCELLED)

        queryset = queryset.distinct()
        return queryset
