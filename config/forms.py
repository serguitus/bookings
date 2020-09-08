# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column
from dal import autocomplete

from django import forms
from django.contrib.admin.widgets import AdminDateWidget
from django.forms import widgets

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
                url='disabled-autocomplete',),
            'room_type': autocomplete.ModelSelect2(
                url='roomtype-autocomplete',
                forward=['provider_service']),
            'board_type': autocomplete.ListSelect2(
                url='boardtype-autocomplete',
                forward=['provider_service']),
            'addon': autocomplete.ModelSelect2(
                url='catalogallotmentaddon-autocomplete',
                forward=['provider_service']),
        }
    class Media:
        js = ['config/js/config_extras.js']


class ProviderAllotmentDetailInlineForm(forms.ModelForm):
    class Meta:
        fields = ('__all__')
        widgets = {
            'room_type': autocomplete.ModelSelect2(
                url='roomtype-autocomplete',
                forward=['service'],
                attrs={'data-placeholder': 'Room Type'}),
            'board_type': autocomplete.ListSelect2(
                url='boardtype-autocomplete',
                forward=['service'],
                attrs={'data-placeholder': 'Board Type'}),
            # 'addon': autocomplete.ModelSelect2(
            #     url='catalogallotmentaddon-autocomplete',
            #     forward=['service'],
            #     attrs={'data-placeholder': 'Addon'}),
        }

    def __init__(self, *args, **kwargs):
        super(ProviderAllotmentDetailInlineForm, self).__init__(*args, **kwargs)
        self.fields['pax_range_min'].widget.attrs['placeholder'] = 'Pax Min'
        self.fields['pax_range_min'].label = 'Pax Min'
        self.fields['pax_range_max'].widget.attrs['placeholder'] = 'Pax Max'
        self.fields['pax_range_max'].label = 'Pax Max'
        self.fields['ad_1_amount'].widget.attrs['placeholder'] = 'SGL'
        self.fields['ch_1_ad_1_amount'].widget.attrs['placeholder'] = '1st Chd'
        self.fields['ch_2_ad_1_amount'].widget.attrs['placeholder'] = '2nd Chd'
        self.fields['ad_2_amount'].widget.attrs['placeholder'] = 'DBL'
        self.fields['ch_1_ad_2_amount'].widget.attrs['placeholder'] = '1st Chd'
        self.fields['ch_2_ad_2_amount'].widget.attrs['placeholder'] = '2nd Chd'
        self.fields['ad_3_amount'].widget.attrs['placeholder'] = 'TPL'
        self.fields['ch_1_ad_3_amount'].widget.attrs['placeholder'] = '1st Chd'
        self.fields['ad_4_amount'].widget.attrs['placeholder'] = 'QUAD'


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
                url='disabled-autocomplete',),
            'location_from': autocomplete.ModelSelect2(url='location-autocomplete'),
            'location_to': autocomplete.ModelSelect2(url='location-autocomplete'),
            'addon': autocomplete.ModelSelect2(
                url='catalogtransferaddon-autocomplete',
                forward=['provider_service']),
        }


class ProviderTransferDetailInlineForm(forms.ModelForm):
    class Meta:
        fields = ('__all__')
        widgets = {
            'location_from': autocomplete.ModelSelect2(url='location-autocomplete'),
            'location_to': autocomplete.ModelSelect2(url='location-autocomplete'),
            'addon': autocomplete.ModelSelect2(
                url='catalogtransferaddon-autocomplete',
                forward=['service']),
        }

    def __init__(self, *args, **kwargs):
        super(ProviderTransferDetailInlineForm, self).__init__(*args, **kwargs)
        self.fields['location_from'].widget.attrs['placeholder'] = 'Select Location'
        self.fields['location_from'].label = 'Origin'
        self.fields['location_to'].widget.attrs['placeholder'] = 'Select Location'
        self.fields['location_to'].label = 'Destination'
        self.fields['pax_range_max'].widget.attrs['placeholder'] = 'Pax Max'
        self.fields['pax_range_max'].label = 'Pax Max'
        self.fields['pax_range_min'].widget.attrs['placeholder'] = 'Pax Min'
        self.fields['pax_range_min'].label = 'Pax Min'
        self.fields['ad_1_amount'].widget.attrs['placeholder'] = 'Adult'
        self.fields['ad_1_amount'].label = 'Cost'
        self.fields['ch_1_ad_1_amount'].widget.attrs['placeholder'] = 'Child'
        self.fields['ch_1_ad_1_amount'].label = 'Chd Cost'


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
                url='disabled-autocomplete',),
            'addon': autocomplete.ModelSelect2(
                url='catalogextraaddon-autocomplete',
                forward=['provider_service']),
        }


