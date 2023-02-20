# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from ckeditor.widgets import CKEditorWidget
from dal import autocomplete

from django.contrib.admin.widgets import AdminDateWidget
from django import forms
from django.forms import widgets

from booking.models import (
    Quote, NewQuoteAllotment, NewQuoteTransfer,
    NewQuoteExtra, QuoteExtraPackage,
    Booking, BaseBookingServicePax, BookingProvidedAllotment,
    BookingProvidedTransfer, BookingProvidedExtra, BookingExtraPackage,
    ProviderBookingPayment, BookingBookDetailAllotment,
    BookingBookDetailExtra, BookingBookDetailTransfer
)

from config.forms import BaseBookDataForm
from config.models import Location

from finance.models import Office


class ServiceForm(forms.Form):
    search_location = forms.ModelChoiceField(
        queryset=Location.objects.all(),
        empty_label='',
        required=False,
        widget=autocomplete.ModelSelect2(
            url='location-autocomplete',
        ),
        label='Search Location',
    )


class MailForm(forms.Form):
    submit_action = forms.CharField(widget=forms.HiddenInput(), required=False)
    mail_from = forms.CharField(widget=forms.HiddenInput(), required=False)
    mail_to = forms.CharField(widget=forms.HiddenInput(), required=False)
    mail_cc = forms.CharField(widget=forms.HiddenInput(), required=False)
    mail_bcc = forms.CharField(widget=forms.HiddenInput(), required=False)
    mail_subject = forms.CharField(widget=forms.HiddenInput(), required=False)
    mail_body = forms.CharField(widget=forms.HiddenInput(), required=False)


class QuoteForm(forms.ModelForm, MailForm):
    class Meta:
        model = Quote
        fields = ('__all__')
        widgets = {
            'agency': autocomplete.ModelSelect2(url='agency-autocomplete'),
            'description': widgets.Textarea(attrs={'cols': 120, 'rows': 4}),
        }
    id = forms.CharField(required=False, widget=forms.HiddenInput())


