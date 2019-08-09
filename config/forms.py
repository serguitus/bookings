# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from dal import autocomplete

from django import forms

from config.models import (
    ProviderAllotmentService, ProviderTransferService, ProviderExtraService,
    AgencyAllotmentService, AgencyTransferService, AgencyExtraService,
)
from finance.models import Agency


class LocationTransferIntervalInlineForm(forms.ModelForm):
    class Meta:
        fields = ('__all__')
        widgets = {
            't_location_from': autocomplete.ModelSelect2(url='location-autocomplete'),
        }


class ProviderAllotmentServiceForm(forms.ModelForm):
    class Meta:
        model = ProviderAllotmentService
        fields = ('__all__')
        widgets = {
            'service': autocomplete.ModelSelect2(url='allotment-autocomplete'),
            'provider': autocomplete.ModelSelect2(url='provider-autocomplete'),
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
        }


class ProviderTransferServiceForm(forms.ModelForm):
    class Meta:
        model = ProviderTransferService
        fields = ('__all__')
        widgets = {
            'provider': autocomplete.ModelSelect2(url='provider-autocomplete'),
            'service': autocomplete.ModelSelect2(url='transfer-autocomplete'),
        }


class ProviderTransferDetailInlineForm(forms.ModelForm):
    class Meta:
        fields = ('__all__')
        widgets = {
            'p_location_from': autocomplete.ModelSelect2(url='location-autocomplete'),
            'p_location_to': autocomplete.ModelSelect2(url='location-autocomplete'),
        }


class ProviderExtraDetailInlineForm(forms.ModelForm):
    class Meta:
        fields = ('__all__')
        widgets = {
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


class AgencyAllotmentServiceForm(forms.ModelForm):
    class Meta:
        model = AgencyAllotmentService
        fields = ('__all__')
        widgets = {
            'agency': autocomplete.ModelSelect2(url='agency-autocomplete'),
            'service': autocomplete.ModelSelect2(url='allotment-autocomplete'),
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
        }


class AgencyTransferServiceForm(forms.ModelForm):
    class Meta:
        model = AgencyTransferService
        fields = ('__all__')
        widgets = {
            'agency': autocomplete.ModelSelect2(url='agency-autocomplete'),
            'service': autocomplete.ModelSelect2(url='transfer-autocomplete'),
        }


class AgencyTransferDetailInlineForm(forms.ModelForm):
    class Meta:
        fields = ('__all__')
        widgets = {
            'a_location_from': autocomplete.ModelSelect2(url='location-autocomplete'),
            'a_location_to': autocomplete.ModelSelect2(url='location-autocomplete'),
        }


class AgencyExtraDetailInlineForm(forms.ModelForm):
    class Meta:
        fields = ('__all__')
        widgets = {
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
    # action = forms.CharField(widget=forms.widgets.HiddenInput, default='export_prices')
    agency = forms.ModelChoiceField(queryset=Agency.objects.all(),
                                    label='Pick Agency to export prices for')
    start_date = forms.DateField(label='Starting Date', required=False)
    end_date = forms.DateField(label='End Date', required=False)