class ProviderExtraDetailInlineForm(forms.ModelForm):
    class Meta:
        fields = ('__all__')
        widgets = {
            'addon': autocomplete.ModelSelect2(
                url='catalogextraaddon-autocomplete',
                forward=['service']),
        }

    def __init__(self, *args, **kwargs):
        super(ProviderExtraDetailInlineForm, self).__init__(*args, **kwargs)
        self.fields['pax_range_max'].widget.attrs['placeholder'] = 'Pax Max'
        self.fields['pax_range_max'].label = 'Pax Max'
        self.fields['pax_range_min'].widget.attrs['placeholder'] = 'Pax Min'
        self.fields['pax_range_min'].label = 'Pax Min'
        self.fields['ad_1_amount'].widget.attrs['placeholder'] = 'Adult'
        self.fields['ad_1_amount'].label = 'Cost'
        # self.fields['ch_1_ad_1_amount'].widget.attrs['placeholder'] = 'Child'
        # self.fields['ch_1_ad_1_amount'].label = 'Chd Cost'


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
                url='disabled-autocomplete',),
            'room_type': autocomplete.ModelSelect2(
                url='roomtype-autocomplete',
                forward=['agency_service']),
            'board_type': autocomplete.ListSelect2(
                url='boardtype-autocomplete',
                forward=['agency_service']),
            'addon': autocomplete.ModelSelect2(
                url='catalogallotmentaddon-autocomplete',
                forward=['service']),
        }


class AgencyAllotmentDetailInlineForm(ProviderAllotmentDetailInlineForm):
    class Meta:
        fields = ('__all__')
        widgets = {
            'room_type': autocomplete.ModelSelect2(
                url='roomtype-autocomplete',
                forward=['service'],
                attrs={'data-placeholder': 'Room Type'}),
            'board_type': autocomplete.ListSelect2(
                url='boardtype-autocomplete',
                forward=['service'],
                attrs={'data-placeholder': 'Board Type'}),
            #'addon': autocomplete.ModelSelect2(
            #    url='catalogallotmentaddon-autocomplete',
            #    forward=['service']),
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
                url='disabled-autocomplete',),
            'location_from': autocomplete.ModelSelect2(url='location-autocomplete'),
            'location_to': autocomplete.ModelSelect2(url='location-autocomplete'),
            'addon': autocomplete.ModelSelect2(
                url='catalogtransferaddon-autocomplete',
                forward=['agency_service']),
        }


class AgencyTransferDetailInlineForm(ProviderTransferDetailInlineForm):
    class Meta:
        fields = ('__all__')
        widgets = {
            'location_from': autocomplete.ModelSelect2(
                url='location-autocomplete'),
            'location_to': autocomplete.ModelSelect2(
                url='location-autocomplete'),
            'addon': autocomplete.ModelSelect2(
                url='catalogtransferaddon-autocomplete',
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
                url='disabled-autocomplete',),
            'addon': autocomplete.ModelSelect2(
                url='catalogextraaddon-autocomplete',
                forward=['agency_service']),
        }


class AgencyExtraDetailInlineForm(ProviderExtraDetailInlineForm):
    class Meta:
        fields = ('__all__')
        widgets = {
            'addon': autocomplete.ModelSelect2(
                url='catalogextraaddon-autocomplete',
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
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'cols': 80,
                'rows': 5,
                'placeholder': 'Service description...',
            }),
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
            attrs={'dropdownParent': '#searchServiceModal',
                   'data-placeholder': 'Filter by Location'},
        ),
        label='',
    )
    search_service = forms.ModelChoiceField(
        queryset=Service.objects.all(),
        empty_label='',
        required=True,
        widget=autocomplete.ModelSelect2(
            url='service-autocomplete',
            attrs={'dropdownParent': '#searchServiceModal',
                   'data-placeholder': 'Select Service to add'},
            forward=['current_service_id', 'search_service_location'],
        ),
        label='',
    )
    make_package = forms.BooleanField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Row(
                Column('search_service_location', css_class='form-group col-md-6 mb-0'),
                Column('search_service', css_class='form-group col-md-6 mb-0'),
                # css_class='form-row'
            ),
            Row(
                Column('make_package', css_class='form-group col-md-12 mb-0'),
                css_class='package-checkbox'
            ),
            'parent_id',
        )


class ExtendCatalogForm(forms.Form):
    _selected_action = forms.CharField(widget=forms.MultipleHiddenInput)
    max_util = forms.IntegerField(required=False,
                                  label='',
                                  help_text='Optionally specify maximum increment',
                                  widget=forms.NumberInput(
                                      attrs={'placeholder': 'Max. Increment'}))
    min_util = forms.IntegerField(required=False,
                                  label='',
                                  help_text='Optionally specify minimum increment',
                                  widget=forms.NumberInput(
                                      attrs={'placeholder': 'Min. Increment'}))
    diff_percent = forms.IntegerField(required=False,
                                      label='',
                                      help_text='Specify a percent value to alter generated values',
                                      widget=forms.NumberInput(
                                          attrs={'placeholder': 'Increment (%)'}))
    diff_value = forms.IntegerField(required=False,
                                    label='',
                                    help_text='Specify an absolute value to alter generated numbers',
                                    widget=forms.NumberInput(
                                        attrs={'placeholder': 'Increment (Abs.)'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Row(
                Column('min_util', css_class='form-group col-md-6 mb-0'),
                Column('max_util', css_class='form-group col-md-6 mb-0'),
                # css_class='form-row'
            ),
            Row(
                Column('diff_percent', css_class='form-group col-md-6 mb-0'),
                Column('diff_value', css_class='form-group col-md-6 mb-0'),
                # css_class='form-row'
            ),
            '_selected_action',
        )
