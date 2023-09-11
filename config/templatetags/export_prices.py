from __future__ import unicode_literals

from django import template

from config.services import ConfigServices

register = template.Library()

@register.inclusion_tag("config/pdf/service_prices.html")
def service_prices(service=None, agency=None, date_from=None, date_to=None, booked_from=None, booked_to=None):
    details = ConfigServices.list_service_prices(service, agency, date_from, date_to, booked_from, booked_to)
    return {
        'service': service,
        'details': details}

# a filter to add css classes to widgets. used to style form fields
@register.filter(name='addclass')
def addclass(value, arg):
    return value.as_widget(attrs={'class': arg})
