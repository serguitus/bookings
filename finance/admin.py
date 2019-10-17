from functools import update_wrapper, partial

from django.conf.urls import url
from django.contrib import admin, messages
from django.contrib.admin.options import csrf_protect_m
from django.contrib.admin import helpers
from django.core.exceptions import ValidationError, PermissionDenied
from django.db import router, transaction
from django.forms.models import modelformset_factory
from django.http import HttpResponseRedirect
from django.template.response import SimpleTemplateResponse, TemplateResponse
from django.utils.encoding import force_text
from django.utils.translation import ugettext as _, ungettext

from reservas.admin import reservas_admin, ExtendedModelAdmin

from finance.models import (
    Agency, Provider, FinantialDocument,
    Deposit, Withdraw, CurrencyExchange, Transfer,
    LoanAccountWithdraw, LoanAccountDeposit,
    LoanEntity, LoanEntityWithdraw, LoanEntityDeposit)
from finance.services import FinanceServices


class IncorrectLookupParameters(Exception):
    pass


@admin.register(Agency)
class AgencyAdmin(admin.ModelAdmin):
    list_display = ('name', 'currency', 'enabled')
    list_filter = ('name', 'currency', 'enabled')
    search_fields = ['name']
    ordering = ('enabled', 'currency', 'name')


@admin.register(Provider)
class ProviderAdmin(admin.ModelAdmin):
    list_display = ('name', 'currency', 'enabled')
    list_filter = ('name', 'currency', 'enabled')
    search_fields = ['name']
    ordering = ('enabled', 'currency', 'name')


@admin.register(LoanEntity)
class LoanEntityAdmin(admin.ModelAdmin):
    list_display = ('name',)
    list_filter = ('name',)
    search_fields = ['name',]
    ordering = ('name',)


admin.site.register(Deposit)

# ### Registering in custom adminSite reservas_admin ###

class FinantialDocumentAdmin(ExtendedModelAdmin):
    readonly_model = True
    delete_allowed = False
    actions_on_top = False
    fields = ('name', 'currency', 'amount', 'date', 'status')
    list_display = ('name', 'currency', 'amount', 'date', 'status')
    list_filter = ('currency', 'currency', 'status', 'date')
    search_fields = ('name',)
    ordering = ['-date', 'currency', 'status']


class BaseFinantialDocumentAdmin(FinantialDocumentAdmin):
    readonly_model = False
    readonly_fields = ('name',)


