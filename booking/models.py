# -*- coding: utf-8 -*-
from __future__ import unicode_literals
"""
Booking models
"""
from concurrency.fields import AutoIncVersionField

from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.db.models.query_utils import Q
from django.contrib.auth.models import User

from accounting.constants import CURRENCIES, CURRENCY_CUC
from accounting.models import Account

from booking.constants import (
    SERVICE_CATEGORY_PACKAGE, SERVICE_CATEGORIES,
    BASE_BOOKING_SERVICE_CATEGORIES,
    BASE_BOOKING_SERVICE_CATEGORY_BOOKING_ALLOTMENT,
    BASE_BOOKING_SERVICE_CATEGORY_BOOKING_TRANSFER,
    BASE_BOOKING_SERVICE_CATEGORY_BOOKING_EXTRA,
    BASE_BOOKING_SERVICE_CATEGORY_BOOKING_PACKAGE,
    BASE_BOOKING_SERVICE_CATEGORY_PACKAGE_ALLOTMENT,
    BASE_BOOKING_SERVICE_CATEGORY_PACKAGE_TRANSFER,
    BASE_BOOKING_SERVICE_CATEGORY_PACKAGE_EXTRA,
    QUOTE_STATUS_LIST, QUOTE_STATUS_DRAFT,
    BOOKING_STATUS_LIST, BOOKING_STATUS_PENDING,
    SERVICE_STATUS_LIST, SERVICE_STATUS_PENDING, SERVICE_STATUS_REQUEST, SERVICE_STATUS_CANCELLED,
    PACKAGE_AMOUNTS_TYPES,
    INVOICE_FORMATS, INVOICE_FORMAT_COMPACT)

