# -*- coding: utf-8 -*-
from __future__ import unicode_literals
"""
Booking models
"""
from django.db import models, transaction

from accounting.constants import CURRENCIES, CURRENCY_CUC

from booking.constants import (
    SERVICE_CATEGORY_PACKAGE, SERVICE_CATEGORIES,
    QUOTE_STATUS_LIST, QUOTE_STATUS_DRAFT,
    BOOKING_STATUS_LIST, BOOKING_STATUS_PENDING,
    SERVICE_STATUS_LIST, SERVICE_STATUS_PENDING,
    PACKAGE_AMOUNTS_BY_PAX, PACKAGE_AMOUNTS_TYPES)

from config.constants import (BOARD_TYPES,
                              SERVICE_CATEGORY_TRANSFER,
                              SERVICE_CATEGORY_ALLOTMENT,
                              SERVICE_CATEGORY_EXTRA)
from config.models import (
    Service,
    ServiceSupplement,
    RoomType, Allotment,
    Transfer, Location, Place, Schedule,
    Extra, Addon,
    AmountDetail, AgencyCatalogue, ProviderCatalogue,
)

from finance.models import Agency, AgencyInvoice, Provider, ProviderInvoice


class RelativeInterval(models.Model):
    class Meta:
        abstract = True
    days_after = models.SmallIntegerField(
        default=0, blank=True, null=True, verbose_name='Days after')
    days_duration = models.SmallIntegerField(
        default=0, blank=True, null=True, verbose_name='Days duration')


class DateInterval(models.Model):
    class Meta:
        abstract = True
    datetime_from = models.DateField(blank=True, null=True, verbose_name='Date From')
    datetime_to = models.DateField(blank=True, null=True, verbose_name='Date To')


class PaxVariantAmounts(models.Model):
    class Meta:
        abstract = True
    cost_single_amount = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True, verbose_name='Cost SGL')
    cost_double_amount = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True, verbose_name='Cost DBL')
    cost_triple_amount = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True, verbose_name='Cost TPL')
    price_single_amount = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True, verbose_name='Price SGL')
    price_double_amount = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True, verbose_name='Price DBL')
    price_triple_amount = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True, verbose_name='Price TPL')
    free_cost_single = models.SmallIntegerField(default=0)
    free_cost_double = models.SmallIntegerField(default=0)
    free_cost_triple = models.SmallIntegerField(default=0)
    free_price_single = models.SmallIntegerField(default=0)
    free_price_double = models.SmallIntegerField(default=0)
    free_price_triple = models.SmallIntegerField(default=0)


class BaseService(models.Model):
    class Meta:
        abstract = True
    name = models.CharField(max_length=250, default='Base Service')
    # this will store the child object type
    service_type = models.CharField(max_length=5, choices=SERVICE_CATEGORIES,
                                    blank=True, null=True)
    # this will store related serice's location
    service_location = models.CharField(max_length=50, blank=True, null=True,
                                        verbose_name='Location')
    description = models.CharField(max_length=1000, blank=True, null=True)
    status = models.CharField(
        max_length=5, choices=SERVICE_STATUS_LIST,
        default=SERVICE_STATUS_PENDING)
    provider = models.ForeignKey(Provider, blank=True, null=True)


class BaseAllotment(BaseService):
    """
    Base Service Allotment
    """
    class Meta:
        abstract = True
    service = models.ForeignKey(Allotment)
    room_type = models.ForeignKey(RoomType)
    board_type = models.CharField(max_length=5, choices=BOARD_TYPES)


class BaseTransfer(BaseService):
    """
    Base Service Transfer
    """
    class Meta:
        abstract = True
    service = models.ForeignKey(Transfer)
    time = models.TimeField(blank=True, null=True)
    quantity = models.SmallIntegerField(default=1)


class BaseExtra(BaseService):
    """
    Base Service Extra
    """
    class Meta:
        abstract = True
    service = models.ForeignKey(Extra)
    addon = models.ForeignKey(Addon, blank=True, null=True)
    time = models.TimeField(blank=True, null=True)
    quantity = models.SmallIntegerField(default=1)
    parameter = models.SmallIntegerField(default=0, verbose_name='Hours')


