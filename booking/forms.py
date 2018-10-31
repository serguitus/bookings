from dal import autocomplete

from booking.models import (
    Order, OrderAllotment, OrderTransfer, OrderExtra,
    Booking, BookingAllotment, BookingTransfer, BookingExtra)
from django import forms


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ('__all__')
        widgets = {
            'agency': autocomplete.ModelSelect2(url='agency-autocomplete'),
        }


class OrderAllotmentInlineForm(forms.ModelForm):
    class Meta:
        fields = ('__all__')
        widgets = {
            'service': autocomplete.ModelSelect2(url='allotment-autocomplete'),
            'provider': autocomplete.ModelSelect2(url='provider-autocomplete'),
            'room_type': autocomplete.ModelSelect2(url='roomtype-autocomplete'),
        }


class OrderAllotmentForm(forms.ModelForm):
    class Meta:
        model = OrderAllotment
        fields = '__all__'
        widgets = {
            'provider': autocomplete.ModelSelect2(url='provider-autocomplete'),
            'service': autocomplete.ModelSelect2(url='allotment-autocomplete'),
            'room_type': autocomplete.ModelSelect2(url='roomtype-autocomplete'),
        }
    id = forms.CharField(widget=forms.HiddenInput())


class OrderTransferInlineForm(forms.ModelForm):
    class Meta:
        fields = ('__all__')
        widgets = {
            'service': autocomplete.ModelSelect2(url='transfer-autocomplete'),
            'provider': autocomplete.ModelSelect2(url='provider-autocomplete'),
            'location_from': autocomplete.ModelSelect2(url='location-autocomplete'),
            'location_to': autocomplete.ModelSelect2(url='location-autocomplete'),
        }


class OrderTransferForm(forms.ModelForm):
    class Meta:
        model = OrderTransfer
        fields = ('__all__')
        widgets = {
            'provider': autocomplete.ModelSelect2(url='provider-autocomplete'),
            'service': autocomplete.ModelSelect2(url='transfer-autocomplete'),
            'location_from': autocomplete.ModelSelect2(url='location-autocomplete'),
            'location_to': autocomplete.ModelSelect2(url='location-autocomplete'),
        }
    id = forms.CharField(widget=forms.HiddenInput())


class OrderExtraInlineForm(forms.ModelForm):
    class Meta:
        fields = ('__all__')
        widgets = {
            'service': autocomplete.ModelSelect2(url='extra-autocomplete'),
            'provider': autocomplete.ModelSelect2(url='provider-autocomplete'),
        }


class OrderExtraForm(forms.ModelForm):
    class Meta:
        model = OrderExtra
        fields = ('__all__')
        widgets = {
            'provider': autocomplete.ModelSelect2(url='provider-autocomplete'),
            'service': autocomplete.ModelSelect2(url='extra-autocomplete'),
        }
    id = forms.CharField(widget=forms.HiddenInput())


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
    id = forms.CharField(widget=forms.HiddenInput())


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
    id = forms.CharField(widget=forms.HiddenInput())


class BookingExtraForm(forms.ModelForm):
    class Meta:
        model = BookingExtra
        fields = ('__all__')
        widgets = {
            'provider': autocomplete.ModelSelect2(url='provider-autocomplete'),
            'service': autocomplete.ModelSelect2(url='extra-autocomplete'),
        }
    id = forms.CharField(widget=forms.HiddenInput())