from config.constants import (
    BOARD_TYPES, AMOUNTS_BY_PAX, 
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

from finance.constants import DOC_TYPE_PROVIDER_PAYMENT_WITHDRAW, STATUS_DRAFT
from finance.models import (
    Office, Agency, AgencyInvoice, AgencyContact,
    Provider, ProviderInvoice, Withdraw)


# Utility method to get a list of
# BookingService child objects from a BookingService list
def _get_child_objects(services):
    TYPE_MODELS = {
        'T': BookingTransfer,
        'E': BookingExtra,
        'A': BookingAllotment,
        'P': BookingPackage,
    }
    objs = []
    for service in services:
        obj = TYPE_MODELS[service.service_type].objects.get(id=service.id)
        objs.append(obj)
    return objs


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

    def validate_date_interval(self):
        if self.datetime_from and self.datetime_to and self.datetime_from > self.datetime_to:
            raise ValidationError('Date From can not be after Date To')


def utility(cost, price):
    if not price is None and not cost is None:
        return price - cost
    return '-'


def utility_percent(cost, price):
    if not price is None and cost:
        return round(100 * (price / cost - 1), 1).__str__() + '%'
    return '-'


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

    @property
    def utility_single(self):
        return utility(self.cost_single_amount, self.price_single_amount)
    utility_single.fget.short_description = 'Util.SGL'

    @property
    def utility_double(self):
        return utility(self.cost_double_amount, self.price_double_amount)
    utility_double.fget.short_description = 'Util.DBL'

    @property
    def utility_triple(self):
        return utility(self.cost_triple_amount, self.price_triple_amount)
    utility_triple.fget.short_description = 'Util.TPL'

    @property
    def utility_percent_single(self):
        return utility_percent(self.cost_single_amount, self.price_single_amount)
    utility_percent_single.fget.short_description = 'Util.SGL %'

    @property
    def utility_percent_double(self):
        return utility_percent(self.cost_double_amount, self.price_double_amount)
    utility_percent_double.fget.short_description = 'Util.DBL %'

    @property
    def utility_percent_triple(self):
        return utility_percent(self.cost_triple_amount, self.price_triple_amount)
    utility_percent_triple.fget.short_description = 'Util.TPL %'


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
    service_addon = models.ForeignKey(Addon, blank=True, null=True)
    status = models.CharField(
        max_length=5, choices=SERVICE_STATUS_LIST,
        default=SERVICE_STATUS_PENDING)
    provider = models.ForeignKey(Provider, blank=True, null=True)


class BaseAllotment(models.Model):
    """
    Base Service Allotment
    """
    class Meta:
        abstract = True
    service = models.ForeignKey(Allotment)
    room_type = models.ForeignKey(RoomType)
    board_type = models.CharField(max_length=5, choices=BOARD_TYPES)


class BaseTransfer(models.Model):
    """
    Base Service Transfer
    """
    class Meta:
        abstract = True
    service = models.ForeignKey(Transfer)
    time = models.TimeField(blank=True, null=True)
    quantity = models.SmallIntegerField(default=1)


class BaseExtra(models.Model):
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
        ordering = ['name']
    amounts_type = models.CharField(
        default=AMOUNTS_BY_PAX, max_length=5, choices=PACKAGE_AMOUNTS_TYPES)
    has_pax_range = models.BooleanField(default=False)
    time = models.TimeField(blank=True, null=True)

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
    schedule_time_from = models.TimeField(blank=True, null=True)
    schedule_time_to = models.TimeField(blank=True, null=True)

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
    seller = models.ForeignKey(User, blank=True, null=True)

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
    extra_single_amount = models.DecimalField(
        max_digits=5, decimal_places=2, default=0.0, verbose_name='Extra SGL')
    extra_double_amount = models.DecimalField(
        max_digits=5, decimal_places=2, default=0.0, verbose_name='Extra DBL')
    extra_triple_amount = models.DecimalField(
        max_digits=5, decimal_places=2, default=0.0, verbose_name='Extra TPL')

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
        self.validate_date_interval()
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
    time = models.TimeField(blank=True, null=True)

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
        self.validate_date_interval()
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
    invoice_booking = models.ForeignKey('Booking')
    booking_name = models.CharField(max_length=100, blank=True, null=True)
    reference = models.CharField(max_length=25, blank=True, null=True)
    date_from = models.DateField(blank=True, null=True)
    date_to = models.DateField(blank=True, null=True)
    cash_amount = models.DecimalField(decimal_places=2, max_digits=9, default=0.0)
    office = models.ForeignKey(Office, blank=True, null=True)
    issued_name = models.CharField(max_length=60, blank=True, null=True)
    date_issued = models.DateField(blank=True, null=True)
    office = models.ForeignKey(Office, blank=True, null=True)
    content_format = models.CharField(
        max_length=1, choices=INVOICE_FORMATS, default=INVOICE_FORMAT_COMPACT)

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


class BookingInvoiceDetail(models.Model):
    class Meta:
        verbose_name = 'Booking Invoice Detail'
        verbose_name_plural = 'Bookings Invoices Details'
    invoice = models.ForeignKey(BookingInvoice)
    description = models.CharField(max_length=100, blank=True, null=True)
    detail = models.CharField(max_length=100, blank=True, null=True)
    date_from = models.DateField(blank=True, null=True)
    date_to = models.DateField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)


class BookingInvoicePartial(models.Model):
    class Meta:
        verbose_name = 'Booking Invoice Partial'
        verbose_name_plural = 'Bookings Invoices Partials'
    invoice = models.ForeignKey(BookingInvoice)
    pax_name = models.CharField(max_length=100, blank=True, null=True)
    is_free = models.BooleanField(default=False)
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
        unique_together = (('invoice',),)

    version = AutoIncVersionField( )
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
    seller = models.ForeignKey(User)
    agency_contact = models.ForeignKey(AgencyContact, blank=True, null=True, verbose_name='Contact')

    @property
    def utility(self):
        return utility(self.cost_amount, self.price_amount)
    utility.fget.short_description = 'Util.'

    @property
    def utility_percent(self):
        return utility_percent(self.cost_amount, self.price_amount)
    utility_percent.fget.short_description = 'Util.%'

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

    def has_notes(self):
        # this shows a waring sign with mouse-over message
        # for bookings with private notes
        if self.p_notes:
            return '<a href="#" data-toggle="tooltip" title="%s"><span class="glyphicon glyphicon-exclamation-sign" aria-hidden="true"></span></a>' % self.p_notes
        return
    has_notes.allow_tags = True
    has_notes.short_description = 'Notes'


