"""
Config Models
"""
from django.db import models

from config.constants import (
    SERVICE_CATEGORIES,
    SERVICE_CATEGORY_EXTRA, SERVICE_CATEGORY_ALLOTMENT, SERVICE_CATEGORY_TRANSFER,
    ROOM_CAPACITIES,
    BOARD_TYPES,
    EXTRA_COST_TYPES,
    ALLOTMENT_COST_TYPES, ALLOTMENT_SUPPLEMENT_COST_TYPES, TRANSFER_SUPPLEMENT_COST_TYPES,
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


class ProviderServiceCatalogue(models.Model):
    """
    ProviderServiceCatalogue
    """
    class Meta:
        verbose_name = 'Provider Service Catalogue'
        verbose_name_plural = 'Providers Services Catalogues'
    service = models.ForeignKey(Service)
    provider = models.ForeignKey(Provider)
    date_from = models.DateField()
    date_to = models.DateField()


class AgencyServiceCatalogue(models.Model):
    """
    AgencyServiceCatalogue
    """
    class Meta:
        verbose_name = 'Agency Service Catalogue'
        verbose_name_plural = 'Agencies Services Catalogues'
    agency = models.ForeignKey(Agency)
    service = models.ForeignKey(Service)
    date_from = models.DateField()
    date_to = models.DateField()


class AmountDetail(models.Model):
    """
    AmountDetail
    """
    class Meta:
        abstract = True
    ad_1_amount = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    ad_2_amount = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    ad_3_amount = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    ad_4_amount = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    ch_1_ad_0_amount = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    ch_1_ad_1_amount = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    ch_1_ad_2_amount = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    ch_1_ad_3_amount = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    ch_1_ad_4_amount = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    ch_2_ad_0_amount = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    ch_2_ad_1_amount = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    ch_2_ad_2_amount = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    ch_2_ad_3_amount = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    ch_2_ad_4_amount = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    ch_3_ad_0_amount = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    ch_3_ad_1_amount = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    ch_3_ad_2_amount = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    ch_3_ad_3_amount = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    ch_3_ad_4_amount = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)


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

    def fill_data(self):
        self.category = SERVICE_CATEGORY_EXTRA


class ExtraSupplement(ServiceSupplement):
    """
    ExtraSupplement
    """
    class Meta:
        verbose_name = 'Extra Supplement'
        verbose_name_plural = 'Extras Supplements'


class ProviderExtraService(ProviderServiceCatalogue):
    """
    ProviderExtraService
    """
    class Meta:
        verbose_name = 'Provider Extra Service'
        verbose_name_plural = 'Providers Extras Services'
    cost_type = models.CharField(
        max_length=5, choices=EXTRA_COST_TYPES)


class ProviderExtraDetail(AmountDetail):
    """
    ProviderExtraDetail
    """
    class Meta:
        verbose_name = 'Provider Extra Detail'
        verbose_name_plural = 'Providers Extras Details'
        unique_together = (('provider_service',),)
    provider_service = models.ForeignKey(ProviderExtraService)


class AgencyExtraService(AgencyServiceCatalogue):
    """
    AgencyExtraService
    """
    class Meta:
        verbose_name = 'Provider Extra Service'
        verbose_name_plural = 'Providers Extras Services'
    cost_type = models.CharField(
        max_length=5, choices=EXTRA_COST_TYPES)


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
    Allotment
    """
    class Meta:
        verbose_name = 'Allotment'
        verbose_name_plural = 'Allotments'
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
    AllotmentBoardType
    """
    class Meta:
        verbose_name = 'Allotment Board Type'
        verbose_name_plural = 'Alloments Boards Types'
        unique_together = (('allotment', 'board_type'),)
    allotment = models.ForeignKey(Allotment)
    board_type = models.CharField(max_length=5, choices=BOARD_TYPES)

    def __str__(self):
        return self.get_board_type_display()


class AllotmentSupplement(ServiceSupplement):
    """
    AllotmentSupplement
    """
    class Meta:
        verbose_name = 'Allotment Supplement'
        verbose_name_plural = 'Allotments Supplements'


