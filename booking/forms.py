# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from ckeditor.widgets import CKEditorWidget
from dal import autocomplete
from django.forms import widgets

from booking.models import (
    Package,
    PackageAllotment, PackageTransfer, PackageExtra,
    PackageProvider, AgencyPackageService,
    Quote, QuoteAllotment, QuoteTransfer, QuoteExtra, QuotePackage,
    QuotePackageAllotment, QuotePackageTransfer, QuotePackageExtra,
    Booking, BookingServicePax, BookingAllotment, BookingTransfer, BookingExtra, BookingPackage,
    BookingPackageAllotment, BookingPackageTransfer, BookingPackageExtra,
    ProviderBookingPayment,
)
from finance.models import Office
from django import forms


class QuoteForm(forms.ModelForm):
    class Meta:
        model = Quote
        fields = ('__all__')
        widgets = {
            'agency': autocomplete.ModelSelect2(url='agency-autocomplete'),
        }
    id = forms.CharField(required=False, widget=forms.HiddenInput())


class PackageAllotmentInlineForm(forms.ModelForm):
    class Meta:
        fields = ('__all__')
        widgets = {
            'service': autocomplete.ModelSelect2(
                url='serviceallotment-autocomplete',
                forward=['provider'],
                ),
            'room_type': autocomplete.ModelSelect2(
                url='roomtype-autocomplete',
                forward=['service'],
                ),
            'board_type': autocomplete.ListSelect2(
                url='boardtype-autocomplete',
                forward=['service']),
            'service_addon': autocomplete.ModelSelect2(
                url='addon-autocomplete',
                forward=['service'],
                ),
            'provider': autocomplete.ModelSelect2(
                url='providerallotment-autocomplete',
                forward=['service', 'room_type', 'board_type', 'service_addon'],
                ),
        }


class PackageTransferInlineForm(forms.ModelForm):
    class Meta:
        fields = ('__all__')
        widgets = {
            'service': autocomplete.ModelSelect2(
                url='servicetransfer-autocomplete',
                forward=['provider'],
                ),
            'location_from': autocomplete.ModelSelect2(url='location-autocomplete'),
            'location_to': autocomplete.ModelSelect2(url='location-autocomplete'),
            'service_addon': autocomplete.ModelSelect2(
                url='addon-autocomplete',
                forward=['service'],
                ),
            'provider': autocomplete.ModelSelect2(
                url='providertransfer-autocomplete',
                forward=['service', 'location_from', 'location_to', 'service_addon'],
                ),
        }


class PackageExtraInlineForm(forms.ModelForm):
    class Meta:
        fields = ('__all__')
        widgets = {
            'service': autocomplete.ModelSelect2(
                url='serviceextra-autocomplete',
                forward=['provider'],
                ),
            'addon': autocomplete.ModelSelect2(
                url='addon-autocomplete',
                forward=['service'],
                ),
            'service_addon': autocomplete.ModelSelect2(
                url='addon-autocomplete',
                forward=['service'],
                ),
            'provider': autocomplete.ModelSelect2(
                url='providerextra-autocomplete',
                forward=['service', 'service_addon'],
                ),
            'pickup_office': autocomplete.ModelSelect2(
                url='carrentaloffice-autocomplete',
                forward=['service',],
                ),
            'dropoff_office': autocomplete.ModelSelect2(
                url='carrentaloffice-autocomplete',
                forward=['service',],
                ),
        }


class PackageAllotmentForm(forms.ModelForm):
    class Meta:
        model = PackageAllotment
        fields = '__all__'
        widgets = {
            'service': autocomplete.ModelSelect2(
                url='serviceallotment-autocomplete',
                forward=['provider'],
                ),
            'room_type': autocomplete.ModelSelect2(
                url='roomtype-autocomplete',
                forward=['service'],
                ),
            'board_type': autocomplete.ListSelect2(
                url='boardtype-autocomplete',
                forward=['service']),
            'service_addon': autocomplete.ModelSelect2(
                url='addon-autocomplete',
                forward=['service'],
                ),
            'provider': autocomplete.ModelSelect2(
                url='providerallotment-autocomplete',
                forward=['service', 'room_type', 'board_type', 'service_addon'],
                ),
        }
    id = forms.CharField(required=False, widget=forms.HiddenInput())


