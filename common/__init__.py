
from django.utils.module_loading import autodiscover_modules

from common.sites import app_site

def autodiscover():
    autodiscover_modules('menus', register_to=app_site)

default_app_config = 'common.apps.CommonConfig'