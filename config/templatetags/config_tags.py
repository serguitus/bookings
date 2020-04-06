from __future__ import unicode_literals
from django import template

from config.tables import (
    ServiceBookDetailTable,
)
register = template.Library()


@register.simple_tag
def servicebookdetail_table(service):
    table = ServiceBookDetailTable(
        service.servicebookdetail_service.all(),
        order_by=('days_after', 'days_duration'))
    return table
