from django.apps import AppConfig
from django.contrib.admin.checks import check_admin_app, check_dependencies
from django.core import checks

class CommonConfig(AppConfig):
    """The default AppConfig for common which does autodiscovery."""
    name = 'common'
    module = 'common'

    def ready(self):
        checks.register(check_dependencies, checks.Tags.admin)
        checks.register(check_admin_app, checks.Tags.admin)
        self.module.autodiscover()
