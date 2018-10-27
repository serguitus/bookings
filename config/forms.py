from dal import autocomplete

from django import forms

from config.models import (
    ProviderAllotmentService, ProviderTransferService, ProviderExtraService,
    AgencyAllotmentService, AgencyTransferService, AgencyExtraService,
)


class ProviderAllotmentServiceForm(forms.ModelForm):
    class Meta:
        model = ProviderAllotmentService
        fields = ('__all__')
        widgets = {
            'provider': autocomplete.ModelSelect2(url='provider-autocomplete'),
            'service': autocomplete.ModelSelect2(url='allotment-autocomplete'),
        }


class ProviderAllotmentDetailInlineForm(forms.ModelForm):
    class Meta:
        fields = ('__all__')
        widgets = {
            'room_type': autocomplete.ModelSelect2(url='roomtype-autocomplete'),
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
            'room_type': autocomplete.ModelSelect2(url='roomtype-autocomplete'),
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