class Package(Service):
    """
    Package Service
    """
    class Meta:
        verbose_name = 'Package'
        verbose_name_plural = 'Packages'
    amounts_type = models.CharField(
        default=PACKAGE_AMOUNTS_BY_PAX, max_length=5, choices=PACKAGE_AMOUNTS_TYPES)
    has_pax_range = models.BooleanField(default=False)

    def fill_data(self):
        self.category = SERVICE_CATEGORY_PACKAGE

    def __str__(self):
        return '%s'  % self.name


class PackageService(BaseService, RelativeInterval):
    """
    Package Service
    """
    class Meta:
        verbose_name = 'Package Service'
        verbose_name_plural = 'Packages Services'
    package = models.ForeignKey(Package, related_name='package_services')

    def fill_data(self):
        pass

    def save(self, *args, **kwargs):
        self.fill_data()
        # Call the "real" save() method.
        super(PackageService, self).save(*args, **kwargs)


class PackageAllotment(PackageService, BaseAllotment):
    """
    Package Service Allotment
    """
    class Meta:
        verbose_name = 'Package Accomodation'
        verbose_name_plural = 'Packages Accomodations'

    def fill_data(self):
        self.name = '%s' % (self.service,)
        self.service_type = SERVICE_CATEGORY_ALLOTMENT


class PackageTransfer(PackageService, BaseTransfer):
    """
    Package Service Transfer
    """
    class Meta:
        verbose_name = 'Package Transfer'
        verbose_name_plural = 'Packages Transfers'
    location_from = models.ForeignKey(
        Location, related_name='package_location_from', verbose_name='Location from')
    place_from = models.ForeignKey(Place, related_name='package_place_from', blank=True, null=True)
    schedule_from = models.ForeignKey(
        Schedule, related_name='package_schedule_from', blank=True, null=True)
    pickup = models.ForeignKey(Allotment, related_name='package_pickup',
                               null=True, blank=True)
    location_to = models.ForeignKey(
        Location, related_name='package_location_to', verbose_name='Location to')
    place_to = models.ForeignKey(Place, related_name='package_place_to', blank=True, null=True)
    schedule_to = models.ForeignKey(
        Schedule, related_name='package_schedule_to', blank=True, null=True)
    dropoff = models.ForeignKey(Allotment, related_name='package_dropoff',
                                null=True, blank=True)

    def fill_data(self):
        # setting name for this booking_service
        self.name = '%s (%s -> %s)' % (self.service,
                                       self.location_from.short_name or self.location_from,
                                       self.location_to.short_name or self.location_to)
        self.service_type = SERVICE_CATEGORY_TRANSFER


class PackageExtra(PackageService, BaseExtra):
    """
    Package Service Extra
    """
    class Meta:
        verbose_name = 'Package Extra'
        verbose_name_plural = 'Packages Extras'

    def fill_data(self):
        # setting name for this booking_service
        self.name = self.service.name
        self.service_type = SERVICE_CATEGORY_EXTRA


class Quote(models.Model):
    """
    Quote
    """
    class Meta:
        verbose_name = 'Quote'
        verbose_name_plural = 'Quotes'
        default_permissions = ('add', 'change',)
    description = models.CharField(max_length=1000)
    agency = models.ForeignKey(Agency)
    reference = models.CharField(max_length=250)
    date_from = models.DateField(blank=True, null=True)
    date_to = models.DateField(blank=True, null=True)
    status = models.CharField(
        max_length=5, choices=QUOTE_STATUS_LIST, default=QUOTE_STATUS_DRAFT)
    currency = models.CharField(
        max_length=5, choices=CURRENCIES, default=CURRENCY_CUC)
    currency_factor = models.DecimalField(max_digits=12, decimal_places=6, default=1.0)
    program = models.CharField(
        max_length=2000, blank=True, null=True, verbose_name='Program')
    history = models.CharField(
        max_length=2000, blank=True, null=True, verbose_name='History')

    def fill_data(self):
        pass

    def save(self, *args, **kwargs):
        self.fill_data()
        # Call the "real" save() method.
        super(Quote, self).save(*args, **kwargs)

    def __str__(self):
        return '%s - %s %s - %s (%s)' % (
            self.agency.name, self.reference,
            self.date_from, self.date_to, self.get_status_display())


