from common.sites import SiteModel

from django.conf.urls import url
from django.contrib import admin, messages
from django.contrib.admin.options import csrf_protect_m, IS_POPUP_VAR, TO_FIELD_VAR
from django.contrib.admin import helpers
from django.contrib.admin.checks import ModelAdminChecks
from django.contrib.admin.utils import unquote
from django.core import checks
from django.core.exceptions import FieldDoesNotExist, ValidationError, PermissionDenied
from django.db import router, transaction
from django import forms
from django.forms.models import modelformset_factory
from django.http import HttpResponseRedirect
from django.template.response import SimpleTemplateResponse, TemplateResponse
from django.utils.encoding import force_text
from django.utils.translation import ugettext as _, ungettext
from django.utils import six

from finance.forms import (
    AccountingForm, CurrencyExchangeForm, TransferForm,
    LoanEntityDocumentForm, LoanAccountDocumentForm,
    ProviderDocumentForm, AgencyDocumentForm)
from finance.models import (
    Office,
    FinantialDocument,
    Deposit, Withdraw, CurrencyExchange, Transfer,
    LoanAccount, LoanAccountDeposit, LoanAccountWithdraw, LoanAccountMatch,
    LoanEntity, LoanEntityDeposit, LoanEntityWithdraw, LoanEntityMatch,
    Agency, AgencyDocumentMatch, AgencyCreditDocument, AgencyDebitDocument,
    AgencyInvoice, AgencyPayment,
    Provider, ProviderDocumentMatch, ProviderCreditDocument, ProviderDebitDocument,
    ProviderInvoice, ProviderPayment)
from finance.services import FinanceService

from functools import update_wrapper, partial

from reservas.admin import reservas_admin, ExtendedModelAdmin
from reservas.admin import bookings_site


MENU_LABEL_FINANCE_BASIC = 'Finance Basic'
MENU_LABEL_FINANCE_LOAN = 'Finance Loan'
MENU_LABEL_FINANCE_ADVANCED = 'Finance Advanced'


class IncorrectLookupParameters(Exception):
    pass


class FinantialDocumentSiteModel(SiteModel):
    readonly_model = True
    delete_allowed = False
    actions_on_top = False
    fields = ('name', 'currency', 'amount', 'date', 'status')
    list_display = ('name', 'currency', 'amount', 'date', 'status')
    #list_filter = ('currency', 'currency', 'status', 'date')
    #search_fields = ('name',)
    ordering = ['-date', 'currency', 'status']


class BaseFinantialDocumentSiteModel(FinantialDocumentSiteModel):
    readonly_model = False
    save_as = True
    readonly_fields = ('name',)


class MatchableChangeListForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance')
        if instance:
            initial = kwargs.get('initial', {})
            if instance.match_id is None:
                initial['included'] = False
                unmatched = instance.amount - instance.matched_amount
                if unmatched < instance.parent_unmatched:
                    initial['match_amount'] = unmatched
                else:
                    initial['match_amount'] = instance.parent_unmatched
            else:
                initial['included'] = True
                initial['match_amount'] = instance.match_matched_amount
            kwargs['initial'] = initial
        super(MatchableChangeListForm, self).__init__(*args, **kwargs)


