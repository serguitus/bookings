# -*- coding: utf-8 -*-
from __future__ import unicode_literals
# Config Models
from datetime import time
from django.db import models
from django.urls import reverse

from config.constants import (
    ROOM_CAPACITIES, BOARD_TYPES, AMOUNTS_BY_PAX,
    SERVICE_CATEGORIES,
    SERVICE_CATEGORY_ALLOTMENT, SERVICE_CATEGORY_TRANSFER, SERVICE_CATEGORY_EXTRA,
    ALLOTMENT_AMOUNTS_TYPES, TRANSFER_AMOUNTS_TYPES, EXTRA_AMOUNTS_TYPES,
    EXTRA_PARAMETER_TYPES, EXTRA_PARAMETER_TYPE_HOURS,)

from finance.models import Agency, Provider

from reservas.custom_settings import ADDON_FOR_NO_ADDON


# Utility method to get a list of
# Service child objects from a Service list
def _get_child_objects(services):
    objs = []
    for service in services:
        obj = SERVICE_MODELS[service.category].objects.get(id=service.id)
        objs.append(obj)
    return objs


class Location(models.Model):
    """
    Location
    """
    class Meta:
        verbose_name = 'Location'
        verbose_name_plural = 'Locations'
        unique_together = (('name',),)
    name = models.CharField(max_length=50)
    enabled = models.BooleanField(default=True)
    short_name = models.CharField(max_length=10, blank=True, null=True)
    ordering = ['name']

    def __str__(self):
        return self.name


class Place(models.Model):
    """
    Place
    """
    class Meta:
        verbose_name = 'Place'
        verbose_name_plural = 'Places'
        unique_together = (('location', 'name',),)
    location = models.ForeignKey(Location,
                                 on_delete=models.CASCADE)
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class TransferInterval(models.Model):
    """
    TransferInterval
    """
    class Meta:
        verbose_name = 'Transfer Interval'
        verbose_name_plural = 'Transfers Intervals'
        unique_together = (('location', 't_location_from',),)
    location = models.ForeignKey(Location,
                                 on_delete=models.CASCADE)
    t_location_from = models.ForeignKey(
        Location,
        on_delete=models.CASCADE,
        related_name='t_location_from',
        verbose_name='Location From')
    interval = models.TimeField()


class Schedule(models.Model):
    """
    Schedule
    """
    class Meta:
        verbose_name = 'Schedule'
        verbose_name_plural = 'Schedules'
        unique_together = (('location', 'number', 'is_arrival'),)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    number = models.CharField(max_length=20)
    is_arrival = models.BooleanField()
    time = models.TimeField()

    def __str__(self):
        return '%s' % self.number


class ServiceCategory(models.Model):
    """
    ServiceCategory
    """
    class Meta:
        verbose_name = 'Service Category'
        verbose_name_plural = 'Services Categories'
        unique_together = (('name',),)
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class RoomType(models.Model):
    """
    RoomType
    """
    class Meta:
        verbose_name = 'Room Type'
        verbose_name_plural = 'Rooms Types'
        unique_together = (('name',),)
        ordering = ['name']
    name = models.CharField(max_length=50)
    enabled = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Addon(models.Model):
    """
    Addon
    """
    class Meta:
        verbose_name = 'Addon'
        verbose_name_plural = 'Addons'
        unique_together = (('name',),)
        ordering = ['name']
    name = models.CharField(max_length=50)
    enabled = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class CarRental(models.Model):
    """
    CarRental
    """
    class Meta:
        verbose_name = 'Car Rental'
        verbose_name_plural = 'Cars Rentals'
        unique_together = (('name',),)
    name = models.CharField(max_length=30)

    def __str__(self):
        return '%s' % (self.name)


