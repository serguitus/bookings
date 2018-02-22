from django.db import models
from django.db.models import Sum
from accounting.models import Account, Movement, Operation
from config.models import Agency, Office, Provider, BoardType, RoomType, PaxType, Service

class DateTimeRange(models.Model):
    class Meta:
        abstract = True
    date_from = models.DateTimeField()
    date_to = models.DateTimeField()

class Sale(models.Model):
    class Meta:
        abstract = True
    list_cost = models.DecimalField(max_digits = 10, decimal_places = 2)
    list_price = models.DecimalField(max_digits = 10, decimal_places = 2)
    cost = models.DecimalField(max_digits = 10, decimal_places = 2)
    price = models.DecimalField(max_digits = 10, decimal_places = 2)

class Booking(Sale, DateTimeRange):
    agency = models.ForeignKey(Agency)
    office = models.ForeignKey(Office)
    description = models.CharField(max_length = 1000)
    reference = models.CharField(max_length = 256)
    deleted = models.BooleanField(default = False)
    
class BookingService(Sale, DateTimeRange):
    booking = models.ForeignKey(Booking)
    service = models.ForeignKey(Service)
    provider = models.ForeignKey(Provider)
    description = models.CharField(max_length = 1000)
    qtty = models.SmallIntegerField(default = 1)
    unit_cost = models.DecimalField(max_digits = 10, decimal_places = 2)
    unit_price = models.DecimalField(max_digits = 10, decimal_places = 2)
    deleted = models.BooleanField(default = False)

class Invoice(models.Model):
    booking = models.ForeignKey(Booking)
    price = models.DecimalField(max_digits = 10, decimal_places = 2)
    file = models.FileField()
    
class BookingAccomodation(BookingService):
    room_type = models.ForeignKey(RoomType)
    board_type = models.ForeignKey(BoardType)
    pax_description = models.CharField(max_length = 40)

    def save(self, *args, **kwargs):
        self.description = self.room_type.code + ' : ' + self.board_type.code + ' : ' + self.pax_description
        return super(BookingService, self).save(*args, **kwargs)
    
class BookingAccomodationPax(models.Model):
    booking_accomodation = models.ForeignKey(BookingAccomodation)
    pax = models.ForeignKey(PaxType)
    qtty = models.SmallIntegerField(default = 1)
    
class AgencyPayment(models.Model):
    agency = models.ForeignKey(Agency)
    amount = models.DecimalField(max_digits = 12, decimal_places = 2)
    operation = models.ForeignKey(Operation)
    deleted = models.BooleanField(default = False)

class AgencyPaymentInvoice(models.Model):
    agency_payment = models.ForeignKey(AgencyPayment)
    invoice = models.ForeignKey(Invoice)
    amount = models.DecimalField(max_digits = 10, decimal_places = 2)
    operation = models.ForeignKey(Operation)

class ProviderPayment(models.Model):
    provider = models.ForeignKey(Provider)
    amount = models.DecimalField(max_digits = 12, decimal_places = 2)
    operation = models.ForeignKey(Operation)
    deleted = models.BooleanField(default = False)

class ProviderPaymentBookingService(models.Model):
    provider_payment = models.ForeignKey(ProviderPayment)
    booking_service = models.ForeignKey(BookingService)
    amount = models.DecimalField(max_digits = 10, decimal_places = 2)
    operation = models.ForeignKey(Operation)

