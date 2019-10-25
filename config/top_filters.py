from datetime import date, timedelta

from django.db.models import Q

from common import filters

from config.models import Location


class RoomTypeTopFilter(filters.ForeignKeyFilter):
    filter_title = 'Select Room Types'
    autocomplete_url = 'roomtype-autocomplete'


class AddonTopFilter(filters.ForeignKeyFilter):
    filter_title = 'Select Addons'
    autocomplete_url = 'addon-autocomplete'


class ServiceCategoryTopFilter(filters.ForeignKeyFilter):
    filter_title = 'Select categories'
    autocomplete_url = 'servicecategory-autocomplete'


class LocationTopFilter(filters.ForeignKeyFilter):
    filter_title = 'Select Locations'
    autocomplete_url = 'location-autocomplete'


class ZoneTopFilter(filters.ForeignKeyFilter):
    filter_title = 'Select Zones'
    autocomplete_url = 'zone-autocomplete'


class AllotmentTopFilter(filters.ForeignKeyFilter):
    filter_title = 'Select Accomodations'
    autocomplete_url = 'allotment-autocomplete'


class TransferTopFilter(filters.ForeignKeyFilter):
    filter_title = 'Select Transfers'
    autocomplete_url = 'transfer-autocomplete'


class ExtraTopFilter(filters.ForeignKeyFilter):
    filter_title = 'Select Extras'
    autocomplete_url = 'extra-autocomplete'


class LocationForProviderTransferTopFilter(filters.ForeignKeyFilter):
    filter_field_path = 'loc1'
    filter_title = 'Select Locations'
    filter_queryset = Location.objects.all()
    autocomplete_url = 'location-autocomplete'

    def queryset(self, request, queryset):
        search_option = self._values[0]
        if search_option and search_option != []:
            queryset = queryset.distinct()
            queryset = queryset.filter(
                Q(providertransferdetail__p_location_from__in=search_option) |
                Q(providertransferdetail__p_location_to__in=search_option))
        return queryset

class ExtraLocationForProviderTransferTopFilter(filters.ForeignKeyFilter):
    filter_field_path = 'loc2'
    filter_title = 'Select Other Locations'
    filter_queryset = Location.objects.all()
    autocomplete_url = 'location-autocomplete'

    def queryset(self, request, queryset):
        search_option = self._values[0]
        if search_option and search_option != []:
            queryset = queryset.distinct()
            queryset = queryset.filter(
                Q(providertransferdetail__p_location_from__in=search_option) |
                Q(providertransferdetail__p_location_to__in=search_option))
        return queryset


class LocationForAgencyTransferTopFilter(filters.ForeignKeyFilter):
    filter_field_path = 'loc1'
    filter_title = 'Select Locations'
    filter_queryset = Location.objects.all()
    autocomplete_url = 'location-autocomplete'

    def queryset(self, request, queryset):
        search_option = self._values[0]
        if search_option and search_option != []:
            queryset = queryset.distinct()
            queryset = queryset.filter(
                Q(agencytransferdetail__a_location_from__in=search_option) |
                Q(agencytransferdetail__a_location_to__in=search_option))
        return queryset


class ExtraLocationForAgencyTransferTopFilter(filters.ForeignKeyFilter):
    filter_field_path = 'loc2'
    filter_title = 'Select Other Locations'
    filter_queryset = Location.objects.all()
    autocomplete_url = 'location-autocomplete'

    def queryset(self, request, queryset):
        search_option = self._values[0]
        if search_option and search_option != []:
            queryset = queryset.distinct()
            queryset = queryset.filter(
                Q(agencytransferdetail__a_location_from__in=search_option) |
                Q(agencytransferdetail__a_location_to__in=search_option))
        return queryset


class DateToTopFilter(filters.DateFilter):
    default_value = [date.today() - timedelta(days=30), None]