class CarRentalOffice(models.Model):
    """
    CarRentalOffice
    """
    class Meta:
        verbose_name = 'Car Rental Office'
        verbose_name_plural = 'Cars Rentals Offices'
        unique_together = (('car_rental', 'office',),)
    car_rental = models.ForeignKey(CarRental, on_delete=models.CASCADE)
    office = models.CharField(max_length=60)

    def __str__(self):
        return '%s - %s' % (self.car_rental, self.office)


class RelativeInterval(models.Model):
    class Meta:
        abstract = True
    days_after = models.SmallIntegerField(
        default=0, blank=True, null=True, verbose_name='Days after')
    days_duration = models.SmallIntegerField(
        default=0, blank=True, null=True, verbose_name='Days duration')


class RouteData(models.Model):
    """
    Transfer Data
    """
    class Meta:
        abstract = True
    location_from = models.ForeignKey(
        Location, on_delete=models.CASCADE,
        related_name='%(class)s_location_from', verbose_name='Location from')
    location_to = models.ForeignKey(
        Location, on_delete=models.CASCADE,
        related_name='%(class)s_location_to', verbose_name='Location to')


class Service(models.Model):
    """
    Service
    """
    class Meta:
        verbose_name = 'Service'
        verbose_name_plural = 'Services'
        unique_together = (('category', 'name'),)
    name = models.CharField(max_length=150)
    description = models.CharField(max_length=3000, blank=True, null=True)
    included_services = models.CharField(max_length=500, blank=True, null=True)
    service_category = models.ForeignKey(
        ServiceCategory,
        on_delete=models.CASCADE,
        blank=True, null=True,
        verbose_name='Category')
    category = models.CharField(max_length=5, choices=SERVICE_CATEGORIES)
    grouping = models.BooleanField(default=False)
    pax_range = models.BooleanField(default=False)
    child_age = models.IntegerField(blank=True, null=True)
    child_discount_percent = models.IntegerField(blank=True, null=True)
    infant_age = models.IntegerField(default=2, blank=True, null=True)
    location = models.ForeignKey(Location,
                                 on_delete=models.CASCADE,
                                 blank=True, null=True)
    new_time = models.TimeField(blank=True, null=True)
    enabled = models.BooleanField(default=True)
    default_as_package = models.BooleanField(default=False)
    is_internal = models.BooleanField(default=False, verbose_name='No Voucher')

    def __init__(self, *args, **kwargs):
        # Call the "real" __init__ method.
        super(Service, self).__init__(*args, **kwargs)
        self.fill_data()

    def fill_data(self):
        pass

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.fill_data()
        # Call the "real" save method.
        super(Service, self).save(force_insert, force_update, using, update_fields)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return _get_child_objects([self])[0].get_absolute_url()


class Chain(models.Model):
    """
    Chain
    """
    class Meta:
        verbose_name = 'Chain'
        verbose_name_plural = 'Chains'
    name = models.CharField(max_length=150)

    def __str__(self):
        return self.name


class Allotment(Service):
    """
    Accomodation
    """
    class Meta:
        verbose_name = 'Accomodation'
        verbose_name_plural = 'Accomodations'
    cost_type = models.CharField(
        max_length=5, choices=ALLOTMENT_AMOUNTS_TYPES, default=AMOUNTS_BY_PAX)
    time_from = models.TimeField(default='16:00')
    time_to = models.TimeField(default='12:00')
    address = models.CharField(max_length=75, blank=True, null=True)
    phone = models.CharField(max_length=30, blank=True, null=True)
    is_shared_point = models.BooleanField(default=False)
    chain = models.ForeignKey(
        Chain, on_delete=models.CASCADE, blank=True, null=True)

    def fill_data(self):
        super(Allotment, self).fill_data()
        self.category = SERVICE_CATEGORY_ALLOTMENT
        self.grouping = True

    def get_absolute_url(self):
        return reverse('common:config_allotment_change', args=[self.id])