class PackageTransferForm(forms.ModelForm):
    class Meta:
        model = PackageTransfer
        fields = ('__all__')
        widgets = {
            'service': autocomplete.ModelSelect2(
                url='servicetransfer-autocomplete',
                forward=['provider'],
                ),
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
                forward=['service', 'location_from'],
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
            'service_addon': autocomplete.ModelSelect2(
                url='addon-autocomplete',
                forward=['service'],
                ),
            'provider': autocomplete.ModelSelect2(
                url='providertransfer-autocomplete',
                forward=['service', 'service_addon',
                         'location_from', 'location_to'],
                ),
        }
    id = forms.CharField(required=False, widget=forms.HiddenInput())


class PackageExtraForm(forms.ModelForm):
    class Meta:
        model = PackageExtra
        fields = ('__all__')
        widgets = {
            'service': autocomplete.ModelSelect2(
                url='serviceextra-autocomplete',
                forward=['provider'],
                ),
            'addon': autocomplete.ModelSelect2(
                url='addon-autocomplete',
                forward=['service'],
                ),
            'service_addon': autocomplete.ModelSelect2(
                url='addon-autocomplete',
                forward=['service'],
                ),
            'provider': autocomplete.ModelSelect2(
                url='providerextra-autocomplete',
                forward=['service', 'service_addon'],
                ),
            'pickup_office': autocomplete.ModelSelect2(
                url='carrentaloffice-autocomplete',
                forward=['service',],
                ),
            'dropoff_office': autocomplete.ModelSelect2(
                url='carrentaloffice-autocomplete',
                forward=['service',],
                ),
        }
    id = forms.CharField(required=False, widget=forms.HiddenInput())


class QuotePackageAllotmentInlineForm(forms.ModelForm):
    class Meta:
        fields = ('__all__')
        widgets = {
            'service': autocomplete.ModelSelect2(
                url='serviceallotment-autocomplete',
                forward=['provider'],
                ),
            'room_type': autocomplete.ModelSelect2(
                url='roomtype-autocomplete',
                forward=['service'],
                ),
            'board_type': autocomplete.ListSelect2(
                url='boardtype-autocomplete',
                forward=['service']),
            'service_addon': autocomplete.ModelSelect2(
                url='addon-autocomplete',
                forward=['service'],
                ),
            'provider': autocomplete.ModelSelect2(
                url='providerallotment-autocomplete',
                forward=['service', 'room_type', 'board_type', 'service_addon'],
                ),
        }


class QuotePackageAllotmentForm(forms.ModelForm):
    class Meta:
        model = QuotePackageAllotment
        fields = '__all__'
        widgets = {
            'service': autocomplete.ModelSelect2(
                url='serviceallotment-autocomplete',
                forward=['provider'],
                ),
            'room_type': autocomplete.ModelSelect2(
                url='roomtype-autocomplete',
                forward=['service'],
                ),
            'board_type': autocomplete.ListSelect2(
                url='boardtype-autocomplete',
                forward=['service']),
            'service_addon': autocomplete.ModelSelect2(
                url='addon-autocomplete',
                forward=['service'],
                ),
            'provider': autocomplete.ModelSelect2(
                url='providerallotment-autocomplete',
                forward=['service', 'room_type', 'board_type', 'service_addon'],
                ),
        }
    id = forms.CharField(required=False, widget=forms.HiddenInput())


class QuotePackageTransferInlineForm(forms.ModelForm):
    class Meta:
        fields = ('__all__')
        widgets = {
            'service': autocomplete.ModelSelect2(
                url='servicetransfer-autocomplete',
                forward=['provider'],
                ),
            'location_from': autocomplete.ModelSelect2(url='location-autocomplete'),
            'location_to': autocomplete.ModelSelect2(url='location-autocomplete'),
            'service_addon': autocomplete.ModelSelect2(
                url='addon-autocomplete',
                forward=['service'],
                ),
            'provider': autocomplete.ModelSelect2(
                url='providertransfer-autocomplete',
                forward=['service', 'location_from', 'location_to', 'service_addon'],
                ),
        }


