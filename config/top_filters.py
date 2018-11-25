from django.db.models import Q

from common import filters

from config.models import Location


class RoomTypeTopFilter(filters.ForeignKeyFilter):
    filter_title = 'Select Room Types'
    autocomplete_url = 'roomtype-autocomplete'


class LocationTopFilter(filters.ForeignKeyFilter):
    filter_title = 'Select Locations'
    autocomplete_url = 'location-autocomplete'


class LocationForProviderTransferTopFilter(filters.ForeignKeyFilter):
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
