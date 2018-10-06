from dal import autocomplete

from booking.models import BookingService
from django import forms


class BookingServiceForm(forms.ModelForm):
    class Meta:
        model = BookingService
        fields = ('__all__')
        widgets = {
            'provider': autocomplete.ModelSelect2(url='provider-autocomplete')
        }
