# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from dal import autocomplete

from django import forms

from finance.models import Deposit


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
        }
