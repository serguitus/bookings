from django.contrib import admin, messages
from django.http import HttpResponseRedirect

# Register your models here.
from models import Caja, Transaction


##### ADMIN CLASSES ####
@admin.register(Caja)
class CajaAdmin(admin.ModelAdmin):
    """ an admin interface for the Cajas """
    list_display = ('__str__', 'balance')
    actions = ['transfer']

    # Admin Action
    def transfer(self, request, queryset):
        """ to make transferences between Cajas """
        caja = list(queryset)
        if len(caja) > 1:
            return self.message_user(request, 'Para Transferir debe seleccionar solo 1 caja',
                                     level=messages.WARNING)
        response = HttpResponseRedirect('/transfer/?from=%s' % caja[0].id)
        print response

    transfer.short_description = "Transferir desde esta Caja"



@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    """ an admin interface for Transactions """
    list_display = ('concept', 'detail', 'caja', 'ammount', 'date')
    list_filter = ('caja',)
    search_fields = ['concept', 'detail']
