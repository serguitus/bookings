from django.contrib.admin import register, ModelAdmin

from common.sites import app_site

from .models import Agency, Provider

@register(Agency, site=app_site)
class AccountMng(ModelAdmin):
    list_display = ('name', 'currency', 'enabled',)
    list_filter = ('name', 'currency', 'enabled',)
    search_fields = ('name',)
    ordering = ('enabled', 'currency', 'name',)

@register(Provider, site=app_site)
class AccountMng(ModelAdmin):
    list_display = ('name', 'currency', 'enabled',)
    list_filter = ('name', 'currency', 'enabled',)
    search_fields = ('name',)
    ordering = ('enabled', 'currency', 'name',)