class QuotePackageTransferForm(forms.ModelForm):
    class Meta:
        model = QuotePackageTransfer
        fields = ('__all__')
        widgets = {
            'service': autocomplete.ModelSelect2(
                url='servicetransfer-autocomplete',
                forward=['provider'],
                ),
            'location_from': autocomplete.ModelSelect2(url='location-autocomplete'),
            'location_to': autocomplete.ModelSelect2(url='location-autocomplete'),
            'service_addon': autocomplete.ModelSelect2(
                url='addon-autocomplete',
                forward=['service'],
                ),
            'provider': autocomplete.ModelSelect2(
                url='providertransfer-autocomplete',
                forward=['service', 'location_from', 'location_to', 'service_addon'],
                ),
        }
    id = forms.CharField(required=False, widget=forms.HiddenInput())


class QuotePackageExtraInlineForm(forms.ModelForm):
    class Meta:
        fields = ('__all__')
        widgets = {
            'service': autocomplete.ModelSelect2(
                url='serviceextra-autocomplete',
                forward=['provider'],
                ),
            'addon': autocomplete.ModelSelect2(
                url='addon-autocomplete',
                forward=['service'],
                ),
            'service_addon': autocomplete.ModelSelect2(
                url='addon-autocomplete',
                forward=['service'],
                ),
            'provider': autocomplete.ModelSelect2(
                url='providerextra-autocomplete',
                forward=['service', 'service_addon'],
                ),
            'pickup_office': autocomplete.ModelSelect2(
                url='carrentaloffice-autocomplete',
                forward=['service',],
                ),
            'dropoff_office': autocomplete.ModelSelect2(
                url='carrentaloffice-autocomplete',
                forward=['service',],
                ),
        }


class QuotePackageExtraForm(forms.ModelForm):
    class Meta:
        model = QuotePackageExtra
        fields = ('__all__')
        widgets = {
            'service': autocomplete.ModelSelect2(
                url='serviceextra-autocomplete',
                forward=['provider'],
                ),
            'addon': autocomplete.ModelSelect2(
                url='addon-autocomplete',
                forward=['service'],
                ),
            'service_addon': autocomplete.ModelSelect2(
                url='addon-autocomplete',
                forward=['service'],
                ),
            'provider': autocomplete.ModelSelect2(
                url='providerextra-autocomplete',
                forward=['service', 'service_addon'],
                ),
            'pickup_office': autocomplete.ModelSelect2(
                url='carrentaloffice-autocomplete',
                forward=['service',],
                ),
            'dropoff_office': autocomplete.ModelSelect2(
                url='carrentaloffice-autocomplete',
                forward=['service',],
                ),
        }
    id = forms.CharField(required=False, widget=forms.HiddenInput())


class QuoteAllotmentInlineForm(forms.ModelForm):
    class Meta:
        fields = ('__all__')
        widgets = {
            'service': autocomplete.ModelSelect2(
                url='serviceallotment-autocomplete',
                forward=['provider'],
                ),
            'room_type': autocomplete.ModelSelect2(
                url='roomtype-autocomplete',
                forward=['service'],
                ),
            'board_type': autocomplete.ListSelect2(
                url='boardtype-autocomplete',
                forward=['service']),
            'service_addon': autocomplete.ModelSelect2(
                url='addon-autocomplete',
                forward=['service'],
                ),
            'provider': autocomplete.ModelSelect2(
                url='providerallotment-autocomplete',
                forward=['service', 'room_type', 'board_type', 'service_addon'],
                ),
        }


