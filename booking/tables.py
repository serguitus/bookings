import django_tables2 as tables

from django.urls import reverse
from django.contrib.admin.utils import quote
from django.utils.html import format_html
from booking.models import (
    PackageService,
    Quote, QuoteService, QuotePaxVariant, QuotePackageService,
    Booking, BookingService, BookingPax, BookingPackageService,
    ProviderBookingPayment, ProviderBookingPaymentService,
)
from booking.constants import (
    PACKAGESERVICE_TYPES, QUOTESERVICE_TYPES, QUOTEPACKAGESERVICE_TYPES,
    BOOKINGSERVICE_TYPES, BOOKINGPACKAGESERVICE_TYPES, BOOTSTRAP_STYLE_STATUS_MAPPING)

from finance.models import (
    AgencyPayment,
)

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
            'price_single_amount', 'utility_percent_single', 'utility_single',
            'price_double_amount', 'utility_percent_double', 'utility_double',
            'price_triple_amount', 'utility_percent_triple', 'utility_triple']

    def __init__(self, *args, **kwargs):
        self.base_columns['utility_percent_single'].verbose_name='Util.SGL %'
        self.base_columns['utility_single'].verbose_name='Util.SGL'
        self.base_columns['utility_percent_double'].verbose_name='Util.DBL %'
        self.base_columns['utility_double'].verbose_name='Util.DBL'
        self.base_columns['utility_percent_triple'].verbose_name='Util.TPL %'
        self.base_columns['utility_triple'].verbose_name='Util.TPL'
        super(QuotePaxVariantTable, self).__init__(*args, **kwargs)


class BookingTable(tables.Table):
    class Meta:
        model = Booking
        template_name = 'django_tables2/bootstrap.html'
        fields = ['id', 'reference', 'agency', 'date_from',
                  'date_to', 'cost_amount', 'price_amount', 'utility_percent', 'utility']

    def __init__(self, *args, **kwargs):
        self.base_columns['utility_percent'].verbose_name='Util.%'
        self.base_columns['utility'].verbose_name='Util.'
        super(BookingTable, self).__init__(*args, **kwargs)

    def render_reference(self, value, record):
        return format_html(
            '<a href="#services-list-%s" data-toggle="collapse">%s</a>' % (record.id, value))

    def before_render(self, request):
        self.columns.hide('id')


class BookingServiceTable(tables.Table):
    check = tables.CheckBoxColumn(
                               attrs={
                                   'th__input': {
                                       'id': 'action-toggle'},
                                   'td__input': {
                                       'class': 'action-select'},
                               })

    class Meta:
        model = BookingService
        template_name = 'booking/bookingservice_list.html'
        fields = ['check', 'name', 'service_location', 'datetime_from',
                  'datetime_to', 'nights', 'description',
                  'cost_amount', 'price_amount',
                  'provider', 'conf_number', 'status', 'cost_amount_paid', 'time']
        attrs = {'class': 'table table-hover table-condensed'}
        row_attrs = {
            'class': lambda record: '{}'.format(BOOTSTRAP_STYLE_STATUS_MAPPING[record.status]),
        }

    def __init__(self, *args, **kwargs):
        # self.base_columns['service_type'].verbose_name='Request emails'
        # self.base_columns['utility_percent'].verbose_name='Util.%'
        # self.base_columns['utility'].verbose_name='Util.'
        self.base_columns['nights'].verbose_name='N'
        self.base_columns['datetime_from'].verbose_name='FROM'
        self.base_columns['datetime_to'].verbose_name='TO'
        self.base_columns['description'].verbose_name='Pax'
        self.base_columns['cost_amount'].verbose_name='Cost'
        self.base_columns['price_amount'].verbose_name='Price'
        self.base_columns['conf_number'].verbose_name='Conf.'
        self.base_columns['time'].visible = False
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


class AgencyPaymentTable(tables.Table):
    class Meta:
        model = AgencyPayment
        template_name = 'booking/agencypayment_table.html'
        fields = ['name', 'date', 'status', 'account', 'amount', 'details']
        attrs = {'class': 'table table-hover table-condensed'}

    def __init__(self, *args, **kwargs):
        self.base_columns['name'].verbose_name='Payment'
        super(AgencyPaymentTable, self).__init__(*args, **kwargs)

    def render_name(self, value, record):
        obj_url = reverse(
            'common:finance_agencypayment_change',
            args=(quote(record.pk),)
        )
        return format_html('<a href="%s">%s</a>' % (obj_url, value))