class BookingPax(models.Model):
    """
    Booking Pax
    """
    class Meta:
        verbose_name = 'Booking Pax'
        verbose_name_plural = 'Booking Rooming List'
        unique_together = (('booking', 'pax_name'),)
    version = AutoIncVersionField( )
    booking = models.ForeignKey(Booking, related_name='rooming_list')
    pax_name = models.CharField(max_length=50)
    pax_age = models.SmallIntegerField(blank=True, null=True, verbose_name='Age')
    pax_group = models.SmallIntegerField(verbose_name='Room')
    is_price_free = models.BooleanField(default=False)
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


class BaseBookingService(BaseService, DateInterval):
    """
    Base Booking Service
    """
    class Meta:
        # abstract = True
        verbose_name = 'Base Booking Service'
        verbose_name_plural = 'Base Bookings Services'
        ordering = ['provider', 'service_type']
    # This holds the confirmation number when it exists

    conf_number = models.CharField(max_length=20, blank=True, null=True)
    cost_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    cost_comments = models.CharField(max_length=1000, blank=True, null=True)
    price_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    price_comments = models.CharField(max_length=1000, blank=True, null=True)
    p_notes = models.CharField(
        max_length=1000, blank=True, null=True, verbose_name='Private Notes')
    provider_notes = models.CharField(
        max_length=1000, blank=True, null=True, verbose_name='Provider Notes')
    manual_cost = models.BooleanField(default=False)
    manual_price = models.BooleanField(default=False)
    base_category = models.CharField(max_length=5, choices=BASE_BOOKING_SERVICE_CATEGORIES, blank=True, null=True)

    cost_amount_to_pay = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    cost_amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    has_payment = models.BooleanField(default=False)
    booking_temp = models.IntegerField(blank=True, null=True)

    @property
    def utility(self):
        return utility(self.cost_amount, self.price_amount)
    utility.fget.short_description = 'Util.'

    @property
    def utility_percent(self):
        return utility_percent(self.cost_amount, self.price_amount)
    utility_percent.fget.short_description = 'Util.%'

    def save(self, *args, **kwargs):
        self.validate_date_interval()
        # Call the "real" save() method.
        super(BaseBookingService, self).save(*args, **kwargs)

    def booking_name(self):
        # gets booking.name for this bookingservice
        child_service = _get_child_objects([self])[0]
        if child_service.base_category in ['PA', 'PE', 'PT']:
            return child_service.booking_package.booking.name
        return child_service.booking.name

    def service_provider(self):
        provider = ''
        if self.provider:
            provider = self.provider.name
            if self.provider.phone:
                provider += ' %s' % self.provider.phone
        return provider


class BookingService(BaseBookingService):
    """
    Booking Service
    """
    class Meta:
        verbose_name = 'Booking Service'
        verbose_name_plural = 'Booking Services'
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

    def pax_quantity(self):
        return self.rooming_list.count()


class BookingServicePax(models.Model):
    """
    Booking Service Pax
    """
    class Meta:
        verbose_name = 'Booking Service Pax'
        verbose_name_plural = 'Booking Service Rooming'
    version = AutoIncVersionField( )
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
    version = AutoIncVersionField( )

    def __unicode__(self):
        return '%s (%s - %s)' % (self.name,
                                 self.datetime_from, self.datetime_to)

    def __str__(self):
        return self.__unicode__()

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
            '40': 0,  # Quad counter
            'und': 0,  # Undefined room counter
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
            '40': 'QUAD',
            'und': 'UNALLOCATED'
        }
        for room in rooms:
            if '%d%d' % (room[0], room[1]) in room_count:
                room_count['%d%d' % (room[0], room[1])] += 1
            else:
                room_count['und'] += 1
        for k in room_count.keys():
            if room_count[k]:
                if dist:
                    dist += ' + '
                dist += '%d %s' % (room_count[k],
                                   room_types[k])
        dist += ' (%s)' % self.board_type
        return dist

    def fill_data(self):
        super(BookingAllotment, self).fill_data()
        self.name = '%s' % (self.service,)
        self.base_category = BASE_BOOKING_SERVICE_CATEGORY_BOOKING_ALLOTMENT
        self.service_type = SERVICE_CATEGORY_ALLOTMENT
        self.description = self.build_description()
        if self.service.location:
            self.service_location = self.service.location.name

    def adult_quantity(self):
        if self.service.child_age:
            return self.rooming_list.filter(
                Q(booking_pax__pax_age__isnull=True) |
                Q(booking_pax__pax_age__gte=self.service.child_age)).count()
        else:
            return self.rooming_list.count()

    def child_quantity(self):
        if self.service.child_age:
            return self.rooming_list.filter(
                booking_pax__pax_age__lt=self.service.child_age).count()
        return 0


