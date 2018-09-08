"""
Config Models
"""
from django.db import models

from config.constants import (
    SERVICE_CATEGORIES,
    SERVICE_CATEGORY_EXTRA, SERVICE_CATEGORY_ALLOTMENT, SERVICE_CATEGORY_TRANSFER,
    ROOM_TYPES,
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


class ServiceProvider(models.Model):
    """
    ServiceProvider
    """
    class Meta:
        verbose_name = 'Service Provider'
        verbose_name_plural = 'Services Providers'
        unique_together = (('service', 'provider'),)
    service = models.ForeignKey(Service)
    provider = models.ForeignKey(Provider)
    child_age = models.IntegerField(blank=True, null=True)


class Cost(models.Model):
    """
    Cost
    """
    class Meta:
        abstract = True
    service_provider = models.ForeignKey(ServiceProvider)
    date_from = models.DateField()
    date_to = models.DateField()


class CostDetail(models.Model):
    """
    CostDetail
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


class SupplementCostDetail(models.Model):
    """
    SupplementCostDetail
    """
    class Meta:
        abstract = True
    supplement = models.ForeignKey(ServiceSupplement)
    ad_amount = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    ch_amount = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)


class PriceCatalogue(models.Model):
    """
    PriceCatalogue
    """
    class Meta:
        verbose_name = 'Price Catalogue'
        verbose_name_plural = 'Prices Catalogues'
        unique_together = (('name',),)
    name = models.CharField(max_length=50)
    price_percent = models.DecimalField(max_digits=4, decimal_places=1, blank=True, null=True)
    price_amount = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)


class ServiceProviderPrice(models.Model):
    """
    ServiceProviderPrice
    """
    class Meta:
        verbose_name = 'Price Catalogue'
        verbose_name_plural = 'Prices Catalogues'
        unique_together = (('catalogue', 'service_provider'),)
    catalogue = models.ForeignKey(PriceCatalogue)
    service_provider = models.ForeignKey(ServiceProvider)
    price_percent = models.DecimalField(max_digits=4, decimal_places=1, blank=True, null=True)
    price_amount = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)


class CostDetailPrice(models.Model):
    """
    CostDetailPrice
    """
    class Meta:
        abstract = True
    catalogue = models.ForeignKey(PriceCatalogue)
    pax_1_price = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    pax_2_price = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    pax_3_price = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)


class SupplementCostDetailPrice(models.Model):
    """
    SupplementCostDetailPrice
    """
    class Meta:
        abstract = True
    catalogue = models.ForeignKey(PriceCatalogue)
    pax_1_price = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)


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

    def fill_data(self):
        self.category = SERVICE_CATEGORY_EXTRA


class ExtraSupplement(ServiceSupplement):
    """
    ExtraSupplement
    """
    class Meta:
        verbose_name = 'Extra Supplement'
        verbose_name_plural = 'Extras Supplements'


class ExtraServiceProvider(ServiceProvider):
    """
    ExtraServiceProvider
    """
    class Meta:
        verbose_name = 'Extra Service Provider'
        verbose_name_plural = 'Extras Services Providers'
    cost_type = models.CharField(
        max_length=5, choices=EXTRA_COST_TYPES)


class ExtraCost(Cost):
    """
    ExtraCost
    """
    class Meta:
        verbose_name = 'Extra Cost'
        verbose_name_plural = 'Extras Costs'


class ExtraCostDetail(CostDetail):
    """
    ExtraCostDetail
    """
    class Meta:
        verbose_name = 'Extra Cost Detail'
        verbose_name_plural = 'Extras Costs Details'
        unique_together = (('cost',),)
    cost = models.ForeignKey(ExtraCost)


class ExtraSupplementCostDetail(SupplementCostDetail):
    """
    ExtraSupplementCostDetail
    """
    class Meta:
        verbose_name = 'Extra Supplement Cost Detail'
        verbose_name_plural = 'Extras Supplement Costs Details'
        unique_together = (('cost', 'supplement'),)
    cost = models.ForeignKey(ExtraCost)


class ExtraCostDetailPrice(CostDetailPrice):
    """
    ExtraCostDetailPrice
    """
    class Meta:
        verbose_name = 'Extra Cost Detail Price'
        verbose_name_plural = 'Extras Costs Details Prices'
        unique_together = (('catalogue', 'cost_detail'),)
    cost_detail = models.ForeignKey(ExtraCostDetail)


class ExtraSupplementCostDetailPrice(SupplementCostDetailPrice):
    """
    ExtraSupplementCostDetailPrice
    """
    class Meta:
        verbose_name = 'Extra Supplement Cost Detail Price'
        verbose_name_plural = 'Extras Supplements Costs Details Prices'
    supplement_cost_detail = models.ForeignKey(ExtraSupplementCostDetail)


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
        unique_together = (('allotment', 'name', 'room_type',),)
    name = models.CharField(max_length=50)
    room_type = models.CharField(max_length=5, choices=ROOM_TYPES)
    allotment = models.ForeignKey(Allotment)
    enabled = models.BooleanField(default=True)

    def __str__(self):
        return '%s (%s)' % (self.name, self.get_room_type_display())


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


class AllotmentServiceProvider(ServiceProvider):
    """
    AllotmentServiceProvider
    """
    class Meta:
        verbose_name = 'Allotment Service Provider'
        verbose_name_plural = 'Allotments Services Providers'
    cost_type = models.CharField(max_length=5, choices=ALLOTMENT_COST_TYPES)


class AllotmentCost(Cost):
    """
    AllotmentCost
    """
    class Meta:
        verbose_name = 'Allotment Cost'
        verbose_name_plural = 'Allotments Costs'


class AllotmentCostDetail(CostDetail):
    """
    AllotmentCostDetail
    """
    class Meta:
        verbose_name = 'Allotment Cost Detail'
        verbose_name_plural = 'Allotments Costs Details'
        unique_together = (('cost', 'room_type', 'board_type'),)
    cost = models.ForeignKey(AllotmentCost)
    room_type = models.ForeignKey(AllotmentRoomType)
    board_type = models.ForeignKey(AllotmentBoardType)


class AllotmentSupplementCostDetail(SupplementCostDetail):
    """
    AllotmentSupplementCostDetail
    """
    class Meta:
        verbose_name = 'Allotment Supplement Cost Detail'
        verbose_name_plural = 'Allotments Supplements Costs Details'
        unique_together = (('cost', 'supplement'),)
    cost = models.ForeignKey(AllotmentCost)
    cost_type = models.CharField(
        max_length=10,
        choices=ALLOTMENT_SUPPLEMENT_COST_TYPES)


class AllotmentCostDetailPrice(CostDetailPrice):
    """
    AllotmentCostDetailPrice
    """
    class Meta:
        verbose_name = 'Allotment Cost Detail Price'
        verbose_name_plural = 'Allotments Costs Details Prices'
        unique_together = (('catalogue', 'cost_detail'),)
    cost_detail = models.ForeignKey(AllotmentCostDetail)


class AllotmentSupplementCostDetailPrice(SupplementCostDetailPrice):
    """
    AllotmentSupplementCostDetailPrice
    """
    class Meta:
        verbose_name = 'Allotment Supplement Cost Detail Price'
        verbose_name_plural = 'Allotments Supplements Costs Details Prices'
    supplement_cost_detail = models.ForeignKey(AllotmentSupplementCostDetail)


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
    location_from = models.ForeignKey(Location, blank=False, null=False, related_name='location_from')
    location_to = models.ForeignKey(Location, blank=False, null=False, related_name='location_to')

    def fill_data(self):
        self.category = SERVICE_CATEGORY_TRANSFER
        var_from = '?'
        if self.location_from:
            var_from = self.location_from.name
        var_to = '?'
        if self.location_to:
            var_to = self.location_to.name
        self.name = 'Transfer FROM: %s - TO: %s' % (var_from, var_to)


class TransferSupplement(ServiceSupplement):
    """
    TransferSupplement
    """
    class Meta:
        verbose_name = 'Transfer Supplement'
        verbose_name_plural = 'Transfers Supplements'


class TransferServiceProvider(ServiceProvider):
    """
    TransferServiceProvider
    """
    class Meta:
        verbose_name = 'Transfer Service Provider'
        verbose_name_plural = 'Transfers Services Providers'
    cost_type = models.CharField(max_length=5, choices=TRANSFER_COST_TYPES)


class TransferCost(Cost):
    """
    TransferCost
    """
    class Meta:
        verbose_name = 'Transfer Cost'
        verbose_name_plural = 'Transfers Costs'


class TransferCostDetail(CostDetail):
    """
    TransferCostDetail
    """
    class Meta:
        verbose_name = 'Transfer Cost Detail'
        verbose_name_plural = 'Transfers Costs Details'
        unique_together = (('cost',),)
    cost = models.ForeignKey(TransferCost)


class TransferSupplementCostDetail(SupplementCostDetail):
    """
    TransferSupplementCostDetail
    """
    class Meta:
        verbose_name = 'Transfer Supplement'
        verbose_name_plural = 'Transfers Supplements'
        unique_together = (('cost', 'supplement'),)
    cost = models.ForeignKey(TransferCost)
    cost_type = models.CharField(
        max_length=10,
        choices=TRANSFER_SUPPLEMENT_COST_TYPES)

class TransferCostDetailPrice(CostDetailPrice):
    """
    TransferCostDetailPrice
    """
    class Meta:
        verbose_name = 'Transfer Cost Detail Price'
        verbose_name_plural = 'Transfer Costs Details Prices'
        unique_together = (('catalogue', 'cost_detail'),)
    cost_detail = models.ForeignKey(TransferCostDetail)

class TransferSupplementCostDetailPrice(SupplementCostDetailPrice):
    """
    TransferSupplementCostDetailPrice
    """
    class Meta:
        verbose_name = 'Transfer Supplement Cost Detail Price'
        verbose_name_plural = 'Transfers Supplements Costs Details Prices'
    supplement_cost_detail = models.ForeignKey(TransferSupplementCostDetail)
