from __future__ import unicode_literals
from datetime import date, timedelta
from common import filters


class DateTopFilter(filters.DateFilter):
    default_value = [date.today() - timedelta(days=30), None]


class PackageTopFilter(filters.ForeignKeyFilter):
    filter_title = 'Select Packages'
    autocomplete_url = 'package-autocomplete'
