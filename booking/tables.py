import django_tables2 as tables

from django.contrib.admin.utils import quote
from django.urls import reverse
from django.utils import formats
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from booking.models import (
    Quote, QuoteService, QuotePaxVariant, QuoteProvidedService,
    NewQuoteServiceBookDetail,
    Booking, BaseBookingService, BookingPax, BookingProvidedService,
    BookingBookDetail,
    ProviderBookingPayment, ProviderPaymentBookingProvided,
)
from booking.constants import (
    QUOTESERVICE_TYPES,
    BOOKINGSERVICE_TYPES,
    BOOTSTRAP_STYLE_QUOTE_STATUS_MAPPING, BOOTSTRAP_STYLE_BOOKING_SERVICE_STATUS_MAPPING,
    QUOTE_BOOK_DETAIL_CATEGORIES)

from finance.models import (
    AgencyPayment,
)


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
        template_name = 'booking/table/quoteservice_table.html'
        fields = ['name', 'base_category', 'status', 'datetime_from', 'datetime_to']

    def render_name(self, value, record):
        obj_url = reverse(
            'common:booking_%s_change' % (QUOTESERVICE_TYPES[record.base_category]),
            args=(quote(record.pk),)
        )
        return format_html('<a href="%s">%s</a>' % (obj_url, value))

    def before_render(self, request):
        self.columns.hide('base_category')


class QuotePaxVariantTable(tables.Table):
    class Meta:
        model = QuotePaxVariant
        template_name = 'booking/table/details_table.html'
        fields = [
            'pax_quantity',
            'cost_single_amount', 'cost_double_amount', 'cost_triple_amount', 'cost_qdrple_amount',
            'price_percent',
            'price_single_amount', 'utility_percent_single', 'utility_single',
            'price_double_amount', 'utility_percent_double', 'utility_double',
            'price_triple_amount', 'utility_percent_triple', 'utility_triple',
            'price_qdrple_amount', 'utility_percent_qdrple', 'utility_qdrple',
        ]

    def __init__(self, *args, **kwargs):
        self.base_columns['utility_percent_single'].verbose_name = 'Util.SGL %'
        self.base_columns['utility_single'].verbose_name = 'Util.SGL'
        self.base_columns['utility_percent_double'].verbose_name = 'Util.DBL %'
        self.base_columns['utility_double'].verbose_name = 'Util.DBL'
        self.base_columns['utility_percent_triple'].verbose_name = 'Util.TPL %'
        self.base_columns['utility_triple'].verbose_name = 'Util.TPL'
        self.base_columns['utility_percent_qdrple'].verbose_name = 'Util.QPL %'
        self.base_columns['utility_qdrple'].verbose_name = 'Util.QPL'
        super(QuotePaxVariantTable, self).__init__(*args, **kwargs)


class QuoteExtraPackageServiceTable(tables.Table):
    class Meta:
        model = QuoteProvidedService
        template_name = 'booking/quotepackageservice_list.html'
        fields = ['name', 'base_category', 'status', 'datetime_from', 'datetime_to']

    def render_name(self, value, record):
        obj_url = reverse(
            'common:booking_%s_change' % (QUOTESERVICE_TYPES[record.base_category]),
            args=(quote(record.pk),)
        )
        return format_html('<a href="%s">%s</a>' % (obj_url, value))

    def before_render(self, request):
        self.columns.hide('base_category')