class BookingTransfer(BookingService, BaseTransfer):
    """
    Booking Service Transfer
    """
    class Meta:
        verbose_name = 'Booking Transfer'
        verbose_name_plural = 'Booking Transfers'
    version = AutoIncVersionField( )
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
    schedule_time_from = models.TimeField(blank=True, null=True)
    schedule_time_to = models.TimeField(blank=True, null=True)

    def build_description(self):
        return '%s pax' % self.rooming_list.count()

    def fill_data(self):
        super(BookingTransfer, self).fill_data()
        # setting name for this booking_service
        self.name = '%s (%s -> %s)' % (
            self.service,
            self.location_from.short_name or self.location_from,
            self.location_to.short_name or self.location_to)
        self.base_category = BASE_BOOKING_SERVICE_CATEGORY_BOOKING_TRANSFER
        self.service_type = SERVICE_CATEGORY_TRANSFER
        self.description = self.build_description()
        self.service_location = self.location_from.name

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.__unicode__()


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
    version = AutoIncVersionField( )

    def build_description(self):
        return '%s pax' % self.rooming_list.count()

    def fill_data(self):
        super(BookingExtra, self).fill_data()
        # setting name for this booking_service
        self.name = self.service.name
        self.base_category = BASE_BOOKING_SERVICE_CATEGORY_BOOKING_EXTRA
        self.service_type = SERVICE_CATEGORY_EXTRA
        self.description = self.build_description()
        if self.service.location:
            self.service_location = self.service.location.name

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.__unicode__()


class BookingPackage(BookingService):
    """
    Booking Service Package
    """
    class Meta:
        verbose_name = 'Booking Package'
        verbose_name_plural = 'Bookings Packages'
    version = AutoIncVersionField()
    service = models.ForeignKey(Package)
    price_by_package_catalogue = models.BooleanField(
        default=True, verbose_name='Use Catalogue Price')
    time = models.TimeField(blank=True, null=True)
    voucher_detail = models.BooleanField(default=False)

    def build_description(self):
        return '%s pax' % self.rooming_list.count()

    def fill_data(self):
        super(BookingPackage, self).fill_data()
        # setting name for this booking_service
        self.name = self.service.name
        self.base_category = BASE_BOOKING_SERVICE_CATEGORY_BOOKING_PACKAGE
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


class BookingPackageService(BaseBookingService):
    """
    Booking Package Service
    """
    class Meta:
        verbose_name = 'Booking Package Service'
        verbose_name_plural = 'Bookings Packages Services'
        ordering = ['datetime_from']
    booking_package = models.ForeignKey(BookingPackage, related_name='booking_package_services')

    def fill_data(self):
        pass

    def save(self, *args, **kwargs):
        self.fill_data()
        # Call the "real" save() method.
        super(BookingPackageService, self).save(*args, **kwargs)

    def booking(self):
        return self.booking_package.booking

    def rooming_list(self):
        return self.booking_package.rooming_list

    def pax_quantity(self):
        return self.booking_package.rooming_list.count()


class BookingPackageAllotment(BookingPackageService, BaseAllotment):
    """
    Booking Package Service Allotment
    """
    class Meta:
        verbose_name = 'Booking Package Accomodation'
        verbose_name_plural = 'Bookings Packages Accomodations'
    version = AutoIncVersionField( )

    def build_description(self):
        """ makes a string detailing room quantity and types"""
        from booking.services import BookingServices
        rooms = BookingServices.find_groups(
            booking_service=self.booking_package, service=self.service, for_cost=True)
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
                dist += '%d %s' % (room_count[k],
                                   room_types[k])
        dist += ' (%s)' % self.board_type
        return dist

    def fill_data(self):
        super(BookingPackageAllotment, self).fill_data()
        self.name = '%s' % (self.service,)
        self.base_category = BASE_BOOKING_SERVICE_CATEGORY_PACKAGE_ALLOTMENT
        self.service_type = SERVICE_CATEGORY_ALLOTMENT
        self.description = self.build_description()

    def adult_quantity(self):
        if self.service.child_age:
            return self.booking_package.rooming_list.filter(
                Q(booking_pax__pax_age__isnull=True) |
                Q(booking_pax__pax_age__gte=self.service.child_age)).count()
        else:
            return self.booking_package.rooming_list.count()

    def child_quantity(self):
        if self.service.child_age:
            return self.booking_package.rooming_list.filter(
                booking_pax__pax_age__lt=self.service.child_age).count()
        return 0


