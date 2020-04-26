from __future__ import unicode_literals

from django import template
from django.forms.models import modelformset_factory

from config.models import (
    ProviderAllotmentDetail, ProviderTransferDetail, ProviderExtraDetail,
    AgencyAllotmentDetail, AgencyTransferDetail, AgencyExtraDetail,
)
from config.tables import (
    ServiceBookDetailTable,
    ProviderAllotmentDetailTable, ProviderTransferDetailTable, ProviderExtraDetailTable,
    AgencyAllotmentDetailTable, AgencyTransferDetailTable, AgencyExtraDetailTable,
)
register = template.Library()


@register.simple_tag
def servicebookdetail_table(service):
    table = ServiceBookDetailTable(
        service.servicebookdetail_service.all(),
        order_by=('days_after', 'days_duration'))
    return table

@register.simple_tag
def providerallotmentdetail_context(providerservice):
    table = ProviderAllotmentDetailTable(
        providerservice.providerallotmentdetail_set.all() \
            .select_related('room_type', 'addon'),
        order_by=('room_type', 'board_type'))
    return {'table': table}

@register.simple_tag
def providertransferdetail_context(providerservice):
    table = ProviderTransferDetailTable(
        providerservice.providertransferdetail_set.all() \
            .select_related('location_from', 'location_to', 'addon'),
        order_by=('location_from', 'location_to'))
    return {'table': table}

@register.simple_tag
def providerextradetail_context(providerservice):
    table = ProviderExtraDetailTable(
        providerservice.providerextradetail_set.all() \
            .select_related('addon'),
        order_by=('addoin', 'pax_range_min', 'pax_range_min'))
    return {'table': table}

@register.simple_tag
def agencyallotmentdetail_context(agencyservice):
    table = AgencyAllotmentDetailTable(
        agencyservice.agencyallotmentdetail_set.all() \
            .select_related('room_type', 'addon'),
        order_by=('room_type', 'board_type'))
    return {'table': table}

@register.simple_tag
def agencytransferdetail_context(agencyservice):
    table = AgencyTransferDetailTable(
        agencyservice.agencytransferdetail_set.all() \
            .select_related('location_from', 'location_to', 'addon'),
        order_by=('location_from', 'location_to'))
    return {'table': table}

@register.simple_tag
def agencyextradetail_context(agencyservice):
    table = AgencyExtraDetailTable(
        agencyservice.agencyextradetail_set.all() \
            .select_related('addon'),
        order_by=('addoin', 'pax_range_min', 'pax_range_min'))
    return {'table': table}
