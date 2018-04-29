from django.contrib import admin

from .models import *

@admin.register(Agency)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('name','currency','enabled',)
    list_filter = ('name','currency','enabled',)
    search_fields = ('name',)
    ordering = ('enabled','currency','name',)

@admin.register(Provider)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('name','currency','enabled',)
    list_filter = ('name','currency','enabled',)
    search_fields = ('name',)
    ordering = ('enabled','currency','name',)

admin.site.register(FinantialDocument)