class BookingPackageTransfer(BookingPackageService, BaseTransfer):
    """
    Booking Package Service Transfer
    """
    class Meta:
        verbose_name = 'Booking Package Transfer'
        verbose_name_plural = 'Bookingss Packages Transfers'
    version = AutoIncVersionField( )
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
    schedule_time_from = models.TimeField(blank=True, null=True)
    schedule_time_to = models.TimeField(blank=True, null=True)

    def build_description(self):
        return '%s pax' % self.booking_package.rooming_list.count()

    def fill_data(self):
        super(BookingPackageTransfer, self).fill_data()
        # setting name for this booking_service
        self.name = '%s (%s -> %s)' % (
            self.service,
            self.location_from.short_name or self.location_from,
            self.location_to.short_name or self.location_to)
        self.base_category = BASE_BOOKING_SERVICE_CATEGORY_PACKAGE_TRANSFER
        self.service_type = SERVICE_CATEGORY_TRANSFER
        self.description = self.build_description()


class BookingPackageExtra(BookingPackageService, BaseExtra):
    """
    Booking Service Extra
    """
    class Meta:
        verbose_name = 'Booking Package Extra'
        verbose_name_plural = 'Bookings Packages Extras'
    version = AutoIncVersionField( )

    def build_description(self):
        return '%s pax' % self.booking_package.rooming_list.count()

    def fill_data(self):
        super(BookingPackageExtra, self).fill_data()
        # setting name for this booking_service
        self.name = self.service.name
        self.base_category = BASE_BOOKING_SERVICE_CATEGORY_PACKAGE_EXTRA
        self.service_type = SERVICE_CATEGORY_EXTRA
        self.description = self.build_description()


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


class PackageProvider(models.Model):
    """
    PackageProvider
    """
    class Meta:
        verbose_name = 'Package Provider'
        verbose_name_plural = 'Packages Providers'
        unique_together = (('service', 'provider'),)
    service = models.ForeignKey(Package)
    provider = models.ForeignKey(Provider)

    def __str__(self):
        return 'Package Prov. - %s : %s' % (self.service, self.provider)

class ProviderBookingPayment(Withdraw):
    """
    ProviderBookingPayment
    """
    class Meta:
        verbose_name = 'Provider Booking Payment'
        verbose_name_plural = 'Providers Bookings Payments'
    provider = models.ForeignKey(Provider)

    def fill_data(self):
        self.document_type = DOC_TYPE_PROVIDER_PAYMENT_WITHDRAW
        account = Account.objects.get(pk=self.account_id)
        self.name = '%s - Prov. (%s) Payment Withdraw from %s of %s %s ' % (
            self.date, self.provider, account, self.amount, account.get_currency_display())
        return self.name

    def delete(self, using=None, keep_parents=False):
        if self.status != STATUS_DRAFT:
            raise ValidationError('Can not delete Payments')

    def __str__(self):
        return 'Prov. - %s : %s' % (self.provider, self.amount)


class ProviderBookingPaymentService(models.Model):
    """
    ProviderBookingPaymentService
    """
    class Meta:
        verbose_name = 'Provider Booking Payment'
        verbose_name_plural = 'Providers Bookings Payments'
        unique_together = (('provider_payment', 'provider_service'),)
    provider_payment = models.ForeignKey(ProviderBookingPayment)
    provider_service = models.ForeignKey(BaseBookingService)
    service_cost_amount_to_pay = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    service_cost_amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return '%s : %s (%s)' % (
            self.provider_payment, self.provider_service, self.amount_paid)
