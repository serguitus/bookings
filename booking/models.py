"""
Booking models
"""
from django.db import models

from accounting.constants import CURRENCIES, CURRENCY_CUC

from booking.constants import (
    ORDER_STATUS_LIST, ORDER_STATUS_PENDING,
    BOOKING_STATUS_LIST, BOOKING_STATUS_PENDING,
    SERVICE_STATUS_LIST, SERVICE_STATUS_PENDING)

from config.constants import (BOARD_TYPES, SERVICE_CATEGORIES,
                              SERVICE_CATEGORY_TRANSFER,
                              SERVICE_CATEGORY_ALLOTMENT,
                              SERVICE_CATEGORY_EXTRA)
from config.models import (
    Service, ServiceSupplement,
    RoomType, Allotment, AllotmentRoomType, AllotmentBoardType,
    Transfer, Location,
    Extra,
)

from finance.models import Agency, AgencyInvoice, Provider, ProviderInvoice

class Order(models.Model):
    """
    Order
    """
    class Meta:
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'
    description = models.CharField(max_length=1000)
    agency = models.ForeignKey(Agency)
    reference = models.CharField(max_length=250)
    date_from = models.DateField(blank=True, null=True)
    date_to = models.DateField(blank=True, null=True)
    status = models.CharField(
        max_length=5, choices=BOOKING_STATUS_LIST, default=ORDER_STATUS_PENDING)
    currency = models.CharField(
        max_length=5, choices=CURRENCIES, default=CURRENCY_CUC)
    currency_factor = models.DecimalField(max_digits=12, decimal_places=6, default=1.0)

    def fill_data(self):
        pass

    def save(self, *args, **kwargs):
        self.fill_data()
        # Call the "real" save() method.
        super(Order, self).save(*args, **kwargs)

    def __str__(self):
        return '%s - %s %s-%s (%s)' % (
            self.agency.name, self.reference, self.date_from, self.date_to, self.get_status_display())


class OrderPax(models.Model):
    """
    Order Pax
    """
    class Meta:
        verbose_name = 'Order Pax'
        verbose_name_plural = 'Orders Paxes'
        unique_together = (('order', 'pax_quantity'),)
    order = models.ForeignKey(Order)
    pax_quantity = models.SmallIntegerField()
    cost_amount = models.DecimalField(max_digits=10, decimal_places=2,
                                      blank=True, null=True)
    cost_comments = models.CharField(max_length=1000, blank=True, null=True)
    price_amount = models.DecimalField(max_digits=10, decimal_places=2,
                                       blank=True, null=True)
    price_comments = models.CharField(max_length=1000, blank=True, null=True)

    def __str__(self):
        return '%s (age: %s)' % (self.pax_name, self.pax_age)


class OrderService(models.Model):
    """
    Order Service
    """
    class Meta:
        verbose_name = 'Order Service'
        verbose_name_plural = 'Order Services'
    order = models.ForeignKey(Order)
    name = models.CharField(max_length=250, default='Booking Service')
    # this will store the child object type
    service_type = models.CharField(max_length=5, choices=SERVICE_CATEGORIES,
                                    blank=True, null=True)
    description = models.CharField(max_length=1000, default='')
    datetime_from = models.DateTimeField(blank=True, null=True)
    datetime_to = models.DateTimeField(blank=True, null=True)
    status = models.CharField(
        max_length=5, choices=SERVICE_STATUS_LIST, default=SERVICE_STATUS_PENDING)
    provider = models.ForeignKey(Provider, blank=True, null=True)

    def fill_data(self):
        pass

    def save(self, *args, **kwargs):
        self.fill_data()
        # Call the "real" save() method.
        super(OrderService, self).save(*args, **kwargs)


