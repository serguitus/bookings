import django_tables2 as tables

from django.urls import reverse
from django.contrib.admin.utils import quote
from django.utils.html import format_html

from finance.models import (
    AgencyInvoice, AgencyPayment,
)


class AgencyInvoiceTable(tables.Table):
    class Meta:
        model = AgencyInvoice
        template_name = 'finance/agencyinvoice_table.html'
        fields = ['name', 'date', 'status', 'amount', 'details']
        attrs = {'class': 'table table-hover table-sm'}

    def __init__(self, *args, **kwargs):
        self.base_columns['name'].verbose_name='Invoice'
        super(AgencyInvoiceTable, self).__init__(*args, **kwargs)

    def render_name(self, value, record):
        obj_url = reverse(
            'common:finance_agencyinvoice_change',
            args=(quote(record.pk),)
        )
        return format_html('<a href="%s">%s</a>' % (obj_url, value))


class AgencyPaymentTable(tables.Table):
    class Meta:
        model = AgencyPayment
        template_name = 'finance/agencypayment_table.html'
        fields = ['name', 'date', 'status', 'account', 'amount', 'details']
        attrs = {'class': 'table table-hover table-sm'}

    def __init__(self, *args, **kwargs):
        self.base_columns['name'].verbose_name='Payment'
        super(AgencyPaymentTable, self).__init__(*args, **kwargs)

    def render_name(self, value, record):
        obj_url = reverse(
            'common:finance_agencypayment_change',
            args=(quote(record.pk),)
        )
        return format_html('<a href="%s">%s</a>' % (obj_url, value))