class QuoteAllotmentForm(forms.ModelForm):
    class Meta:
        model = QuoteAllotment
        fields = '__all__'
        widgets = {
            'service': autocomplete.ModelSelect2(
                url='serviceallotment-autocomplete',
                forward=['provider'],
                ),
            'room_type': autocomplete.ModelSelect2(
                url='roomtype-autocomplete',
                forward=['service'],
                ),
            'board_type': autocomplete.ListSelect2(
                url='boardtype-autocomplete',
                forward=['service']),
            'service_addon': autocomplete.ModelSelect2(
                url='addon-autocomplete',
                forward=['service'],
                ),
            'provider': autocomplete.ModelSelect2(
                url='providerallotment-autocomplete',
                forward=['service', 'room_type', 'board_type', 'service_addon'],
                ),
        }
    id = forms.CharField(required=False, widget=forms.HiddenInput())
    nights = forms.IntegerField(initial=0)


class QuoteTransferInlineForm(forms.ModelForm):
    class Meta:
        fields = ('__all__')
        widgets = {
            'service': autocomplete.ModelSelect2(
                url='servicetransfer-autocomplete',
                forward=['provider'],
                ),
            'location_from': autocomplete.ModelSelect2(url='location-autocomplete'),
            'location_to': autocomplete.ModelSelect2(url='location-autocomplete'),
            'service_addon': autocomplete.ModelSelect2(
                url='addon-autocomplete',
                forward=['service'],
                ),
            'provider': autocomplete.ModelSelect2(
                url='providertransfer-autocomplete',
                forward=['service', 'location_from', 'location_to', 'service_addon'],
                ),
        }


class QuoteTransferForm(forms.ModelForm):
    class Meta:
        model = QuoteTransfer
        fields = ('__all__')
        widgets = {
            'service': autocomplete.ModelSelect2(
                url='servicetransfer-autocomplete',
                forward=['provider'],
                ),
            'location_from': autocomplete.ModelSelect2(url='location-autocomplete'),
            'location_to': autocomplete.ModelSelect2(url='location-autocomplete'),
            'service_addon': autocomplete.ModelSelect2(
                url='addon-autocomplete',
                forward=['service'],
                ),
            'provider': autocomplete.ModelSelect2(
                url='providertransfer-autocomplete',
                forward=['service', 'location_from', 'location_to', 'service_addon'],
                ),
        }
    id = forms.CharField(required=False, widget=forms.HiddenInput())


class QuoteExtraInlineForm(forms.ModelForm):
    class Meta:
        fields = ('__all__')
        widgets = {
            'service': autocomplete.ModelSelect2(
                url='serviceextra-autocomplete',
                forward=['provider'],
                ),
            'addon': autocomplete.ModelSelect2(
                url='addon-autocomplete',
                forward=['service'],
                ),
            'service_addon': autocomplete.ModelSelect2(
                url='addon-autocomplete',
                forward=['service'],
                ),
            'provider': autocomplete.ModelSelect2(
                url='providerextra-autocomplete',
                forward=['service', 'service_addon'],
                ),
            'pickup_office': autocomplete.ModelSelect2(
                url='carrentaloffice-autocomplete',
                forward=['service',],
                ),
            'dropoff_office': autocomplete.ModelSelect2(
                url='carrentaloffice-autocomplete',
                forward=['service',],
                ),
        }


class QuoteExtraForm(forms.ModelForm):
    class Meta:
        model = QuoteExtra
        fields = ('__all__')
        widgets = {
            'service': autocomplete.ModelSelect2(
                url='serviceextra-autocomplete',
                forward=['provider'],
                ),
            'addon': autocomplete.ModelSelect2(
                url='addon-autocomplete',
                forward=['service'],
                ),
            'service_addon': autocomplete.ModelSelect2(
                url='addon-autocomplete',
                forward=['service'],
                ),
            'provider': autocomplete.ModelSelect2(
                url='providerextra-autocomplete',
                forward=['service', 'service_addon'],
                ),
            'description': widgets.Textarea(attrs={'cols': 120, 'rows': 4}),
            'pickup_office': autocomplete.ModelSelect2(
                url='carrentaloffice-autocomplete',
                forward=['service',],
                ),
            'dropoff_office': autocomplete.ModelSelect2(
                url='carrentaloffice-autocomplete',
                forward=['service',],
                ),
        }
    id = forms.CharField(required=False, widget=forms.HiddenInput())


