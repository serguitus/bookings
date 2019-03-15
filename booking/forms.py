from dal import autocomplete
from django.forms import widgets

from booking.models import (
    PackageAllotment, PackageTransfer, PackageExtra,
    Quote, QuoteAllotment, QuoteTransfer, QuoteExtra, QuotePackage,
    QuotePackageAllotment, QuotePackageTransfer, QuotePackageExtra,
    Booking, BookingServicePax, BookingAllotment, BookingTransfer, BookingExtra)
from finance.models import Office
from django import forms


class QuoteForm(forms.ModelForm):
    class Meta:
        model = Quote
        fields = ('__all__')
        widgets = {
            'agency': autocomplete.ModelSelect2(url='agency-autocomplete'),
        }


class PackageAllotmentInlineForm(forms.ModelForm):
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


class PackageTransferInlineForm(forms.ModelForm):
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


class PackageExtraInlineForm(forms.ModelForm):
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


class PackageAllotmentForm(forms.ModelForm):
    class Meta:
        model = PackageAllotment
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


class PackageTransferForm(forms.ModelForm):
    class Meta:
        model = PackageTransfer
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


class PackageExtraForm(forms.ModelForm):
    class Meta:
        model = PackageExtra
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


class QuotePackageAllotmentInlineForm(forms.ModelForm):
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


class QuotePackageAllotmentForm(forms.ModelForm):
    class Meta:
        model = QuotePackageAllotment
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


class QuotePackageTransferInlineForm(forms.ModelForm):
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


class QuotePackageTransferForm(forms.ModelForm):
    class Meta:
        model = QuotePackageTransfer
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


class QuotePackageExtraInlineForm(forms.ModelForm):
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


class QuotePackageExtraForm(forms.ModelForm):
    class Meta:
        model = QuotePackageExtra
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


class QuotePackageInlineForm(forms.ModelForm):
    class Meta:
        fields = ('__all__')
        widgets = {
            'service': autocomplete.ModelSelect2(url='package-autocomplete'),
            'provider': autocomplete.ModelSelect2(
                url='providerpackage-autocomplete',
                forward=['service'],
                ),
        }


class QuotePackageForm(forms.ModelForm):
    class Meta:
        model = QuotePackage
        fields = ('__all__')
        widgets = {
            'service': autocomplete.ModelSelect2(url='package-autocomplete'),
            'provider': autocomplete.ModelSelect2(
                url='providerpackage-autocomplete',
                forward=['service'],
                ),
        }
    id = forms.CharField(required=False, widget=forms.HiddenInput())


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ('__all__')
        widgets = {
            'agency': autocomplete.ModelSelect2(url='agency-autocomplete'),
            'p_notes': widgets.Textarea(attrs={'cols': 120, 'rows': 4}),
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


class VouchersConfigForm(forms.Form):
    # states = forms.ChoiceField(settings.ESTADOS)
    # this helps to point back to current booking
    # referer = forms.HiddenInput()
    # the list of selected services to make vouchers from
    # id = forms.MultiValueField()
    # here comes also some inputs to select logo and other details
    office = forms.ModelChoiceField(queryset=Office.objects.all())
    # extra = forms.CharField()
