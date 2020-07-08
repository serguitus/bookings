import django_tables2 as tables

from django.contrib.admin.utils import quote
from django.urls import reverse
from django.utils.html import format_html

from config.models import (
    ServiceBookDetail,
    ProviderAllotmentDetail, ProviderTransferDetail, ProviderExtraDetail,
    AgencyAllotmentDetail, AgencyTransferDetail, AgencyExtraDetail,
)
from config.constants import (
    SERVICE_BOOK_DETAIL_CATEGORIES,
)


class ServiceBookDetailTable(tables.Table):
    class Meta:
        model = ServiceBookDetail
        template_name = 'config/table/servicebookdetail_table.html'
        fields = ['name', 'description', 'base_service__category', 'days_after', 'days_duration']

    def render_name(self, value, record):
        obj_url = reverse(
            'common:config_%s_change' % (SERVICE_BOOK_DETAIL_CATEGORIES[record.base_service.category]),
            args=(quote(record.pk),)
        )
        return format_html('<a href="%s">%s</a>' % (obj_url, value))

    def before_render(self, request):
        self.columns.hide('base_service__category')


class ProviderAllotmentDetailTable(tables.Table):
    class Meta:
        attrs = {'class': 'table table-hover table-condensed'}
        model = ProviderAllotmentDetail
        fields = [
            'edit', 'room_type', 'board_type', 'pax_range_min',
            'pax_range_max', 'ad_1_amount', 'ch_1_ad_1_amount',
            'ch_2_ad_1_amount', 'ad_2_amount', 'ch_1_ad_2_amount',
            'ch_2_ad_2_amount', 'ad_3_amount', 'ch_1_ad_3_amount',
            'ad_4_amount']

    edit = tables.TemplateColumn(
        template_name="config/include/table_edit.html",
        extra_context={
            "edit_url": 'common:config_providerallotmentdetail_change'
        },
        verbose_name='Edit')

    def __init__(self, *args, **kwargs):
        self.base_columns['pax_range_min'].verbose_name = 'Pax Min'
        self.base_columns['pax_range_max'].verbose_name = 'Pax Max'
        self.base_columns['ch_1_ad_1_amount'].verbose_name = '(1st/2nd) Chd'
        self.base_columns['ch_1_ad_2_amount'].verbose_name = '(1st/2nd) Chd'
        self.base_columns['ch_1_ad_3_amount'].verbose_name = '1st Chd'
        super(ProviderAllotmentDetailTable, self).__init__(*args, **kwargs)

    def render_ch_1_ad_1_amount(self, value, record):
        return format_html('{}/{}'.format(value, record.ch_2_ad_1_amount))

    def render_ch_1_ad_2_amount(self, value, record):
        return format_html('{}/{}'.format(value, record.ch_2_ad_2_amount))

    def before_render(self, request):
        self.columns.hide('ch_2_ad_1_amount')
        self.columns.hide('ch_2_ad_2_amount')


class ProviderTransferDetailTable(tables.Table):
    class Meta:
        attrs = {'class': 'table table-hover table-condensed'}
        model = ProviderTransferDetail
        fields = [
            'edit', 'location_from', 'location_to', 'addon', 'pax_range_min', 'pax_range_max',
            'ad_1_amount', 'ch_1_ad_1_amount']

    edit = tables.TemplateColumn(
        template_name="config/include/table_edit.html",
        extra_context={
            "edit_url": 'common:config_providertransferdetail_change'
        },
        verbose_name='Edit')

    def __init__(self, *args, **kwargs):
        self.base_columns['pax_range_min'].verbose_name = 'Pax Min'
        self.base_columns['pax_range_max'].verbose_name = 'Pax Max'
        self.base_columns['ad_1_amount'].verbose_name = 'Cost'
        self.base_columns['ch_1_ad_1_amount'].verbose_name = 'Chd Cost'
        self.base_columns['location_from'].verbose_name = 'Origin'
        self.base_columns['location_to'].verbose_name = 'Destination'
        super(ProviderTransferDetailTable, self).__init__(*args, **kwargs)


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

    def __init__(self, *args, **kwargs):
        self.base_columns['pax_range_min'].verbose_name = 'Pax Min'
        self.base_columns['pax_range_max'].verbose_name = 'Pax Max'
        self.base_columns['ad_1_amount'].verbose_name = 'Cost'
        # self.base_columns['ch_1_ad_1_amount'].verbose_name = 'Child Cost'
        super(ProviderExtraDetailTable, self).__init__(*args, **kwargs)


class AgencyAllotmentDetailTable(ProviderAllotmentDetailTable):
    class Meta:
        attrs = {'class': 'table table-hover table-condensed'}
        model = AgencyAllotmentDetail
        fields = [
            'edit', 'room_type', 'board_type', 'pax_range_min',
            'pax_range_max', 'ad_1_amount', 'ch_1_ad_1_amount',
            'ch_2_ad_1_amount', 'ad_2_amount', 'ch_1_ad_2_amount',
            'ch_2_ad_2_amount', 'ad_3_amount', 'ch_1_ad_3_amount',
            'ad_4_amount']

    edit = tables.TemplateColumn(
        template_name="config/include/table_edit.html",
        extra_context={
            "edit_url": 'common:config_agencyallotmentdetail_change'
        },
        verbose_name='Edit')


class AgencyTransferDetailTable(ProviderTransferDetailTable):
    class Meta:
        attrs = {'class': 'table table-hover table-condensed'}
        model = AgencyTransferDetail
        fields = [
            'edit', 'location_from', 'location_to', 'reversible', 'addon',
            'pax_range_min', 'pax_range_max',
            'ad_1_amount', 'ch_1_ad_1_amount']

    edit = tables.TemplateColumn(
        template_name="config/include/table_edit.html",
        extra_context={
            "edit_url": 'common:config_agencytransferdetail_change'
        },
        verbose_name='Edit')
    reversible = tables.BooleanColumn()



class AgencyExtraDetailTable(ProviderExtraDetailTable):
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
