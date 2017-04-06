from django.contrib import admin

# Register your models here.

from models import Caja, Transaction

@admin.register(Caja)
class CajaAdmin(admin.ModelAdmin):
    """ an admin interface for the Cajas """
    list_display = ('__str__', 'ammount')


admin.site.register(Transaction)