class QuotePackageInlineForm(forms.ModelForm):
    class Meta:
        fields = ('__all__')
        widgets = {
            'service': autocomplete.ModelSelect2(
                url='servicepackage-autocomplete',
                forward=['provider'],
                ),
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
            'service': autocomplete.ModelSelect2(
                url='servicepackage-autocomplete',
                forward=['provider'],
                ),
            'provider': autocomplete.ModelSelect2(
                url='providerpackage-autocomplete',
                forward=['service'],
                ),
        }
    id = forms.CharField(required=False, widget=forms.HiddenInput())


class MailForm(forms.Form):
    submit_action = forms.CharField(widget=forms.HiddenInput(), required=False)
    mail_from = forms.CharField(widget=forms.HiddenInput(), required=False)
    mail_to = forms.CharField(widget=forms.HiddenInput(), required=False)
    mail_cc = forms.CharField(widget=forms.HiddenInput(), required=False)
    mail_bcc = forms.CharField(widget=forms.HiddenInput(), required=False)
    mail_subject = forms.CharField(widget=forms.HiddenInput(), required=False)
    mail_body = forms.CharField(widget=forms.HiddenInput(), required=False)


class BookingForm(forms.ModelForm, MailForm):
    class Meta:
        model = Booking
        fields = ('__all__')
        widgets = {
            'agency': autocomplete.ModelSelect2(url='agency-autocomplete'),
            'agency_contact': autocomplete.ModelSelect2(
                url='agencycontact-autocomplete',
                forward=['agency'],
            ),
            'p_notes': widgets.Textarea(attrs={'cols': 120, 'rows': 4}),
        }
    id = forms.CharField(required=False, widget=forms.HiddenInput())


class BookingServicePaxInlineForm(forms.ModelForm):
    class Meta:
        fields = '__all__'
        widgets = {
            'booking_pax': autocomplete.ModelSelect2(
                url='bookingpax-autocomplete',
                forward=['booking', 'booking_service']),
        }


class BookingAllotmentForm(forms.ModelForm, MailForm):
    class Meta:
        model = BookingAllotment
        fields = '__all__'
        widgets = {
            'service': autocomplete.ModelSelect2(
                url='serviceallotment-autocomplete',
                forward=['provider'],
                ),
            'room_type': autocomplete.ModelSelect2(
                url='roomtype-autocomplete',
                forward=['service'],
                ),
            'board_type': autocomplete.ListSelect2(
                url='boardtype-autocomplete',
                forward=['service']),
            'service_addon': autocomplete.ModelSelect2(
                url='addon-autocomplete',
                forward=['service'],
                ),
            'provider': autocomplete.ModelSelect2(
                url='providerallotment-autocomplete',
                forward=['service', 'room_type', 'board_type', 'service_addon'],
                ),
            'p_notes': widgets.Textarea(attrs={'cols': 120, 'rows': 4}),
            'v_notes': widgets.Textarea(attrs={'cols': 120, 'rows': 4}),
            'provider_notes': widgets.Textarea(attrs={'cols': 120, 'rows': 4}),
        }
    id = forms.CharField(required=False, widget=forms.HiddenInput())
    nights = forms.IntegerField(initial=0)


class BookingTransferForm(forms.ModelForm, MailForm):
    class Meta:
        model = BookingTransfer
        fields = ('__all__')
        widgets = {
            'service': autocomplete.ModelSelect2(
                url='servicetransfer-autocomplete',
                forward=['provider'],
                ),
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
                forward=['service', 'location_from'],
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
            'service_addon': autocomplete.ModelSelect2(
                url='addon-autocomplete',
                forward=['service'],
                ),
            'provider': autocomplete.ModelSelect2(
                url='providertransfer-autocomplete',
                forward=['service', 'location_from', 'location_to', 'service_addon'],
                ),
            'p_notes': widgets.Textarea(attrs={'cols': 120, 'rows': 4}),
            'v_notes': widgets.Textarea(attrs={'cols': 120, 'rows': 4}),
            'provider_notes': widgets.Textarea(attrs={'cols': 120, 'rows': 4}),
        }
    id = forms.CharField(required=False, widget=forms.HiddenInput())


