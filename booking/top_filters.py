from __future__ import unicode_literals
from common import filters
from booking.constants import BOOKING_STATUS_CANCELLED
from datetime import date, timedelta
from django.db.models import F, Q


class SellerTopFilter(filters.ForeignKeyFilter):
    filter_title = 'Select Sellers'
    autocomplete_url = 'seller-autocomplete'


class CancelledTopFilter(filters.BooleanFilter):
    default_value = ["False"]
    filter_title = 'Cancelled'
    filter_field_path = 'cancelled'

    def queryset(self, request, queryset):
        search_option = self._values[0]
        if search_option == "True":
            queryset = queryset.filter(status__exact=BOOKING_STATUS_CANCELLED)
        if search_option == "False":
            queryset = queryset.exclude(status__exact=BOOKING_STATUS_CANCELLED)

        queryset = queryset.distinct()
        return queryset


class InternalReferenceTopFilter(filters.TextFilter):
    filter_title = 'TNX Ref.'

    def queryset(self, request, queryset):
        search_terms = self._values[0]
        if search_terms and search_terms != '':
            try:
                number = int(search_terms)
                if not self.field_path:
                    self.field_path = 'id'
                queryset = queryset.filter(**{self.field_path: number - 20000})
            except:
                queryset = queryset.none()
        return queryset


class PaidTopFilter(filters.BooleanFilter):
    filter_title = 'Paid'
    filter_field_path = 'paid'

    def queryset(self, request, queryset):
        search_option = self._values[0]
        if search_option == "True":
            queryset = queryset.exclude(cost_amount_to_pay=0)
            queryset = queryset.filter(cost_amount_to_pay=F('cost_amount_paid'))
        if search_option == "False":
            queryset = queryset.filter(
                Q(cost_amount_to_pay=0)
                |
                ~Q(cost_amount_to_pay=F('cost_amount_paid')))

        queryset = queryset.distinct()
        return queryset


class BookingPaidTopFilter(filters.BooleanFilter):
    filter_title = 'Charged'
    filter_field_path = 'charged'

    def queryset(self, request, queryset):
        search_option = self._values[0]
        if search_option == "True":
            queryset = queryset.exclude(status__exact=BOOKING_STATUS_CANCELLED)
            queryset = queryset.filter(
                invoice__isnull=False, invoice__amount=F('invoice__matched_amount'))
        if search_option == "False":
            queryset = queryset.exclude(status__exact=BOOKING_STATUS_CANCELLED)
            queryset = queryset.exclude(
                invoice__isnull=False, invoice__amount=F('invoice__matched_amount'))

        queryset = queryset.distinct()
        return queryset