class Transfer(Service):
    """
    Transfer
    """
    class Meta:
        verbose_name = 'Transfer'
        verbose_name_plural = 'Transfers'
    cost_type = models.CharField(max_length=5, choices=TRANSFER_AMOUNTS_TYPES)
    max_capacity = models.IntegerField(blank=True, null=True)
    is_shared = models.BooleanField(default=False)
    has_pickup_time = models.BooleanField(default=False)
    is_ticket = models.BooleanField(default=False)

    def fill_data(self):
        super(Transfer, self).fill_data()
        self.category = SERVICE_CATEGORY_TRANSFER
        self.grouping = False

    def get_absolute_url(self):
        return reverse('common:config_transfer_change', args=[self.id])


class Extra(Service):
    """
    Extra
    """
    class Meta:
        verbose_name = 'Extra'
        verbose_name_plural = 'Extras'
    cost_type = models.CharField(
        max_length=5, choices=EXTRA_AMOUNTS_TYPES)
    parameter_type = models.CharField(
        max_length=5, choices=EXTRA_PARAMETER_TYPES)
    has_pax_range = models.BooleanField(default=False)
    max_capacity = models.IntegerField(blank=True, null=True)
    car_rental = models.ForeignKey(CarRental,
                                   on_delete=models.CASCADE,
                                   blank=True, null=True)

    def fill_data(self):
        super(Extra, self).fill_data()
        self.category = SERVICE_CATEGORY_EXTRA
        self.grouping = False

    def __str__(self):
        if self.parameter_type == EXTRA_PARAMETER_TYPE_HOURS:
            return '%s (Hours)' % self.name
        return '%s' % self.name

    def get_absolute_url(self):
        return reverse('common:config_extra_change', args=[self.id])


class BookServiceData(models.Model):
    """
    Book Data
    """
    class Meta:
        abstract = True
    name = models.CharField(max_length=250, default='Detail')
    description = models.CharField(max_length=1000, blank=True, null=True)
    base_service = models.ForeignKey(Service,
                                     on_delete=models.CASCADE,
                                     related_name='%(class)s_base_service')
    base_location = models.ForeignKey(
        Location,
        on_delete=models.CASCADE,
        related_name='%(class)s_base_location',
        blank=True, null=True,
        verbose_name='Location')
    provider = models.ForeignKey(Provider,
                                 on_delete=models.CASCADE,
                                 blank=True, null=True)
    service_addon = models.ForeignKey(
        Addon, on_delete=models.CASCADE,
        related_name='%(class)s_service_addon',
        blank=True, null=True,
        verbose_name='Addon')
    time = models.TimeField(blank=True, null=True)

    @property
    def service_type(self):
        return self.base_service.category

    @property
    def service_location(self):
        if self.base_location:
            return self.base_location.name


class BookAllotmentData(models.Model):
    """
    Book Allotment Data
    """
    class Meta:
        abstract = True
    room_type = models.ForeignKey(RoomType, on_delete=models.CASCADE,
                                  related_name='%(class)s_room_type')
    board_type = models.CharField(max_length=5, choices=BOARD_TYPES)


class BookTransferData(RouteData):
    """
    Book Transfer Data
    """
    class Meta:
        abstract = True
    quantity = models.SmallIntegerField(default=1)
    place_from = models.ForeignKey(
        Place, on_delete=models.CASCADE,
        related_name='%(class)s_place_from',
        blank=True, null=True)
    schedule_from = models.ForeignKey(
        Schedule, on_delete=models.CASCADE,
        related_name='%(class)s_schedule_from',
        blank=True, null=True)
    pickup = models.ForeignKey(
        Allotment, on_delete=models.CASCADE,
        related_name='%(class)s_pickup',
        null=True, blank=True)
    place_to = models.ForeignKey(Place, on_delete=models.CASCADE,
                                 related_name='%(class)s_place_to',
                                 blank=True, null=True)
    schedule_to = models.ForeignKey(
        Schedule, on_delete=models.CASCADE,
        related_name='%(class)s_schedule_to',
        blank=True, null=True)
    dropoff = models.ForeignKey(
        Allotment, on_delete=models.CASCADE,
        related_name='%(class)s_dropoff',
        null=True, blank=True)
    schedule_time_from = models.TimeField(blank=True, null=True)
    schedule_time_to = models.TimeField(blank=True, null=True)


