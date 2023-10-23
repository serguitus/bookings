# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from ckeditor.widgets import CKEditorWidget

from dal import autocomplete

from django import forms


class AccountingForm(forms.ModelForm):
    class Meta:
        fields = ('__all__')
        widgets = {
            'account': autocomplete.ModelSelect2(url='account-autocomplete'),
        }


class CurrencyExchangeForm(AccountingForm):
    class Meta:
        fields = ('__all__')
        widgets = {
            'account': autocomplete.ModelSelect2(url='account-autocomplete'),
            'exchange_account': autocomplete.ModelSelect2(url='account-autocomplete'),
        }


class TransferForm(AccountingForm):
    class Meta:
        fields = ('__all__')
        widgets = {
            'account': autocomplete.ModelSelect2(url='account-autocomplete'),
            'transfer_account': autocomplete.ModelSelect2(url='account-autocomplete'),
        }


class LoanEntityDocumentForm(AccountingForm):
    class Meta:
        fields = ('__all__')
        widgets = {
            'account': autocomplete.ModelSelect2(url='account-autocomplete'),
            'loan_entity': autocomplete.ModelSelect2(url='loanentity-autocomplete'),
        }


class LoanAccountDocumentForm(AccountingForm):
    class Meta:
        fields = ('__all__')
        widgets = {
            'account': autocomplete.ModelSelect2(url='account-autocomplete'),
            'loan_account': autocomplete.ModelSelect2(url='loanaccount-autocomplete'),
        }


class ProviderDocumentForm(forms.ModelForm):
    class Meta:
        fields = ('__all__')
        widgets = {
            'provider': autocomplete.ModelSelect2(url='provider-autocomplete'),
        }


class AgencyDocumentForm(forms.ModelForm):
    class Meta:
        fields = ('__all__')
        widgets = {
            'agency': autocomplete.ModelSelect2(url='agency-autocomplete'),
            'account': autocomplete.ModelSelect2(url='account-autocomplete'),
        }


class OfficeForm(forms.ModelForm):
    class Meta:
        fields = ('__all__')
        widgets = {
            'bank_details': CKEditorWidget(attrs={'class': 'form-control'})
        }


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
