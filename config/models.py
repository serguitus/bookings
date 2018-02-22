from django.db import models
from accounting.models import Account
from .constants import COST_BY, COST_BY_PAX, COST_BY_ROON


class DateRange(models.Model):
    class Meta:
        abstract = True

    date_from = models.DateField()
    date_to = models.DateField()


class Office(models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=500, blank=True, null=True)


class OfficeAccount(models.Model):
    office = models.ForeignKey(Office)
    account = models.ForeignKey(Account)


class Provider(models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=500, blank=True, null=True)
    account = models.ForeignKey(Account)


class OfficeProviderAccount(models.Model):
    office = models.ForeignKey(Office)
    provider = models.ForeignKey(Provider)
    account = models.ForeignKey(Account)


class Agency(models.Model):
    class Meta:
        verbose_name = 'Agency'
        verbose_name_plural = 'Agencies'

    name = models.CharField(max_length=50)
    description = models.CharField(max_length=500, blank=True, null=True)
    account = models.ForeignKey(Account)


class OfficeAgencyAccount(models.Model):
    office = models.ForeignKey(Office)
    agency = models.ForeignKey(Agency)
    account = models.ForeignKey(Account)


class BoardType(models.Model):
    class Meta:
        verbose_name = 'Board Type'
        verbose_name_plural = 'Boards Types'

    code = models.CharField(max_length=10)
    name = models.CharField(max_length=20)


class RoomType(models.Model):
    class Meta:
        verbose_name = 'Room Type'
        verbose_name_plural = 'Rooms Types'

    code = models.CharField(max_length=20)
    name = models.CharField(max_length=40)


class PaxType(models.Model):
    class Meta:
        verbose_name = 'Pax Type'
        verbose_name_plural = 'Paxes Types'

    code = models.CharField(max_length=10)
    name = models.CharField(max_length=20)
    age_from = models.IntegerField()
    age_to = models.IntegerField()


class ServiceCategory(models.Model):
    class Meta:
        verbose_name = 'Service Category'
        verbose_name_plural = 'Services Categories'
    name = models.CharField(max_length=50)


class Service(models.Model):
    name = models.CharField(max_length=50)
    category = models.ForeignKey(ServiceCategory)


class Location(models.Model):
    name = models.CharField(max_length=50)


class Accommodation(Service):
    location = models.ForeignKey(Location)


class AccommodationBoardType(models.Model):
    class Meta:
        verbose_name = 'Accommodation Board Type'
        verbose_name_plural = 'Accommodations Boards Types'
    accommodation = models.ForeignKey(Accommodation)
    provider = models.ForeignKey(Provider)
    board_type = models.ForeignKey(BoardType)


class AccommodationRoomType(models.Model):
    class Meta:
        verbose_name = 'Accommodation Room Type'
        verbose_name_plural = 'Accommodations Rooms Types'
    accommodation = models.ForeignKey(Accommodation)
    provider = models.ForeignKey(Provider)
    room_type = models.ForeignKey(RoomType)


class AccommodationPaxes(models.Model):
    class Meta:
        verbose_name = 'Accommodation Paxes'
        verbose_name_plural = 'Accommodations Paxes'
    accommodation = models.ForeignKey(Accommodation)
    provider = models.ForeignKey(Provider)
    paxes = models.CharField(max_length=50)


class AccommodationAvailability(DateRange):
    class Meta:
        verbose_name = 'Accommodation Availability'
        verbose_name_plural = 'Accommodations Availabilities'

    accommodation = models.ForeignKey(Accommodation)
    provider = models.ForeignKey(Provider)
    room_type = models.ForeignKey(RoomType)
    availability = models.SmallIntegerField(default=10)


class AccommodationCost(DateRange):
    class Meta:
        abstract = True
    name = models.CharField(max_length=50)
    accommodation = models.ForeignKey(Accommodation)
    provider = models.ForeignKey(Provider)
    room_type = models.ForeignKey(RoomType)
    board_type = models.ForeignKey(BoardType)
    cost = models.DecimalField(max_digits=8, decimal_places=2)


class AgencyPrice(models.Model):
    class Meta:
        abstract = True
    agency = models.ForeignKey(Agency)
    price = models.DecimalField(max_digits=8, decimal_places=2)


class AccommodationRoomCost(AccommodationCost):
    class Meta:
        verbose_name = 'Accommodation Room Cost'
        verbose_name_plural = 'Accommodations Rooms Costs'
    paxes = models.CharField(max_length=50)


class AccommodationRoomPrice(AgencyPrice):
    class Meta:
        verbose_name = 'Accommodation Room Price'
        verbose_name_plural = 'Accommodations Rooms Prices'
    accommodation_room_cost = models.ForeignKey(AccommodationRoomCost)


class AccommodationSuplementCost(AccommodationCost):
    class Meta:
        verbose_name = 'Accommodation Suplement Cost'
        verbose_name_plural = 'Accommodations Suplements Costs'
    cost_by = models.CharField(
        max_length=10, choices=COST_BY, default=COST_BY_PAX)


class AccommodationSuplementPrice(AgencyPrice):
    class Meta:
        verbose_name = 'Accommodation Suplement Price'
        verbose_name_plural = 'Accommodations Suplements Prices'
    accommodation_suplement_cost = models.ForeignKey(
        AccommodationSuplementCost)
