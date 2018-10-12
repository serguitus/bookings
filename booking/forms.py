from dal import autocomplete

from booking.models import Booking, BookingAllotment, BookingTransfer, BookingExtra
from django import forms


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ('__all__')
        widgets = {
            'agency': autocomplete.ModelSelect2(url='agency-autocomplete'),
        }


class BookingAllotmentForm(forms.ModelForm):
    class Meta:
        model = BookingAllotment
        fields = ('__all__')
        widgets = {
            'provider': autocomplete.ModelSelect2(url='provider-autocomplete'),
            'service': autocomplete.ModelSelect2(url='allotment-autocomplete'),
            'room_type': autocomplete.ModelSelect2(url='roomtype-autocomplete'),
        }


class BookingTransferForm(forms.ModelForm):
    class Meta:
        model = BookingTransfer
        fields = ('__all__')
        widgets = {
            'provider': autocomplete.ModelSelect2(url='provider-autocomplete'),
            'service': autocomplete.ModelSelect2(url='transfer-autocomplete'),
            'location_from': autocomplete.ModelSelect2(url='location-autocomplete'),
            'location_to': autocomplete.ModelSelect2(url='location-autocomplete'),
        }


class BookingExtraForm(forms.ModelForm):
    class Meta:
        model = BookingExtra
        fields = ('__all__')
        widgets = {
            'provider': autocomplete.ModelSelect2(url='provider-autocomplete'),
            'service': autocomplete.ModelSelect2(url='extra-autocomplete'),
        }