class BookingTable(tables.Table):
    class Meta:
        model = Booking
        template_name = 'django_tables2/bootstrap.html'
        fields = ['id', 'reference', 'agency', 'date_from',
                  'date_to', 'cost_amount', 'price_amount', 'utility_percent', 'utility']

    def __init__(self, *args, **kwargs):
        self.base_columns['utility_percent'].verbose_name = 'Util.%'
        self.base_columns['utility'].verbose_name = 'Util.'
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
        model = BaseBookingService
        template_name = 'booking/bookingservice_list.html'
        fields = ['check', 'name', 'service_location', 'datetime_from',
                  'datetime_to', 'nights', 'description',
                  'cost_amount', 'price_amount',
                  'provider', 'conf_number', 'status', 'cost_amount_paid', 'time']
        attrs = {'class': 'table table-hover table-sm'}
        row_attrs = {
            'class': lambda record: '{}'.format(BOOTSTRAP_STYLE_BOOKING_SERVICE_STATUS_MAPPING[record.status]),
        }

    def __init__(self, *args, **kwargs):
        # self.base_columns['utility_percent'].verbose_name='Util.%'
        # self.base_columns['utility'].verbose_name='Util.'
        self.base_columns['nights'].verbose_name = 'N'
        self.base_columns['datetime_from'].verbose_name = 'FROM'
        self.base_columns['datetime_to'].verbose_name = 'TO'
        self.base_columns['description'].verbose_name = 'Pax'
        self.base_columns['cost_amount'].verbose_name = 'Cost'
        self.base_columns['price_amount'].verbose_name = 'Price'
        self.base_columns['conf_number'].verbose_name = 'Conf.'
        self.base_columns['time'].visible = False
        super(BookingServiceTable, self).__init__(*args, **kwargs)

    def render_name(self, value, record):
        obj_url = reverse(
            'common:booking_%s_change' % (BOOKINGSERVICE_TYPES[record.base_category]),
            args=(quote(record.pk),)
        )
        return format_html('<a href="%s">%s</a>' % (obj_url, value))

    def render_base_category(self, value, record):
        email_url = reverse(
            'send_service_request',
            args=(record.pk,)
        )
        return format_html('<a class="btn btn-primary" href="%s">Request</a>' % (email_url))


class AgencyPaymentTable(tables.Table):
    class Meta:
        model = AgencyPayment
        template_name = 'booking/table/agencypayment_table.html'
        fields = ['name', 'date', 'status', 'account', 'amount', 'details']
        attrs = {'class': 'table table-hover table-sm'}

    def __init__(self, *args, **kwargs):
        self.base_columns['name'].verbose_name = 'Payment'
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
        template_name = 'booking/table/providerbookingpayment_table.html'
        fields = ['name', 'date', 'status', 'account', 'services_amount',
                'currency_rate', 'amount', 'details']
        attrs = {'class': 'table table-hover table-sm'}

    def __init__(self, *args, **kwargs):
        self.base_columns['services_amount'].verbose_name = 'Serv.Amount'
        self.base_columns['currency_rate'].verbose_name = 'Rate'
        super(ProviderBookingPaymentTable, self).__init__(*args, **kwargs)

    def render_name(self, value, record):
        obj_url = reverse(
            'common:booking_providerbookingpayment_change',
            args=(quote(record.pk),)
        )
        return format_html('<a href="%s">%s</a>' % (obj_url, value))


class ProviderPaymentBookingProvidedTable(tables.Table):
    class Meta:
        model = ProviderPaymentBookingProvided
        template_name = 'booking/table/providerpaymentbookingprovided_table.html'
        fields = [
            'provider_service_booking', 'provider_service_name',
            'provider_service_datetime_from', 'provider_service_datetime_to',
            'provider_service_status', 'service_cost_amount_to_pay', 'service_cost_amount_paid',
            'amount_paid']
        attrs = {'class': 'table table-hover table-sm'}

    def __init__(self, *args, **kwargs):
        self.base_columns['service_cost_amount_to_pay'].verbose_name = 'Serv.To Pay'
        self.base_columns['service_cost_amount_paid'].verbose_name = 'Serv.Paid'
        self.base_columns['amount_paid'].verbose_name = 'Paid'
        super(ProviderPaymentBookingProvidedTable, self).__init__(*args, **kwargs)

    def render_name(self, value, record):
        obj_url = reverse(
            'common:booking_providerbookingpayment_change',
            args=(quote(record.pk),)
        )
        return format_html('<a href="%s">%s</a>' % (obj_url, value))