class BookingExtraForm(forms.ModelForm, MailForm):
    class Meta:
        model = BookingExtra
        fields = ('__all__')
        widgets = {
            'service': autocomplete.ModelSelect2(
                url='serviceextra-autocomplete',
                forward=['provider'],
                ),
            'addon': autocomplete.ModelSelect2(
                url='addon-autocomplete',
                forward=['service'],
                ),
            'service_addon': autocomplete.ModelSelect2(
                url='addon-autocomplete',
                forward=['service'],
                ),
            'provider': autocomplete.ModelSelect2(
                url='providerextra-autocomplete',
                forward=['service', 'service_addon'],
                ),
            'p_notes': widgets.Textarea(attrs={'cols': 120, 'rows': 4}),
            'v_notes': widgets.Textarea(attrs={'cols': 120, 'rows': 4}),
            'provider_notes': widgets.Textarea(attrs={'cols': 120, 'rows': 4}),
            'pickup_office': autocomplete.ModelSelect2(
                url='carrentaloffice-autocomplete',
                forward=['service',],
                ),
            'dropoff_office': autocomplete.ModelSelect2(
                url='carrentaloffice-autocomplete',
                forward=['service',],
                ),
        }
    id = forms.CharField(required=False, widget=forms.HiddenInput())
    nights = forms.IntegerField(initial=0)


class BookingPackageForm(forms.ModelForm, MailForm):
    class Meta:
        model = BookingPackage
        fields = '__all__'
        widgets = {
            'service': autocomplete.ModelSelect2(
                url='servicepackage-autocomplete',
                forward=['provider'],
                ),
            'provider': autocomplete.ModelSelect2(
                url='providerpackage-autocomplete',
                forward=['service'],
                ),
            'p_notes': widgets.Textarea(attrs={'cols': 120, 'rows': 4}),
            'v_notes': widgets.Textarea(attrs={'cols': 120, 'rows': 4}),
            'provider_notes': widgets.Textarea(attrs={'cols': 120, 'rows': 4}),
        }
    id = forms.CharField(required=False, widget=forms.HiddenInput())


class BookingPackageAllotmentForm(forms.ModelForm, MailForm):
    class Meta:
        model = BookingPackageAllotment
        fields = '__all__'
        widgets = {
            'service': autocomplete.ModelSelect2(
                url='serviceallotment-autocomplete',
                forward=['provider'],
                ),
            'room_type': autocomplete.ModelSelect2(
                url='roomtype-autocomplete',
                forward=['service'],
                ),
            'board_type': autocomplete.ListSelect2(
                url='boardtype-autocomplete',
                forward=['service']),
            'service_addon': autocomplete.ModelSelect2(
                url='addon-autocomplete',
                forward=['service'],
                ),
            'provider': autocomplete.ModelSelect2(
                url='providerallotment-autocomplete',
                forward=['service', 'room_type', 'board_type', 'service_addon'],
                ),
        }
    id = forms.CharField(required=False, widget=forms.HiddenInput())


class BookingPackageTransferForm(forms.ModelForm, MailForm):
    class Meta:
        model = BookingPackageTransfer
        fields = ('__all__')
        widgets = {
            'service': autocomplete.ModelSelect2(
                url='servicetransfer-autocomplete',
                forward=['provider'],
                ),
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
                forward=['service', 'location_from'],
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
            'service_addon': autocomplete.ModelSelect2(
                url='addon-autocomplete',
                forward=['service'],
                ),
            'provider': autocomplete.ModelSelect2(
                url='providertransfer-autocomplete',
                forward=['service', 'location_from', 'location_to', 'service_addon'],
                ),
        }
    id = forms.CharField(required=False, widget=forms.HiddenInput())


