from django.contrib import admin

# Register your models here.

from models import Caja, Transaction

admin.site.register(Caja)
admin.site.register(Transaction)