class QuotePaxVariant(PaxVariantAmounts):
    """
    Quote Pax
    """
    class Meta:
        verbose_name = 'Quote Pax'
        verbose_name_plural = 'Quotes Paxes'
        unique_together = (('quote', 'pax_quantity'),)
    quote = models.ForeignKey(Quote, related_name='quote_paxvariants')
    pax_quantity = models.SmallIntegerField()
    price_percent = models.SmallIntegerField(blank=True, null=True, verbose_name='Price %')

    def __str__(self):
        return '%s paxes' % (self.pax_quantity)


class QuoteService(BaseService, DateInterval):
    """
    Quote Service
    """
    class Meta:
        verbose_name = 'Quote Service'
        verbose_name_plural = 'Quote Services'
        default_permissions = ('add', 'change',)
    quote = models.ForeignKey(Quote, related_name='quote_services')

    def save(self, *args, **kwargs):
        self.fill_data()
        # Call the "real" save() method.
        super(QuoteService, self).save(*args, **kwargs)


class QuoteServicePaxVariant(PaxVariantAmounts):
    """
    Quote Service Pax Variant
    """
    class Meta:
        verbose_name = 'Quote Service Pax Variant'
        verbose_name_plural = 'Quotes Services Paxes Variants'
        unique_together = (('quote_pax_variant', 'quote_service'),)
    quote_pax_variant = models.ForeignKey(QuotePaxVariant, verbose_name='Pax Variant')
    quote_service = models.ForeignKey(QuoteService, related_name='quoteservice_paxvariants')
    manual_costs = models.BooleanField(default=False, verbose_name='Manual Costs')
    manual_prices = models.BooleanField(default=False, verbose_name='Manual Prices')

    def __str__(self):
        return self.quote_pax_variant.__str__()


class QuoteAllotment(QuoteService, BaseAllotment):
    """
    Quote Service Allotment
    """
    class Meta:
        verbose_name = 'Quote Accomodation'
        verbose_name_plural = 'Quotes Accomodations'
        default_permissions = ('add', 'change',)

    def fill_data(self):
        self.name = '%s' % (self.service,)
        self.service_type = SERVICE_CATEGORY_ALLOTMENT


class QuoteTransfer(QuoteService, BaseTransfer):
    """
    Quote Service Transfer
    """
    class Meta:
        verbose_name = 'Quote Transfer'
        verbose_name_plural = 'Quotes Transfers'
        default_permissions = ('add', 'change',)
    location_from = models.ForeignKey(
        Location, related_name='quote_location_from', verbose_name='Location from')
    location_to = models.ForeignKey(
        Location, related_name='quote_location_to', verbose_name='Location to')

    def fill_data(self):
        # setting name for this booking_service
        self.name = '%s (%s -> %s)' % (self.service,
                                       self.location_from.short_name or self.location_from,
                                       self.location_to.short_name or self.location_to)
        self.service_type = SERVICE_CATEGORY_TRANSFER


class QuoteExtra(QuoteService, BaseExtra):
    """
    Quote Service Extra
    """
    class Meta:
        verbose_name = 'Quote Extra'
        verbose_name_plural = 'Quotes Extras'
        default_permissions = ('add', 'change',)

    def fill_data(self):
        # setting name for this booking_service
        self.name = self.service.name
        self.service_type = SERVICE_CATEGORY_EXTRA


