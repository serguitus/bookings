"""
Config Models
"""
from django.db import models

from config.constants import (
    SERVICE_CATEGORIES,
    SERVICE_CATEGORY_EXTRA, SERVICE_CATEGORY_ALLOTMENT, SERVICE_CATEGORY_TRANSFER,
    ROOM_CAPACITIES,
    BOARD_TYPES,
    EXTRA_COST_TYPES, EXTRA_PARAMETER_TYPES,
    ALLOTMENT_SUPPLEMENT_COST_TYPES, TRANSFER_SUPPLEMENT_COST_TYPES,
    TRANSFER_COST_TYPES)

from finance.models import Agency, Provider


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
    name = models.CharField(max_length=50)
    enabled = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Service(models.Model):
    """
    Service
    """
    class Meta:
        verbose_name = 'Service'
        verbose_name_plural = 'Services'
        unique_together = (('category', 'name'),)
    name = models.CharField(max_length=150)
    category = models.CharField(max_length=5, choices=SERVICE_CATEGORIES)
    grouping = models.BooleanField(default=False)
    child_age = models.IntegerField(blank=True, null=True)
    enabled = models.BooleanField(default=True)

    def __init__(self, *args, **kwargs):
        # Call the "real" __init__ method.
        super(Service, self).__init__(*args, **kwargs)
        self.fill_data()

    def fill_data(self):
        pass

    def save(self, *args, **kwargs):
        self.fill_data()
        # Call the "real" save method.
        super(Service, self).save(*args, **kwargs)

    def __str__(self):
        return self.name


class ServiceSupplement(models.Model):
    """
    ServiceSupplement
    """
    class Meta:
        verbose_name = 'Service Supplement'
        verbose_name_plural = 'Services Supplements'
        unique_together = (('service', 'name'),)
    name = models.CharField(max_length=50)
    service = models.ForeignKey(Service)
    datetime_from = models.DateTimeField()
    datetime_to = models.DateTimeField()
    automatic = models.BooleanField(default=True)
    enabled = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class ProviderCatalogue(models.Model):
    """
    ProviderCatalogue
    """
    class Meta:
        abstract = True
    provider = models.ForeignKey(Provider)
    date_from = models.DateField()
    date_to = models.DateField()


class AgencyCatalogue(models.Model):
    """
    AgencyCatalogue
    """
    class Meta:
        abstract = True
    agency = models.ForeignKey(Agency)
    date_from = models.DateField()
    date_to = models.DateField()


class AmountDetail(models.Model):
    """
    AmountDetail
    """
    class Meta:
        abstract = True
    ad_1_amount = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True, verbose_name='SGL')
    ad_2_amount = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True, verbose_name='DBL')
    ad_3_amount = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True, verbose_name='TPL')
    ad_4_amount = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True, verbose_name='QAD')
    ch_1_ad_0_amount = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True, verbose_name='1st CHD')
    ch_1_ad_1_amount = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True, verbose_name='1st CHD')
    ch_1_ad_2_amount = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True, verbose_name='1st CHD')
    ch_1_ad_3_amount = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True, verbose_name='1st CHD')
    ch_1_ad_4_amount = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True, verbose_name='1st CHD')
    ch_2_ad_0_amount = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True, verbose_name='2nd CHD')
    ch_2_ad_1_amount = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True, verbose_name='2nd CHD')
    ch_2_ad_2_amount = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True, verbose_name='2nd CHD')
    ch_2_ad_3_amount = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True, verbose_name='2nd CHD')
    ch_2_ad_4_amount = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True, verbose_name='2nd CHD')
    ch_3_ad_0_amount = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True, verbose_name='3rd CHD')
    ch_3_ad_1_amount = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True, verbose_name='3rd CHD')
    ch_3_ad_2_amount = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True, verbose_name='3rd CHD')
    ch_3_ad_3_amount = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True, verbose_name='3rd CHD')
    ch_3_ad_4_amount = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True, verbose_name='3rd CHD')


#===============================================================================
# Extra
#===============================================================================
class Extra(Service):
    """
    Extra
    """
    class Meta:
        verbose_name = 'Extra'
        verbose_name_plural = 'Extras'
    cost_type = models.CharField(
        max_length=5, choices=EXTRA_COST_TYPES)
    parameter_type = models.CharField(
        max_length=5, choices=EXTRA_PARAMETER_TYPES)
    max_capacity = models.IntegerField(blank=True, null=True)

    def fill_data(self):
        self.category = SERVICE_CATEGORY_EXTRA


class ExtraSupplement(ServiceSupplement):
    """
    ExtraSupplement
    """
    class Meta:
        verbose_name = 'Extra Supplement'
        verbose_name_plural = 'Extras Supplements'


class ProviderExtraService(ProviderCatalogue):
    """
    ProviderExtraService
    """
    class Meta:
        verbose_name = 'Provider Extra Service'
        verbose_name_plural = 'Providers Extras Services'
    service = models.ForeignKey(Extra)


class ProviderExtraDetail(AmountDetail):
    """
    ProviderExtraDetail
    """
    class Meta:
        verbose_name = 'Provider Extra Detail'
        verbose_name_plural = 'Providers Extras Details'
        unique_together = (('provider_service',),)
    provider_service = models.ForeignKey(ProviderExtraService)


class AgencyExtraService(AgencyCatalogue):
    """
    AgencyExtraService
    """
    class Meta:
        verbose_name = 'Agency Extra Service'
        verbose_name_plural = 'Agency Extras Services'
    service = models.ForeignKey(Extra)


class AgencyExtraDetail(AmountDetail):
    """
    AgencyExtraDetail
    """
    class Meta:
        verbose_name = 'Agency Extra Detail'
        verbose_name_plural = 'Agencies Extras Details'
        unique_together = (('agency_service',),)
    agency_service = models.ForeignKey(AgencyExtraService)


