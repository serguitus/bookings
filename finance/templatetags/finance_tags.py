from __future__ import unicode_literals
from django import template

from finance.models import (
    AgencyInvoice, AgencyPayment,
)
from finance.tables import (
    AgencyInvoiceTable, AgencyPaymentTable,
)
from booking.services import BookingServices


register = template.Library()


@register.simple_tag
def agencyinvoice_table(payment):
    table = AgencyInvoiceTable(
        AgencyInvoice.objects.filter(agencydocumentmatch__credit_document=payment),
        order_by=('date',),
    )
    return table


@register.simple_tag
def agencypayment_table(invoice):
    table = AgencyPaymentTable(
        AgencyPayment.objects.filter(agencydocumentmatch__debit_document=invoice),
        order_by=('date',),
    )
    return table
