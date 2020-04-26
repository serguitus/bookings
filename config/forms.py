# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from dal import autocomplete

from django import forms
from django.contrib.admin.widgets import AdminDateWidget

from config.models import (
    Location,
    Service,
    ProviderAllotmentService, ProviderTransferService, ProviderExtraService,
    ProviderAllotmentDetail, ProviderTransferDetail, ProviderExtraDetail,
    AgencyAllotmentService, AgencyTransferService, AgencyExtraService,
    AgencyAllotmentDetail, AgencyTransferDetail, AgencyExtraDetail,
)
from finance.models import Agency


class LocationTransferIntervalInlineForm(forms.ModelForm):
    class Meta:
        fields = ('__all__')
        widgets = {
            't_location_from': autocomplete.ModelSelect2(url='location-autocomplete'),
        }


class TransferZoneForm(forms.ModelForm):
    class Meta:
        fields = ('__all__')
        widgets = {
            'transfer': autocomplete.ModelSelect2(url='zonetransfer-autocomplete'),
        }


class TransferPickupTimeInlineForm(forms.ModelForm):
    class Meta:
        fields = ('__all__')
        widgets = {
            'location': autocomplete.ModelSelect2(url='location-autocomplete'),
        }


class ProviderAllotmentServiceForm(forms.ModelForm):
    class Meta:
        model = ProviderAllotmentService
        fields = ('__all__')
        widgets = {
            'service': autocomplete.ModelSelect2(url='allotment-autocomplete'),
            'provider': autocomplete.ModelSelect2(url='provider-autocomplete'),
        }


class ProviderAllotmentDetailForm(forms.ModelForm):
    class Meta:
        model = ProviderAllotmentDetail
        fields = ('__all__')
        widgets = {
            'provider_service': autocomplete.ModelSelect2(
                url='disabled-autocomplete',
                attrs={'disabled': 'true'}),
            'room_type': autocomplete.ModelSelect2(
                url='roomtype-autocomplete',
                forward=['provider_service']),
            'board_type': autocomplete.ListSelect2(
                url='boardtype-autocomplete',
                forward=['provider_service']),
            'addon': autocomplete.ModelSelect2(
                url='addon-autocomplete',
                forward=['provider_service']),
        }


class ProviderAllotmentDetailInlineForm(forms.ModelForm):
    class Meta:
        fields = ('__all__')
        widgets = {
            'room_type': autocomplete.ModelSelect2(
                url='roomtype-autocomplete',
                forward=['service']),
            'board_type': autocomplete.ListSelect2(
                url='boardtype-autocomplete',
                forward=['service']),
            'addon': autocomplete.ModelSelect2(
                url='addon-autocomplete',
                forward=['service']),
        }


class ProviderTransferServiceForm(forms.ModelForm):
    class Meta:
        model = ProviderTransferService
        fields = ('__all__')
        widgets = {
            'provider': autocomplete.ModelSelect2(url='provider-autocomplete'),
            'service': autocomplete.ModelSelect2(url='transfer-autocomplete'),
        }


class ProviderTransferDetailForm(forms.ModelForm):
    class Meta:
        model = ProviderTransferDetail
        fields = ('__all__')
        widgets = {
            'provider_service': autocomplete.ModelSelect2(
                url='disabled-autocomplete',
                attrs={'disabled': 'true'}),
            'location_from': autocomplete.ModelSelect2(url='location-autocomplete'),
            'location_to': autocomplete.ModelSelect2(url='location-autocomplete'),
            'addon': autocomplete.ModelSelect2(
                url='addon-autocomplete',
                forward=['provider_service']),
        }


class ProviderTransferDetailInlineForm(forms.ModelForm):
    class Meta:
        fields = ('__all__')
        widgets = {
            'location_from': autocomplete.ModelSelect2(url='location-autocomplete'),
            'location_to': autocomplete.ModelSelect2(url='location-autocomplete'),
            'addon': autocomplete.ModelSelect2(
                url='addon-autocomplete',
                forward=['service']),
        }