class QuotePackage(QuoteService):
    """
    Quote Service Package
    """
    class Meta:
        verbose_name = 'Quote Package'
        verbose_name_plural = 'Quotes Packages'
        default_permissions = ('add', 'change',)
    service = models.ForeignKey(Package)
    price_by_package_catalogue = models.BooleanField(
        default=False, verbose_name='Prices By Catalogue')

    def fill_data(self):
        # setting name for this quote_service
        self.name = self.service.name
        self.service_type = SERVICE_CATEGORY_PACKAGE

    def save(self, *args, **kwargs):
        with transaction.atomic(savepoint=False):
            super(QuotePackage, self).save(*args, **kwargs)

    def __str__(self):
        return '%s - %s' % (self.quote, self.service)


class QuotePackageService(BaseService, DateInterval):
    """
    Quote Package Service
    """
    class Meta:
        verbose_name = 'Quote Package Service'
        verbose_name_plural = 'Quotes Packages Services'
        default_permissions = ('add', 'change',)
    quote_package = models.ForeignKey(QuotePackage, related_name='quotepackage_services')

    def fill_data(self):
        pass

    def save(self, *args, **kwargs):
        self.fill_data()
        # Call the "real" save() method.
        super(QuotePackageService, self).save(*args, **kwargs)


class QuotePackageServicePaxVariant(PaxVariantAmounts):
    """
    Quote Package Service Pax Variant
    """
    class Meta:
        verbose_name = 'Quote Package Service Pax Variant'
        verbose_name_plural = 'Quotes Packages Services Paxes Variants'
        unique_together = (('quotepackage_pax_variant', 'quotepackage_service'),)
    quotepackage_pax_variant = models.ForeignKey(QuoteServicePaxVariant, verbose_name='Pax Variant')
    quotepackage_service = models.ForeignKey(QuotePackageService, related_name='quotepackageservice_paxvariants')
    manual_costs = models.BooleanField(default=False, verbose_name='Manual Costs')
    manual_prices = models.BooleanField(default=False, verbose_name='Manual Prices')


class QuotePackageAllotment(QuotePackageService, BaseAllotment):
    """
    Quote Package Service Allotment
    """
    class Meta:
        verbose_name = 'Quote Package Accomodation'
        verbose_name_plural = 'Quotes Packages Accomodations'
        default_permissions = ('add', 'change',)

    def fill_data(self):
        self.name = '%s' % (self.service,)
        self.service_type = SERVICE_CATEGORY_ALLOTMENT


class QuotePackageTransfer(QuotePackageService, BaseTransfer):
    """
    Quote Package Service Transfer
    """
    class Meta:
        verbose_name = 'Quote Package Transfer'
        verbose_name_plural = 'Quotes Packages Transfers'
        default_permissions = ('add', 'change',)
    location_from = models.ForeignKey(
        Location, related_name='quote_package_location_from', verbose_name='Location from')
    location_to = models.ForeignKey(
        Location, related_name='quote_package_location_to', verbose_name='Location to')

    def fill_data(self):
        # setting name for this quote_service
        self.name = '%s (%s -> %s)' % (self.service,
                                       self.location_from.short_name or self.location_from,
                                       self.location_to.short_name or self.location_to)
        self.service_type = SERVICE_CATEGORY_TRANSFER


class QuotePackageExtra(QuotePackageService, BaseExtra):
    """
    Quote Service Extra
    """
    class Meta:
        verbose_name = 'Quote Package Extra'
        verbose_name_plural = 'Quotes Packages Extras'
        default_permissions = ('add', 'change',)

    def fill_data(self):
        # setting name for this quote_service
        self.name = self.service.name
        self.service_type = SERVICE_CATEGORY_EXTRA


class BookingInvoice(AgencyInvoice):
    class Meta:
        verbose_name = 'Booking Invoice'
        verbose_name_plural = 'Bookings Invoices'
    booking_name = models.CharField(max_length=100, blank=True, null=True)
    reference = models.CharField(max_length=25, blank=True, null=True)
    date_from = models.DateField(blank=True, null=True)
    date_to = models.DateField(blank=True, null=True)

    def fill_data(self):
        super(BookingInvoice, self).fill_data()
        self.name = 'Booking Invoice to %s - %s Price %s %s' % (
            self.agency, self.date, self.amount, self.get_currency_display())