class BookingPackageExtraForm(forms.ModelForm, MailForm):
    class Meta:
        model = BookingPackageExtra
        fields = ('__all__')
        widgets = {
            'service': autocomplete.ModelSelect2(
                url='serviceextra-autocomplete',
                forward=['provider'],
                ),
            'addon': autocomplete.ModelSelect2(
                url='addon-autocomplete',
                forward=['service'],
                ),
            'service_addon': autocomplete.ModelSelect2(
                url='addon-autocomplete',
                forward=['service'],
                ),
            'provider': autocomplete.ModelSelect2(
                url='providerextra-autocomplete',
                forward=['service', 'service_addon'],
                ),
            'pickup_office': autocomplete.ModelSelect2(
                url='carrentaloffice-autocomplete',
                forward=['service',],
                ),
            'dropoff_office': autocomplete.ModelSelect2(
                url='carrentaloffice-autocomplete',
                forward=['service',],
                ),
        }
    id = forms.CharField(required=False, widget=forms.HiddenInput())


class PackageProviderForm(forms.ModelForm):
    class Meta:
        model = PackageProvider
        fields = ('__all__')
        widgets = {
            'service': autocomplete.ModelSelect2(url='package-autocomplete'),
            'provider': autocomplete.ModelSelect2(url='provider-autocomplete'),
        }


class AgencyPackageServiceForm(forms.ModelForm):
    class Meta:
        model = AgencyPackageService
        fields = ('__all__')
        widgets = {
            'agency': autocomplete.ModelSelect2(url='agency-autocomplete'),
            'service': autocomplete.ModelSelect2(url='package-autocomplete'),
        }


class EmailProviderForm(forms.Form):
    from_address = forms.EmailField(
        label='FROM',
        widget=widgets.TextInput(
            attrs={'class': 'form-control'})
    )
    to_address = forms.EmailField(
        label='TO',
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
        label='Body',
        widget=CKEditorWidget(
            attrs={'class': 'form-control'}))

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(EmailProviderForm, self).__init__(*args, **kwargs)
        self.initial['from_address'] = self.user.email


class EmailPopupForm(forms.Form):
    mail_from = forms.EmailField(
        label='FROM',
        widget=widgets.TextInput(
            attrs={'class': 'form-control',
                   'id': 'm_from'})
    )
    mail_to = forms.EmailField(
        label='TO',
        widget=widgets.TextInput(
            attrs={'class': 'form-control',
                   'id': 'm_to'})
    )
    mail_cc = forms.EmailField(
        label='CC',
        widget=widgets.TextInput(
            attrs={'class': 'form-control',
                   'id': 'm_cc'})
    )
    mail_bcc = forms.EmailField(
        label='BCC',
        widget=widgets.TextInput(
            attrs={'class': 'form-control',
                   'id': 'm_bcc'})
    )
    mail_subject = forms.CharField(
        max_length=100,
        label='Subject',
        widget=widgets.TextInput(
            attrs={'class': 'form-control',
                   'id': 'm_subject'}))
    mail_body = forms.CharField(
        label='Body',
        widget=CKEditorWidget(
            attrs={'class': 'form-control',
                   'id': 'm_body'}))


class VouchersConfigForm(MailForm):
    # states = forms.ChoiceField(settings.ESTADOS)
    # this helps to point back to current booking
    # referer = forms.HiddenInput()
    # the list of selected services to make vouchers from
    # id = forms.MultiValueField()
    # here comes also some inputs to select logo and other details
    office = forms.ModelChoiceField(queryset=Office.objects.all())


class PackageForm(forms.ModelForm):
    class Meta:
        model = Package
        fields = ('__all__')
        widgets = {
            'location': autocomplete.ModelSelect2(url='location-autocomplete'),
            'description': widgets.Textarea(attrs={'cols': 120, 'rows': 4}),
        }