class MatchableModelAdmin(BaseFinantialDocumentAdmin):
    match_model = None
    match_fields = []
    match_list_display = []
    match_list_editable = []

    def pending_amount(self, obj):
        return obj.amount - obj.matched_amount

    def get_matchlist_formset(self, request, **kwargs):
        """
        Returns a FormSet class for use on the changelist page if list_editable
        is used.
        """
        defaults = {
            "formfield_callback": partial(
                self.formfield_for_dbfield, request=request),
        }
        defaults.update(kwargs)
        return modelformset_factory(
            self.model, self.get_changelist_form(request), extra=0,
            fields=self.match_list_editable, **defaults
        )

    def get_urls(self):

        def wrap(view):

            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)

            wrapper.model_admin = self
            return update_wrapper(wrapper, view)

        new_urls = [
            url(r'^(?P<pk>[-\w]+)/match/$', wrap(self.matchlist_view), name='matchlist-view')
        ]
        return new_urls + super(MatchableModelAdmin, self).get_urls()

    @csrf_protect_m
    def matchlist_view(self, request, pk, extra_context=None):
        """
        The 'match list' admin view for this model.
        """
        from django.contrib.admin.views.main import ERROR_FLAG
        match_obj = reservas_admin._registry[self.match_model]
        opts = match_obj.model._meta
        # opts = self.model._meta
        app_label = opts.app_label
        if not self.has_change_permission(request, None):
            raise PermissionDenied

        list_display = self.match_list_display
        list_display_links = match_obj.get_list_display_links(request, list_display)
        list_filter = match_obj.get_list_filter(request)
        search_fields = match_obj.get_search_fields(request)
        list_select_related = match_obj.get_list_select_related(request)
        obj_id = pk

        # Check actions to see if any are available on this changelist
        actions = match_obj.get_actions(request)
        if actions:
            # Add the action checkboxes if there are any actions available.
            list_display = ['action_checkbox'] + list(list_display)

        MatchList = match_obj.get_matchlist(request)
        try:
            cl = MatchList(
                request, match_obj.model, list_display,
                list_display_links, list_filter, match_obj.date_hierarchy,
                search_fields, list_select_related, match_obj.list_per_page,
                match_obj.list_max_show_all, match_obj.match_list_editable, match_obj,
                self.match_fields, self.model, obj_id
            )
        except IncorrectLookupParameters:
            # Wacky lookup parameters were given, so redirect to the main
            # changelist page, without parameters, and pass an 'invalid=1'
            # parameter via the query string. If wacky parameters were given
            # and the 'invalid=1' parameter was already in the query string,
            # something is screwed up with the database, so display an error
            # page.
            if ERROR_FLAG in request.GET.keys():
                return SimpleTemplateResponse('admin/invalid_setup.html', {
                    'title': _('Database error'),
                })
            return HttpResponseRedirect(request.path + '?' + ERROR_FLAG + '=1')

        # If the request was POSTed, this might be a bulk action or a bulk
        # edit. Try to look up an action or confirmation first, but if this
        # isn't an action the POST will fall through to the bulk edit check,
        # below.
        action_failed = False
        selected = request.POST.getlist(helpers.ACTION_CHECKBOX_NAME)

        # Actions with no confirmation
        if (actions and request.method == 'POST' and
                'index' in request.POST and '_save' not in request.POST):
            if selected:
                response = self.response_action(request, queryset=cl.get_queryset(request))
                if response:
                    return response
                else:
                    action_failed = True
            else:
                msg = _("Items must be selected in order to perform "
                        "actions on them. No items have been changed.")
                match_obj.message_user(request, msg, messages.WARNING)
                action_failed = True

        # Actions with confirmation
        if (actions and request.method == 'POST' and
                helpers.ACTION_CHECKBOX_NAME in request.POST and
                'index' not in request.POST and '_save' not in request.POST):
            if selected:
                response = match_obj.response_action(request, queryset=cl.get_queryset(request))
                if response:
                    return response
                else:
                    action_failed = True

        if action_failed:
            # Redirect back to the changelist page to avoid resubmitting the
            # form if the user refreshes the browser or uses the "No, take
            # me back" button on the action confirmation page.
            return HttpResponseRedirect(request.get_full_path())

        # If we're allowing changelist editing, we need to construct a formset
        # for the changelist given all the fields to be edited. Then we'll
        # use the formset to validate/process POSTed data.
        formset = cl.formset = None

        # Handle POSTed bulk-edit data.
        if request.method == 'POST' and cl.list_editable and '_save' in request.POST:
            FormSet = match_obj.get_matchlist_formset(request)
            formset = cl.formset = FormSet(request.POST, request.FILES, queryset=match_obj.get_queryset(request))
            if formset.is_valid():
                changecount = 0
                for form in formset.forms:
                    if form.has_changed():
                        obj = match_obj.save_form(request, form, change=True)
                        match_obj.save_model(request, obj, form, change=True)
                        match_obj.save_related(request, form, formsets=[], change=True)
                        change_msg = match_obj.construct_change_message(request, form, None)
                        match_obj.log_change(request, obj, change_msg)
                        changecount += 1

                if changecount:
                    if changecount == 1:
                        name = force_text(opts.verbose_name)
                    else:
                        name = force_text(opts.verbose_name_plural)
                    msg = ungettext(
                        "%(count)s %(name)s was changed successfully.",
                        "%(count)s %(name)s were changed successfully.",
                        changecount
                    ) % {
                        'count': changecount,
                        'name': name,
                        'obj': force_text(obj),
                    }
                    match_obj.message_user(request, msg, messages.SUCCESS)

                return HttpResponseRedirect(request.get_full_path())

        # Handle GET -- construct a formset for display.
        elif cl.list_editable:
            FormSet = match_obj.get_matchlist_formset(request)
            formset = cl.formset = FormSet(queryset=cl.result_list)

        # Build the list of media to be used by the formset.
        if formset:
            media = match_obj.media + formset.media
        else:
            media = match_obj.media

        # Build the action form and populate it with available actions.
        if actions:
            action_form = match_obj.action_form(auto_id=None)
            action_form.fields['action'].choices = match_obj.get_action_choices(request)
            media += action_form.media
        else:
            action_form = None

        selection_note_all = ungettext(
            '%(total_count)s selected',
            'All %(total_count)s selected',
            cl.result_count
        )

        context = dict(
            match_obj.admin_site.each_context(request),
            module_name=force_text(opts.verbose_name_plural),
            selection_note=_('0 of %(cnt)s selected') % {'cnt': len(cl.result_list)},
            selection_note_all=selection_note_all % {'total_count': cl.result_count},
            title=cl.title,
            is_popup=cl.is_popup,
            to_field=cl.to_field,
            cl=cl,
            media=media,
            has_add_permission=match_obj.has_add_permission(request),
            opts=cl.opts,
            action_form=action_form,
            actions_on_top=match_obj.actions_on_top,
            actions_on_bottom=match_obj.actions_on_bottom,
            actions_selection_counter=match_obj.actions_selection_counter,
            preserved_filters=match_obj.get_preserved_filters(request),
        )
        context.update(extra_context or {})

        request.current_app = match_obj.admin_site.name

        return TemplateResponse(request, match_obj.change_list_template or [
            'admin/%s/%s/change_list.html' % (app_label, opts.model_name),
            'admin/%s/change_list.html' % app_label,
            'admin/change_list.html'
        ], context)


