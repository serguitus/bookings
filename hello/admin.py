from django.contrib import admin

# Register your models here.

from django.contrib.admin.models import LogEntry


class LogEntryAdmin(admin.ModelAdmin):
    model = LogEntry
    search_fields = ['change_message']
    list_display = ['action_time', 'user', 'content_type', 'object_repr', 'change_message', ]


admin.site.register(LogEntry, LogEntryAdmin)
