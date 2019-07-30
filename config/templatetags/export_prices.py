from __future__ import unicode_literals

from django import template

from config.services import ConfigServices

register = template.Library()

@register.inclusion_tag("config/pdf/service_prices.html")
def service_prices(service=None, agency=None, date_from=None, date_to=None):
    details = ConfigServices.list_service_prices(service, agency, date_from, date_to)
    return {'details': details}