#===============================================================================
# Allotment
#===============================================================================
class Allotment(Service):
    """
    Accomodation
    """
    class Meta:
        verbose_name = 'Accomodation'
        verbose_name_plural = 'Accomodation'
    location = models.ForeignKey(Location)
    time_from = models.TimeField(default='16:00')
    time_to = models.TimeField(default='12:00')

    def fill_data(self):
        self.category = SERVICE_CATEGORY_ALLOTMENT
        self.grouping = True


class AllotmentRoomType(models.Model):
    """
    AllotmentRoomType
    """
    class Meta:
        verbose_name = 'Allotment Room Type'
        verbose_name_plural = 'Allotments Rooms Types'
        unique_together = (('allotment', 'room_type', 'room_capacity'),)
    allotment = models.ForeignKey(Allotment)
    room_type = models.ForeignKey(RoomType)
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
    allotment = models.ForeignKey(Allotment)
    board_type = models.CharField(max_length=5, choices=BOARD_TYPES)

    def __str__(self):
        return self.get_board_type_display()


class AllotmentSupplement(ServiceSupplement):
    """
    AccomodationSupplement
    """
    class Meta:
        verbose_name = 'Accomodation Supplement'
        verbose_name_plural = 'Accomodation Supplements'


class ProviderAllotmentService(ProviderCatalogue):
    """
    ProviderAccomodationService
    """
    class Meta:
        verbose_name = 'Accomodation Service Provider'
        verbose_name_plural = 'Accomodation Service Providers'
    service = models.ForeignKey(Allotment)


class ProviderAllotmentDetail(AmountDetail):
    """
    ProviderAccomodationDetail
    """
    class Meta:
        verbose_name = 'Accomodation Provider Detail'
        verbose_name_plural = 'Accomodation Provider Details'
        unique_together = (('provider_service', 'room_type', 'board_type'),)
    provider_service = models.ForeignKey(ProviderAllotmentService)
    room_type = models.ForeignKey(RoomType)
    board_type = models.CharField(max_length=5, choices=BOARD_TYPES)


class AgencyAllotmentService(AgencyCatalogue):
    """
    AgencyAccomodationService
    """
    class Meta:
        verbose_name = 'Agency Accomodation Service'
        verbose_name_plural = 'Agency Accomodation Services'
    service = models.ForeignKey(Allotment)


class AgencyAllotmentDetail(AmountDetail):
    """
    AgencyAccomodationDetail
    """
    class Meta:
        verbose_name = 'Agency Accomodation Detail'
        verbose_name_plural = 'Agency Accomodation Details'
        unique_together = (('agency_service', 'room_type', 'board_type'),)
    agency_service = models.ForeignKey(AgencyAllotmentService)
    room_type = models.ForeignKey(RoomType)
    board_type = models.CharField(max_length=5, choices=BOARD_TYPES)


class AllotmentRoomAvailability(models.Model):
    """
    AccomodationRoomAvailability
    """
    class Meta:
        verbose_name = 'Accomodation Availability'
        verbose_name_plural = 'Accomodation Availabilities'
    room_type = models.ForeignKey(AllotmentRoomType)
    availability = models.SmallIntegerField(default=10)
    date_from = models.DateField()
    date_to = models.DateField()


#===============================================================================
# TRANFER
#===============================================================================
class Transfer(Service):
    """
    Transfer
    """
    class Meta:
        verbose_name = 'Transfer'
        verbose_name_plural = 'Transfers'
    cost_type = models.CharField(max_length=5, choices=TRANSFER_COST_TYPES)
    max_capacity = models.IntegerField(blank=True, null=True)

    def fill_data(self):
        self.category = SERVICE_CATEGORY_TRANSFER


class TransferSupplement(ServiceSupplement):
    """
    TransferSupplement
    """
    class Meta:
        verbose_name = 'Transfer Supplement'
        verbose_name_plural = 'Transfers Supplements'


class ProviderTransferService(ProviderCatalogue):
    """
    ProviderTransferService
    """
    class Meta:
        verbose_name = 'Provider Transfer Service'
        verbose_name_plural = 'Providers Transfers Services'
    service = models.ForeignKey(Transfer)


class ProviderTransferDetail(AmountDetail):
    """
    ProviderTransferDetail
    """
    class Meta:
        verbose_name = 'Provider Transfer Detail'
        verbose_name_plural = 'Providers Transfers Details'
        unique_together = (('provider_service', 'p_location_from', 'p_location_to',),)
    provider_service = models.ForeignKey(ProviderTransferService)
    p_location_from = models.ForeignKey(Location, related_name='p_location_from', verbose_name='Location from')
    p_location_to = models.ForeignKey(Location, related_name='p_location_to', verbose_name='Location to')


class AgencyTransferService(AgencyCatalogue):
    """
    AgencyTransferService
    """
    class Meta:
        verbose_name = 'Agency Transfer Service'
        verbose_name_plural = 'Agencies Transfers Services'
    service = models.ForeignKey(Transfer)


class AgencyTransferDetail(AmountDetail):
    """
    AgencyTransferDetail
    """
    class Meta:
        verbose_name = 'Agency Transfer Detail'
        verbose_name_plural = 'Agencies Transfers Details'
        unique_together = (('agency_service', 'a_location_from', 'a_location_to',),)
    agency_service = models.ForeignKey(AgencyTransferService)
    a_location_from = models.ForeignKey(Location, related_name='a_location_from', verbose_name='Location from')
    a_location_to = models.ForeignKey(Location, related_name='a_location_to', verbose_name='Location to')


