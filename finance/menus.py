from django.contrib.admin import register, ModelAdmin

from common.sites import app_site

from finance.models import Agency, Provider, Deposit


@register(Agency, site=app_site)
class AgencyAdmin(ModelAdmin):
    list_display = ('name', 'currency', 'enabled',)
    list_filter = ('name', 'currency', 'enabled',)
    search_fields = ('name',)
    ordering = ('enabled', 'currency', 'name',)


@register(Provider, site=app_site)
class ProviderAdmin(ModelAdmin):
    list_display = ('name', 'currency', 'enabled',)
    list_filter = ('name', 'currency', 'enabled',)
    search_fields = ('name',)
    ordering = ('enabled', 'currency', 'name',)


@register(Deposit, site=app_site)
class DepositAdmin(ModelAdmin):
    list_display = ['name', 'date', 'amount', 'status']
    search_fields = ['name', 'amount']
    ordering = ['date']

    def get_urls(self):
        urls = super(DepositAdmin, self).get_urls()
        return urls
        # TODO: uncomment to add new urls
        # my_urls = [
        #     url(r'^my_view/$', self.my_view),
        # ]
        # return my_urls + urls