class DepositAdmin(BaseFinantialDocumentAdmin):
    fields = ('name', 'account', 'amount', 'date', 'status')
    list_display = ('name', 'account', 'amount', 'date', 'status')
    list_filter = ('currency', 'account', 'status', 'date')

    def save_model(self, request, obj, form, change):
        # overrides base class method
        return FinanceServices.save_deposit(request.user, obj)


class WithdrawAdmin(DepositAdmin):

    def save_model(self, request, obj, form, change):
        # overrides base class method
        return FinanceServices.save_withdraw(request.user, obj)


class CurrencyExchangeAdmin(BaseFinantialDocumentAdmin):
    fields = ('name', 'account', 'amount', 'date', 'status', 'exchange_account', 'exchange_amount')
    list_display = (
        'name', 'account', 'amount', 'date', 'status', 'exchange_account', 'exchange_amount')
    list_filter = ('currency', 'account', 'status', 'date')

    def save_model(self, request, obj, form, change):
        # overrides base class method
        return FinanceServices.save_currency_exchange(request.user, obj)


class TransferAdmin(BaseFinantialDocumentAdmin):
    fields = ('name', 'account', 'transfer_account', 'amount', 'date', 'status')
    list_display = ('name', 'account', 'transfer_account', 'amount', 'date', 'status')
    list_filter = ('currency', 'account', 'status', 'date')

    def save_model(self, request, obj, form, change):
        # overrides base class method
        return FinanceServices.save_transfer(request.user, obj)


class LoanAccountDocumentAdmin(MatchableModelAdmin):
    """
    base class for loan accounts deposits and withdraws
    """
    fields = ('name', 'account', 'loan_account', 'amount', 'date', 'status')
    list_display = ['name', 'account', 'loan_account', 'amount', 'date', 'status']
    list_filter = ('currency', 'account', 'status', 'date')
    match_fields = ['account', 'loan_account']
    match_list_display = ['account', 'loan_account', 'amount', 'pending_amount', 'date']
    match_list_editable = ['amount']


class LoanAccountDepositAdmin(LoanAccountDocumentAdmin):
    """
    class for loan account deposits
    """
    match_model = LoanAccountWithdraw

    def save_model(self, request, obj, form, change):
        # overrides base class method
        return FinanceServices.save_loan_account_deposit(request.user, obj)


class LoanAccountWithdrawAdmin(LoanAccountDocumentAdmin):
    """
    class for loan account withdraws
    """
    match_model = LoanAccountDeposit

    def save_model(self, request, obj, form, change):
        # overrides base class method
        return FinanceServices.save_loan_account_withdraw(request.user, obj)


class LoanEntityDocumentAdmin(MatchableModelAdmin):
    """
    base class for loan entities deposits and withdraws
    """
    fields = ('name', 'account', 'loan_entity', 'amount', 'date', 'status')
    list_display = ['name', 'account', 'loan_entity', 'amount', 'date', 'status']
    list_filter = ('currency', 'account', 'status', 'date')
    match_fields = ['account', 'loan_entity']
    match_list_display = ['account', 'loan_entity', 'amount', 'pending_amount', 'date']
    match_list_editable = ['amount']


class LoanEntityDepositAdmin(LoanEntityDocumentAdmin):
    """
    class for loan entity deposits
    """
    match_model = LoanEntityWithdraw

    def save_model(self, request, obj, form, change):
        # overrides base class method
        return FinanceServices.save_loan_entity_deposit(request.user, obj)


class LoanEntityWithdrawAdmin(LoanEntityDocumentAdmin):
    """
    class for loan entity withdraws
    """
    match_model = LoanEntityDeposit

    def save_model(self, request, obj, form, change):
        # overrides base class method
        return FinanceServices.save_loan_entity_withdraw(request.user, obj)


reservas_admin.register(Provider, ProviderAdmin)
reservas_admin.register(Agency, AgencyAdmin)
reservas_admin.register(LoanEntity, LoanEntityAdmin)
reservas_admin.register(FinantialDocument, FinantialDocumentAdmin)
reservas_admin.register(Deposit, DepositAdmin)
reservas_admin.register(Withdraw, WithdrawAdmin)
reservas_admin.register(CurrencyExchange, CurrencyExchangeAdmin)
reservas_admin.register(Transfer, TransferAdmin)
reservas_admin.register(LoanAccountWithdraw, LoanAccountWithdrawAdmin)
reservas_admin.register(LoanAccountDeposit, LoanAccountDepositAdmin)
reservas_admin.register(LoanEntityWithdraw, LoanEntityWithdrawAdmin)
reservas_admin.register(LoanEntityDeposit, LoanEntityDepositAdmin)
