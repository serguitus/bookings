from dal import autocomplete

from django import forms

from finance.models import Deposit


class AllotmentRoomTypeInlineForm(forms.ModelForm):
    class Meta:
        fields = ('__all__')
        widgets = {
            'room_type': autocomplete.ModelSelect2(url='roomtype-autocomplete'),
        }

class TransferForm(forms.ModelForm):
    class Meta:
        fields = ('__all__')
        widgets = {
            'location_from': autocomplete.ModelSelect2(url='location-autocomplete'),
            'location_to': autocomplete.ModelSelect2(url='location-autocomplete'),
        }