class ProviderBookingPaymentTable(tables.Table):
    class Meta:
        model = ProviderBookingPayment
        template_name = 'booking/providerbookingpayment_table.html'
        fields = ['name', 'date', 'status', 'account', 'services_amount',
                'currency_rate', 'amount', 'details']
        attrs = {'class': 'table table-hover table-condensed'}

    def __init__(self, *args, **kwargs):
        self.base_columns['services_amount'].verbose_name='Serv.Amount'
        self.base_columns['currency_rate'].verbose_name='Rate'
        super(ProviderBookingPaymentTable, self).__init__(*args, **kwargs)

    def render_name(self, value, record):
        obj_url = reverse(
            'common:booking_providerbookingpayment_change',
            args=(quote(record.pk),)
        )
        return format_html('<a href="%s">%s</a>' % (obj_url, value))


class ProviderBookingPaymentServiceTable(tables.Table):
    class Meta:
        model = ProviderBookingPaymentService
        template_name = 'booking/providerbookingpaymentservice_table.html'
        fields = ['provider_service_booking', 'provider_service_name',
            'provider_service_datetime_from', 'provider_service_datetime_to',
            'provider_service_status', 'service_cost_amount_to_pay', 'service_cost_amount_paid',
            'amount_paid']
        attrs = {'class': 'table table-hover table-condensed'}

    def __init__(self, *args, **kwargs):
        self.base_columns['service_cost_amount_to_pay'].verbose_name='Serv.To Pay'
        self.base_columns['service_cost_amount_paid'].verbose_name='Serv.Paid'
        self.base_columns['amount_paid'].verbose_name='Paid'
        super(ProviderBookingPaymentServiceTable, self).__init__(*args, **kwargs)

    def render_name(self, value, record):
        obj_url = reverse(
            'common:booking_providerbookingpayment_change',
            args=(quote(record.pk),)
        )
        return format_html('<a href="%s">%s</a>' % (obj_url, value))


class BookingConfirmationTable(tables.Table):
    class Meta:
        model = BookingService
        template_name = 'booking/bookingservice_list.html'
        fields = ['name', 'service_location', 'datetime_from',
                  'datetime_to', 'nights', 'description',
                  'conf_number', 'status']
        attrs = {'class': 'table',
                 'style': 'width:100%',
                 'border': '1',}
        row_attrs = {
            'class': lambda record: '{}'.format(BOOTSTRAP_STYLE_STATUS_MAPPING[record.status]),
        }

    def __init__(self, *args, **kwargs):
        # self.base_columns['service_type'].verbose_name='Request emails'
        # self.base_columns['utility_percent'].verbose_name='Util.%'
        # self.base_columns['utility'].verbose_name='Util.'
        self.base_columns['nights'].verbose_name='N'
        self.base_columns['datetime_from'].verbose_name='FROM'
        self.base_columns['datetime_to'].verbose_name='TO'
        self.base_columns['description'].verbose_name='Pax'
        self.base_columns['conf_number'].verbose_name='Conf.'
        super(BookingConfirmationTable, self).__init__(*args, **kwargs)


class QuoteConfirmationTable(tables.Table):
    class Meta:
        model = QuoteService
        template_name = 'booking/bookingservice_list.html'
        fields = ['name', 'datetime_from',
                  'datetime_to']  # 'description',
        #  'conf_number', 'status']
        attrs = {'class': 'table',
                 'style': 'width:100%',
                 'border': '1'}
        row_attrs = {
            'class': lambda record: '{}'.format(
                BOOTSTRAP_STYLE_STATUS_MAPPING[record.status]),
        }

    def __init__(self, *args, **kwargs):
        # self.base_columns['service_type'].verbose_name='Request emails'
        # self.base_columns['utility_percent'].verbose_name='Util.%'
        # self.base_columns['utility'].verbose_name='Util.'
        # self.base_columns['nights'].verbose_name='N'
        self.base_columns['datetime_from'].verbose_name='FROM'
        self.base_columns['datetime_to'].verbose_name='TO'
        #self.base_columns['description'].verbose_name='Pax'
        #self.base_columns['conf_number'].verbose_name='Conf.'
        super(QuoteConfirmationTable, self).__init__(*args, **kwargs)