class BookingInvoiceLine(models.Model):
    class Meta:
        verbose_name = 'Booking Invoice Line'
        verbose_name_plural = 'Bookings Invoices Lines'
    invoice = models.ForeignKey(BookingInvoice)
    bookingservice_name = models.CharField(max_length=100, blank=True, null=True)
    service_name = models.CharField(max_length=100, blank=True, null=True)
    date_from = models.DateField(blank=True, null=True)
    date_to = models.DateField(blank=True, null=True)
    qtty = models.IntegerField(blank=True, null=True)
    unit = models.CharField(max_length=20, blank=True, null=True)
    unit_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)


class BookingInvoicePartial(models.Model):
    class Meta:
        verbose_name = 'Booking Invoice Partial'
        verbose_name_plural = 'Bookings Invoices Partials'
    invoice = models.ForeignKey(BookingInvoice)
    pax_name = models.CharField(max_length=100, blank=True, null=True)
    detail2 = models.CharField(max_length=100, blank=True, null=True)
    partial_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)


class Booking(models.Model):
    """
    Booking
    """
    class Meta:
        verbose_name = 'Booking'
        verbose_name_plural = 'Bookings'
        default_permissions = ('add', 'change',)
        permissions = (
            ("change_amounts", "Can change amounts of Booking"),
        )
    name = models.CharField(max_length=100)
    agency = models.ForeignKey(Agency)
    reference = models.CharField(max_length=25, blank=True, null=True, verbose_name='TTOO Ref')
    date_from = models.DateField(blank=True, null=True)
    date_to = models.DateField(blank=True, null=True)
    status = models.CharField(
        max_length=5, choices=BOOKING_STATUS_LIST, default=BOOKING_STATUS_PENDING)
    currency = models.CharField(
        max_length=5, choices=CURRENCIES, default=CURRENCY_CUC)
    currency_factor = models.DecimalField(max_digits=12, decimal_places=6, default=1.0)
    cost_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    cost_comments = models.CharField(max_length=1000, blank=True, null=True)
    price_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    price_comments = models.CharField(max_length=1000, blank=True, null=True)
    invoice = models.ForeignKey(BookingInvoice, blank=True, null=True)
    is_package_price = models.BooleanField(default=False, verbose_name='Package Price')
    package_sgl_price_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.0, verbose_name='Price SGL')
    package_dbl_price_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.0, verbose_name='Price DBL')
    package_tpl_price_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.0, verbose_name='Price TPL')
    # a field to add global notes to a booking
    p_notes = models.CharField(
        max_length=1000, blank=True, null=True, verbose_name='Private Notes')

    def internal_reference(self):
        if self.id:
            code = self.id
            return '%s' % (20000 + int(code))
        return ''
    internal_reference.short_description = 'TNX'

    def fill_data(self):
        pass

    def save(self, *args, **kwargs):
        self.fill_data()
        # Call the "real" save() method.
        super(Booking, self).save(*args, **kwargs)

    def __str__(self):
        return self.__unicode__()

    def __unicode__(self):
        return '%s - %s (%s) (%s)' % (
            self.agency.name, self.name,
            self.reference, self.get_status_display())


class BookingPax(models.Model):
    """
    Booking Pax
    """
    class Meta:
        verbose_name = 'Booking Pax'
        verbose_name_plural = 'Booking Rooming List'
        unique_together = (('booking', 'pax_name'),)
    booking = models.ForeignKey(Booking, related_name='rooming_list')
    pax_name = models.CharField(max_length=50)
    pax_age = models.SmallIntegerField(blank=True, null=True, verbose_name='Age')
    pax_group = models.SmallIntegerField(verbose_name='Room')
    cost_amount = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True, verbose_name='Cost')
    cost_comments = models.CharField(max_length=1000, blank=True, null=True)
    price_amount = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True, verbose_name='Price')
    price_comments = models.CharField(max_length=1000, blank=True, null=True)

    def __str__(self):
        return self.__unicode__()

    def __unicode__(self):
        if self.pax_age:
            return '%s (age: %s)' % (self.pax_name, self.pax_age)
        else:
            return '%s' % (self.pax_name)


