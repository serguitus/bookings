from datetime import date, timedelta

from django.db.models import F, Q

from common import filters

from config.models import Location, Transfer, Provider


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


class AllotmentTopFilter(filters.ForeignKeyFilter):
    filter_title = 'Select Accomodations'
    autocomplete_url = 'allotment-autocomplete'


class TransferTopFilter(filters.ForeignKeyFilter):
    filter_title = 'Select Transfers'
    autocomplete_url = 'transfer-autocomplete'


class ProviderDetailTransferTopFilter(filters.ForeignKeyFilter):
    filter_field_path = 'provider_service__service'
    filter_title = 'Select Transfers'
    filter_queryset = Transfer.objects.all()
    autocomplete_url = 'transfer-autocomplete'

    def queryset(self, request, queryset):
        search_option = self._values[0]
        if search_option and search_option != []:
            queryset = queryset.distinct()
            queryset = queryset.filter(
                Q(provider_service__service__in=search_option))
        return queryset


class TransferDetailProviderTopFilter(filters.ForeignKeyFilter):
    filter_field_path = 'provider_service__provider'
    filter_title = 'Select Providers'
    filter_queryset = Provider.objects.all()
    autocomplete_url = 'provider-autocomplete'

    def queryset(self, request, queryset):
        search_option = self._values[0]
        if search_option and search_option != []:
            queryset = queryset.distinct()
            queryset = queryset.filter(
                Q(provider_service__provider__in=search_option))
        return queryset


class ExtraTopFilter(filters.ForeignKeyFilter):
    filter_title = 'Select Extras'
    autocomplete_url = 'extra-autocomplete'


class ProviderTransferDetailLocationTopFilter(filters.ForeignKeyFilter):
    filter_field_path = 'Location'
    filter_title = 'Select Locations'
    filter_queryset = Location.objects.all()
    autocomplete_url = 'location-autocomplete'

    def queryset(self, request, queryset):
        search_option = self._values[0]
        if search_option and search_option != []:
            queryset = queryset.distinct()
            if len(search_option) == 1:
                queryset = queryset.filter(
                    Q(location_from=search_option[0]) |
                    Q(location_to=search_option[0]))
            else:
                queryset = queryset.filter(
                    (
                        Q(location_from__in=search_option) &
                        Q(location_to__in=search_option) &
                        ~Q(location_from=F('location_to'))
                    )
                )

        return queryset


class ProviderTransferLocationTopFilter(filters.ForeignKeyFilter):
    filter_field_path = 'loc1'
    filter_title = 'Select Locations'
    filter_queryset = Location.objects.all()
    autocomplete_url = 'location-autocomplete'

    def queryset(self, request, queryset):
        search_option = self._values[0]
        if search_option and search_option != []:
            queryset = queryset.distinct()
            queryset = queryset.filter(
                Q(providertransferdetail__location_from__in=search_option) |
                Q(providertransferdetail__location_to__in=search_option))
        return queryset


class ProviderTransferLocationAdditionalTopFilter(filters.ForeignKeyFilter):
    filter_field_path = 'loc2'
    filter_title = 'Select Other Locations'
    filter_queryset = Location.objects.all()
    autocomplete_url = 'location-autocomplete'

    def queryset(self, request, queryset):
        search_option = self._values[0]
        if search_option and search_option != []:
            queryset = queryset.distinct()
            queryset = queryset.filter(
                Q(providertransferdetail__location_from__in=search_option) |
                Q(providertransferdetail__location_to__in=search_option))
        return queryset


class AgencyTransferLocationTopFilter(filters.ForeignKeyFilter):
    filter_field_path = 'loc1'
    filter_title = 'Select Locations'
    filter_queryset = Location.objects.all()
    autocomplete_url = 'location-autocomplete'

    def queryset(self, request, queryset):
        search_option = self._values[0]
        if search_option and search_option != []:
            queryset = queryset.distinct()
            queryset = queryset.filter(
                Q(agencytransferdetail__location_from__in=search_option) |
                Q(agencytransferdetail__location_to__in=search_option))
        return queryset


class AgencyTransferLocationAdditionalTopFilter(filters.ForeignKeyFilter):
    filter_field_path = 'loc2'
    filter_title = 'Select Other Locations'
    filter_queryset = Location.objects.all()
    autocomplete_url = 'location-autocomplete'

    def queryset(self, request, queryset):
        search_option = self._values[0]
        if search_option and search_option != []:
            queryset = queryset.distinct()
            queryset = queryset.filter(
                Q(agencytransferdetail__location_from__in=search_option) |
                Q(agencytransferdetail__location_to__in=search_option))
        return queryset


class DateTopFilter(filters.DateFilter):
    default_value = [date.today() - timedelta(days=30), None]


class PackageTopFilter(filters.ForeignKeyFilter):
    filter_title = 'Select Packages'
    autocomplete_url = 'package-autocomplete'

