from django.contrib import admin

from finance.models import (Agency, Provider, Deposit,
                            Withdraw)
# Register your models here.

admin.site.register(Agency)
admin.site.register(Provider)
admin.site.register(Deposit)
admin.site.register(Withdraw)