class BookService(models.Model):
    """
    Booking Service
    """
    class Meta:
        abstract = True
    # This holds the confirmation number when it exists
    conf_number = models.CharField(max_length=20, blank=True, null=True)
    cost_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    cost_comments = models.CharField(max_length=1000, blank=True, null=True)
    price_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    price_comments = models.CharField(max_length=1000, blank=True, null=True)
    provider_invoice = models.ForeignKey(ProviderInvoice, blank=True, null=True)
    p_notes = models.CharField(
        max_length=1000, blank=True, null=True, verbose_name='Private Notes')
    provider_notes = models.CharField(
        max_length=1000, blank=True, null=True, verbose_name='Provider Notes')
    manual_cost = models.BooleanField(default=False)
    manual_price = models.BooleanField(default=False)


class BookingService(BaseService, BookService, DateInterval):
    """
    Booking Service
    """
    class Meta:
        verbose_name = 'Booking Service'
        verbose_name_plural = 'Booking Services'
        default_permissions = ('add', 'change',)
        ordering = ['datetime_from']
    booking = models.ForeignKey(Booking, related_name='booking_services')
    v_notes = models.CharField(
        max_length=1000, blank=True, null=True, verbose_name='Voucher Notes')

    def fill_data(self):
        pass

    def save(self, *args, **kwargs):
        self.fill_data()
        # Call the "real" save() method.
        super(BookingService, self).save(*args, **kwargs)

    def pax_qantities(self):
        return self.rooming_list.count()


class BookingServicePax(models.Model):
    """
    Booking Service Pax
    """
    class Meta:
        verbose_name = 'Booking Service Pax'
        verbose_name_plural = 'Booking Service Rooming'
    booking_pax = models.ForeignKey(BookingPax)
    booking_service = models.ForeignKey(BookingService, related_name='rooming_list')
    group = models.SmallIntegerField(verbose_name='Room')
    cost_amount = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True, verbose_name='Cost')
    cost_comments = models.CharField(max_length=1000, blank=True, null=True)
    is_cost_free = models.BooleanField(default=False)
    price_amount = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True, verbose_name='Price')
    price_comments = models.CharField(max_length=1000, blank=True, null=True)
    is_price_free = models.BooleanField(default=False)

    def fill_data(self):
        pass

    def save(self, *args, **kwargs):
        self.fill_data()
        # Call the "real" save() method.
        super(BookingServicePax, self).save(*args, **kwargs)

    def __str__(self):
        return self.__unicode__()

    def __unicode__(self):
        if self.booking_pax.pax_age:
            return '%s (age: %s)' % (
                self.booking_pax.pax_name,
                self.booking_pax.pax_age)
        else:
            return '%s' % (self.booking_pax.pax_name)


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
        super(BookingServiceSupplement, self).save(*args, **kwargs)


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
        super(ServiceSupplementBookingPax, self).save(*args, **kwargs)


class BookingAllotment(BookingService, BaseAllotment):
    """
    Booking Service Allotment
    """
    class Meta:
        verbose_name = 'Booking Accomodation'
        verbose_name_plural = 'Bookings Accomodations'
        default_permissions = ('add', 'change',)

    def build_description(self):
        """ makes a string detailing room quantity and types"""
        from booking.services import BookingServices
        rooms = BookingServices.find_groups(
            booking_service=self, service=self.service, for_cost=True)
        dist = ''
        room_count = {
            '00': 0,  # NONE counter
            '10': 0,  # SGL counter
            '20': 0,  # DBL counter
            '30': 0,  # TPL counter
            '11': 0,  # SGL+1Child
            '21': 0,  # DBL+1Child
            '22': 0,  # DBL+2Child
            '31': 0,  # TPL+1Child
            '40': 0,
        }
        room_types = {
            '00': 'NONE',
            '10': 'SGL',
            '20': 'DBL',
            '30': 'TPL',
            '11': 'SGL&1Chld',
            '21': 'DBL&1Chld',
            '22': 'DBL&2Chld',
            '31': 'TPL&1Chld',
            '40': 'QUAD'
        }
        for room in rooms:
            room_count['%d%d' % (room[0], room[1])] += 1
        for k in room_count.keys():
            if room_count[k]:
                if dist:
                    dist += ' + '
                dist += '%d %s' % (room_count[k], room_types[k])
        return dist

    def fill_data(self):
        self.name = '%s' % (self.service,)
        self.service_type = SERVICE_CATEGORY_ALLOTMENT
        self.description = self.build_description()
        self.service_location = self.service.location.name


