from django.db import models
from django.db.models import Sum

from accounting.models import *

from booking.constants import *

from config.models import *

from finance.models import *

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
    class Meta:
        verbose_name = 'Booking'
        verbose_name_plural = 'Bookings'
    description = models.CharField(max_length = 1000)
    reference = models.CharField(max_length = 256)
    status = models.CharField(max_length=2, choices = BOOKING_STATUS_LIST, default = BOOKING_STATUS_REQUEST)
    agency_invoice = models.ForeignKey(AgencyInvoice)

class BookingPax(models.Model):
    class Meta:
        verbose_name = 'Booking Pax'
        verbose_name_plural = 'Bookings Paxes'
    name = models.CharField(max_length = 50)
    age = models.SmallIntegerField()
    

class BookingService(Sale, DateTimeRange):
    class Meta:
        verbose_name = 'Booking Service'
        verbose_name_plural = 'Bookings Services'
    booking = models.ForeignKey(Booking)
    service = models.ForeignKey(Service)
    description = models.CharField(max_length = 1000)
    status = models.CharField(max_length=2, choices = SERVICE_STATUS_LIST, default = SERVICE_STATUS_REQUEST)
    provider_invoice = models.ForeignKey(ProviderInvoice)


class BookingAllotment(BookingService):
    class Meta:
        verbose_name = 'Booking Allotment'
        verbose_name_plural = 'Bookings Allotments'
    allotment = models.ForeignKey(Allotment)


class BookingTransfer(BookingService):
    class Meta:
        verbose_name = 'Booking Transfer'
        verbose_name_plural = 'Bookings Transfers'
    transfer = models.ForeignKey(Transfer)


class BookingServiceLine(Sale, DateTimeRange):
    class Meta:
        verbose_name = 'Booking Service Line'
        verbose_name_plural = 'Bookings Services Lines'
    booking_service = models.ForeignKey(BookingService)
    description = models.CharField(max_length = 1000)
    list_unit_cost = models.DecimalField(max_digits = 10, decimal_places = 2)
    list_unit_price = models.DecimalField(max_digits = 10, decimal_places = 2)
    status = models.CharField(max_length=2, choices = LINE_STATUS_LIST, default = LINE_STATUS_REQUEST)
    provider_invoice = models.ForeignKey(ProviderInvoice)


class BookingAllotmentLine(BookingServiceLine, AllotmentDefinition):
    class Meta:
        verbose_name = 'Booking Allotment Line'
        verbose_name_plural = 'Bookings Allotments Lines'


class BookingAllotmentLinePax(models.Model):
    class Meta:
        verbose_name = 'Booking Allotment Line Pax'
        verbose_name_plural = 'Bookings Allotments Lines Paxes'
    booking_allotment_line = models.ForeignKey(BookingAllotmentLine)
    booking_pax = models.ForeignKey(BookingPax)


class BookingTransferLine(BookingServiceLine, TransferDefinition):
    class Meta:
        verbose_name = 'Booking Transfer Line'
        verbose_name_plural = 'Bookings Transfers Lines'
    pax_qtty = models.SmallIntegerField()
    transport_qtty = models.SmallIntegerField(default=1)


class BookingServiceLineSupplement(Sale, DateTimeRange):
    class Meta:
        verbose_name = 'Booking Service Line Supplement'
        verbose_name_plural = 'Bookings Services Lines Supplements'
    booking_service_line = models.ForeignKey(BookingServiceLine)
    description = models.CharField(max_length = 1000)


class BookingAllotmentLineSupplement(BookingServiceLineSupplement):
    class Meta:
        verbose_name = 'Booking Allotment Line Supplement'
        verbose_name_plural = 'Bookings Allotments Lines Supplements'
    supplement = models.ForeignKey(AllotmentSupplement)


class BookingTransferLineSupplement(BookingServiceLineSupplement):
    class Meta:
        verbose_name = 'Booking Transfer Line Supplement'
        verbose_name_plural = 'Bookings Transfers Lines Supplements'
    supplement = models.ForeignKey(TransferSupplement)
    hours = models.SmallIntegerField(default=1)