class MatchableSiteModel(BaseFinantialDocumentSiteModel):
    
    change_actions = [dict(name='match', label='Match')]

    match_model = None
    match_fieldsets = None
    match_fields = []

    match_child_model = None
    match_child_model_keyfield = None
    match_related_fields = []

    match_parent_model = None
    match_model_parent_field = None
    match_model_child_field = None

    match_date_hierarchy = None
    match_list_display = []
    match_list_per_page = 100
    match_list_max_show_all = True
    match_list_select_related = []
    match_list_editable = [
        'included', 'match_amount'
    ]
    match_list_search_fields = []

    def get_changelist_form(self, request, **kwargs):
        return MatchableChangeListForm

    def do_match_saving(self):
        pass

    def get_change_tools(self):
        return [dict(name='match', label='Match', view_def=self.match_view)]

    #@csrf_protect_m
    def match_view(self, request, object_id, extra_context=None):
        return self._match_view(request, object_id, extra_context)

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

        if self.match_parent_model is None:
            formset_parent_model = self.model
        else:
            formset_parent_model = self.match_parent_model
            
        result =  modelformset_factory(
            formset_parent_model, self.get_changelist_form(request), extra=0,
            fields=self.match_list_editable, **defaults
        )
        return result

    def get_match_parent_fields(self, request, obj=None):
        if self.match_fields:
            return self.match_fields
        form = self.get_form(request, obj, fields=None)
        return list(form.base_fields) + list(self.get_readonly_fields(request, obj))

    def get_match_parent_readonly_fields(self, request, obj=None):
        result = list()
        fieldsets = self.get_match_parent_fields(request, obj)
        for fieldset in fieldsets:
            if isinstance(fieldset, six.string_types):
                result.append(fieldset)
            else:
               for field in fieldset:
                    result.append(field)
        return result

    def get_match_parent_fieldsets(self, request, obj=None):
        """
        Hook for specifying match parent fieldsets.
        """
        if self.match_fieldsets:
            return self.match_fieldsets
        return [(None, {'fields': self.get_match_parent_fields(request, obj)})]

    def build_matches(self, forms):
        result = list()
        for form in forms:
            if form.is_valid():
                included = form.cleaned_data['included']
                if included:
                    match_id = None
                    if hasattr(form.cleaned_data, 'match_id'):
                        match_id = form.cleaned_data['match_id']
                    child = form.cleaned_data[self.match_child_model_keyfield]
                    match_amount = form.cleaned_data['match_amount']
                    result.append(
                        dict(
                            match_id=match_id,
                            child=child,
                            match_amount=match_amount,
                        )
                    )
        return result

    def save_matches(self, parent, matches):
        pass

    def _match_view(self, request, object_id, extra_context=None):
        """
        The 'match list' view for this model.
        """
        from django.contrib.admin.views.main import ERROR_FLAG

        if self.match_parent_model is None:
            match_parent_sitemodel = self
        else:
            match_parent_sitemodel = self.admin_site._registry[self.match_parent_model]
 
        match_child_sitemodel = self.admin_site._registry[self.match_child_model]

        opts = match_child_sitemodel.model._meta

        # opts = self.model._meta
        app_label = opts.app_label
        if not self.has_permission(request, 'match'):
            raise PermissionDenied

        match_list_display = self.match_list_display
        match_list_display_links = match_child_sitemodel.get_list_display_links(request, match_list_display)
        match_list_filter = match_child_sitemodel.get_list_filter(request)
        match_top_filters = match_child_sitemodel.get_top_filters(request)
        match_date_hierarchy = self.match_date_hierarchy
        match_list_search_fields = self.match_list_search_fields
        match_list_select_related = self.match_list_select_related
        match_list_per_page = self.match_list_per_page
        match_list_max_show_all = self.match_list_max_show_all
        match_list_editable = self.match_list_editable

        to_field = request.POST.get(TO_FIELD_VAR, request.GET.get(TO_FIELD_VAR))

        obj = self.get_object(request, unquote(object_id), to_field)

        if not self.has_permission(request, 'match', obj):
            raise PermissionDenied

        if obj is None:
            return self._get_obj_does_not_exist_redirect(request, opts, object_id)

        MatchList = self.get_matchlist(request)
        try:
            cl = MatchList(
                request, match_list_display,
                match_list_display_links, match_list_filter, match_top_filters, match_date_hierarchy,
                match_list_search_fields, match_list_select_related, match_list_per_page,
                match_list_max_show_all, match_list_editable, match_parent_sitemodel, object_id, match_child_sitemodel
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

        # If we're allowing changelist editing, we need to construct a formset
        # for the changelist given all the fields to be edited. Then we'll
        # use the formset to validate/process POSTed data.
        formset = cl.formset = None

        # Handle POSTed bulk-edit data.
        if request.method == 'POST' and '_save' in request.POST:
            FormSet = self.get_matchlist_formset(request)
            formset = cl.formset = FormSet(request.POST, request.FILES, queryset=self.get_queryset(request))
            if formset.is_valid():
                matches = self.build_matches(formset.forms)
                try:
                    self.save_matches(obj, matches)
                    msg = "Matched successfully."
                    self.message_user(request, msg, messages.SUCCESS)
                except ValidationError as ex:
                    for message in ex.messages:
                        self.message_user(request, message, messages.ERROR)

            return HttpResponseRedirect(request.get_full_path())

        # Handle GET -- construct a formset for display.
        elif cl.list_editable:
            FormSet = self.get_matchlist_formset(request)
            formset = cl.formset = FormSet(queryset=cl.result_list)

        ModelForm = self.get_form(request, obj)

        form = ModelForm(instance=obj)
        formsets, inline_instances = self._create_formsets(request, obj, change=True)

        adminForm = helpers.AdminForm(
            form,
            list(self.get_match_parent_fieldsets(request, obj)),
            self.get_prepopulated_fields(request, obj),
            self.get_match_parent_readonly_fields(request, obj),
            model_admin=self)
        media = self.media + adminForm.media

        # Build the list of media to be used by the formset.
        if formset:
            media += self.media + formset.media
        else:
            media += self.media

        action_form = None

        selection_note_all = ungettext(
            '%(total_count)s selected',
            'All %(total_count)s selected',
            cl.result_count
        )

        ModelForm = self.get_form(request, obj)
        form = ModelForm(instance=obj)
        formsets, inline_instances = self._create_formsets(request, obj, change=True)

        context = dict(
            self.admin_site.each_context(request),
            title=_('Change %s') % force_text(opts.verbose_name),
            adminform=adminForm,
            change=True,
            object_id=object_id,
            original=obj,
            save_as=False,
            change_actions=False,
            show_save = False,
            show_save_and_continue = False,
            has_add_permission=False,
            has_change_permission=True,
            has_delete_permission=False,
            is_popup=(IS_POPUP_VAR in request.POST or
                      IS_POPUP_VAR in request.GET),
            to_field=to_field,
            media=media,
            inline_admin_formsets=[],
            errors=helpers.AdminErrorList(form, formsets),
            preserved_filters=self.get_preserved_filters(request),

            module_name=force_text(opts.verbose_name_plural),
            selection_note=_('0 of %(cnt)s selected') % {'cnt': len(cl.result_list)},
            selection_note_all=selection_note_all % {'total_count': cl.result_count},
            cl=cl,
            opts=cl.opts,
            action_form=action_form,
            actions_on_top=self.actions_on_top,
            actions_on_bottom=self.actions_on_bottom,
            actions_selection_counter=self.actions_selection_counter,
        )
        context.update(self.get_model_extra_context(request))
        context.update(extra_context or {})

        request.current_app = self.admin_site.name

        return TemplateResponse(request, 'finance/match.html', context)

    def get_matchlist(self, request, **kwargs):
        from finance.views import MatchList

        return MatchList


class DepositSiteModel(BaseFinantialDocumentSiteModel):
    model_order = 2010
    menu_label = MENU_LABEL_FINANCE_BASIC
    fields = ('name', 'account', 'amount', 'date', 'status', 'details')
    list_display = ('name', 'account', 'amount', 'date', 'status')
    top_filters = ('name', 'account', 'status', 'date')
    form = AccountingForm
    totalsum_list = ['amount']

    def save_model(self, request, obj, form, change):
        # overrides base class method
        return FinanceService.save_deposit(request.user, obj)


class WithdrawSiteModel(DepositSiteModel):
    model_order = 2020

    def save_model(self, request, obj, form, change):
        # overrides base class method
        return FinanceService.save_withdraw(request.user, obj)


class CurrencyExchangeSiteModel(BaseFinantialDocumentSiteModel):
    model_order = 2030
    menu_label = MENU_LABEL_FINANCE_BASIC
    fields = ('name', 'account', 'amount', 'date', 'status', 'exchange_account', 'exchange_amount')
    list_display = (
        'name', 'account', 'amount', 'date', 'status', 'exchange_account', 'exchange_amount')
    list_filter = ('currency', 'account', 'status', 'date')
    form = CurrencyExchangeForm

    def save_model(self, request, obj, form, change):
        # overrides base class method
        return FinanceService.save_currency_exchange(request.user, obj)


class TransferSiteModel(BaseFinantialDocumentSiteModel):
    model_order = 2040
    menu_label = MENU_LABEL_FINANCE_BASIC
    fields = ('name', 'account', 'transfer_account', 'amount', 'date', 'status')
    list_display = ('name', 'account', 'transfer_account', 'amount', 'date', 'status')
    list_filter = ('currency', 'account', 'status', 'date')
    form = TransferForm

    def save_model(self, request, obj, form, change):
        # overrides base class method
        return FinanceService.save_transfer(request.user, obj)


class LoanEntitySiteModel(SiteModel):
    model_order = 3010
    menu_label = MENU_LABEL_FINANCE_LOAN
    menu_group = 'Entity Loan'

    fields = ('name',)
    list_display = ('name',)
    list_filter = ('name',)
    search_fields = ['name',]
    ordering = ('name',)


class LoanEntityDocumentSiteModel(MatchableSiteModel):
    """
    base class for loan entities deposits and withdraws
    """
    fields = ('name', ('loan_entity', 'account'), ('amount', 'matched_amount'), ('date', 'status'))
    list_display = ['name', 'loan_entity', 'account', 'amount', 'matched_amount', 'date', 'status']
    list_filter = ('currency', 'account', 'status', 'date', 'loan_entity')

    readonly_fields = ('name', 'matched_amount',)
    form = LoanEntityDocumentForm

    match_child_model_keyfield = 'loanentitydocument_ptr'
    match_model = LoanEntityMatch
    match_fields = ('name', ('loan_entity', 'account'), ('amount', 'matched_amount'), ('date', 'status'))
    match_related_fields = ['account', 'loan_entity']
    match_list_display = [
        'name', 'included', 'match_amount'
    ]


class LoanEntityDepositSiteModel(LoanEntityDocumentSiteModel):
    """
    class for loan entity deposits
    """
    model_order = 3020
    menu_label = MENU_LABEL_FINANCE_LOAN

    match_model_parent_field = 'loan_entity_deposit'
    match_model_child_field = 'loan_entity_withdraw'
    match_child_model = LoanEntityWithdraw

    def save_model(self, request, obj, form, change):
        # overrides base class method
        return FinanceService.save_loan_entity_deposit(request.user, obj)

    def save_matches(self, parent, matches):
        # overrides base class method
        return FinanceService.match_loan_entity_document(parent, matches, True)


class LoanEntityWithdrawSiteModel(LoanEntityDocumentSiteModel):
    """
    class for loan entity withdraws
    """
    model_order = 3030
    menu_label = MENU_LABEL_FINANCE_LOAN

    match_model_parent_field = 'loan_entity_withdraw'
    match_model_child_field = 'loan_entity_deposit'
    match_child_model = LoanEntityDeposit

    def save_model(self, request, obj, form, change):
        # overrides base class method
        return FinanceService.save_loan_entity_withdraw(request.user, obj)

    def save_matches(self, parent, matches):
        # overrides base class method
        return FinanceService.match_loan_entity_document(parent, matches, False)


class LoanAccountSiteModel(SiteModel):
    model_order = 3110
    menu_label = MENU_LABEL_FINANCE_LOAN
    menu_group = 'Account Loan'

    fields = ('account', 'credit_amount', 'debit_amount', 'matched_amount')
    list_display = ('account', 'credit_amount', 'debit_amount', 'matched_amount')
    list_filter = ('account__name', 'account__currency',)
    ordering = ['account__name',]
    readonly_fields = ('credit_amount', 'debit_amount', 'matched_amount')

    form = AccountingForm


class LoanAccountDocumentSiteModel(MatchableSiteModel):
    """
    base class for loan accounts deposits and withdraws
    """
    fields = ('name', ('loan_account', 'account'), ('amount', 'matched_amount'), ('date', 'status'))
    list_display = ['name', 'loan_account', 'account', 'amount', 'matched_amount', 'date', 'status']
    list_filter = ('currency', 'account', 'status', 'date', 'loan_account')

    readonly_fields = ('name', 'matched_amount',)
    form = LoanAccountDocumentForm

    match_child_model_keyfield = 'loanaccountdocument_ptr'
    match_model = LoanAccountMatch
    match_fields = ('name', ('loan_account', 'account'), ('amount', 'matched_amount'), ('date', 'status'))
    match_related_fields = ['account', 'loan_account']
    match_list_display = [
        'name', 'included', 'match_amount'
    ]


class LoanAccountDepositSiteModel(LoanAccountDocumentSiteModel):
    """
    class for loan account deposits
    """
    model_order = 3120
    menu_label = MENU_LABEL_FINANCE_LOAN

    match_model_parent_field = 'loan_account_deposit'
    match_model_child_field = 'loan_account_withdraw'
    match_child_model = LoanAccountWithdraw

    def save_model(self, request, obj, form, change):
        # overrides base class method
        return FinanceService.save_loan_account_deposit(request.user, obj)

    def save_matches(self, parent, matches):
        # overrides base class method
        return FinanceService.match_loan_account_document(parent, matches, True)


class LoanAccountWithdrawSiteModel(LoanAccountDocumentSiteModel):
    """
    class for loan account withdraws
    """
    model_order = 3130
    menu_label = MENU_LABEL_FINANCE_LOAN

    match_model_parent_field = 'loan_account_withdraw'
    match_model_child_field = 'loan_account_deposit'
    match_child_model = LoanAccountDeposit

    def save_model(self, request, obj, form, change):
        # overrides base class method
        return FinanceService.save_loan_account_withdraw(request.user, obj)

    def save_matches(self, parent, matches):
        # overrides base class method
        return FinanceService.match_loan_account_document(parent, matches, False)


class OfficeSiteModel(SiteModel):
    model_order = 4010
    menu_label = MENU_LABEL_FINANCE_ADVANCED
    fields = ('name', 'logo', 'address', 'detail1', 'detail2')
    list_display = ('name', 'logo', 'address')


class ProviderSiteModel(SiteModel):
    model_order = 4110
    menu_label = MENU_LABEL_FINANCE_ADVANCED
    menu_group = 'Finace Provider'
    list_display = ('name', 'email', 'phone',
                    'currency', 'enabled')
    # list_filter = ('name', 'currency', 'enabled')
    top_filters = ['name', 'email']
    ordering = ('enabled', 'currency', 'name')


class ProviderDocumentSiteModel(MatchableSiteModel):
    """
    class for provider documents
    """
    fields = ('name', 'provider', 'currency','amount', 'matched_amount', 'date', 'status')
    list_display = ['name', 'provider', 'currency', 'amount', 'matched_amount', 'date', 'status']
    top_filters = ('currency', 'provider', 'status', 'date')

    readonly_fields = ('name', 'matched_amount',)

    form = ProviderDocumentForm

    match_model = ProviderDocumentMatch
    match_fields = ('name', ('provider', 'currency'), ('amount', 'matched_amount'), ('date', 'status'))
    match_related_fields = ['provider', 'currency']
    match_list_display = [
        'name', 'included', 'match_amount'
    ]


class ProviderDebitDocumentSiteModel(ProviderDocumentSiteModel):
    """
    class for provider debit documents
    """
    match_model_parent_field = 'debit_document'
    match_model_child_field = 'credit_document'
    match_parent_model = ProviderDebitDocument
    match_child_model = ProviderCreditDocument
    match_child_model_keyfield = 'providerdocument_ptr'


class ProviderCreditDocumentSiteModel(ProviderDocumentSiteModel):
    """
    class for provider credit documents
    """
    match_model_parent_field = 'credit_document'
    match_model_child_field = 'debit_document'
    match_parent_model = ProviderCreditDocument
    match_child_model = ProviderDebitDocument
    match_child_model_keyfield = 'providerdocument_ptr'


class ProviderInvoiceSiteModel(ProviderDebitDocumentSiteModel):
    """
    class for provider invoices
    """
    model_order = 4120
    menu_label = MENU_LABEL_FINANCE_ADVANCED

    def save_model(self, request, obj, form, change):
        # overrides base class method
        return FinanceService.save_provider_invoice(request.user, obj)

    def save_matches(self, parent, matches):
        # overrides base class method
        return FinanceService.match_provider_document(parent, matches, False)


class ProviderPaymentSiteModel(ProviderCreditDocumentSiteModel):
    """
    class for provider payments
    """
    model_order = 4130
    menu_label = MENU_LABEL_FINANCE_ADVANCED

    def save_model(self, request, obj, form, change):
        # overrides base class method
        return FinanceService.save_provider_payment(request.user, obj)

    def save_matches(self, parent, matches):
        # overrides base class method
        return FinanceService.match_provider_document(parent, matches, True)


class AgencySiteModel(SiteModel):
    model_order = 4210
    menu_label = MENU_LABEL_FINANCE_ADVANCED
    menu_group = 'Finace Agency'
    list_display = ('name', 'currency', 'enabled')
    list_filter = ('name', 'currency', 'enabled')
    search_fields = ['name']
    ordering = ('enabled', 'currency', 'name')


class AgencyDocumentSiteModel(MatchableSiteModel):
    """
    class for agency documents
    """
    fields = ('name', 'agency', 'currency','amount', 'matched_amount', 'date', 'status')
    list_display = ['name', 'agency', 'currency', 'amount', 'matched_amount', 'date', 'status']
    top_filters = ('currency', 'agency', 'status', 'date')

    readonly_fields = ('name', 'matched_amount',)
    form = AgencyDocumentForm

    match_model = AgencyDocumentMatch
    match_fields = ('name', ('agency', 'currency'), ('amount', 'matched_amount'), ('date', 'status'))
    match_related_fields = ['agency', 'currency']
    match_list_display = [
        'name', 'included', 'match_amount', 'agencydocument_ptr'
    ]


class AgencyDebitDocumentSiteModel(AgencyDocumentSiteModel):
    """
    class for agency debit documents
    """
    match_model_parent_field = 'debit_document'
    match_model_child_field = 'credit_document'
    match_child_model = AgencyCreditDocument
    match_child_model_keyfield = 'agencydocument_ptr'


class AgencyCreditDocumentSiteModel(AgencyDocumentSiteModel):
    """
    class for agency credit documents
    """
    match_model_parent_field = 'credit_document'
    match_model_child_field = 'debit_document'
    match_child_model = AgencyDebitDocument
    match_child_model_keyfield = 'agencydocument_ptr'


class AgencyInvoiceSiteModel(MatchableSiteModel):
    """
    class for agency invoices
    """
    model_order = 4220
    menu_label = MENU_LABEL_FINANCE_ADVANCED

    def save_model(self, request, obj, form, change):
        # overrides base class method
        return FinanceService.save_agency_invoice(request.user, obj)

    def save_matches(self, parent, matches):
        # overrides base class method
        return FinanceService.match_agency_document(parent, matches, False)


class AgencyPaymentSiteModel(MatchableSiteModel):
    """
    class for agency payments
    """
    model_order = 4230
    menu_label = MENU_LABEL_FINANCE_ADVANCED

    def save_model(self, request, obj, form, change):
        # overrides base class method
        return FinanceService.save_agency_payment(request.user, obj)

    def save_matches(self, parent, matches):
        # overrides base class method
        return FinanceService.match_agency_document(parent, matches, True)


bookings_site.register(Deposit, DepositSiteModel)
bookings_site.register(Withdraw, WithdrawSiteModel)
bookings_site.register(CurrencyExchange, CurrencyExchangeSiteModel)
bookings_site.register(Transfer, TransferSiteModel)

bookings_site.register(LoanEntity, LoanEntitySiteModel)
bookings_site.register(LoanEntityDeposit, LoanEntityDepositSiteModel)
bookings_site.register(LoanEntityWithdraw, LoanEntityWithdrawSiteModel)
bookings_site.register(LoanAccount, LoanAccountSiteModel)
bookings_site.register(LoanAccountDeposit, LoanAccountDepositSiteModel)
bookings_site.register(LoanAccountWithdraw, LoanAccountWithdrawSiteModel)

bookings_site.register(Office, OfficeSiteModel)

bookings_site.register(Provider, ProviderSiteModel)
bookings_site.register(ProviderCreditDocument, ProviderCreditDocumentSiteModel)
bookings_site.register(ProviderDebitDocument, ProviderDebitDocumentSiteModel)
bookings_site.register(ProviderPayment, ProviderPaymentSiteModel)
bookings_site.register(ProviderInvoice, ProviderInvoiceSiteModel)

bookings_site.register(Agency, AgencySiteModel)
bookings_site.register(AgencyCreditDocument, AgencyCreditDocumentSiteModel)
bookings_site.register(AgencyDebitDocument, AgencyDebitDocumentSiteModel)
bookings_site.register(AgencyPayment, AgencyPaymentSiteModel)
bookings_site.register(AgencyInvoice, AgencyInvoiceSiteModel)