class BookingTransfer(BookingService, BaseTransfer):
    """
    Booking Service Transfer
    """
    class Meta:
        verbose_name = 'Booking Transfer'
        verbose_name_plural = 'Booking Transfers'
        default_permissions = ('add', 'change',)
    location_from = models.ForeignKey(
        Location, related_name='location_from', verbose_name='Location from')
    place_from = models.ForeignKey(
        Place, related_name='place_from', blank=True, null=True)
    schedule_from = models.ForeignKey(
        Schedule, related_name='schedule_from', blank=True, null=True)
    pickup = models.ForeignKey(
        Allotment, related_name='transfer_pickup', null=True, blank=True)
    location_to = models.ForeignKey(
        Location, related_name='location_to', verbose_name='Location to')
    place_to = models.ForeignKey(
        Place, related_name='place_to', blank=True, null=True)
    schedule_to = models.ForeignKey(
        Schedule, related_name='schedule_to', blank=True, null=True)
    dropoff = models.ForeignKey(
        Allotment, related_name='transfer_dropoff', null=True, blank=True)

    def build_description(self):
        return '%s pax' % self.rooming_list.count()

    def fill_data(self):
        # setting name for this booking_service
        self.name = '%s (%s -> %s)' % (
            self.service,
            self.location_from.short_name or self.location_from,
            self.location_to.short_name or self.location_to)
        self.service_type = SERVICE_CATEGORY_TRANSFER
        self.description = self.build_description()
        self.service_location = self.location_from.name


class BookingTransferSupplement(BookingServiceSupplement):
    """
    Transfer Supplement
    """
    class Meta:
        verbose_name = 'Booking Transfer Line Supplement'
        verbose_name_plural = 'Booking Transfer Line Supplements'
    quantity = models.SmallIntegerField(default=1)


class BookingExtra(BookingService, BaseExtra):
    """
    Booking Service Extra
    """
    class Meta:
        verbose_name = 'Booking Extra'
        verbose_name_plural = 'Booking Extras'
        default_permissions = ('add', 'change',)

    def build_description(self):
        return '%s pax' % self.rooming_list.count()

    def fill_data(self):
        # setting name for this booking_service
        self.name = self.service.name
        self.service_type = SERVICE_CATEGORY_EXTRA
        self.description = self.build_description()
        self.service_location = self.service.location.name


class BookingPackage(BookingService):
    """
    Booking Service Package
    """
    class Meta:
        verbose_name = 'Booking Package'
        verbose_name_plural = 'Bookings Packages'
        default_permissions = ('add', 'change',)
    service = models.ForeignKey(Package)
    price_by_package_catalogue = models.BooleanField(
        default=True, verbose_name='Use Catalogue Price')

    def build_description(self):
        return '%s pax' % self.rooming_list.count()

    def fill_data(self):
        # setting name for this booking_service
        self.name = self.service.name
        self.service_type = SERVICE_CATEGORY_PACKAGE
        self.description = self.build_description()
        # TODO define a location for packages to show
        # maybe first packageservice location
        self.service_location = ''

    def save(self, *args, **kwargs):
        with transaction.atomic(savepoint=False):
            super(BookingPackage, self).save(*args, **kwargs)

    def __str__(self):
        return self.__unicode__()

    def __unicode__(self):
        return '%s : %s' % (self.name, self.booking)


