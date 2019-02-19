from dal import autocomplete

from booking.models import (
    Quote, QuoteAllotment, QuoteTransfer, QuoteExtra,
    Booking, BookingServicePax, BookingAllotment, BookingTransfer, BookingExtra)
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
            'room_type': autocomplete.ModelSelect2(
                url='roomtype-autocomplete',
                forward=['service'],
                ),
            'board_type': autocomplete.ListSelect2(
                url='boardtype-autocomplete',
                forward=['service']),
            'provider': autocomplete.ModelSelect2(
                url='providerallotment-autocomplete',
                forward=['service', 'room_type', 'board_type'],
                ),
        }


class QuoteAllotmentForm(forms.ModelForm):
    class Meta:
        model = QuoteAllotment
        fields = '__all__'
        widgets = {
            'service': autocomplete.ModelSelect2(url='allotment-autocomplete'),
            'room_type': autocomplete.ModelSelect2(
                url='roomtype-autocomplete',
                forward=['service'],
                ),
            'board_type': autocomplete.ListSelect2(
                url='boardtype-autocomplete',
                forward=['service']),
            'provider': autocomplete.ModelSelect2(
                url='providerallotment-autocomplete',
                forward=['service', 'room_type', 'board_type'],
                ),
        }
    id = forms.CharField(required=False, widget=forms.HiddenInput())


class QuoteTransferInlineForm(forms.ModelForm):
    class Meta:
        fields = ('__all__')
        widgets = {
            'service': autocomplete.ModelSelect2(url='transfer-autocomplete'),
            'location_from': autocomplete.ModelSelect2(url='location-autocomplete'),
            'location_to': autocomplete.ModelSelect2(url='location-autocomplete'),
            'provider': autocomplete.ModelSelect2(
                url='providertransfer-autocomplete',
                forward=['service', 'location_from', 'location_to'],
                ),
        }


class QuoteTransferForm(forms.ModelForm):
    class Meta:
        model = QuoteTransfer
        fields = ('__all__')
        widgets = {
            'service': autocomplete.ModelSelect2(url='transfer-autocomplete'),
            'location_from': autocomplete.ModelSelect2(url='location-autocomplete'),
            'location_to': autocomplete.ModelSelect2(url='location-autocomplete'),
            'provider': autocomplete.ModelSelect2(
                url='providertransfer-autocomplete',
                forward=['service', 'location_from', 'location_to'],
                ),
        }
    id = forms.CharField(required=False, widget=forms.HiddenInput())


class QuoteExtraInlineForm(forms.ModelForm):
    class Meta:
        fields = ('__all__')
        widgets = {
            'service': autocomplete.ModelSelect2(url='extra-autocomplete'),
            'addon': autocomplete.ModelSelect2(
                url='addon-autocomplete',
                forward=['service'],
                ),
            'provider': autocomplete.ModelSelect2(
                url='providerextra-autocomplete',
                forward=['service', 'addon'],
                ),
        }


class QuoteExtraForm(forms.ModelForm):
    class Meta:
        model = QuoteExtra
        fields = ('__all__')
        widgets = {
            'service': autocomplete.ModelSelect2(url='extra-autocomplete'),
            'addon': autocomplete.ModelSelect2(
                url='addon-autocomplete',
                forward=['service'],
                ),
            'provider': autocomplete.ModelSelect2(
                url='providerextra-autocomplete',
                forward=['service', 'addon'],
                ),
        }
    id = forms.CharField(required=False, widget=forms.HiddenInput())


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ('__all__')
        widgets = {
            'agency': autocomplete.ModelSelect2(url='agency-autocomplete'),
        }


class BookingServicePaxInlineForm(forms.ModelForm):
    class Meta:
        fields = '__all__'
        widgets = {
            'booking_pax': autocomplete.ModelSelect2(
                url='bookingpax-autocomplete',
                forward=['booking', 'booking_service']),
        }


class BookingAllotmentInlineForm(forms.ModelForm):
    class Meta:
        fields = '__all__'
        widgets = {
            'service': autocomplete.ModelSelect2(url='allotment-autocomplete'),
            'room_type': autocomplete.ModelSelect2(
                url='roomtype-autocomplete',
                forward=['service'],
                ),
            'board_type': autocomplete.ListSelect2(
                url='boardtype-autocomplete',
                forward=['service']),
            'provider': autocomplete.ModelSelect2(
                url='providerallotment-autocomplete',
                forward=['service', 'room_type', 'board_type'],
                ),
        }


