import django_tables2 as tables

from django.contrib.admin.utils import quote
from django.urls import reverse
from django.utils.html import format_html

from config.models import (
    ServiceDetail,
    ProviderAllotmentDetail, ProviderTransferDetail, ProviderExtraDetail,
    AgencyAllotmentDetail, AgencyTransferDetail, AgencyExtraDetail,
)
from config.constants import (
    SERVICE_DETAIL_CATEGORIES,
)


class ServiceDetailTable(tables.Table):
    class Meta:
        model = ServiceDetail
        template_name = 'config/servicedetail_list.html'
        fields = ['name', 'description', 'base_detail_service__category', 'days_after', 'days_duration']

    def render_name(self, value, record):
        obj_url = reverse(
            'common:config_%s_change' % (SERVICE_DETAIL_CATEGORIES[record.base_detail_service.category]),
            args=(quote(record.pk),)
        )
        return format_html('<a href="%s">%s</a>' % (obj_url, value))

    def before_render(self, request):
        self.columns.hide('base_detail_service__category')


class ProviderAllotmentDetailTable(tables.Table):
    class Meta:
        attrs = {'class': 'table table-hover table-condensed'}
        model = ProviderAllotmentDetail
        fields = [
            'edit', 'room_type', 'board_type', 'addon', 'pax_range_min', 'pax_range_max',
            'ad_1_amount', 'ad_2_amount', 'ad_3_amount', 'ad_4_amount']

    edit = tables.TemplateColumn(
        template_name="config/include/table_edit.html",
        extra_context={
            "edit_url": 'common:config_providerallotmentdetail_change'
        },
        verbose_name='Edit')


class ProviderTransferDetailTable(tables.Table):
    class Meta:
        attrs = {'class': 'table table-hover table-condensed'}
        model = ProviderTransferDetail
        fields = [
            'edit', 'p_location_from', 'p_location_to', 'addon', 'pax_range_min', 'pax_range_max',
            'ad_1_amount', 'ch_1_ad_1_amount']

    edit = tables.TemplateColumn(
        template_name="config/include/table_edit.html",
        extra_context={
            "edit_url": 'common:config_providertransferdetail_change'
        },
        verbose_name='Edit')


class ProviderExtraDetailTable(tables.Table):
    class Meta:
        attrs = {'class': 'table table-hover table-condensed'}
        model = ProviderExtraDetail
        fields = ['edit', 'pax_range_min', 'pax_range_max', 'addon', 'ad_1_amount']

    edit = tables.TemplateColumn(
        template_name="config/include/table_edit.html",
        extra_context={
            "edit_url": 'common:config_providerextradetail_change'
        },
        verbose_name='Edit')


class AgencyAllotmentDetailTable(tables.Table):
    class Meta:
        attrs = {'class': 'table table-hover table-condensed'}
        model = AgencyAllotmentDetail
        fields = [
            'edit', 'room_type', 'board_type', 'addon', 'pax_range_min', 'pax_range_max',
            'ad_1_amount', 'ad_2_amount', 'ad_3_amount', 'ad_4_amount']

    edit = tables.TemplateColumn(
        template_name="config/include/table_edit.html",
        extra_context={
            "edit_url": 'common:config_agencyallotmentdetail_change'
        },
        verbose_name='Edit')


class AgencyTransferDetailTable(tables.Table):
    class Meta:
        attrs = {'class': 'table table-hover table-condensed'}
        model = AgencyTransferDetail
        fields = [
            'edit', 'a_location_from', 'a_location_to', 'addon', 'pax_range_min', 'pax_range_max',
            'ad_1_amount', 'ch_1_ad_1_amount']

    edit = tables.TemplateColumn(
        template_name="config/include/table_edit.html",
        extra_context={
            "edit_url": 'common:config_agencytransferdetail_change'
        },
        verbose_name='Edit')


class AgencyExtraDetailTable(tables.Table):
    class Meta:
        attrs = {'class': 'table table-hover table-condensed'}
        model = AgencyExtraDetail
        fields = ['edit', 'pax_range_min', 'pax_range_max', 'addon', 'ad_1_amount']

    edit = tables.TemplateColumn(
        template_name="config/include/table_edit.html",
        extra_context={
            "edit_url": 'common:config_agencyextradetail_change'
        },
        verbose_name='Edit')