class ProviderBookingPaymentForm(forms.ModelForm):
    class Meta:
        model = ProviderBookingPayment
        fields = ('__all__')
        widgets = {
            'provider': autocomplete.ModelSelect2(url='provider-autocomplete'),
            'account': autocomplete.ModelSelect2(url='account-autocomplete'),
        }


class ProviderBookingPaymentServiceForm(forms.Form):
    service_payment_id = forms.CharField(required=False,
                                         widget=forms.HiddenInput())
    service_id = forms.CharField(required=False, widget=forms.HiddenInput())
    service_conf = forms.CharField(disabled=True, required=True, label='Conf.')
    service_booking = forms.CharField(disabled=True, required=False)
    service_booking_ref = forms.CharField(disabled=True, required=False, label='Ref.')
    service_from = forms.CharField(disabled=True, required=False, label='From')
    service_to = forms.CharField(disabled=True, required=False, label='To')
    service_name = forms.CharField(disabled=True, required=False)
    saved_amount_to_pay = forms.DecimalField(
        label='Saved To Pay', required=False,
        disabled=True, widget=forms.TextInput(
            attrs={'readonly':'readonly', 'style':'text-align: right; width: 100px;'}))
    saved_amount_paid = forms.DecimalField(
        label='Saved Paid', required=False,
        disabled=True, widget=forms.TextInput(
            attrs={'readonly':'readonly', 'style':'text-align: right; width: 100px;'}))
    service_amount_to_pay = forms.DecimalField(
        label='Serv.To Pay', required=False,
        disabled=True, widget=forms.TextInput(
            attrs={'readonly':'readonly', 'style':'text-align: right; width: 100px;'}))
    service_amount_paid = forms.DecimalField(
        label='Serv.Paid', required=False,
        disabled=True, widget=forms.TextInput(
            attrs={'readonly':'readonly', 'style':'text-align: right; width: 100px;'}))
    is_selected = forms.BooleanField(label='sel', required=False,
        widget=forms.CheckboxInput(
            attrs={'style':'text-align: center; width: 40px;'}
        ))
    amount_paid = forms.DecimalField(
        label='Paid', required=False,
        decimal_places=2, widget=forms.NumberInput(
            attrs={'style':'text-align: right; width: 100px;'}))


class ProviderBookingPaymentServiceReadonlyForm(forms.Form):
    service_payment_id = forms.CharField(required=False,
                                         widget=forms.HiddenInput())
    service_id = forms.CharField(required=False, widget=forms.HiddenInput())
    service_name = forms.CharField(disabled=True, required=False)
    service_conf = forms.CharField(disabled=True, required=True, label='Conf.')
    service_booking = forms.CharField(disabled=True, required=False)
    service_booking_ref = forms.CharField(disabled=True, required=False,
                                          label='Ref.')
    service_from = forms.CharField(disabled=True, required=False, label='From')
    service_to = forms.CharField(disabled=True, required=False, label='To')
    saved_amount_to_pay = forms.DecimalField(label='Saved To Pay',
                                             required=False,
                                             disabled=True)
    saved_amount_paid = forms.DecimalField(label='Saved Paid', required=False,
                                           disabled=True)
    service_amount_to_pay = forms.DecimalField(
        label='Serv.To Pay', required=False,
        disabled=True, widget=forms.TextInput(
            attrs={'readonly':'readonly', 'style':'text-align: right; width: 100px;'}))
    service_amount_paid = forms.DecimalField(
        label='Serv.Paid', required=False,
        disabled=True, widget=forms.TextInput(
            attrs={'readonly':'readonly', 'style':'text-align: right; width: 100px;'}))
    is_selected = forms.BooleanField(label='sel', required=False,
        disabled=True, widget=forms.CheckboxInput(
            attrs={'style':'text-align: center; width: 40px;'}
        ))
    amount_paid = forms.DecimalField(
        label='Paid', required=False,
        decimal_places=2, disabled=True, widget=forms.NumberInput(
            attrs={'style':'text-align: right; width: 100px;'}))