class ProviderExtraServiceForm(forms.ModelForm):
    class Meta:
        model = AgencyExtraService
        fields = ('__all__')
        widgets = {
            'provider': autocomplete.ModelSelect2(url='provider-autocomplete'),
            'service': autocomplete.ModelSelect2(url='extra-autocomplete'),
        }


class ProviderExtraDetailForm(forms.ModelForm):
    class Meta:
        model = ProviderExtraDetail
        fields = ('__all__')
        widgets = {
            'provider_service': autocomplete.ModelSelect2(
                url='disabled-autocomplete',
                attrs={'disabled': 'true'}),
            'addon': autocomplete.ModelSelect2(
                url='addon-autocomplete',
                forward=['provider_service']),
        }


class ProviderExtraDetailInlineForm(forms.ModelForm):
    class Meta:
        fields = ('__all__')
        widgets = {
            'addon': autocomplete.ModelSelect2(
                url='addon-autocomplete',
                forward=['service']),
        }


class AgencyAllotmentServiceForm(forms.ModelForm):
    class Meta:
        model = AgencyAllotmentService
        fields = ('__all__')
        widgets = {
            'agency': autocomplete.ModelSelect2(url='agency-autocomplete'),
            'service': autocomplete.ModelSelect2(url='allotment-autocomplete'),
        }


class AgencyAllotmentDetailForm(forms.ModelForm):
    class Meta:
        model = AgencyAllotmentDetail
        fields = ('__all__')
        widgets = {
            'agency_service': autocomplete.ModelSelect2(
                url='disabled-autocomplete',
                attrs={'disabled': 'true'}),
            'room_type': autocomplete.ModelSelect2(
                url='roomtype-autocomplete',
                forward=['agency_service']),
            'board_type': autocomplete.ListSelect2(
                url='boardtype-autocomplete',
                forward=['agency_service']),
        }


class AgencyAllotmentDetailInlineForm(forms.ModelForm):
    class Meta:
        fields = ('__all__')
        widgets = {
            'room_type': autocomplete.ModelSelect2(
                url='roomtype-autocomplete',
                forward=['service']),
            'board_type': autocomplete.ListSelect2(
                url='boardtype-autocomplete',
                forward=['service']),
            'addon': autocomplete.ModelSelect2(
                url='addon-autocomplete',
                forward=['service']),
        }


class AgencyTransferServiceForm(forms.ModelForm):
    class Meta:
        model = AgencyTransferService
        fields = ('__all__')
        widgets = {
            'agency': autocomplete.ModelSelect2(url='agency-autocomplete'),
            'service': autocomplete.ModelSelect2(url='transfer-autocomplete'),
        }


class AgencyTransferDetailForm(forms.ModelForm):
    class Meta:
        model = AgencyTransferDetail
        fields = ('__all__')
        widgets = {
            'agency_service': autocomplete.ModelSelect2(
                url='disabled-autocomplete',
                attrs={'disabled': 'true'}),
            'location_from': autocomplete.ModelSelect2(url='location-autocomplete'),
            'location_to': autocomplete.ModelSelect2(url='location-autocomplete'),
            'addon': autocomplete.ModelSelect2(
                url='addon-autocomplete',
                forward=['agency_service']),
        }


class AgencyTransferDetailInlineForm(forms.ModelForm):
    class Meta:
        fields = ('__all__')
        widgets = {
            'location_from': autocomplete.ModelSelect2(url='location-autocomplete'),
            'location_to': autocomplete.ModelSelect2(url='location-autocomplete'),
            'addon': autocomplete.ModelSelect2(
                url='addon-autocomplete',
                forward=['service']),
        }


class AgencyExtraServiceForm(forms.ModelForm):
    class Meta:
        model = AgencyExtraService
        fields = ('__all__')
        widgets = {
            'agency': autocomplete.ModelSelect2(url='agency-autocomplete'),
            'service': autocomplete.ModelSelect2(url='extra-autocomplete'),
        }


class AgencyExtraDetailForm(forms.ModelForm):
    class Meta:
        model = AgencyExtraDetail
        fields = ('__all__')
        widgets = {
            'agency_service': autocomplete.ModelSelect2(
                url='disabled-autocomplete',
                attrs={'disabled': 'true'}),
            'addon': autocomplete.ModelSelect2(
                url='addon-autocomplete',
                forward=['agency_service']),
        }