class ProviderBookingPaymentReportTable(tables.Table):
    class Meta:
        model = ProviderPaymentBookingProvided
        template_name = 'booking/table/providerpaymentbookingprovided_table.html'
        fields = ['provider_service_booking',
                  'provider_service_name',
                  'provider_service_ref', 'service_cost_amount_to_pay',
                  'provider_service_datetime_from',
                  'provider_service_datetime_to',
                  'service_cost_amount_pending',
                  'amount_paid', 'provider_service_balance']
        attrs = {'class': 'table table-hover table-sm'}
        order_by = ('datetime_from', 'datetime_to')

    def __init__(self, *args, **kwargs):
        self.base_columns['provider_service_booking'].verbose_name = 'Booking'
        self.base_columns['provider_service_name'].verbose_name = 'Service'
        self.base_columns['provider_service_ref'].verbose_name = 'Reference'
        self.base_columns['provider_service_datetime_from'].verbose_name = 'From'
        self.base_columns['provider_service_datetime_to'].verbose_name = 'To'
        self.base_columns['service_cost_amount_to_pay'].verbose_name = 'Total'
        self.base_columns['service_cost_amount_pending'].verbose_name = 'Pending'
        self.base_columns['amount_paid'].verbose_name = 'Paid'
        self.base_columns['provider_service_balance'].verbose_name = 'Balance'
        super(ProviderBookingPaymentReportTable, self).__init__(
            *args, **kwargs)

    def render_provider_service_datetime_from(self, value, record):
        if value:
            return formats.date_format(value, 'd-b-Y')

    def render_provider_service_datetime_to(self, value, record):
        if value:
            return formats.date_format(value, 'd-b-Y')


class BookingConfirmationTable(tables.Table):
    class Meta:
        model = BaseBookingService
        template_name = 'booking/bookingservice_list.html'
        fields = ['name', 'service_location', 'datetime_from',
                  'datetime_to', 'nights', 'description',
                  'conf_number', 'price_amount']
        attrs = {'class': 'table',
                 'style': 'width:100%',
                 'border': '1',}
        row_attrs = {
            'class': lambda record: '{}'.format(BOOTSTRAP_STYLE_BOOKING_SERVICE_STATUS_MAPPING[record.status]),
        }

    def __init__(self, *args, **kwargs):
        # self.base_columns['utility_percent'].verbose_name='Util.%'
        # self.base_columns['utility'].verbose_name='Util.'
        self.base_columns['nights'].verbose_name = 'N'
        self.base_columns['datetime_from'].verbose_name = 'FROM'
        self.base_columns['datetime_to'].verbose_name = 'TO'
        self.base_columns['description'].verbose_name = 'Pax'
        self.base_columns['conf_number'].verbose_name = 'Conf.'
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
                BOOTSTRAP_STYLE_QUOTE_STATUS_MAPPING[record.status]),
        }

    def __init__(self, *args, **kwargs):
        # self.base_columns['utility_percent'].verbose_name='Util.%'
        # self.base_columns['utility'].verbose_name='Util.'
        self.base_columns['name'].verbose_name='Service'
        self.base_columns['datetime_from'].verbose_name = 'FROM'
        self.base_columns['datetime_to'].verbose_name = 'TO'
        #self.base_columns['description'].verbose_name='Pax'
        #self.base_columns['conf_number'].verbose_name='Conf.'
        super(QuoteConfirmationTable, self).__init__(*args, **kwargs)

    def render_name(self, value, record):
        details = ''
        if record.description:
            details = ': {}'.format(record.description)
        return '{}{}'.format(value, details)


class BookingServiceSummaryTable(tables.Table):
    class Meta:
        model = BaseBookingService
        template_name = 'booking/include/base_table.html'
        fields = ['name', 'datetime_from', 'datetime_to', 'provider', 'status']
        attrs = {'class': 'table table-hover table-sm'}
        row_attrs = {
            'class': lambda record: '{}'.format(BOOTSTRAP_STYLE_BOOKING_SERVICE_STATUS_MAPPING[record.status]),
        }


class BookingPaxTable(tables.Table):
    class Meta:
        model = BookingPax
        template_name = 'booking/bookingservice_list.html'
        fields = ['pax_name', 'pax_age']


class BookingVouchersTable(tables.Table):
    class Meta:
        model = BaseBookingService
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
        super(BookingVouchersTable, self).__init__(*args, **kwargs)

    def render_name(self, value, record):
        obj_url = reverse(
            'common:booking_%s_change' % (BOOKINGSERVICE_TYPES[record.base_category]),
            args=(quote(record.pk),)
        )
        return format_html('<a href="%s">%s</a>' % (obj_url, value))