class PackageAllotmentInlineForm(forms.ModelForm, ServiceForm):
    class Meta:
        fields = ('__all__')
        widgets = {
            'service': autocomplete.ModelSelect2(
                url='serviceallotment-autocomplete',
                forward=['provider', 'search_location'],
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


class PackageTransferInlineForm(forms.ModelForm, ServiceForm):
    class Meta:
        fields = ('__all__')
        widgets = {
            'service': autocomplete.ModelSelect2(
                url='servicetransfer-autocomplete',
                forward=['provider', 'search_location', 'location_from', 'location_to'],
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


class PackageExtraInlineForm(forms.ModelForm, ServiceForm):
    class Meta:
        fields = ('__all__')
        widgets = {
            'service': autocomplete.ModelSelect2(
                url='serviceextra-autocomplete',
                forward=['provider', 'search_location'],
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


class NewQuoteAllotmentForm(forms.ModelForm, ServiceForm):
    class Meta:
        model = NewQuoteAllotment
        fields = '__all__'
        widgets = {
            'quote': autocomplete.ModelSelect2(
                url='disabled-autocomplete',),
            'quote_package': autocomplete.ModelSelect2(
                url='disabled-autocomplete',),
            'service': autocomplete.ModelSelect2(
                url='serviceallotment-autocomplete',
                forward=['provider', 'search_location'],
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
            'contract_code': autocomplete.ListSelect2(
                url='allotmentcontract-autocomplete',
                forward=[
                    'quote', 'provider', 'service', 'date_from', 'date_to',
                    'service_addon', 'room_type', 'board_type'],
                ),
        }
    id = forms.CharField(required=False, widget=forms.HiddenInput())
    nights = forms.IntegerField(initial=0)

    def __init__(self, *args, **kwargs):
        super(NewQuoteAllotmentForm, self).__init__(*args, **kwargs)
        self.fields['contract_code'].widget.choices = [
            [self.instance.contract_code, self.instance.contract_code]]


class NewQuoteTransferForm(forms.ModelForm, ServiceForm):
    class Meta:
        model = NewQuoteTransfer
        fields = ('__all__')
        widgets = {
            'quote': autocomplete.ModelSelect2(
                url='disabled-autocomplete',),
            'quote_package': autocomplete.ModelSelect2(
                url='disabled-autocomplete',),
            'service': autocomplete.ModelSelect2(
                url='servicetransfer-autocomplete',
                forward=['provider', 'search_location', 'location_from', 'location_to'],
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
            'contract_code': autocomplete.ListSelect2(
                url='transfercontract-autocomplete',
                forward=[
                    'quote', 'provider', 'service', 'date_from', 'date_to',
                    'service_addon', 'location_from', 'location_to'],
                ),
        }
    id = forms.CharField(required=False, widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        super(NewQuoteTransferForm, self).__init__(*args, **kwargs)
        self.fields['contract_code'].widget.choices = [
            [self.instance.contract_code, self.instance.contract_code]]


class NewQuoteExtraForm(forms.ModelForm, ServiceForm):
    class Meta:
        model = NewQuoteExtra
        fields = ('__all__')
        widgets = {
            'quote': autocomplete.ModelSelect2(
                url='disabled-autocomplete',),
            'quote_package': autocomplete.ModelSelect2(
                url='disabled-autocomplete',),
            'service': autocomplete.ModelSelect2(
                url='serviceextra-autocomplete',
                forward=['provider', 'search_location'],
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
                forward=['service'],
                ),
            'dropoff_office': autocomplete.ModelSelect2(
                url='carrentaloffice-autocomplete',
                forward=['service'],
                ),
            'contract_code': autocomplete.ListSelect2(
                url='extracontract-autocomplete',
                forward=[
                    'quote', 'provider', 'service', 'date_from', 'date_to',
                    'service_addon'],
                ),
        }
    id = forms.CharField(required=False, widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        super(NewQuoteExtraForm, self).__init__(*args, **kwargs)
        self.fields['contract_code'].widget.choices = [
            [self.instance.contract_code, self.instance.contract_code]]


class QuoteExtraPackageForm(forms.ModelForm, ServiceForm):
    class Meta:
        model = QuoteExtraPackage
        fields = ('__all__')
        widgets = {
            'booking': autocomplete.ModelSelect2(
                url='disabled-autocomplete',),
            'service': autocomplete.ModelSelect2(
                url='serviceextra-autocomplete',
                forward=['provider', 'search_location'],
                ),
            'provider': autocomplete.ModelSelect2(
                url='providerextra-autocomplete',
                forward=['service'],
                ),
        }
    id = forms.CharField(required=False, widget=forms.HiddenInput())


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


class BaseBookingServicePaxInlineForm(forms.ModelForm):
    class Meta:
        fields = '__all__'
        widgets = {
            'booking_pax': autocomplete.ModelSelect2(
                url='bookingpax-autocomplete',
                forward=['booking', 'booking_service']),
        }


class BookingProvidedAllotmentForm(forms.ModelForm, MailForm, ServiceForm):
    class Meta:
        model = BookingProvidedAllotment
        fields = '__all__'
        widgets = {
            'booking': autocomplete.ModelSelect2(
                url='disabled-autocomplete',),
            'booking_package': autocomplete.ModelSelect2(
                url='disabled-autocomplete',),
            'service': autocomplete.ModelSelect2(
                url='serviceallotment-autocomplete',
                forward=['provider', 'search_location'],
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
            'new_v_notes': widgets.Textarea(attrs={'cols': 120, 'rows': 4}),
            'provider_notes': widgets.Textarea(attrs={'cols': 120, 'rows': 4}),
            'contract_code': autocomplete.ListSelect2(
                url='allotmentcontract-autocomplete',
                forward=[
                    'booking', 'provider', 'service', 'date_from', 'date_to',
                    'service_addon', 'room_type', 'board_type'],
                ),
        }
    id = forms.CharField(required=False, widget=forms.HiddenInput())
    nights = forms.IntegerField(initial=0)

    def __init__(self, *args, **kwargs):
        super(BookingProvidedAllotmentForm, self).__init__(*args, **kwargs)
        self.fields['contract_code'].widget.choices = [
            [self.instance.contract_code, self.instance.contract_code]]


class BookingProvidedTransferForm(forms.ModelForm, MailForm, ServiceForm):
    class Meta:
        model = BookingProvidedTransfer
        fields = ('__all__')
        widgets = {
            'booking': autocomplete.ModelSelect2(
                url='disabled-autocomplete',),
            'booking_package': autocomplete.ModelSelect2(
                url='disabled-autocomplete',),
            'service': autocomplete.ModelSelect2(
                url='servicetransfer-autocomplete',
                forward=['provider', 'search_location', 'location_from', 'location_to'],
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
            'new_v_notes': widgets.Textarea(attrs={'cols': 120, 'rows': 4}),
            'provider_notes': widgets.Textarea(attrs={'cols': 120, 'rows': 4}),
            'contract_code': autocomplete.ListSelect2(
                url='transfercontract-autocomplete',
                forward=[
                    'booking', 'provider', 'service', 'date_from', 'date_to',
                    'service_addon', 'location_from', 'location_to'],
                ),
        }
    id = forms.CharField(required=False, widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        super(BookingProvidedTransferForm, self).__init__(*args, **kwargs)
        self.fields['contract_code'].widget.choices = [
            [self.instance.contract_code, self.instance.contract_code]]


class BookingProvidedExtraForm(forms.ModelForm, MailForm, ServiceForm):
    class Meta:
        model = BookingProvidedExtra
        fields = ('__all__')
        widgets = {
            'booking': autocomplete.ModelSelect2(
                url='disabled-autocomplete',),
            'booking_package': autocomplete.ModelSelect2(
                url='disabled-autocomplete',),
            'service': autocomplete.ModelSelect2(
                url='serviceextra-autocomplete',
                forward=['provider', 'search_location'],
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
            'new_v_notes': widgets.Textarea(attrs={'cols': 120, 'rows': 4}),
            'provider_notes': widgets.Textarea(attrs={'cols': 120, 'rows': 4}),
            'pickup_office': autocomplete.ModelSelect2(
                url='carrentaloffice-autocomplete',
                forward=['service',],
                ),
            'dropoff_office': autocomplete.ModelSelect2(
                url='carrentaloffice-autocomplete',
                forward=['service',],
                ),
            'contract_code': autocomplete.ListSelect2(
                url='extracontract-autocomplete',
                forward=[
                    'booking', 'provider', 'service', 'date_from', 'date_to',
                    'service_addon'],
                ),
        }
    id = forms.CharField(required=False, widget=forms.HiddenInput())
    nights = forms.IntegerField(initial=0)

    def __init__(self, *args, **kwargs):
        super(BookingProvidedExtraForm, self).__init__(*args, **kwargs)
        self.fields['contract_code'].widget.choices = [
            [self.instance.contract_code, self.instance.contract_code]]


class BookingExtraPackageForm(forms.ModelForm, MailForm, ServiceForm):
    class Meta:
        model = BookingExtraPackage
        fields = '__all__'
        widgets = {
            'booking': autocomplete.ModelSelect2(
                url='disabled-autocomplete',),
            'service': autocomplete.ModelSelect2(
                url='serviceextra-autocomplete',
                forward=['provider', 'search_location'],
                ),
            'provider': autocomplete.ModelSelect2(
                url='providerextra-autocomplete',
                forward=['service'],
                ),
            'p_notes': widgets.Textarea(attrs={'cols': 120, 'rows': 4}),
            'new_v_notes': widgets.Textarea(attrs={'cols': 120, 'rows': 4}),
            'provider_notes': widgets.Textarea(attrs={'cols': 120, 'rows': 4}),
        }
    id = forms.CharField(required=False, widget=forms.HiddenInput())


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


class ProviderBookingPaymentForm(forms.ModelForm, MailForm):
    booking_ref_filter = forms.CharField(required=False)
    internal_ref_filter = forms.CharField(required=False)
    booking_name_filter = forms.CharField(required=False)
    date_widget = AdminDateWidget()
    date_from_filter = forms.CharField(required=False, widget=date_widget)
    date_to_filter = forms.CharField(required=False, widget=date_widget)
    confirm_number_filter = forms.CharField(required=False)
    class Meta:
        model = ProviderBookingPayment
        fields = ('__all__')
        widgets = {
            'provider': autocomplete.ModelSelect2(url='provider-autocomplete'),
            'account': autocomplete.ModelSelect2(url='account-autocomplete'),
        }


class ProviderPaymentBookingProvidedForm(forms.Form):
    service_payment_id = forms.CharField(required=False,
                                         widget=forms.HiddenInput())
    service_id = forms.CharField(required=False, widget=forms.HiddenInput())
    service_conf = forms.CharField(disabled=True, required=False, label='Conf.')
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


class ProviderPaymentBookingProvidedReadonlyForm(forms.Form):
    service_payment_id = forms.CharField(required=False,
                                         widget=forms.HiddenInput())
    service_id = forms.CharField(required=False, widget=forms.HiddenInput())
    service_name = forms.CharField(disabled=True, required=False)
    service_conf = forms.CharField(disabled=True, required=False, label='Conf.')
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


class BookingExtraComponentInlineForm(forms.ModelForm):
    class Meta:
        fields = '__all__'
        widgets = {
            'component': autocomplete.ModelSelect2(url='extra-autocomplete'),
        }


class NewQuoteServiceBookDetailAllotmentForm(forms.ModelForm, BaseBookDataForm):
    class Meta:
        fields = ('__all__')
        widgets = {
            'quote_service': autocomplete.ModelSelect2(
                url='disabled-autocomplete',
                ),
            'book_service': autocomplete.ModelSelect2(
                url='serviceallotment-autocomplete',
                forward=['search_location'],
                ),
            'room_type': autocomplete.ModelSelect2(
                url='roomtype-autocomplete',
                forward=['book_service'],
                ),
            'board_type': autocomplete.ListSelect2(
                url='boardtype-autocomplete',
                forward=['book_service']),
            'service_addon': autocomplete.ModelSelect2(
                url='addon-autocomplete',
                forward=['book_service'],
                ),
            'contract_code': autocomplete.ListSelect2(
                url='allotmentcontract-autocomplete',
                forward=[
                    'quote_service', 'provider', 'book_service', 'date_from', 'date_to',
                    'service_addon', 'room_type', 'board_type'],
                ),
        }


class NewQuoteServiceBookDetailTransferForm(forms.ModelForm, BaseBookDataForm):
    class Meta:
        fields = ('__all__')
        widgets = {
            'quote_service': autocomplete.ModelSelect2(
                url='disabled-autocomplete',
                ),
            'book_service': autocomplete.ModelSelect2(
                url='servicetransfer-autocomplete',
                forward=['search_location', 'location_from', 'location_to'],
                ),
            'location_from': autocomplete.ModelSelect2(url='location-autocomplete'),
            'location_to': autocomplete.ModelSelect2(url='location-autocomplete'),
            'service_addon': autocomplete.ModelSelect2(
                url='addon-autocomplete',
                forward=['book_service'],
                ),
            'contract_code': autocomplete.ListSelect2(
                url='transfercontract-autocomplete',
                forward=[
                    'quote_service', 'provider', 'book_service', 'date_from', 'date_to',
                    'service_addon', 'location_from', 'location_to'],
                ),
        }


class NewQuoteServiceBookDetailExtraForm(forms.ModelForm, BaseBookDataForm):
    class Meta:
        fields = ('__all__')
        widgets = {
            'quote_service': autocomplete.ModelSelect2(
                url='service-autocomplete',
                ),
            'book_service': autocomplete.ModelSelect2(
                url='serviceextra-autocomplete',
                forward=['search_location'],
                ),
            'service_addon': autocomplete.ModelSelect2(
                url='addon-autocomplete',
                forward=['book_service'],
                ),
            'pickup_office': autocomplete.ModelSelect2(
                url='carrentaloffice-autocomplete',
                forward=['book_service',],
                ),
            'dropoff_office': autocomplete.ModelSelect2(
                url='carrentaloffice-autocomplete',
                forward=['book_service',],
                ),
            'contract_code': autocomplete.ListSelect2(
                url='extracontract-autocomplete',
                forward=[
                    'quote_service', 'provider', 'book_service', 'date_from', 'date_to',
                    'service_addon'],
                ),
        }


class BookingBookDetailAllotmentForm(forms.ModelForm, BaseBookDataForm):
    class Meta:
        model = BookingBookDetailAllotment
        fields = ('__all__')
        widgets = {
            'booking_service': autocomplete.ModelSelect2(
                url='disabled-autocomplete',
                ),
            'book_service': autocomplete.ModelSelect2(
                url='serviceallotment-autocomplete',
                forward=['search_location'],
                ),
            'room_type': autocomplete.ModelSelect2(
                url='roomtype-autocomplete',
                forward=['book_service'],
                ),
            'board_type': autocomplete.ListSelect2(
                url='boardtype-autocomplete',
                forward=['book_service']),
            'service_addon': autocomplete.ModelSelect2(
                url='addon-autocomplete',
                forward=['book_service'],
                ),
            'provider': autocomplete.ModelSelect2(
                url='providerallotment-autocomplete',
                forward=['book_service'],
                ),
            'contract_code': autocomplete.ListSelect2(
                url='allotmentcontract-autocomplete',
                forward=[
                    'booking_service', 'provider', 'book_service', 'date_from', 'date_to',
                    'service_addon', 'room_type', 'board_type'],
                ),
        }

    def __init__(self, *args, **kwargs):
        super(BookingBookDetailAllotmentForm, self).__init__(*args, **kwargs)
        self.fields['contract_code'].widget.choices = [
            [self.instance.contract_code, self.instance.contract_code]]


class BookingBookDetailTransferForm(forms.ModelForm, BaseBookDataForm):
    class Meta:
        model = BookingBookDetailTransfer
        fields = ('__all__')
        widgets = {
            'booking_service': autocomplete.ModelSelect2(
                url='disabled-autocomplete',
                ),
            'book_service': autocomplete.ModelSelect2(
                url='servicetransfer-autocomplete',
                forward=['search_location', 'location_from', 'location_to'],
                ),
            'location_from': autocomplete.ModelSelect2(url='location-autocomplete'),
            'location_to': autocomplete.ModelSelect2(url='location-autocomplete'),
            'service_addon': autocomplete.ModelSelect2(
                url='addon-autocomplete',
                forward=['book_service'],
                ),
            'provider': autocomplete.ModelSelect2(
                url='providertransfer-autocomplete',
                forward=['book_service'],
                ),
            'contract_code': autocomplete.ListSelect2(
                url='transfercontract-autocomplete',
                forward=[
                    'booking_service', 'provider', 'book_service', 'date_from', 'date_to',
                    'service_addon', 'location_from', 'location_to'],
                ),
        }

    def __init__(self, *args, **kwargs):
        super(BookingBookDetailTransferForm, self).__init__(*args, **kwargs)
        self.fields['contract_code'].widget.choices = [
            [self.instance.contract_code, self.instance.contract_code]]


class BookingBookDetailExtraForm(forms.ModelForm, BaseBookDataForm):
    class Meta:
        model = BookingBookDetailExtra
        fields = ('__all__')
        widgets = {
            'booking_service': autocomplete.ModelSelect2(
                url='service-autocomplete',
                ),
            'book_service': autocomplete.ModelSelect2(
                url='serviceextra-autocomplete',
                forward=['search_location'],
                ),
            'service_addon': autocomplete.ModelSelect2(
                url='addon-autocomplete',
                forward=['book_service'],
                ),
            'pickup_office': autocomplete.ModelSelect2(
                url='carrentaloffice-autocomplete',
                forward=['book_service',],
                ),
            'dropoff_office': autocomplete.ModelSelect2(
                url='carrentaloffice-autocomplete',
                forward=['boo_service',],
                ),
            'provider': autocomplete.ModelSelect2(
                url='providerextra-autocomplete',
                forward=['book_service'],
                ),
            'contract_code': autocomplete.ListSelect2(
                url='extracontract-autocomplete',
                forward=[
                    'booking_service', 'provider', 'book_service', 'date_from', 'date_to',
                    'service_addon'],
                ),
        }

    def __init__(self, *args, **kwargs):
        super(BookingBookDetailExtraForm, self).__init__(*args, **kwargs)
        self.fields['contract_code'].widget.choices = [
            [self.instance.contract_code, self.instance.contract_code]]