class AgencyExtraDetailInlineForm(forms.ModelForm):
    class Meta:
        fields = ('__all__')
        widgets = {
            'addon': autocomplete.ModelSelect2(
                url='addon-autocomplete',
                forward=['service']),
        }


class AllotmentRoomTypeInlineForm(forms.ModelForm):
    class Meta:
        fields = ('__all__')
        widgets = {
            'room_type': autocomplete.ModelSelect2(url='roomtype-autocomplete'),
        }


class ExtraAddonInlineForm(forms.ModelForm):
    class Meta:
        fields = ('__all__')
        widgets = {
            'addon': autocomplete.ModelSelect2(url='addon-autocomplete'),
        }


class ServiceAddonInlineForm(forms.ModelForm):
    class Meta:
        fields = ('__all__')
        widgets = {
            'addon': autocomplete.ModelSelect2(url='addon-autocomplete'),
        }


class PricesExportForm(forms.Form):
    agency = forms.ModelChoiceField(queryset=Agency.objects.all(),
                                    label='Pick Agency to export prices for')
    start_date = forms.DateField(label='Starting Date', required=False,
                                 widget=AdminDateWidget())
    end_date = forms.DateField(label='End Date', required=False,
                               widget=AdminDateWidget())


class ExtraForm(forms.ModelForm):
    class Meta:
        fields = ('__all__')
        widgets = {
            'car_rental': autocomplete.ModelSelect2(url='carrental-autocomplete'),
            'location': autocomplete.ModelSelect2(url='location-autocomplete'),
        }


class ExtraComponentInlineForm(forms.ModelForm):
    class Meta:
        fields = ('__all__')
        widgets = {
            'component': autocomplete.ModelSelect2(url='extra-autocomplete'),
        }


class ServiceForm(forms.ModelForm):
    search_location = forms.ModelChoiceField(
        queryset=Location.objects.all(),
        empty_label='',
        required=False,
        widget=autocomplete.ModelSelect2(
            url='location-autocomplete',
        ),
        label='Search Location',
    )


class BaseBookDataForm(forms.Form):
    search_location = forms.ModelChoiceField(
        queryset=Location.objects.all(),
        empty_label='',
        required=False,
        widget=autocomplete.ModelSelect2(
            url='location-autocomplete',
        ),
        label='Search Location',
    )


class ServiceBookDetailForm(forms.ModelForm, BaseBookDataForm):
    class Meta:
        fields = ('__all__')
        widgets = {
            'service': autocomplete.ModelSelect2(
                url='disabled-autocomplete',
                ),
            'base_service': autocomplete.ModelSelect2(
                url='service-autocomplete',
                forward=['search_location'],
                ),
        }


class ServiceBookDetailAllotmentForm(forms.ModelForm, BaseBookDataForm):
    class Meta:
        fields = ('__all__')
        widgets = {
            'service': autocomplete.ModelSelect2(
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
        }


class ServiceBookDetailTransferForm(forms.ModelForm, BaseBookDataForm):
    class Meta:
        fields = ('__all__')
        widgets = {
            'service': autocomplete.ModelSelect2(
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
        }


class ServiceBookDetailExtraForm(forms.ModelForm, BaseBookDataForm):
    class Meta:
        fields = ('__all__')
        widgets = {
            'service': autocomplete.ModelSelect2(
                url='disabled-autocomplete',
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
        }


class SearchServiceForm(forms.Form):
    parent_id = forms.IntegerField(widget=forms.HiddenInput())
    search_service_location = forms.ModelChoiceField(
        queryset=Location.objects.all(),
        empty_label='',
        required=False,
        widget=autocomplete.ModelSelect2(
            url='location-autocomplete',
        ),
        label='Search Location',
    )
    service = forms.ModelChoiceField(
        queryset=Service.objects.all(),
        empty_label='',
        required=True,
        widget=autocomplete.ModelSelect2(
            url='service-autocomplete',
            forward=['current_service_id', 'search_service_location',],
        ),
        label='Service',
    )
