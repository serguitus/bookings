from weakref import WeakSet

from django.contrib.admin.options import ModelAdmin
from django.contrib.admin.sites import AdminSite
from django.utils.translation import ugettext as _, ugettext_lazy

all_sites = WeakSet()


class CommonSite(AdminSite):

    index_template = 'index.html'
    # Text to put at the end of each page's <title>.
    site_title = ugettext_lazy('Application Site')

    # Text to put in each page's <h1>.
    site_header = ugettext_lazy('Application Site')

    # Text to put at the top of the admin index page.
    index_title = ugettext_lazy('Application Site')

    @property
    def urls(self):
        return self.get_urls(), 'reservas', self.name


class CommonModel(ModelAdmin):
    site_actions = []


app_site = CommonSite(name='reservas')