class BookingExtraPackageServiceSummaryTable(tables.Table):
    class Meta:
        model = BookingProvidedService
        template_name = 'booking/include/base_table.html'
        fields = [
            'name', 'datetime_from', 'datetime_to', 'provider', 'cost_amount', 'price_amount', 'status']
        attrs = {'class': 'table table-hover table-sm'}
        row_attrs = {
            'class': lambda record: '{}'.format(BOOTSTRAP_STYLE_BOOKING_SERVICE_STATUS_MAPPING[record.status]),
        }

    def render_name(self, value, record):
        obj_url = reverse(
            'common:booking_%s_change' % (BOOKINGSERVICE_TYPES[record.base_category]),
            args=(quote(record.pk),)
        )
        return format_html('<a href="%s">%s</a>' % (obj_url, value))


class BookingServiceUpdateTable(tables.Table):
    class Meta:
        model = BaseBookingService
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
            'common:booking_%s_change' % (BOOKINGSERVICE_TYPES[record.base_category]),
            args=(quote(record.pk),)
        )
        return format_html('<a href="%s">%s</a>' % (obj_url, value))


class TitledCheckBoxColumn(tables.CheckBoxColumn):
    @property
    def header(self):
        title = self.attrs.get('title', '')
        return mark_safe('%s %s' % (super(TitledCheckBoxColumn, self).header, title))


class AddPaxBookingServicesTable(tables.Table):
    class Meta:
        model = BaseBookingService
        # fields update_cost_amount and update_price_amount are lazy
        # they contain computed values that will be saved upon save action
        template_name = 'booking/add_pax_bookingservices.html'
        fields = ['pk', 'reset_pk', 'name', 'datetime_from', 'datetime_to',
                  'cost_amount', 'price_amount', 'status', 'conf_number', 'provider']
    pk = TitledCheckBoxColumn(
        accessor='pk',
        attrs={
            'title' : 'Add',
            'th__input': {
                'id': 'action-toggle'},
            'td__input': {
                'class': 'action-select'},
        })
    reset_pk = TitledCheckBoxColumn(
        accessor='pk',
        attrs={
            'title' : 'Reset',
            'th__input': {
                'id': 'action-reset-toggle'},
            'td__input': {
                'class': 'action-reset-select'},
        })

    def __init__(self, *args, **kwargs):
        self.base_columns['cost_amount'].verbose_name = 'Cost'
        self.base_columns['price_amount'].verbose_name = 'Price'
        self.base_columns['datetime_from'].verbose_name = 'From'
        self.base_columns['datetime_to'].verbose_name = 'To'
        super(AddPaxBookingServicesTable, self).__init__(*args, **kwargs)

    def render_name(self, value, record):
        obj_url = reverse(
            'common:booking_%s_change' % (BOOKINGSERVICE_TYPES[record.base_category]),
            args=(quote(record.pk),)
        )
        return format_html('<a href="%s">%s</a>' % (obj_url, value))


class NewQuoteServiceBookDetailTable(tables.Table):
    class Meta:
        model = NewQuoteServiceBookDetail
        template_name = 'booking/table/quoteservicebookdetail_table.html'
        fields = ['name', 'description', 'base_service__category', 'datetime_from', 'time']

    def render_name(self, value, record):
        obj_url = reverse(
            'common:booking_%s_change' % (QUOTE_BOOK_DETAIL_CATEGORIES[record.base_service.category]),
            args=(quote(record.pk),)
        )
        return format_html('<a href="%s">%s</a>' % (obj_url, value))

    def before_render(self, request):
        self.columns.hide('base_service__category')


class BookingBookDetailTable(tables.Table):
    class Meta:
        model = BookingBookDetail
        template_name = 'booking/table/bookingbookdetail_table.html'
        fields = ['name', 'description', 'cost_amount', 'price_amount', 'base_service__category', 'datetime_from', 'time']

    def render_name(self, value, record):
        obj_url = reverse(
            'common:booking_%s_change' % (BOOKINGSERVICE_TYPES[record.base_category]),
            args=(quote(record.pk),)
        )
        return format_html('<a href="%s">%s</a>' % (obj_url, value))

    def before_render(self, request):
        self.columns.hide('base_service__category')
