"""
Config Models
"""
from django.db import models

from config.constants import (
    SERVICE_CATEGORIES, ROOM_TYPES, BOARD_TYPES,
    EXTRA_COST_TYPES,
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
    name = models.CharField(max_length=50)
    enabled = models.BooleanField(default=True)


class Service(models.Model):
    """
    Service
    """
    class Meta:
        verbose_name = 'Service'
        verbose_name_plural = 'Services'
    name = models.CharField(max_length=50)
    category = models.CharField(max_length=5, choices=SERVICE_CATEGORIES)
    enabled = models.BooleanField(default=True)


class ServiceSupplement(models.Model):
    """
    ServiceSupplement
    """
    class Meta:
        verbose_name = 'Service Supplement'
        verbose_name_plural = 'Services Supplements'
    name = models.CharField(max_length=50)
    service = models.ForeignKey(Service)
    datetime_from = models.DateTimeField()
    datetime_to = models.DateTimeField()
    automatic = models.BooleanField(default=True)
    enabled = models.BooleanField(default=True)


class ServiceProvider(models.Model):
    """
    ServiceProvider
    """
    class Meta:
        verbose_name = 'Service Provider'
        verbose_name_plural = 'Services Providers'
    service = models.ForeignKey(Service)
    provider = models.ForeignKey(Provider)
    senior_age_from = models.IntegerField(null=True)
    child_age_to = models.IntegerField(null=True)
    baby_age_to = models.IntegerField(null=True)


class Cost(models.Model):
    """
    Cost
    """
    class Meta:
        verbose_name = 'Cost'
        verbose_name_plural = 'Costs'
    service_provider = models.ForeignKey(ServiceProvider)
    date_from = models.DateField()
    date_to = models.DateField()


class CostDetail(models.Model):
    """
    CostDetail
    """
    class Meta:
        verbose_name = 'Cost Detail'
        verbose_name_plural = 'Costs Details'
    cost = models.ForeignKey(Cost)
    adult_unit_cost = models.DecimalField(max_digits=8, decimal_places=2)
    senior_unit_cost = models.DecimalField(max_digits=8, decimal_places=2, null=True)
    child_unit_cost = models.DecimalField(max_digits=8, decimal_places=2, null=True)
    baby_unit_cost = models.DecimalField(max_digits=8, decimal_places=2, null=True)


class SupplementCostDetail(models.Model):
    """
    SupplementCostDetail
    """
    class Meta:
        verbose_name = 'Supplement Cost Detail'
        verbose_name_plural = 'Supplements Costs Details'
    cost = models.ForeignKey(Cost)
    supplement = models.ForeignKey(ServiceSupplement)
    adult_unit_cost = models.DecimalField(max_digits=8, decimal_places=2)
    senior_unit_cost = models.DecimalField(max_digits=8, decimal_places=2, null=True)
    child_unit_cost = models.DecimalField(max_digits=8, decimal_places=2, null=True)
    baby_unit_cost = models.DecimalField(max_digits=8, decimal_places=2, null=True)


class PriceCatalogue(models.Model):
    """
    PriceCatalogue
    """
    class Meta:
        verbose_name = 'Price Catalogue'
        verbose_name_plural = 'Prices Catalogues'
    name = models.CharField(max_length=50)
    price_percent = models.DecimalField(max_digits=4, decimal_places=1)
    price_amount = models.DecimalField(max_digits=8, decimal_places=2)


class ServiceProviderPrice(models.Model):
    """
    ServiceProviderPrice
    """
    class Meta:
        verbose_name = 'Price Catalogue'
        verbose_name_plural = 'Prices Catalogues'
    catalogue = models.ForeignKey(PriceCatalogue)
    service_provider = models.ForeignKey(ServiceProvider)
    price_percent = models.DecimalField(max_digits=4, decimal_places=1)
    price_amount = models.DecimalField(max_digits=8, decimal_places=2)


class CostDetailPrice(models.Model):
    """
    CostDetailPrice
    """
    class Meta:
        verbose_name = 'Cost Detail Price'
        verbose_name_plural = 'Costs Details Prices'
    catalogue = models.ForeignKey(PriceCatalogue)
    cost_detail = models.ForeignKey(CostDetail)
    adult_unit_price = models.DecimalField(max_digits=8, decimal_places=2)
    senior_unit_price = models.DecimalField(max_digits=8, decimal_places=2, null=True)
    child_unit_price = models.DecimalField(max_digits=8, decimal_places=2, null=True)
    baby_unit_price = models.DecimalField(max_digits=8, decimal_places=2, null=True)


class SupplementCostDetailPrice(models.Model):
    """
    SupplementCostDetailPrice
    """
    class Meta:
        verbose_name = 'Supplement Cost Detail Price'
        verbose_name_plural = 'Supplements Costs Details Prices'
    catalogue = models.ForeignKey(PriceCatalogue)
    supplement_cost_detail = models.ForeignKey(SupplementCostDetail)
    adult_unit_price = models.DecimalField(max_digits=8, decimal_places=2)
    senior_unit_price = models.DecimalField(max_digits=8, decimal_places=2, null=True)
    child_unit_price = models.DecimalField(max_digits=8, decimal_places=2, null=True)
    baby_unit_price = models.DecimalField(max_digits=8, decimal_places=2, null=True)


class AgencyPriceCatalogue(models.Model):
    """
    AgencyPriceCatalogue
    """
    class Meta:
        verbose_name = 'Agency Price Catalogue'
        verbose_name_plural = 'Agencies Prices Catalogues'
        unique_together = (('agency',),)
    agency = models.ForeignKey(Agency)
    price_catalogue = models.ForeignKey(PriceCatalogue)


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


class ExtraServiceProvider(ServiceProvider):
    """
    ExtraServiceProvider
    """
    class Meta:
        verbose_name = 'Extra Service Provider'
        verbose_name_plural = 'Extras Services Providers'
    cost_type = models.CharField(
        max_length=5, choices=EXTRA_COST_TYPES)


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


class AllotmentRoomType(models.Model):
    """
    AllotmentRoomType
    """
    class Meta:
        verbose_name = 'Allotment Room Type'
        verbose_name_plural = 'Allotments Rooms Types'
    name = models.CharField(max_length=50)
    allotment = models.ForeignKey(Allotment)
    room_type = models.CharField(max_length=5, choices=ROOM_TYPES)
    enabled = models.BooleanField(default=True)


class AllotmentBoardType(models.Model):
    """
    AllotmentBoardType
    """
    class Meta:
        verbose_name = 'Allotment Board Type'
        verbose_name_plural = 'Alloments Boards Types'
    allotment = models.ForeignKey(Allotment)
    board_type = models.CharField(max_length=5, choices=BOARD_TYPES)


class AllotmentCostDetail(CostDetail):
    """
    AllotmentCostDetail
    """
    class Meta:
        verbose_name = 'Allotment Cost Detail'
        verbose_name_plural = 'Allotments Costs Details'
    room_type = models.ForeignKey(AllotmentRoomType)
    board_type = models.CharField(max_length=5, choices=BOARD_TYPES)


class AllotmentSupplementCostDetail(SupplementCostDetail):
    """
    AllotmentSupplementCostDetail
    """
    class Meta:
        verbose_name = 'Allotment Supplement Cost Detail'
        verbose_name_plural = 'Allotments Supplements Costs Details'
    cost_type = models.CharField(
        max_length=10,
        choices=ALLOTMENT_SUPPLEMENT_COST_TYPES)


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
    location_from = models.ForeignKey(Location, related_name='location_from')
    location_to = models.ForeignKey(Location, related_name='location_to')


class TransferServiceProvider(ServiceProvider):
    """
    TransferServiceProvider
    """
    class Meta:
        verbose_name = 'Transfer Service Provider'
        verbose_name_plural = 'Transfers Services Providers'
    cost_type = models.CharField(max_length=5, choices=TRANSFER_COST_TYPES)


class TransferSupplementCostDetail(SupplementCostDetail):
    """
    TransferSupplementCostDetail
    """
    class Meta:
        verbose_name = 'Transfer Supplement'
        verbose_name_plural = 'Transfers Supplements'
    cost_type = models.CharField(
        max_length=10,
        choices=TRANSFER_SUPPLEMENT_COST_TYPES)
