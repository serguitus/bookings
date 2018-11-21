from common import filters

from config.models import Location


class RoomTypeTopFilter(filters.ForeignKeyFilter):

    autocomplete_url = 'roomtype-autocomplete'


class LocationForProviderTransferTopFilter(filters.ForeignKeyFilter):

    filter_queryset = Location.objects.all()
    autocomplete_url = 'location-autocomplete'

    def queryset(self, request, queryset):
        search_option = self._values[0]
        if search_option and search_option != []:
            lookup = 'providertransferdetail__p_location_from__in'
            queryset = queryset.distinct()
            queryset = queryset.filter(**{lookup: search_option})
        return queryset
