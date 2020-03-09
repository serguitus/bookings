import django_tables2 as tables

from django.contrib.admin.utils import quote
from django.urls import reverse
from django.utils.html import format_html

from config.models import (
    ServiceDetail,
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
