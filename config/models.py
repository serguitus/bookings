from django.db import models
from accounting.models import Account
from finance.models import Agency, Provider
from .constants import *


class DateRange(models.Model):
    class Meta:
        abstract = True
    date_from = models.DateField()
    date_to = models.DateField()


class ProviderCost(models.Model):
    class Meta:
        abstract = True
    name = models.CharField(max_length=50)
    provider = models.ForeignKey(Provider)
    cost = models.DecimalField(max_digits=8, decimal_places=2)


class AgencyPrice(models.Model):
    class Meta:
        abstract = True
    name = models.CharField(max_length=50)
    agency = models.ForeignKey(Agency)
    price = models.DecimalField(max_digits=8, decimal_places=2)


class Service(models.Model):
    name = models.CharField(max_length=50)
    category = models.CharField(max_length=1, choices=SERVICE_CATEGORIES)
    enabled = models.BooleanField(default=True)


class Location(models.Model):
    name = models.CharField(max_length=50)
    enabled = models.BooleanField(default=True)


#===============================================================================
# Allotment
#===============================================================================
class Allotment(Service):
    location = models.ForeignKey(Location)


class AllotmentRoom(models.Model):
    class Meta:
        verbose_name = 'Allotment Room'
        verbose_name_plural = 'Allotments Rooms'

    name = models.CharField(max_length=50)
    allotment = models.ForeignKey(Allotment)
    enabled = models.BooleanField(default=True)


class AllotmentSupplement(models.Model):
    class Meta:
        verbose_name = 'Allotment Supplement'
        verbose_name_plural = 'Allotments Supplements'

    name = models.CharField(max_length=50)
    allotment = models.ForeignKey(Allotment)
    cost_type = models.CharField(
        max_length=10,
        choices=ALLOTMENT_SUPPLEMENT_COST_TYPES)
    automatic = models.BooleanField(default=True)
    enabled = models.BooleanField(default=True)


class AllotmentPaxTypeDefinition(models.Model):
    class Meta:
        verbose_name = 'Allotment Pax Type Definition'
        verbose_name_plural = 'Allotments Paxes Types Definitions'
    pax_type = models.CharField(max_length=1, choices=PAX_TYPES)
    age_from = models.IntegerField()
    age_to = models.IntegerField()


class AllotmentBoardType(models.Model):
    class Meta:
        verbose_name = 'Allotment Board Type'
        verbose_name_plural = 'Alloments Boards Types'
    allotment = models.ForeignKey(Allotment)
    board_type = models.CharField(max_length=2, choices=BOARD_TYPES)


class AllotmentPaxCombo(models.Model):
    class Meta:
        verbose_name = 'Allotment Pax Combo'
        verbose_name_plural = 'Allotments Paxes Combos'
    allotment = models.ForeignKey(Allotment)
    pax_combo = models.CharField(max_length=5, choices=PAX_COMBOS)


class AllotmentDefinition(models.Model):
    class Meta:
        abstract = True
    allotment = models.ForeignKey(Allotment)
    room_type = models.ForeignKey(AllotmentRoom)
    board_type = models.CharField(max_length=2, choices=BOARD_TYPES)
    pax_combo = models.CharField(max_length=5, choices=PAX_COMBOS)


class ProviderAllotmentCost(ProviderCost, DateRange, AllotmentDefinition):
    class Meta:
        verbose_name = 'Provider Allotment Cost'
        verbose_name_plural = 'Providers Allotments Costs'


class AgencyAllotmentPrice(AgencyPrice):
    class Meta:
        verbose_name = 'Agency Allotment Price'
        verbose_name_plural = 'Agencies Allotments Prices'
    provider_allotment_cost = models.ForeignKey(ProviderAllotmentCost)


class ProviderAllotmentSupplementCost(ProviderCost, DateRange, AllotmentDefinition):
    class Meta:
        verbose_name = 'Provider Allotment Supplement Cost'
        verbose_name_plural = 'Providers Allotments Supplements Costs'
    allotment_supplement = models.ForeignKey(AllotmentSupplement)


class AgencyAllotmentSuplementPrice(AgencyPrice):
    class Meta:
        verbose_name = 'Agency Allotment Suplement Price'
        verbose_name_plural = 'Agencies Allotments Suplements Prices'
    provider_allotment_supplement_cost = models.ForeignKey(ProviderAllotmentSupplementCost)


class ProviderAllotmentRoomAvailability(DateRange):
    class Meta:
        verbose_name = 'Allotment Availability'
        verbose_name_plural = 'Allotments Availabilities'
    provider = models.ForeignKey(Provider)
    allotment = models.ForeignKey(Allotment)
    room_type = models.ForeignKey(AllotmentRoom)
    availability = models.SmallIntegerField(default=10)


#===============================================================================
# TRANFER
#===============================================================================
class TransportType(models.Model):
    class Meta:
        verbose_name = 'Transport Type'
        verbose_name_plural = 'Transport Types'
    name = models.CharField(max_length=50)
    max_capacity = models.SmallIntegerField()
    cost_type = models.CharField(max_length=1, choices=TRANSPORT_COST_TYPES)


class TransferLocation(models.Model):
    location = models.ForeignKey(Location)
    enabled = models.BooleanField(default=True)


class Transfer(Service):
    location_from = models.ForeignKey(TransferLocation, related_name='location_from')
    location_to = models.ForeignKey(TransferLocation, related_name='location_to')


class TransferDefinition(models.Model):
    class Meta:
        abstract = True
    transfer = models.ForeignKey(Transfer)
    transport_type = models.ForeignKey(TransportType)


class TransferTransport(TransferDefinition):
    class Meta:
        verbose_name = 'Transfer Transport'
        verbose_name_plural = 'Transfers Transports'


class TransferSupplement(models.Model):
    class Meta:
        verbose_name = 'Transfer Supplement'
        verbose_name_plural = 'Transfers Supplements'

    name = models.CharField(max_length=50)
    transfer = models.ForeignKey(Transfer)
    cost_type = models.CharField(
        max_length=10,
        choices=TRANSFER_SUPPLEMENT_COST_TYPES)
    automatic = models.BooleanField(default=True)
    enabled = models.BooleanField(default=True)


class ProviderTransferCost(ProviderCost, DateRange, TransferDefinition):
    class Meta:
        verbose_name = 'Provider Transfer Cost'
        verbose_name_plural = 'Providers Transfers Costs'


class AgencyTransferPrice(AgencyPrice):
    class Meta:
        verbose_name = 'Agency Transfer Price'
        verbose_name_plural = 'Agencies Tranfers Prices'
    provider_transfer_cost = models.ForeignKey(ProviderTransferCost)


class ProviderTransferSupplementCost(ProviderCost, DateRange, TransferDefinition):
    class Meta:
        verbose_name = 'Provider Transfer Supplement Cost'
        verbose_name_plural = 'Providers Transfers Supplements Costs'
    transfer_supplement = models.ForeignKey(TransferSupplement)


class AgencyTransferSupplementPrice(AgencyPrice):
    class Meta:
        verbose_name = 'Agency Transfer Price'
        verbose_name_plural = 'Agencies Tranfers Prices'
    provider_transfer_supplement_cost = models.ForeignKey(ProviderTransferSupplementCost)