class BookExtraData(models.Model):
    """
    Book Extra Data
    """
    class Meta:
        abstract = True
    quantity = models.SmallIntegerField(default=1)
    parameter = models.SmallIntegerField(default=0, verbose_name='Hours')
    pickup_office = models.ForeignKey(
        CarRentalOffice, on_delete=models.CASCADE,
        related_name='%(class)s_pickup_office',
        blank=True, null=True)
    dropoff_office = models.ForeignKey(
        CarRentalOffice, on_delete=models.CASCADE,
        related_name='%(class)s_dropoff_office',
        blank=True, null=True)


class ServiceAddon(models.Model):
    """
    ServiceAddon
    """
    class Meta:
        verbose_name = 'Service Addon'
        verbose_name_plural = 'Services Addons'
        unique_together = (('service', 'addon',),)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    addon = models.ForeignKey(Addon, on_delete=models.CASCADE)

    def __str__(self):
        return '%s for %s' % (self.addon, self.service)


class Catalog(models.Model):
    class Meta:
        abstract = True
    contract_code = models.CharField(max_length=40, blank=True, null=False, default='')
    booked_from = models.DateField(blank=True, null=True)
    booked_to = models.DateField(blank=True, null=True)
    date_from = models.DateField()
    date_to = models.DateField()


class ProviderCatalogue(Catalog):
    """
    ProviderCatalogue
    """
    class Meta:
        abstract = True
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE)

    def get_detail_objects(self):
        return None


class AgencyCatalogue(Catalog):
    """
    AgencyCatalogue
    """
    class Meta:
        abstract = True
    agency = models.ForeignKey(Agency, on_delete=models.CASCADE)

    def get_detail_objects(self):
        return None


class AmountDetail(models.Model):
    """
    AmountDetail
    """
    class Meta:
        abstract = True
    ad_1_amount = models.DecimalField(
        max_digits=8, decimal_places=2, blank=True, null=True,
        verbose_name='SGL')
    ad_2_amount = models.DecimalField(
        max_digits=8, decimal_places=2, blank=True, null=True,
        verbose_name='DBL')
    ad_3_amount = models.DecimalField(
        max_digits=8, decimal_places=2, blank=True, null=True,
        verbose_name='TPL')
    ad_4_amount = models.DecimalField(
        max_digits=8, decimal_places=2, blank=True, null=True,
        verbose_name='QAD')
    ch_1_ad_0_amount = models.DecimalField(
        max_digits=8, decimal_places=2, blank=True, null=True,
        verbose_name='1st CHD')
    ch_1_ad_1_amount = models.DecimalField(
        max_digits=8, decimal_places=2, blank=True, null=True,
        verbose_name='1st CHD')
    ch_1_ad_2_amount = models.DecimalField(
        max_digits=8, decimal_places=2, blank=True, null=True,
        verbose_name='1st CHD')
    ch_1_ad_3_amount = models.DecimalField(
        max_digits=8, decimal_places=2, blank=True, null=True,
        verbose_name='1st CHD')
    ch_1_ad_4_amount = models.DecimalField(
        max_digits=8, decimal_places=2, blank=True, null=True,
        verbose_name='1st CHD')
    ch_2_ad_0_amount = models.DecimalField(
        max_digits=8, decimal_places=2, blank=True, null=True,
        verbose_name='2nd CHD')
    ch_2_ad_1_amount = models.DecimalField(
        max_digits=8, decimal_places=2, blank=True, null=True,
        verbose_name='2nd CHD')
    ch_2_ad_2_amount = models.DecimalField(
        max_digits=8, decimal_places=2, blank=True, null=True,
        verbose_name='2nd CHD')
    ch_2_ad_3_amount = models.DecimalField(
        max_digits=8, decimal_places=2, blank=True, null=True,
        verbose_name='2nd CHD')
    ch_2_ad_4_amount = models.DecimalField(
        max_digits=8, decimal_places=2, blank=True, null=True,
        verbose_name='2nd CHD')
    ch_3_ad_0_amount = models.DecimalField(
        max_digits=8, decimal_places=2, blank=True, null=True,
        verbose_name='3rd CHD')
    ch_3_ad_1_amount = models.DecimalField(
        max_digits=8, decimal_places=2, blank=True, null=True,
        verbose_name='3rd CHD')
    ch_3_ad_2_amount = models.DecimalField(
        max_digits=8, decimal_places=2, blank=True, null=True,
        verbose_name='3rd CHD')
    ch_3_ad_3_amount = models.DecimalField(
        max_digits=8, decimal_places=2, blank=True, null=True,
        verbose_name='3rd CHD')
    ch_3_ad_4_amount = models.DecimalField(
        max_digits=8, decimal_places=2, blank=True, null=True,
        verbose_name='3rd CHD')