class OrderAllotment(OrderService):
    """
    Order Service Allotment
    """
    class Meta:
        verbose_name = 'Order Allotment'
        verbose_name_plural = 'Orders Allotments'
    service = models.ForeignKey(Allotment)
    room_type = models.ForeignKey(RoomType)
    board_type = models.CharField(max_length=5, choices=BOARD_TYPES)

    def fill_data(self):
        self.name = '%s' % (self.service,)
        self.service_type = SERVICE_CATEGORY_ALLOTMENT


class OrderTransfer(OrderService):
    """
    Order Service Transfer
    """
    class Meta:
        verbose_name = 'Order Transfer'
        verbose_name_plural = 'Orders Transfers'
    service = models.ForeignKey(Transfer)
    location_from = models.ForeignKey(Location, related_name='order_location_from', verbose_name='Location from')
    location_to = models.ForeignKey(Location, related_name='order_location_to', verbose_name='Location to')

    def fill_data(self):
        # setting name for this booking_service
        self.name = '%s (%s -> %s)' % (self.service,
                                       self.location_from.short_name or self.location_from,
                                       self.location_to.short_name or self.location_to)
        self.service_type = SERVICE_CATEGORY_TRANSFER


class OrderExtra(OrderService):
    """
    Order Service Extra
    """
    class Meta:
        verbose_name = 'Order Extra'
        verbose_name_plural = 'Orders Extras'
    service = models.ForeignKey(Extra)
    parameter = models.SmallIntegerField()

    def fill_data(self):
        self.service_type = SERVICE_CATEGORY_EXTRA


class OrderServicePax(models.Model):
    """
    Booking Service Pax
    """
    class Meta:
        verbose_name = 'Order Service Pax'
        verbose_name_plural = 'Orders Services Paxes'
    order_pax = models.ForeignKey(OrderPax)
    order_service = models.ForeignKey(OrderService)
    cost_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    cost_comments = models.CharField(max_length=1000, blank=True, null=True)
    price_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    price_comments = models.CharField(max_length=1000, blank=True, null=True)

    def fill_data(self):
        pass

    def save(self, *args, **kwargs):
        self.fill_data()
        # Call the "real" save() method.
        super(OrderServicePax, self).save(*args, **kwargs)


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
    date_from = models.DateField(blank=True, null=True)
    date_to = models.DateField(blank=True, null=True)
    status = models.CharField(
        max_length=5, choices=BOOKING_STATUS_LIST, default=BOOKING_STATUS_PENDING)
    currency = models.CharField(
        max_length=5, choices=CURRENCIES, default=CURRENCY_CUC)
    currency_factor = models.DecimalField(max_digits=12, decimal_places=6, default=1.0)
    cost_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    cost_comments = models.CharField(max_length=1000, blank=True, null=True)
    price_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    price_comments = models.CharField(max_length=1000, blank=True, null=True)
    agency_invoice = models.ForeignKey(AgencyInvoice,blank=True, null=True)

    def internal_reference(self):
        code = self.id
        return 'I-%s' % code

    def fill_data(self):
        pass

    def save(self, *args, **kwargs):
        self.fill_data()
        # Call the "real" save() method.
        super(Booking, self).save(*args, **kwargs)

    def __str__(self):
        return '%s - %s %s-%s (%s)' % (
            self.agency.name, self.reference, self.date_from, self.date_to, self.get_status_display())


class BookingPax(models.Model):
    """
    Booking Pax
    """
    class Meta:
        verbose_name = 'Booking Pax'
        verbose_name_plural = 'Bookings Paxes'
        unique_together = (('booking', 'pax_name'),)
    booking = models.ForeignKey(Booking, related_name='rooming_list')
    pax_name = models.CharField(max_length=50)
    pax_age = models.SmallIntegerField(blank=True, null=True)
    pax_group = models.SmallIntegerField()
    cost_amount = models.DecimalField(max_digits=10, decimal_places=2,
                                      blank=True, null=True)
    cost_comments = models.CharField(max_length=1000, blank=True, null=True)
    price_amount = models.DecimalField(max_digits=10, decimal_places=2,
                                       blank=True, null=True)
    price_comments = models.CharField(max_length=1000, blank=True, null=True)

    def __str__(self):
        return '%s (age: %s)' % (self.pax_name, self.pax_age)