class BookingServiceSummaryTable(tables.Table):
    class Meta:
        model = BookingService
        template_name = 'booking/include/base_table.html'
        fields = ['name', 'datetime_from', 'datetime_to', 'provider', 'status']
        attrs = {'class': 'table table-hover table-condensed'}
        row_attrs = {
            'class': lambda record: '{}'.format(BOOTSTRAP_STYLE_STATUS_MAPPING[record.status]),
        }


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
        fields = [
            'name', 'datetime_from', 'datetime_to',
            'cost_amount', 'price_amount', 'utility_percent', 'utility',
            'provider', 'status', 'cost_amount_paid']

    def __init__(self, *args, **kwargs):
        self.base_columns['utility_percent'].verbose_name='Util.%'
        self.base_columns['utility'].verbose_name='Util.'
        super(BookingPackageServiceTable, self).__init__(*args, **kwargs)

    def render_name(self, value, record):
        obj_url = reverse(
            'common:booking_%s_change' % (BOOKINGPACKAGESERVICE_TYPES[record.service_type]),
            args=(quote(record.pk),)
        )
        return format_html('<a href="%s">%s</a>' % (obj_url, value))


class BookingPackageServiceSummaryTable(tables.Table):
    class Meta:
        model = BookingPackageService
        template_name = 'booking/include/base_table.html'
        fields = [
            'name', 'datetime_from', 'datetime_to', 'provider', 'status']
        attrs = {'class': 'table table-hover table-condensed'}
        row_attrs = {
            'class': lambda record: '{}'.format(BOOTSTRAP_STYLE_STATUS_MAPPING[record.status]),
        }


class BookingServiceUpdateTable(tables.Table):
    class Meta:
        model = BookingService
        # fields update_cost_amount and update_price_amount are lazy
        # they contain computed values that will be saved upon save action
        template_name = 'booking/bookingservice_list.html'
        fields = ['pk', 'name', 'datetime_from', 'datetime_to',
                  'cost_amount', 'update_cost_amount',
                  'price_amount', 'update_price_amount',
                  'status', 'conf_number', 'provider']
    pk = tables.CheckBoxColumn(accessor='pk',
                               attrs={
                                   'th__input': {
                                       'id': 'action-toggle'},
                                   'td__input': {
                                       'class': 'action-select'},
                               })

    def __init__(self, *args, **kwargs):
        self.base_columns['update_cost_amount'].verbose_name = 'New Cost'
        self.base_columns['update_price_amount'].verbose_name = 'New Price'
        self.base_columns['cost_amount'].verbose_name = 'Saved Cost'
        self.base_columns['price_amount'].verbose_name = 'Saved Price'
        self.base_columns['datetime_from'].verbose_name = 'From'
        self.base_columns['datetime_to'].verbose_name = 'To'
        super(BookingServiceUpdateTable, self).__init__(*args, **kwargs)

    def render_name(self, value, record):
        obj_url = reverse(
            'common:booking_%s_change' % (BOOKINGSERVICE_TYPES[record.service_type]),
            args=(quote(record.pk),)
        )
        return format_html('<a href="%s">%s</a>' % (obj_url, value))


class AddPaxBookingServicesTable(tables.Table):
    class Meta:
        model = BookingService
        # fields update_cost_amount and update_price_amount are lazy
        # they contain computed values that will be saved upon save action
        template_name = 'booking/add_pax_bookingservices.html'
        fields = ['pk', 'name', 'datetime_from', 'datetime_to',
                  'cost_amount', 'price_amount', 'status', 'conf_number', 'provider']
    pk = tables.CheckBoxColumn(accessor='pk',
                               attrs={
                                   'th__input': {
                                       'id': 'action-toggle'},
                                   'td__input': {
                                       'class': 'action-select'},
                               })

    def __init__(self, *args, **kwargs):
        self.base_columns['cost_amount'].verbose_name = 'Cost'
        self.base_columns['price_amount'].verbose_name = 'Price'
        self.base_columns['datetime_from'].verbose_name = 'From'
        self.base_columns['datetime_to'].verbose_name = 'To'
        super(AddPaxBookingServicesTable, self).__init__(*args, **kwargs)

    def render_name(self, value, record):
        obj_url = reverse(
            'common:booking_%s_change' % (BOOKINGSERVICE_TYPES[record.service_type]),
            args=(quote(record.pk),)
        )
        return format_html('<a href="%s">%s</a>' % (obj_url, value))