class AllotmentRoomType(models.Model):
    """
    AllotmentRoomType
    """
    class Meta:
        verbose_name = 'Allotment Room Type'
        verbose_name_plural = 'Allotments Rooms Types'
        unique_together = (('allotment', 'room_type', 'room_capacity'),)
    allotment = models.ForeignKey(Allotment, on_delete=models.CASCADE)
    room_type = models.ForeignKey(RoomType, on_delete=models.CASCADE)
    room_capacity = models.CharField(max_length=5, choices=ROOM_CAPACITIES)

    def __str__(self):
        return '%s (%s)' % (self.room_type, self.get_room_capacity_display())


class AllotmentBoardType(models.Model):
    """
    AccomodationBoardType
    """
    class Meta:
        verbose_name = 'Accomodation Board Type'
        verbose_name_plural = 'Accomodation Board Types'
        unique_together = (('allotment', 'board_type'),)
    allotment = models.ForeignKey(Allotment, on_delete=models.CASCADE)
    board_type = models.CharField(max_length=5, choices=BOARD_TYPES)

    def __str__(self):
        return 'Board {}'.format(self.board_type)


class ProviderAllotmentService(ProviderCatalogue):
    """
    ProviderAccomodationService
    """
    class Meta:
        verbose_name = 'Accomodation Cost'
        verbose_name_plural = 'Accomodation Costs'
        unique_together = (('provider', 'service', 'date_from', 'date_to', 'contract_code'),)
    service = models.ForeignKey(Allotment, on_delete=models.CASCADE)

    def __str__(self):
        return '{} by {} ({} to {})'.format(self.service,
                                            self.provider,
                                            self.date_from,
                                            self.date_to)

    def get_detail_objects(self):
        return self.providerallotmentdetail_set.all()


class ProviderAllotmentDetail(AmountDetail):
    """
    ProviderAccomodationDetail
    """
    class Meta:
        verbose_name = 'Accomodation Cost Detail'
        verbose_name_plural = 'Accomodation Cost Details'
        unique_together = (
            ('provider_service', 'room_type', 'board_type', 'addon',
             'pax_range_min', 'pax_range_max'),)
    provider_service = models.ForeignKey(ProviderAllotmentService,
                                         on_delete=models.CASCADE)
    room_type = models.ForeignKey(RoomType, on_delete=models.CASCADE)
    board_type = models.CharField(max_length=5, choices=BOARD_TYPES)
    addon = models.ForeignKey(Addon, on_delete=models.CASCADE,
                              default=ADDON_FOR_NO_ADDON)
    pax_range_min = models.SmallIntegerField(default=0)
    pax_range_max = models.SmallIntegerField(default=0)
    single_supplement = models.IntegerField(blank=True, null=True,
                                            verbose_name='SGL Suppl.')
    third_pax_discount = models.IntegerField(blank=True, null=True,
                                             verbose_name='TPL Dscnt %')

    def __str__(self):
        return 'Cost for {} ({})'.format(self.provider_service,
                                         self.room_type)


