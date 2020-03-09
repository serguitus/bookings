from __future__ import unicode_literals
from django import template

from config.tables import (
    ServiceDetailTable,
)
register = template.Library()


@register.simple_tag
def servicedetail_table(service):
    table = ServiceDetailTable(
        service.service_details.all(),
        order_by=('days_after', 'days_duration'))
    return table
