from dal import autocomplete

from django import forms

from finance.models import Deposit


class DepositForm(forms.ModelForm):
    class Meta:
        model = Deposit
        fields = ('__all__')
        widgets = {
            'account': autocomplete.ModelSelect2(url='account-autocomplete')
        }