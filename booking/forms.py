from dal import autocomplete

from booking.models import (
    Quote, QuoteAllotment, QuoteTransfer, QuoteExtra,
    Booking, BookingAllotment, BookingTransfer, BookingExtra)
from django import forms


class QuoteForm(forms.ModelForm):
    class Meta:
        model = Quote
        fields = ('__all__')
        widgets = {
            'agency': autocomplete.ModelSelect2(url='agency-autocomplete'),
        }


class QuoteAllotmentInlineForm(forms.ModelForm):
    class Meta:
        fields = ('__all__')
        widgets = {
            'service': autocomplete.ModelSelect2(url='allotment-autocomplete'),
            'provider': autocomplete.ModelSelect2(url='provider-autocomplete'),
            'room_type': autocomplete.ModelSelect2(url='roomtype-autocomplete'),
        }


class QuoteAllotmentForm(forms.ModelForm):
    class Meta:
        model = QuoteAllotment
        fields = '__all__'
        widgets = {
            'provider': autocomplete.ModelSelect2(url='provider-autocomplete'),
            'service': autocomplete.ModelSelect2(url='allotment-autocomplete'),
            'room_type': autocomplete.ModelSelect2(url='roomtype-autocomplete'),
        }
    id = forms.CharField(required=False, widget=forms.HiddenInput())


class QuoteTransferInlineForm(forms.ModelForm):
    class Meta:
        fields = ('__all__')
        widgets = {
            'service': autocomplete.ModelSelect2(url='transfer-autocomplete'),
            'provider': autocomplete.ModelSelect2(url='provider-autocomplete'),
            'location_from': autocomplete.ModelSelect2(url='location-autocomplete'),
            'location_to': autocomplete.ModelSelect2(url='location-autocomplete'),
        }


class QuoteTransferForm(forms.ModelForm):
    class Meta:
        model = QuoteTransfer
        fields = ('__all__')
        widgets = {
            'provider': autocomplete.ModelSelect2(url='provider-autocomplete'),
            'service': autocomplete.ModelSelect2(url='transfer-autocomplete'),
            'location_from': autocomplete.ModelSelect2(url='location-autocomplete'),
            'location_to': autocomplete.ModelSelect2(url='location-autocomplete'),
        }
    id = forms.CharField(required=False, widget=forms.HiddenInput())


class QuoteExtraInlineForm(forms.ModelForm):
    class Meta:
        fields = ('__all__')
        widgets = {
            'service': autocomplete.ModelSelect2(url='extra-autocomplete'),
            'provider': autocomplete.ModelSelect2(url='provider-autocomplete'),
        }


class QuoteExtraForm(forms.ModelForm):
    class Meta:
        model = QuoteExtra
        fields = ('__all__')
        widgets = {
            'provider': autocomplete.ModelSelect2(url='provider-autocomplete'),
            'service': autocomplete.ModelSelect2(url='extra-autocomplete'),
        }
    id = forms.CharField(required=False, widget=forms.HiddenInput())


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
        fields = '__all__'
        widgets = {
            'provider': autocomplete.ModelSelect2(url='provider-autocomplete'),
            'service': autocomplete.ModelSelect2(url='allotment-autocomplete'),
            'room_type': autocomplete.ModelSelect2(url='roomtype-autocomplete'),
        }
    id = forms.CharField(required=False, widget=forms.HiddenInput())


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
    id = forms.CharField(required=False, widget=forms.HiddenInput())


class BookingExtraForm(forms.ModelForm):
    class Meta:
        model = BookingExtra
        fields = ('__all__')
        widgets = {
            'provider': autocomplete.ModelSelect2(url='provider-autocomplete'),
            'service': autocomplete.ModelSelect2(url='extra-autocomplete'),
        }
    id = forms.CharField(required=False, widget=forms.HiddenInput())