class BookingAllotmentForm(forms.ModelForm):
    class Meta:
        model = BookingAllotment
        fields = '__all__'
        widgets = {
            'service': autocomplete.ModelSelect2(url='allotment-autocomplete'),
            'room_type': autocomplete.ModelSelect2(
                url='roomtype-autocomplete',
                forward=['service'],
                ),
            'board_type': autocomplete.ListSelect2(
                url='boardtype-autocomplete',
                forward=['service']),
            'provider': autocomplete.ModelSelect2(
                url='providerallotment-autocomplete',
                forward=['service', 'room_type', 'board_type'],
                ),
        }
    id = forms.CharField(required=False, widget=forms.HiddenInput())


class BookingTransferInlineForm(forms.ModelForm):
    class Meta:
        fields = ('__all__')
        widgets = {
            'service': autocomplete.ModelSelect2(url='transfer-autocomplete'),
            'location_from': autocomplete.ModelSelect2(url='location-autocomplete'),
            'pickup': autocomplete.ModelSelect2(
                url='pickup-autocomplete',
                forward=['location_from', 'service'],
                ),
            'location_to': autocomplete.ModelSelect2(url='location-autocomplete'),
            'dropoff': autocomplete.ModelSelect2(
                url='dropoff-autocomplete',
                forward=['location_to', 'service'],
                ),
            'provider': autocomplete.ModelSelect2(
                url='providertransfer-autocomplete',
                forward=['service', 'location_from', 'location_to'],
                ),
        }


class BookingTransferForm(forms.ModelForm):
    class Meta:
        model = BookingTransfer
        fields = ('__all__')
        widgets = {
            'service': autocomplete.ModelSelect2(url='transfer-autocomplete'),
            'location_from': autocomplete.ModelSelect2(url='location-autocomplete'),
            'place_from': autocomplete.ModelSelect2(
                url='place-autocomplete',
                forward=['location_from'],
                ),
            'pickup': autocomplete.ModelSelect2(
                url='pickup-autocomplete',
                forward=['location_from', 'service'],
                ),
            'schedule_from': autocomplete.ModelSelect2(
                url='arrival-autocomplete',
                forward=['location_from'],
                ),
            'location_to': autocomplete.ModelSelect2(url='location-autocomplete'),
            'place_to': autocomplete.ModelSelect2(
                url='place-autocomplete',
                forward=['location_to'],
                ),
            'dropoff': autocomplete.ModelSelect2(
                url='dropoff-autocomplete',
                forward=['location_to', 'service'],
                ),
            'schedule_to': autocomplete.ModelSelect2(
                url='departure-autocomplete',
                forward=['location_to'],
                ),
            'provider': autocomplete.ModelSelect2(
                url='providertransfer-autocomplete',
                forward=['service', 'location_from', 'location_to'],
                ),
        }
    id = forms.CharField(required=False, widget=forms.HiddenInput())


class BookingExtraInlineForm(forms.ModelForm):
    class Meta:
        fields = ('__all__')
        widgets = {
            'service': autocomplete.ModelSelect2(url='extra-autocomplete'),
            'addon': autocomplete.ModelSelect2(
                url='addon-autocomplete',
                forward=['service'],
                ),
            'provider': autocomplete.ModelSelect2(
                url='providerextra-autocomplete',
                forward=['service', 'addon'],
                ),
        }


class BookingExtraForm(forms.ModelForm):
    class Meta:
        model = BookingExtra
        fields = ('__all__')
        widgets = {
            'service': autocomplete.ModelSelect2(url='extra-autocomplete'),
            'addon': autocomplete.ModelSelect2(
                url='addon-autocomplete',
                forward=['service'],
                ),
            'provider': autocomplete.ModelSelect2(
                url='providerextra-autocomplete',
                forward=['service', 'addon'],
                ),
        }
    id = forms.CharField(required=False, widget=forms.HiddenInput())


from django.forms import widgets
class EmailProviderForm(forms.Form):
    from_address = forms.EmailField(
        label='From',
        widget=widgets.TextInput(
            attrs={'class': 'form-control'})
    )
    to_address = forms.EmailField(
        label='To',
        widget=widgets.TextInput(
            attrs={'class': 'form-control'})
    )
    cc_address = forms.EmailField(
        label='CC',
        widget=widgets.TextInput(
            attrs={'class': 'form-control'})
    )
    bcc_address = forms.EmailField(
        label='BCC',
        widget=widgets.TextInput(
            attrs={'class': 'form-control'})
    )
    subject = forms.CharField(
        max_length=100,
        label='Subject',
        widget=widgets.TextInput(
            attrs={'class': 'form-control'}))
    body = forms.CharField(
        max_length=1000,
        label='Body',
        widget=widgets.Textarea(
            attrs={'class': 'form-control'}))

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(EmailProviderForm, self).__init__(*args, **kwargs)
        self.initial['from_address'] = self.user.email
