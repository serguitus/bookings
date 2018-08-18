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
        widgets = {
            'account': autocomplete.ModelSelect2(url='account-autocomplete'),
            'exchange_account': autocomplete.ModelSelect2(url='account-autocomplete'),
        }


class TransferForm(AccountingForm):
    class Meta:
        widgets = {
            'account': autocomplete.ModelSelect2(url='account-autocomplete'),
            'transfer_account': autocomplete.ModelSelect2(url='account-autocomplete'),
        }

class LoanEntityDocumentForm(AccountingForm):
    class Meta:
        widgets = {
            'account': autocomplete.ModelSelect2(url='account-autocomplete'),
            'loan_entity': autocomplete.ModelSelect2(url='loanentity-autocomplete'),
        }

class LoanAccountDocumentForm(AccountingForm):
    class Meta:
        widgets = {
            'account': autocomplete.ModelSelect2(url='account-autocomplete'),
            'loan_account': autocomplete.ModelSelect2(url='loanaccount-autocomplete'),
        }
