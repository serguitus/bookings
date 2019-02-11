from datetime import date, timedelta
from common import filters

class DateTopFilter(filters.DateFilter):
    default_value = [date.today() - timedelta(days=30), None]