class AgencyAllotmentService(AgencyCatalogue):
    """
    AgencyAccomodationService
    """
    class Meta:
        verbose_name = 'Accomodation Price'
        verbose_name_plural = 'Accomodation Prices'
        unique_together = (('agency', 'service', 'date_from', 'date_to', 'contract_code'),)
    service = models.ForeignKey(Allotment, on_delete=models.CASCADE)

    def __str__(self):
        return '{} for {} ({} to {})'.format(
            self.service,
            self.agency,
            self.date_from,
            self.date_to)

    def get_detail_objects(self):
        return self.agencyallotmentdetail_set.all()


class AgencyAllotmentDetail(AmountDetail):
    """
    AgencyAccomodationDetail
    """
    class Meta:
        verbose_name = 'Accomodation Price Detail'
        verbose_name_plural = 'Accomodation Price Details'
        unique_together = (
            ('agency_service', 'room_type', 'board_type', 'addon',
             'pax_range_min', 'pax_range_max'),)
    agency_service = models.ForeignKey(AgencyAllotmentService,
                                       on_delete=models.CASCADE)
    room_type = models.ForeignKey(RoomType, on_delete=models.CASCADE)
    board_type = models.CharField(max_length=5, choices=BOARD_TYPES)
    addon = models.ForeignKey(Addon, on_delete=models.CASCADE,
                              default=ADDON_FOR_NO_ADDON)
    pax_range_min = models.SmallIntegerField(default=0)
    pax_range_max = models.SmallIntegerField(default=0)

    def __str__(self):
        return 'Price for {} ({})'.format(self.agency_service,
                                          self.room_type)


class TransferZone(models.Model):
    """
    Transfer Zone
    """
    class Meta:
        verbose_name = 'Transfer Zone'
        verbose_name_plural = 'Transfers Zones'
        unique_together = (('transfer', 'name',),)
    name = models.CharField(max_length=50)
    transfer = models.ForeignKey(Transfer, on_delete=models.CASCADE)
    ordering = ['transfer', 'name']

    def __str__(self):
        return '%s - %s' % (self.transfer, self.name)


class TransferPickupTime(models.Model):
    """
    Transfer Pickup Time
    """
    class Meta:
        verbose_name = 'Transfer Pickup Time'
        verbose_name_plural = 'Transfer Pickups Times'
        unique_together = (('transfer_zone', 'location',),)
    transfer_zone = models.ForeignKey(TransferZone, on_delete=models.CASCADE,
                                      verbose_name='Pickup Zone')
    location = models.ForeignKey(Location, on_delete=models.CASCADE,
                                 verbose_name='Dropoff Location')
    pickup_time = models.TimeField()


class AllotmentTransferZone(models.Model):
    """
    Allotment Transfer Zone
    """
    class Meta:
        verbose_name = 'Allotment Transfer Zone'
        verbose_name_plural = 'Allotments Transfers Zones'
        unique_together = (('allotment', 'transfer_zone'),)
    allotment = models.ForeignKey(Allotment, on_delete=models.CASCADE)
    transfer_zone = models.ForeignKey(TransferZone, on_delete=models.CASCADE)


class ProviderTransferService(ProviderCatalogue):
    """
    ProviderTransferService
    """
    class Meta:
        verbose_name = 'Transfer Cost'
        verbose_name_plural = 'Transfer Cost'
        unique_together = (('provider', 'service', 'date_from', 'date_to', 'contract_code'),)
    service = models.ForeignKey(Transfer, on_delete=models.CASCADE)

    def __str__(self):
        return '{} by {} ({} to {})'.format(self.service,
                                            self.provider,
                                            self.date_from,
                                            self.date_to)


    def get_detail_objects(self):
        return self.providertransferdetail_set.all()


