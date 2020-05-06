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

class_mapping = {
    'ProviderAllotmentService': ProviderAllotmentDetailTable,
    'AgencyAllotmentService': AgencyAllotmentDetailTable,
    'ProviderTransferService': ProviderTransferDetailTable,
    'AgencyTransferService': AgencyTransferDetailTable,
    'ProviderExtraService': ProviderExtraDetailTable,
    'AgencyExtraService': AgencyExtraDetailTable,
}

# related fields per service type to build catalog tables
table_related_fields = {
    'ProviderAllotmentService': ['room_type', 'addon'],
    'AgencyAllotmentService': ['room_type', 'addon'],
    'ProviderTransferService': ['location_from', 'location_to', 'addon'],
    'AgencyTransferService': ['location_from', 'location_to', 'addon'],
    'ProviderExtraService': ['addon'],
    'AgencyExtraService': ['addon'],
}

# ordering fields per service type to build catalog tables
table_ordering_fields = {
    'ProviderAllotmentService': ['room_type', 'board_type'],
    'AgencyAllotmentService': ['room_type', 'board_type'],
    'ProviderTransferService': ['location_from', 'location_to'],
    'AgencyTransferService': ['location_from', 'location_to'],
    'ProviderExtraService': ['addon', 'pax_range_min', 'pax_range_min'],
    'AgencyExtraService': ['addon', 'pax_range_min', 'pax_range_min'],
}


@register.simple_tag
def servicebookdetail_table(service):
    table = ServiceBookDetailTable(
        service.servicebookdetail_service.all(),
        order_by=('days_after', 'days_duration'))
    return table


@register.simple_tag
def catalog_detail_context(providerservice):
    obj_class = providerservice.__class__.__name__
    table = class_mapping[obj_class](
        providerservice.get_detail_objects()
        .select_related(
            *table_related_fields[obj_class]),
        order_by=table_ordering_fields[obj_class])
    return {'table': table}
