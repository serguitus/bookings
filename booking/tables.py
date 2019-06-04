import django_tables2 as tables

from django.urls import reverse
from django.contrib.admin.utils import quote
from django.utils.html import format_html
from booking.models import (
    PackageService,
    Quote, QuoteService, QuotePaxVariant, QuotePackageService,
    Booking, BookingService, BookingPax, BookingPackageService)
from booking.constants import (
    PACKAGESERVICE_TYPES, QUOTESERVICE_TYPES, QUOTEPACKAGESERVICE_TYPES,
    BOOKINGSERVICE_TYPES, BOOKINGPACKAGESERVICE_TYPES)


class PackageServiceTable(tables.Table):
    class Meta:
        model = PackageService
        template_name = 'booking/packageservice_list.html'
        fields = ['name', 'service_type', 'days_after', 'days_duration']

    def render_name(self, value, record):
        obj_url = reverse(
            'common:booking_%s_change' % (PACKAGESERVICE_TYPES[record.service_type]),
            args=(quote(record.pk),)
        )
        return format_html('<a href="%s">%s</a>' % (obj_url, value))

    def before_render(self, request):
        self.columns.hide('service_type')


class QuoteTable(tables.Table):
    class Meta:
        model = Quote
        template_name = 'django_tables2/bootstrap.html'
        fields = ['id', 'reference', 'agency', 'date_from', 'date_to', 'currency', 'status']

    def render_reference(self, value, record):
        return format_html(
            '<a href="#services-list-%s" data-toggle="collapse">%s</a>' % (record.id, value))

    def before_render(self, request):
        self.columns.hide('id')


class QuoteServiceTable(tables.Table):
    class Meta:
        model = QuoteService
        template_name = 'booking/quoteservice_list.html'
        fields = ['name', 'service_type', 'status', 'datetime_from', 'datetime_to']

    def render_name(self, value, record):
        obj_url = reverse(
            'common:booking_%s_change' % (QUOTESERVICE_TYPES[record.service_type]),
            args=(quote(record.pk),)
        )
        return format_html('<a href="%s">%s</a>' % (obj_url, value))

    def before_render(self, request):
        self.columns.hide('service_type')


class QuotePackageServiceTable(tables.Table):
    class Meta:
        model = QuotePackageService
        template_name = 'booking/quotepackageservice_list.html'
        fields = ['name', 'service_type', 'status', 'datetime_from', 'datetime_to']

    def render_name(self, value, record):
        obj_url = reverse(
            'common:booking_%s_change' % (QUOTEPACKAGESERVICE_TYPES[record.service_type]),
            args=(quote(record.pk),)
        )
        return format_html('<a href="%s">%s</a>' % (obj_url, value))

    def before_render(self, request):
        self.columns.hide('service_type')


class QuotePaxVariantTable(tables.Table):
    class Meta:
        model = QuotePaxVariant
        template_name = 'booking/quoteservice_list.html'
        fields = [
            'pax_quantity',
            'cost_single_amount', 'cost_double_amount', 'cost_triple_amount',
            'price_percent',
            'price_single_amount', 'price_double_amount', 'price_triple_amount']


class BookingTable(tables.Table):
    class Meta:
        model = Booking
        template_name = 'django_tables2/bootstrap.html'
        fields = ['id', 'reference', 'agency', 'date_from',
                  'date_to', 'cost_amount', 'price_amount']

    def render_reference(self, value, record):
        return format_html(
            '<a href="#services-list-%s" data-toggle="collapse">%s</a>' % (record.id, value))

    def before_render(self, request):
        self.columns.hide('id')


class BookingServiceTable(tables.Table):
    class Meta:
        model = BookingService
        template_name = 'booking/bookingservice_list.html'
        fields = ['name', 'service_location', 'datetime_from',
                  'datetime_to', 'description',
                  'cost_amount', 'price_amount',
                  'provider', 'service_type', 'status']

    def __init__(self, *args, **kwargs):
        # self.base_columns['service_type'].verbose_name='Request emails'
        super(BookingServiceTable, self).__init__(*args, **kwargs)

    def render_name(self, value, record):
        obj_url = reverse(
            'common:booking_%s_change' % (BOOKINGSERVICE_TYPES[record.service_type]),
            args=(quote(record.pk),)
        )
        return format_html('<a href="%s">%s</a>' % (obj_url, value))

    def render_service_type(self, value, record):
        email_url = reverse(
            'send_service_request',
            args=(record.pk,)
        )
        return format_html('<a class="btn btn-primary" href="%s">Request</a>' % (email_url))

    #    def before_render(self, request):
    #        self.columns.hide('service_type')


class BookingPaxTable(tables.Table):
    class Meta:
        model = BookingPax
        template_name = 'booking/bookingservice_list.html'
        fields = ['pax_name', 'pax_age']


class BookingVouchersTable(tables.Table):
    class Meta:
        model = BookingService
        template_name = 'booking/bookingservice_list.html'
        fields = ['pk', 'name', 'datetime_from', 'datetime_to',
                  'status', 'conf_number', 'provider']
    pk = tables.CheckBoxColumn(accessor='pk',
                               attrs={
                                   'th__input': {
                                       'id': 'action-toggle'},
                                   'td__input': {
                                       'class': 'action-select'},
                               })

    def __init__(self, *args, **kwargs):
        # self.base_columns['service_type'].verbose_name='Request emails'
        super(BookingVouchersTable, self).__init__(*args, **kwargs)

    def render_name(self, value, record):
        obj_url = reverse(
            'common:booking_%s_change' % (BOOKINGSERVICE_TYPES[record.service_type]),
            args=(quote(record.pk),)
        )
        return format_html('<a href="%s">%s</a>' % (obj_url, value))


class BookingPackageServiceTable(tables.Table):
    class Meta:
        model = BookingPackageService
        template_name = 'booking/bookingpackageservice_list.html'
        fields = ['name', 'service_type', 'datetime_from', 'datetime_to', 'cost_amount', 'price_amount', 'provider']

    def render_name(self, value, record):
        obj_url = reverse(
            'common:booking_%s_change' % (BOOKINGPACKAGESERVICE_TYPES[record.service_type]),
            args=(quote(record.pk),)
        )
        return format_html('<a href="%s">%s</a>' % (obj_url, value))

    def before_render(self, request):
        self.columns.hide('service_type')
