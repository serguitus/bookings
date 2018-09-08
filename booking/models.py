"""
Booking models
"""
from django.db import models

from accounting.constants import CURRENCIES, CURRENCY_CUC

from booking.constants import (
    BOOKING_STATUS_LIST, BOOKING_STATUS_PENDING,
    SERVICE_STATUS_LIST, SERVICE_STATUS_PENDING)

from config.constants import BOARD_TYPES
from config.models import Service, ServiceSupplement, AllotmentRoomType

from finance.models import Agency, AgencyInvoice, Provider, ProviderInvoice

class Booking(models.Model):
    """
    Booking
    """
    class Meta:
        verbose_name = 'Booking'
        verbose_name_plural = 'Bookings'
        default_permissions = ('add', 'change',)
    description = models.CharField(max_length=1000)
    agency = models.ForeignKey(Agency)
    reference = models.CharField(max_length=250)
    date_from = models.DateField()
    date_to = models.DateField()
    status = models.CharField(
        max_length=5, choices=BOOKING_STATUS_LIST, default=BOOKING_STATUS_PENDING)
    currency = models.CharField(
        max_length=5, choices=CURRENCIES, default=CURRENCY_CUC)
    currency_factor = models.DecimalField(max_digits=12, decimal_places=6)
    cost_amount = models.DecimalField(max_digits=10, decimal_places=2)
    cost_comments = models.CharField(max_length=1000)
    price_amount = models.DecimalField(max_digits=10, decimal_places=2)
    price_comments = models.CharField(max_length=1000)
    agency_invoice = models.ForeignKey(AgencyInvoice, blank=True, null=True)

    def fill_data(self):
        pass

    def save(self, *args, **kwargs):
        self.fill_data()
        # Call the "real" save() method.
        super(Booking, self).save(*args, **kwargs)


class BookingPax(models.Model):
    """
    Booking Pax
    """
    class Meta:
        verbose_name = 'Booking Pax'
        verbose_name_plural = 'Bookings Paxes'
        unique_together = (('booking', 'pax_name'),)
    booking = models.ForeignKey(Booking)
    pax_name = models.CharField(max_length=50)
    pax_age = models.SmallIntegerField(blank=True, null=True)
    pax_group = models.SmallIntegerField()
    cost_amount = models.DecimalField(max_digits=10, decimal_places=2)
    cost_comments = models.CharField(max_length=1000)
    price_amount = models.DecimalField(max_digits=10, decimal_places=2)
    price_comments = models.CharField(max_length=1000)


class BookingService(models.Model):
    """
    Booking Service
    """
    class Meta:
        verbose_name = 'Booking Service'
        verbose_name_plural = 'Bookings Services'
        default_permissions = ('add', 'change',)
    booking = models.ForeignKey(Booking)
    service = models.ForeignKey(Service)
    description = models.CharField(max_length=1000)
    datetime_from = models.DateTimeField()
    datetime_to = models.DateTimeField()
    status = models.CharField(
        max_length=5, choices=SERVICE_STATUS_LIST, default=SERVICE_STATUS_PENDING)
    cost_amount = models.DecimalField(max_digits=10, decimal_places=2)
    cost_comments = models.CharField(max_length=1000)
    price_amount = models.DecimalField(max_digits=10, decimal_places=2)
    price_comments = models.CharField(max_length=1000)
    provider = models.ForeignKey(Provider)
    provider_invoice = models.ForeignKey(ProviderInvoice)

    def fill_data(self):
        pass

    def save(self, *args, **kwargs):
        self.fill_data()
        # Call the "real" save() method.
        super().save(*args, **kwargs)