class BookingService(models.Model):
    """
    Booking Service
    """
    class Meta:
        verbose_name = 'Booking Service'
        verbose_name_plural = 'Booking Services'
        default_permissions = ('add', 'change',)
    booking = models.ForeignKey(Booking, related_name='booking_services')
    name = models.CharField(max_length=250, default='Booking Service')
    # this will store the child object type
    service_type = models.CharField(max_length=5, choices=SERVICE_CATEGORIES,
                                    blank=True, null=True)
    description = models.CharField(max_length=1000, default='')
    datetime_from = models.DateTimeField(blank=True, null=True)
    datetime_to = models.DateTimeField(blank=True, null=True)
    status = models.CharField(
        max_length=5, choices=SERVICE_STATUS_LIST, default=SERVICE_STATUS_PENDING)
    cost_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    cost_comments = models.CharField(max_length=1000, blank=True, null=True)
    price_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    price_comments = models.CharField(max_length=1000, blank=True, null=True)
    provider = models.ForeignKey(Provider, blank=True, null=True)
    provider_invoice = models.ForeignKey(ProviderInvoice, blank=True, null=True)

    def fill_data(self):
        pass

    def save(self, *args, **kwargs):
        self.fill_data()
        # Call the "real" save() method.
        super(BookingService, self).save(*args, **kwargs)


class BookingServicePax(models.Model):
    """
    Booking Service Pax
    """
    class Meta:
        verbose_name = 'Booking Service Pax'
        verbose_name_plural = 'Bookings Services Paxes'
    booking_pax = models.ForeignKey(BookingPax)
    booking_service = models.ForeignKey(BookingService)
    group = models.SmallIntegerField()
    cost_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    cost_comments = models.CharField(max_length=1000, blank=True, null=True)
    price_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    price_comments = models.CharField(max_length=1000, blank=True, null=True)

    def fill_data(self):
        pass

    def save(self, *args, **kwargs):
        self.fill_data()
        # Call the "real" save() method.
        super(BookingServicePax, self).save(*args, **kwargs)


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
    service = models.ForeignKey(Extra)
    quantity = models.SmallIntegerField()
    parameter = models.SmallIntegerField()

    def fill_data(self):
        self.service_type = SERVICE_CATEGORY_EXTRA


class BookingAllotment(BookingService):
    """
    Booking Service Allotment
    """
    class Meta:
        verbose_name = 'Booking Allotment'
        verbose_name_plural = 'Bookings Allotments'
    service = models.ForeignKey(Allotment)
    room_type = models.ForeignKey(RoomType)
    board_type = models.CharField(max_length=5, choices=BOARD_TYPES)

    def fill_data(self):
        self.name = '%s' % (self.service,)
        self.service_type = SERVICE_CATEGORY_ALLOTMENT


class BookingTransfer(BookingService):
    """
    Booking Service Transfer
    """
    class Meta:
        verbose_name = 'Booking Transfer'
        verbose_name_plural = 'Bookings Transfers'
    service = models.ForeignKey(Transfer)
    location_from = models.ForeignKey(Location, related_name='location_from')
    location_to = models.ForeignKey(Location, related_name='location_to')
    quantity = models.SmallIntegerField(default=1)

    def fill_data(self):
        # setting name for this booking_service
        self.name = '%s (%s -> %s)' % (self.service,
                                       self.location_from.short_name or self.location_from,
                                       self.location_to.short_name or self.location_to)
        self.service_type = SERVICE_CATEGORY_TRANSFER


class BookingTransferSupplement(BookingServiceSupplement):
    """
    Transfer Supplement
    """
    class Meta:
        verbose_name = 'Booking Transfer Line Supplement'
        verbose_name_plural = 'Bookings Transfers Lines Supplements'
    quantity = models.SmallIntegerField(default=1)