class ProviderTransferDetail(AmountDetail, RouteData):
    """
    ProviderTransferDetail
    """
    class Meta:
        verbose_name = 'Transfer Cost Detail'
        verbose_name_plural = 'Transfer Cost Details'
        unique_together = (
            ('provider_service', 'location_from', 'location_to', 'addon',
             'pax_range_min', 'pax_range_max'),)
    provider_service = models.ForeignKey(ProviderTransferService,
                                         on_delete=models.CASCADE)
    addon = models.ForeignKey(Addon, on_delete=models.CASCADE,
                              default=ADDON_FOR_NO_ADDON)
    pax_range_min = models.SmallIntegerField(default=0)
    pax_range_max = models.SmallIntegerField(default=0)

    def __str__(self):
        return 'Cost for {} ({})'.format(self.provider_service,
                                         self.addon)

    @property
    def cost_type(self):
        if self.provider_service:
            return self.provider_service.service.get_cost_type_display()
        return ''


class AgencyTransferService(AgencyCatalogue):
    """
    AgencyTransferService
    """
    class Meta:
        verbose_name = 'Transfer Price'
        verbose_name_plural = 'Transfer Prices'
        unique_together = (('agency', 'service', 'date_from', 'date_to', 'contract_code'),)
    service = models.ForeignKey(Transfer, on_delete=models.CASCADE)

    def __str__(self):
        return '{} for {} ({} to {})'.format(
            self.service,
            self.agency,
            self.date_from,
            self.date_to)

    def get_detail_objects(self):
        return self.agencytransferdetail_set.all()


class AgencyTransferDetail(AmountDetail, RouteData):
    """
    AgencyTransferDetail
    """
    class Meta:
        verbose_name = 'Transfer Price Detail'
        verbose_name_plural = 'Transfer Price Details'
        unique_together = ((
            'agency_service', 'location_from', 'location_to', 'addon',
            'pax_range_min', 'pax_range_max'),)
    agency_service = models.ForeignKey(AgencyTransferService,
                                       on_delete=models.CASCADE)
    addon = models.ForeignKey(Addon,
                              on_delete=models.CASCADE,
                              default=ADDON_FOR_NO_ADDON)
    pax_range_min = models.SmallIntegerField(default=0)
    pax_range_max = models.SmallIntegerField(default=0)
    not_reversible = models.BooleanField(default=False)

    def __str__(self):
        return 'Price for {} ({})'.format(
            self.agency_service,
            self.addon)

    @property
    def reversible(self):
        """ convenience filter to inverse values at tables """
        return not self.not_reversible


class ProviderExtraService(ProviderCatalogue):
    """
    ProviderExtraService
    """
    class Meta:
        verbose_name = 'Extra Cost'
        verbose_name_plural = 'Extra Costs'
        unique_together = (('provider', 'service', 'date_from', 'date_to', 'contract_code'),)
    service = models.ForeignKey(Extra, on_delete=models.CASCADE)

    def __str__(self):
        return 'Prov.Extra - %s : %s' % (self.provider, self.service)

    def get_detail_objects(self):
        return self.providerextradetail_set.all()


class ProviderExtraDetail(AmountDetail):
    """
    ProviderExtraDetail
    """
    class Meta:
        verbose_name = 'Extra Cost Detail'
        verbose_name_plural = 'Extra Cost Details'
        unique_together = ('provider_service',
                           'addon',
                           'pax_range_min',
                           'pax_range_max')
    provider_service = models.ForeignKey(ProviderExtraService,
                                         on_delete=models.CASCADE)
    addon = models.ForeignKey(Addon,
                              on_delete=models.CASCADE,
                              default=ADDON_FOR_NO_ADDON)
    pax_range_min = models.SmallIntegerField(default=0)
    pax_range_max = models.SmallIntegerField(default=0)


