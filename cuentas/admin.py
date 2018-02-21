from django.conf.urls import url
from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.utils.html import format_html
from django.core.urlresolvers import reverse

from .exceptions import Error
from .forms import DepositForm, WithdrawForm, TransferForm

# Register your models here.
from models import Caja, Transaction


##### ADMIN CLASSES ####
@admin.register(Caja)
class CajaAdmin(admin.ModelAdmin):
    """ an admin interface for the Cajas """
    date_heirarchy = (
        'modified',
    )
    list_display = ('__str__', 'balance', 'modified', 'account_actions')
    actions = ['transfer']
    readonly_fields = (
        'id',
        #'user',
        'modified',
        'balance',
        'account_actions', 
    )
    #list_select_related = (
    #    'user',
    #)

    def get_urls(self):
        urls = super(CajaAdmin, self).get_urls()
        custom_urls = [
            url(
                r'^(?P<account_id>.+)/deposit/$',
                self.admin_site.admin_view(self.process_deposit),
                name='account-deposit',
            ),
            url(
                r'^(?P<account_id>.+)/withdraw/$',
                self.admin_site.admin_view(self.process_withdraw),
                name='account-withdraw',
            ),
            url(
                r'^(?P<account_id>.+)/transfer/$',
                self.admin_site.admin_view(self.process_transfer),
                name='account-transfer',
            ),
        ]
        return custom_urls + urls


    def account_actions(self, obj):
        # TODO: Render action buttons
        return format_html(
            '<a class="button" href="{}">Deposit</a>&nbsp;'
            '<a class="button" href="{}">Withdraw</a>&nbsp'
            '<a class="button" href="{}">Transfer</a>',
            reverse('admin:account-deposit', args=[obj.pk]),
            reverse('admin:account-withdraw', args=[obj.pk]),
            reverse('admin:account-transfer', args=[obj.pk])
        )
    account_actions.short_description = 'Account Actions'
    account_actions.allow_tags = True

    def process_deposit(self, request, account_id, *args, **kwargs):
        return self.process_action(
            request=request,
            account_id=account_id,
            action_form=DepositForm,
            action_title='Deposit',
        )


    def process_withdraw(self, request, account_id, *args, **kwargs):
        return self.process_action(
            request=request,
            account_id=account_id,
            action_form=WithdrawForm,
            action_title='Withdraw',
        )


    def process_transfer(self, request, account_id, *args, **kwargs):
        name = Caja.objects.get(id=account_id).__str__()
        return self.process_action(
             request=request,
             account_id=account_id,
             action_form=TransferForm,
             action_title='Transference from %s' % name,
             )


    def process_action(self, request, account_id, action_form, action_title):
        caja = self.get_object(request, account_id)

        if request.method != 'POST':
            form = action_form()

        else:
            form = action_form(request.POST)
            if form.is_valid():
                try:
                    form.save(caja, request.user)
                    self.message_user(request, 'Operation Successful')

                except Error as e:
                    # If save() raised, the form will a have a non
                    # field error containing an informative message.
                    pass

            else:
                self.message_user(request, 'Success')
                url = reverse(
                    'admin:account_account_change',
                    args=[caja.pk],
                    current_app=self.admin_site.name,
                )
                return HttpResponseRedirect(url)

        context = self.admin_site.each_context(request)
        context['opts'] = self.model._meta
        context['form'] = form
        context['account'] = caja
        context['title'] = action_title

        return TemplateResponse(
            request,
            'admin/account/account_action.html',
            context,
        )

    # Admin Action
    def transfer(self, request, queryset):
        """ to make transferences between Cajas """
        caja = list(queryset)
        if len(caja) > 1:
            return self.message_user(request, 'Para Transferir debe seleccionar solo 1 caja',
                                     level=messages.WARNING)
        response = HttpResponseRedirect('/transfer/?from=%s' % caja[0].id)
        #print response

    transfer.short_description = "Transferir desde esta Caja"



@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    """ an admin interface for Transactions """
    list_display = ('concept', 'detail', 'caja', 'ammount', 'date')
    readonly_fields = ('concept', 'detail', 'caja', 'ammount', 'date',
                       'user', 'transaction_type', 'reference_type')
    list_filter = ('caja',)
    search_fields = ['concept', 'detail']

