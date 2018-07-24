from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _

class FinanceConfig(AppConfig):
    name = 'finance'
    icon = '<i class="material-icons">people</i>'
    verbose_name = _('Finances')