class BookingServiceGroup(models.Model):
    """
    Booking Service Group
    """
    class Meta:
        verbose_name = 'Booking Service Group'
        verbose_name_plural = 'Bookings Services Group'
    booking_service = models.ForeignKey(BookingService)
    group = models.SmallIntegerField()
    cost_amount = models.DecimalField(max_digits=10, decimal_places=2)
    cost_comments = models.CharField(max_length=1000)
    price_amount = models.DecimalField(max_digits=10, decimal_places=2)
    price_comments = models.CharField(max_length=1000)

    def fill_data(self):
        pass

    def save(self, *args, **kwargs):
        self.fill_data()
        # Call the "real" save() method.
        super().save(*args, **kwargs)


class BookingPaxServiceGroup(models.Model):
    """
    Booking Pax Service Group
    """
    class Meta:
        verbose_name = 'Booking Pax Service Group'
        verbose_name_plural = 'Bookings Paxes Services Groups'
    booking_pax = models.ForeignKey(BookingPax)
    service_group = models.ForeignKey(BookingServiceGroup)
    cost_amount = models.DecimalField(max_digits=10, decimal_places=2)
    cost_comments = models.CharField(max_length=1000)
    price_amount = models.DecimalField(max_digits=10, decimal_places=2)
    price_comments = models.CharField(max_length=1000)

    def fill_data(self):
        pass

    def save(self, *args, **kwargs):
        self.fill_data()
        # Call the "real" save() method.
        super().save(*args, **kwargs)


class BookingServiceSupplement(models.Model):
    """
    Booking Service Supplement
    """
    class Meta:
        verbose_name = 'Booking Service Supplement'
        verbose_name_plural = 'Bookings Services Supplements'
    booking_service = models.ForeignKey(BookingService)
    supplement = models.ForeignKey(ServiceSupplement)
    cost_amount = models.DecimalField(max_digits=10, decimal_places=2)
    cost_comments = models.CharField(max_length=1000)
    price_amount = models.DecimalField(max_digits=10, decimal_places=2)
    price_comments = models.CharField(max_length=1000)

    def fill_data(self):
        pass

    def save(self, *args, **kwargs):
        self.fill_data()
        # Call the "real" save() method.
        super().save(*args, **kwargs)


class ServiceSupplementBookingPax(models.Model):
    """
    Service Supplement Booking Pax
    """
    class Meta:
        verbose_name = 'Service Supplement Booking Pax'
        verbose_name_plural = 'Services Supplements Bookings Paxes'
    service_supplment = models.ForeignKey(BookingServiceSupplement)
    booking_pax = models.ForeignKey(BookingPax)
    supplement_qtty = models.SmallIntegerField(default=1)
    description = models.CharField(max_length=1000)
    datetime_from = models.DateTimeField()
    datetime_to = models.DateTimeField()
    cost_amount = models.DecimalField(max_digits=10, decimal_places=2)
    cost_comments = models.CharField(max_length=1000)
    price_amount = models.DecimalField(max_digits=10, decimal_places=2)
    price_comments = models.CharField(max_length=1000)

    def fill_data(self):
        pass

    def save(self, *args, **kwargs):
        self.fill_data()
        # Call the "real" save() method.
        super().save(*args, **kwargs)


class BookingExtra(BookingService):
    """
    Booking Service Extra
    """
    class Meta:
        verbose_name = 'Booking Extra'
        verbose_name_plural = 'Bookings Extras'
    extra_qtty = models.SmallIntegerField()


class BookingAllotment(BookingService):
    """
    Booking Service Allotment
    """
    class Meta:
        verbose_name = 'Booking Allotment'
        verbose_name_plural = 'Bookings Allotments'
    room_type = models.ForeignKey(AllotmentRoomType)
    board_type = models.CharField(max_length=5, choices=BOARD_TYPES)


class BookingTransfer(BookingService):
    """
    Booking Service Transfer
    """
    class Meta:
        verbose_name = 'Booking Transfer'
        verbose_name_plural = 'Bookings Transfers'


class BookingTransferSupplement(BookingServiceSupplement):
    """
    Transfer Supplement
    """
    class Meta:
        verbose_name = 'Booking Transfer Line Supplement'
        verbose_name_plural = 'Bookings Transfers Lines Supplements'
    hours = models.SmallIntegerField()