class ProviderAllotmentService(ProviderServiceCatalogue):
    """
    ProviderAllotmentService
    """
    class Meta:
        verbose_name = 'Provider Allotment Service'
        verbose_name_plural = 'Providers Allotments Services'
    cost_type = models.CharField(max_length=5, choices=ALLOTMENT_COST_TYPES)


class ProviderAllotmentDetail(AmountDetail):
    """
    ProviderAllotmentDetail
    """
    class Meta:
        verbose_name = 'Provider Allotment Detail'
        verbose_name_plural = 'Providers Allotments Details'
        unique_together = (('provider_service', 'room_type', 'board_type'),)
    provider_service = models.ForeignKey(ProviderAllotmentService)
    room_type = models.ForeignKey(RoomType)
    board_type = models.CharField(max_length=5, choices=BOARD_TYPES)


class AgencyAllotmentService(AgencyServiceCatalogue):
    """
    AgencyAllotmentService
    """
    class Meta:
        verbose_name = 'Agency Allotment Service'
        verbose_name_plural = 'Agencies Allotments Services'
    cost_type = models.CharField(max_length=5, choices=ALLOTMENT_COST_TYPES)


class AgencyAllotmentDetail(AmountDetail):
    """
    AgencyAllotmentDetail
    """
    class Meta:
        verbose_name = 'Agency Allotment Detail'
        verbose_name_plural = 'Agencies Allotments Details'
        unique_together = (('agency_service', 'room_type', 'board_type'),)
    agency_service = models.ForeignKey(AgencyAllotmentService)
    room_type = models.ForeignKey(RoomType)
    board_type = models.CharField(max_length=5, choices=BOARD_TYPES)


class AllotmentRoomAvailability(models.Model):
    """
    AllotmentRoomAvailability
    """
    class Meta:
        verbose_name = 'Allotment Availability'
        verbose_name_plural = 'Allotments Availabilities'
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
    # location_from = models.ForeignKey(Location, related_name='location_from')
    # location_to = models.ForeignKey(Location, related_name='location_to')

    def fill_data(self):
        self.category = SERVICE_CATEGORY_TRANSFER


class TransferSupplement(ServiceSupplement):
    """
    TransferSupplement
    """
    class Meta:
        verbose_name = 'Transfer Supplement'
        verbose_name_plural = 'Transfers Supplements'


class ProviderTransferService(ProviderServiceCatalogue):
    """
    ProviderTransferService
    """
    class Meta:
        verbose_name = 'Provider Transfer Service'
        verbose_name_plural = 'Providers Transfers Services'
    cost_type = models.CharField(max_length=5, choices=TRANSFER_COST_TYPES)


class ProviderTransferDetail(AmountDetail):
    """
    ProviderTransferDetail
    """
    class Meta:
        verbose_name = 'Provider Transfer Detail'
        verbose_name_plural = 'Providers Transfers Details'
        unique_together = (('provider_service', 'p_location_from', 'p_location_to',),)
    provider_service = models.ForeignKey(ProviderTransferService)
    p_location_from = models.ForeignKey(Location, related_name='p_location_from')
    p_location_to = models.ForeignKey(Location, related_name='p_location_to')


class AgencyTransferService(AgencyServiceCatalogue):
    """
    AgencyTransferService
    """
    class Meta:
        verbose_name = 'Agency Transfer Service'
        verbose_name_plural = 'Agencies Transfers Services'
    cost_type = models.CharField(max_length=5, choices=TRANSFER_COST_TYPES)


class AgencyTransferDetail(AmountDetail):
    """
    AgencyTransferDetail
    """
    class Meta:
        verbose_name = 'Agency Transfer Detail'
        verbose_name_plural = 'Agencies Transfers Details'
        unique_together = (('agency_service', 'a_location_from', 'a_location_to',),)
    agency_service = models.ForeignKey(AgencyTransferService)
    a_location_from = models.ForeignKey(Location, related_name='a_location_from')
    a_location_to = models.ForeignKey(Location, related_name='a_location_to')