class AgencyExtraService(AgencyCatalogue):
    """
    AgencyExtraService
    """
    class Meta:
        verbose_name = 'Extra Price'
        verbose_name_plural = 'Extras Prices'
        unique_together = (('agency', 'service', 'date_from', 'date_to', 'contract_code'),)
    service = models.ForeignKey(Extra, on_delete=models.CASCADE)

    def __str__(self):
        return 'Ag.Extra - %s : %s' % (self.agency, self.service)

    def get_detail_objects(self):
        return self.agencyextradetail_set.all()


class AgencyExtraDetail(AmountDetail):
    """
    AgencyExtraDetail
    """
    class Meta:
        verbose_name = 'Extra Price Detail'
        verbose_name_plural = 'Extra Price Details'
        unique_together = ('agency_service',
                           'addon',
                           'pax_range_min',
                           'pax_range_max')
    agency_service = models.ForeignKey(AgencyExtraService,
                                       on_delete=models.CASCADE)
    addon = models.ForeignKey(Addon,
                              on_delete=models.CASCADE,
                              default=ADDON_FOR_NO_ADDON)
    pax_range_min = models.SmallIntegerField(default=0)
    pax_range_max = models.SmallIntegerField(default=0)


# ===============================================================================
# BOOK DETAILS
# ===============================================================================

class ServiceBookDetail(BookServiceData, RelativeInterval):
    """
    Service Detail
    """
    class Meta:
        verbose_name = 'Service Detail'
        verbose_name_plural = 'Services Details'
    service = models.ForeignKey(Service,
                                on_delete=models.CASCADE,
                                related_name='%(class)s_service')

    def fill_data(self):
        pass

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.fill_data()
        # Call the "real" save() method.
        super(ServiceBookDetail, self).save(force_insert, force_update, using, update_fields)


class ServiceBookDetailAllotment(ServiceBookDetail, BookAllotmentData):
    """
    Service Book Detail Allotment
    """
    class Meta:
        verbose_name = 'Service Book Detail Accomodation'
        verbose_name_plural = 'Services Book Details Accomodations'
    book_service = models.ForeignKey(Allotment,
                                     on_delete=models.CASCADE)

    def fill_data(self):
        self.base_service = self.book_service
        super(ServiceBookDetailAllotment, self).fill_data()
        self.name = '%s - %s' % (self.service, self.book_service)
        self.time = time(23, 59, 59)


class ServiceBookDetailTransfer(ServiceBookDetail, BookTransferData):
    """
    Service Book Detail Transfer
    """
    class Meta:
        verbose_name = 'Service Book Detail Transfer'
        verbose_name_plural = 'Services Book Details Transfers'
    book_service = models.ForeignKey(Transfer,
                                     on_delete=models.CASCADE)

    def fill_data(self):
        self.base_service = self.book_service
        super(ServiceBookDetailTransfer, self).fill_data()
        self.name = '%s - %s (%s -> %s)' % (
            self.service, self.book_service,
            self.location_from.short_name or self.location_from,
            self.location_to.short_name or self.location_to)


class ServiceBookDetailExtra(ServiceBookDetail, BookExtraData):
    """
    Service Book Detail Extra
    """
    class Meta:
        verbose_name = 'Service Book Detail Extra'
        verbose_name_plural = 'Services Book Details Extras'
    book_service = models.ForeignKey(Extra,
                                     on_delete=models.CASCADE)

    def fill_data(self):
        self.base_service = self.book_service
        super(ServiceBookDetailExtra, self).fill_data()
        self.name = '%s - %s' % (self.service, self.book_service)

SERVICE_MODELS = {
    SERVICE_CATEGORY_ALLOTMENT: Allotment,
    SERVICE_CATEGORY_TRANSFER: Transfer,
    SERVICE_CATEGORY_EXTRA: Extra,
}