class BookingPackageService(BaseService, BookService, DateInterval):
    """
    Booking Package Service
    """
    class Meta:
        verbose_name = 'Booking Package Service'
        verbose_name_plural = 'Bookingss Packages Services'
        default_permissions = ('add', 'change',)
    booking_package = models.ForeignKey(BookingPackage, related_name='booking_package_services')

    def fill_data(self):
        pass

    def save(self, *args, **kwargs):
        self.fill_data()
        # Call the "real" save() method.
        super(BookingPackageService, self).save(*args, **kwargs)


class BookingPackageAllotment(BookingPackageService, BaseAllotment):
    """
    Booking Package Service Allotment
    """
    class Meta:
        verbose_name = 'Booking Package Accomodation'
        verbose_name_plural = 'Bookings Packages Accomodations'
        default_permissions = ('add', 'change',)

    def fill_data(self):
        self.name = '%s' % (self.service,)
        self.service_type = SERVICE_CATEGORY_ALLOTMENT


class BookingPackageTransfer(BookingPackageService, BaseTransfer):
    """
    Booking Package Service Transfer
    """
    class Meta:
        verbose_name = 'Booking Package Transfer'
        verbose_name_plural = 'Bookingss Packages Transfers'
        default_permissions = ('add', 'change',)
    location_from = models.ForeignKey(
        Location, related_name='booking_package_location_from', verbose_name='Location from')
    place_from = models.ForeignKey(
        Place, related_name='booking_package_place_from', blank=True, null=True)
    schedule_from = models.ForeignKey(
        Schedule, related_name='booking_package_schedule_from', blank=True, null=True)
    pickup = models.ForeignKey(
        Allotment, related_name='booking_package_transfer_pickup', null=True, blank=True)
    location_to = models.ForeignKey(
        Location, related_name='booking_package_location_to', verbose_name='Location to')
    place_to = models.ForeignKey(
        Place, related_name='booking_package_place_to', blank=True, null=True)
    schedule_to = models.ForeignKey(
        Schedule, related_name='booking_package_schedule_to', blank=True, null=True)
    dropoff = models.ForeignKey(
        Allotment, related_name='booking_package_transfer_dropoff', null=True, blank=True)

    def fill_data(self):
        # setting name for this quote_service
        self.name = '%s (%s -> %s)' % (
            self.service,
            self.location_from.short_name or self.location_from,
            self.location_to.short_name or self.location_to)
        self.service_type = SERVICE_CATEGORY_TRANSFER


class BookingPackageExtra(BookingPackageService, BaseExtra):
    """
    Booking Service Extra
    """
    class Meta:
        verbose_name = 'Booking Package Extra'
        verbose_name_plural = 'Bookings Packages Extras'
        default_permissions = ('add', 'change',)

    def fill_data(self):
        # setting name for this quote_service
        self.name = self.service.name
        self.service_type = SERVICE_CATEGORY_EXTRA


class ProviderPackageService(ProviderCatalogue):
    """
    ProviderPackageService
    """
    class Meta:
        verbose_name = 'Provider Package Service'
        verbose_name_plural = 'Providers Packages Services'
        unique_together = (('provider', 'service', 'date_from', 'date_to'),)
    service = models.ForeignKey(Package)

    def __str__(self):
        return 'Pvdr.Package - %s : %s' % (self.provider, self.service)


class AgencyPackageService(AgencyCatalogue):
    """
    AgencyPackageService
    """
    class Meta:
        verbose_name = 'Agency Package Service'
        verbose_name_plural = 'Agency Packages Services'
        unique_together = (('agency', 'service', 'date_from', 'date_to'),)
    service = models.ForeignKey(Package)

    def __str__(self):
        return 'Ag.Package - %s : %s' % (self.agency, self.service)


class AgencyPackageDetail(AmountDetail):
    """
    AgencyPackageDetail
    """
    class Meta:
        verbose_name = 'Agency Package Detail'
        verbose_name_plural = 'Agencies Package Details'
        unique_together = ('agency_service','pax_range_min', 'pax_range_max')
    agency_service = models.ForeignKey(AgencyPackageService)
    pax_range_min = models.SmallIntegerField(blank=True, null=True)
    pax_range_max = models.SmallIntegerField(blank=True, null=True)
