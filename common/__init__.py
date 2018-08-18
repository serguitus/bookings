
from django.utils.module_loading import autodiscover_modules


def autodiscover():
    autodiscover_modules('common_site')

default_app_config = 'common.apps.CommonConfig'
