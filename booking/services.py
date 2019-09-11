# -*- coding: utf-8 -*-
from __future__ import unicode_literals

"""
Booking Service
"""
from datetime import date, datetime, timedelta

from django.contrib.admin.models import LogEntry, ADDITION, CHANGE
from django.contrib.admin.options import get_content_type_for_model
from django.db import transaction
from django.db.models import Q
from django.utils.encoding import force_text

from booking import constants
from booking.models import (
    Quote, QuoteService, QuotePaxVariant, QuoteServicePaxVariant, QuotePackageServicePaxVariant,
    QuoteAllotment, QuoteTransfer, QuoteExtra, QuotePackage,
    QuotePackageService, QuotePackageAllotment, QuotePackageTransfer, QuotePackageExtra,
    Package, PackageAllotment, PackageTransfer, PackageExtra,
    AgencyPackageService, AgencyPackageDetail,
    Booking, BookingService, BookingPax, BookingServicePax,
    BookingAllotment, BookingTransfer, BookingExtra, BookingPackage,
    BookingPackageService, BookingPackageAllotment, BookingPackageTransfer, BookingPackageExtra,
    BookingInvoice, BookingInvoiceDetail, BookingInvoiceLine, BookingInvoicePartial)

from config.models import ProviderAllotmentDetail, ProviderTransferDetail, ProviderExtraDetail
from config.services import ConfigServices
from config.views import (
    provider_allotment_queryset, provider_transfer_queryset, provider_extra_queryset)

from finance.constants import STATUS_CANCELLED, STATUS_READY
from finance.services import FinanceService
from finance.models import Agency

from reservas.custom_settings import ADDON_FOR_NO_ADDON


class BookingServices(object):
    """
    Booking Services
    """

    @classmethod
    def cancel_bookinginvoice(cls, user, booking):
        # cancel non cancelled invoices associated to booking
        invoices = list(
            BookingInvoice.objects.all().filter(invoice_booking=booking).exclude(status=STATUS_CANCELLED))
        if invoices:
            for invoice in invoices:
                invoice.status = STATUS_CANCELLED
                FinanceService.save_agency_invoice(user, invoice, BookingInvoice)
                LogEntry.objects.log_action(
                    user_id=user.pk,
                    content_type_id=get_content_type_for_model(invoice).pk,
                    object_id=invoice.pk,
                    object_repr=force_text(invoice),
                    action_flag=CHANGE,
                    change_message="Booking Invoice Cancelled",
                )
            if booking.invoice:
                booking.invoice = None
                booking.save(update_fields=['invoice'])
                LogEntry.objects.log_action(
                    user_id=user.pk,
                    content_type_id=get_content_type_for_model(booking).pk,
                    object_id=booking.pk,
                    object_repr=force_text(booking),
                    action_flag=CHANGE,
                    change_message="Booking Invoice Cancelled",
                )


    @classmethod
    def _find_booking_package_paxes(cls, booking):
        pax_list = list(BookingPax.objects.filter(booking=booking.id))
        groups = dict()
        for pax in pax_list:
            if pax.pax_group is None:
                continue
            if not groups.__contains__(pax.pax_group):
                groups[pax.pax_group] = dict()
                groups[pax.pax_group]['qtty'] = 0
                groups[pax.pax_group]['free'] = 0
            groups[pax.pax_group]['qtty'] += 1
            if pax.is_price_free:
                groups[pax.pax_group]['free'] += 1
        result = dict()
        result['1'] = dict()
        result['1']['qtty'] = 0
        result['1']['free'] = 0
        result['2'] = dict()
        result['2']['qtty'] = 0
        result['2']['free'] = 0
        result['3'] = dict()
        result['3']['qtty'] = 0
        result['3']['free'] = 0
        for group in groups.values():
            if group['qtty'] == 1:
                result['1']['qtty'] += group['qtty']
                if group['free'] > 0:
                    result['1']['free'] += group['free']
            elif group['qtty'] == 2:
                result['2']['qtty'] += group['qtty']
                if group['free'] > 0:
                    result['2']['free'] += group['free']
            elif group['qtty'] == 3:
                result['3']['qtty'] += group['qtty']
                if group['free'] > 0:
                    result['3']['free'] += group['free']
        return result


    @classmethod
    def create_bookinginvoice(cls, user, booking):
        with transaction.atomic(savepoint=False):
            if booking.invoice:
                return False

            invoice = BookingInvoice()
            invoice.invoice_booking = booking

            invoice.agency = booking.agency
            invoice.currency = booking.currency
            invoice.amount = booking.price_amount
            invoice.status = STATUS_READY

            invoice.booking_name = booking.name
            invoice.reference = booking.reference
            invoice.date_from = booking.date_from
            invoice.date_to = booking.date_to

            invoice.date_issued = date.today()
            invoice.issued_name = booking.seller.get_full_name()

            FinanceService.save_agency_invoice(user, invoice, BookingInvoice)
            LogEntry.objects.log_action(
                user_id=user.pk,
                content_type_id=get_content_type_for_model(invoice).pk,
                object_id=invoice.pk,
                object_repr=force_text(invoice),
                action_flag=ADDITION,
                change_message="Booking Invoice Created",
            )

            if booking.is_package_price:
                # obtain detail
                paxes = cls._find_booking_package_paxes(booking)
                if paxes['1']['qtty'] > 0:
                    invoice_detail = BookingInvoiceDetail()
                    invoice_detail.invoice = invoice
                    invoice_detail.description = "PACKAGE PRICE IN SINGLE %s x Pax" % booking.package_sgl_price_amount
                    invoice_detail.detail = "%s Pax" % (paxes['1']['qtty'] - paxes['1']['free'])
                    invoice_detail.date_from = booking.date_from
                    invoice_detail.date_to = booking.date_to
                    invoice_detail.price = (paxes['1']['qtty'] - paxes['1']['free']) * booking.package_sgl_price_amount
                    invoice_detail.save()
                if paxes['2']['qtty'] > 0:
                    invoice_detail = BookingInvoiceDetail()
                    invoice_detail.invoice = invoice
                    invoice_detail.description = "PACKAGE PRICE IN DOUBLE %s x Pax" % booking.package_dbl_price_amount
                    invoice_detail.detail = "%s Pax" % (paxes['2']['qtty'] - paxes['2']['free'])
                    invoice_detail.date_from = booking.date_from
                    invoice_detail.date_to = booking.date_to
                    invoice_detail.price = (paxes['2']['qtty'] - paxes['2']['free']) * booking.package_dbl_price_amount
                    invoice_detail.save()
                if paxes['3']['qtty'] > 0:
                    invoice_detail = BookingInvoiceDetail()
                    invoice_detail.invoice = invoice
                    invoice_detail.description = "PACKAGE PRICE IN TRIPLE %s x Pax" % booking.package_tpl_price_amount
                    invoice_detail.detail = "%s Pax" % (paxes['3']['qtty'] - paxes['3']['free'])
                    invoice_detail.date_from = booking.date_from
                    invoice_detail.date_to = booking.date_to
                    invoice_detail.price = (paxes['3']['qtty'] - paxes['3']['free']) * booking.package_tpl_price_amount
                    invoice_detail.save()

            # obtain lines
            booking_service_list = BookingService.objects.filter(
                booking=booking.id).all()
            for booking_service in booking_service_list:
                invoice_line = BookingInvoiceLine()
                invoice_line.invoice = invoice
                invoice_line.date_from = booking_service.datetime_from
                invoice_line.date_to = booking_service.datetime_to
                invoice_line.bookingservice_name = booking_service.name
                invoice_line.price = booking_service.price_amount

                invoice_line.save()

            # obtain partials
            booking_pax_list = BookingPax.objects.filter(booking=booking.id).all()
            for booking_pax in booking_pax_list:
                invoice_partial = BookingInvoicePartial()
                invoice_partial.invoice = invoice
                invoice_partial.pax_name = booking_pax.pax_name
                invoice_partial.is_free = booking_pax.is_price_free
                invoice_partial.save()

            booking.invoice = invoice
            booking.save()
            LogEntry.objects.log_action(
                user_id=user.pk,
                content_type_id=get_content_type_for_model(booking).pk,
                object_id=booking.pk,
                object_repr=force_text(booking),
                action_flag=CHANGE,
                change_message="Booking Invoice Created",
            )
            return True


    @classmethod
    def build_bookingservice_paxes(cls, bookingservice, pax_list, user=None):
        for service_pax in pax_list:
            bookingservice_pax = BookingServicePax()
            bookingservice_pax.booking_service = bookingservice
            bookingservice_pax.booking_pax = service_pax.booking_pax
            bookingservice_pax.group = service_pax.group

            bookingservice_pax.avoid_bookingservice_update = True
            bookingservice_pax.avoid_booking_update = True
            bookingservice_pax.save()

    @classmethod
    def build_booking_from_quote(cls, quote_id, rooming, user=None):
        try:
            quote = Quote.objects.get(pk=quote_id)
        except Quote.DoesNotExist:
            return None, 'Quote with id %s Not Found' % quote_id
        try:
            with transaction.atomic(savepoint=False):
                # create booking
                booking = Booking()
                booking.name = quote.reference
                booking.agency = quote.agency
                booking.reference = '< reference> '
                booking.seller = quote.seller or user
                # date_from auto
                # date_to auto
                # status auto
                booking.currency = quote.currency
                booking.currency_factor = quote.currency_factor
                # cost_amount auto
                # cost_comments auto
                # price_amount auto
                # cost_comments auto
                # invoice empty
                booking.is_package_price = True
                pax_variant = cls._find_quote_paxvariant_for_booking_rooming(quote, rooming)
                booking.package_sgl_price_amount = pax_variant.price_single_amount
                booking.package_dbl_price_amount = pax_variant.price_double_amount
                booking.package_tpl_price_amount = pax_variant.price_triple_amount
                if booking.package_sgl_price_amount is None:
                    booking.package_sgl_price_amount = 0
                if booking.package_dbl_price_amount is None:
                    booking.package_dbl_price_amount = 0
                if booking.package_tpl_price_amount is None:
                    booking.package_tpl_price_amount = 0

                booking.avoid_bookingservices_update = True
                booking.save()

                # create pax list
                pax_list = list()
                for pax in rooming:
                    if pax['pax_name'] and pax['pax_group']:
                        booking_pax = BookingPax()
                        booking_pax.booking = booking
                        booking_pax.pax_name = pax['pax_name']
                        booking_pax.pax_age = pax['pax_age']
                        booking_pax.pax_group = pax['pax_group']
                        booking_pax.is_price_free = pax['is_price_free']
                        booking_pax.avoid_booking_update = True
                        booking_pax.save()

                        service_pax = BookingServicePax()
                        service_pax.booking_pax = booking_pax
                        service_pax.group = booking_pax.pax_group
                        pax_list.append(service_pax)

                # create bookingallotment list
                for quote_allotment in QuoteAllotment.objects.filter(quote_id=quote.id).all():
                    booking_allotment = BookingAllotment()
                    booking_allotment.booking = booking
                    booking_allotment.conf_number = '< confirm number >'
                    booking_allotment.name = quote_allotment.name
                    cls._copy_service_info(
                        dst_service=booking_allotment, src_service=quote_allotment)
                    booking_allotment.room_type = quote_allotment.room_type
                    booking_allotment.board_type = quote_allotment.board_type

                    # find service variant
                    service_pax_variant = cls._find_quoteservice_paxvariant_for_bookingservice(
                        quote_allotment, pax_variant)

                    if service_pax_variant:
                        cls.setup_bookingservice_amounts_from_quote(
                            bookingservice=booking_allotment,
                            service_paxvariant=service_pax_variant,
                            pax_list=pax_list)
                    else:
                        cls.setup_bookingservice_amounts(booking_allotment, pax_list)
                    booking_allotment.avoid_update = True
                    booking_allotment.avoid_booking_update = True
                    booking_allotment.save()

                    # create bookingservicepax list
                    cls.build_bookingservice_paxes(booking_allotment, pax_list, user)

                # create bookingtransfer list
                for quote_transfer in QuoteTransfer.objects.filter(quote_id=quote.id).all():
                    booking_transfer = BookingTransfer()
                    booking_transfer.booking = booking
                    booking_transfer.conf_number = '< confirm number >'
                    booking_transfer.name = quote_transfer.name
                    cls._copy_service_info(
                        dst_service=booking_transfer, src_service=quote_transfer)
                    # time
                    booking_transfer.quantity = ConfigServices.get_service_quantity(
                        booking_transfer.service, len(pax_list))
                    booking_transfer.location_from = quote_transfer.location_from
                    # place_from
                    # schedule_from
                    # pickup
                    booking_transfer.location_to = quote_transfer.location_to
                    # place_to
                    # schedule_to
                    # dropoff

                    # find service variant
                    service_pax_variant = cls._find_quoteservice_paxvariant_for_bookingservice(
                        quote_transfer, pax_variant)

                    if service_pax_variant:
                        cls.setup_bookingservice_amounts_from_quote(
                            bookingservice=booking_transfer,
                            service_paxvariant=service_pax_variant,
                            pax_list=pax_list)
                    else:
                        cls.setup_bookingservice_amounts(booking_transfer, pax_list)
                    booking_transfer.avoid_update = True
                    booking_transfer.avoid_booking_update = True
                    booking_transfer.save()

                    # create bookingservicepax list
                    cls.build_bookingservice_paxes(booking_transfer, pax_list, user)

                # create bookingextra list
                for quote_extra in QuoteExtra.objects.filter(quote_id=quote.id).all():
                    booking_extra = BookingExtra()
                    booking_extra.booking = booking
                    booking_extra.conf_number = '< confirm number >'
                    booking_extra.name = quote_extra.name
                    cls._copy_service_info(
                        dst_service=booking_extra, src_service=quote_extra)
                    booking_extra.addon = quote_extra.addon
                    booking_extra.time = quote_extra.time
                    booking_extra.quantity = quote_extra.quantity
                    booking_extra.parameter = quote_extra.parameter

                    # find service variant
                    service_pax_variant = cls._find_quoteservice_paxvariant_for_bookingservice(
                        quote_extra, pax_variant)

                    if service_pax_variant:
                        cls.setup_bookingservice_amounts_from_quote(
                            bookingservice=booking_extra,
                            service_paxvariant=service_pax_variant,
                            pax_list=pax_list)
                    else:
                        cls.setup_bookingservice_amounts(booking_extra, pax_list)
                    booking_extra.avoid_update = True
                    booking_extra.avoid_booking_update = True
                    booking_extra.save()

                    # create bookingservicepax list
                    cls.build_bookingservice_paxes(booking_extra, pax_list, user)

                # create bookingpackage list
                for quote_package in QuotePackage.objects.filter(quote_id=quote.id).all():
                    booking_package = BookingPackage()
                    booking_package.booking = booking
                    booking_package.conf_number = '< confirm number >'
                    booking_package.name = quote_package.name
                    cls._copy_service_info(
                        dst_service=booking_package, src_service=quote_package)

                    # find service variant
                    service_pax_variant = cls._find_quoteservice_paxvariant_for_bookingservice(
                        quote_package, pax_variant)

                    if service_pax_variant:
                        cls.setup_bookingservice_amounts_from_quote(
                            bookingservice=booking_package,
                            service_paxvariant=service_pax_variant,
                            pax_list=pax_list)
                    else:
                        cls.setup_bookingservice_amounts(booking_package, pax_list)
                    booking_package.avoid_update = True
                    booking_package.avoid_booking_update = True
                    booking_package.avoid_package_services = True
                    booking_package.save()

                    # create bookingservicepax list
                    cls.build_bookingservice_paxes(booking_package, pax_list, user)

                    # create bookingpackageallotment list
                    for quotepackage_allotment in QuotePackageAllotment.objects.filter(
                            quote_package_id=quote_package.id).all():
                        bookingpackage_allotment = BookingPackageAllotment()
                        bookingpackage_allotment.booking_package = booking_package
                        bookingpackage_allotment.conf_number = '< confirm number >'
                        bookingpackage_allotment.name = quotepackage_allotment.name
                        cls._copy_service_info(
                            dst_service=bookingpackage_allotment,
                            src_service=quotepackage_allotment)
                        bookingpackage_allotment.room_type = quotepackage_allotment.room_type
                        bookingpackage_allotment.board_type = quotepackage_allotment.board_type

                        if service_pax_variant:
                            cls.setup_bookingservice_amounts_from_quote(
                                bookingservice=bookingpackage_allotment,
                                service_paxvariant=service_pax_variant,
                                pax_list=pax_list)
                        else:
                            cls.setup_bookingservice_amounts(bookingpackage_allotment, pax_list)
                        bookingpackage_allotment.avoid_bookingpackage_update = True
                        bookingpackage_allotment.avoid_bookingpackageservice_update = True
                        bookingpackage_allotment.save()

                    # create bookingpackagetransfer list
                    for quotepackage_transfer in QuotePackageTransfer.objects.filter(
                            quote_package_id=quote_package.id).all():
                        bookingpackage_transfer = BookingPackageTransfer()
                        bookingpackage_transfer.booking_package = booking_package
                        bookingpackage_transfer.conf_number = '< confirm number >'
                        bookingpackage_transfer.name = quotepackage_transfer.name
                        cls._copy_service_info(
                            dst_service=bookingpackage_transfer, src_service=quotepackage_transfer)
                        # time
                        bookingpackage_transfer.quantity = ConfigServices.get_service_quantity(
                            bookingpackage_transfer.service, len(pax_list))
                        bookingpackage_transfer.location_from = quotepackage_transfer.location_from
                        # place_from
                        # schedule_from
                        # pickup
                        bookingpackage_transfer.location_to = quotepackage_transfer.location_to
                        # place_to
                        # schedule_to
                        # dropoff

                        if service_pax_variant:
                            cls.setup_bookingservice_amounts_from_quote(
                                bookingservice=bookingpackage_transfer,
                                service_paxvariant=service_pax_variant,
                                pax_list=pax_list)
                        else:
                            cls.setup_bookingservice_amounts(bookingpackage_transfer, pax_list)
                        bookingpackage_transfer.avoid_bookingpackage_update = True
                        bookingpackage_transfer.avoid_bookingpackageservice_update = True
                        bookingpackage_transfer.save()

                    # create bookingextra list
                    for quotepackage_extra in QuotePackageExtra.objects.filter(
                            quote_package_id=quote_package.id).all():
                        bookingpackage_extra = BookingPackageExtra()
                        bookingpackage_extra.booking_package = booking_package
                        bookingpackage_extra.conf_number = '< confirm number >'
                        bookingpackage_extra.name = quotepackage_extra.name
                        cls._copy_service_info(
                            dst_service=bookingpackage_extra, src_service=quotepackage_extra)
                        bookingpackage_extra.addon = quotepackage_extra.addon
                        bookingpackage_extra.time = quotepackage_extra.time
                        bookingpackage_extra.quantity = quotepackage_extra.quantity
                        bookingpackage_extra.parameter = quotepackage_extra.parameter

                        if service_pax_variant:
                            cls.setup_bookingservice_amounts_from_quote(
                                bookingservice=bookingpackage_extra,
                                service_paxvariant=service_pax_variant,
                                pax_list=pax_list)
                        else:
                            cls.setup_bookingservice_amounts(bookingpackage_extra, pax_list)
                        bookingpackage_extra.avoid_bookingpackage_update = True
                        bookingpackage_extra.avoid_bookingpackageservice_update = True
                        bookingpackage_extra.save()

                # update booking
                cls.update_booking(booking)
                return booking, 'Booking Succesfully Created'
        except Exception as ex:
            return None, 'Error on Booking Building : %s' % (ex)
        return None, 'Error on Booking Building'

    @classmethod
    def update_quote(cls, quote_or_service):

        if hasattr(quote_or_service, 'avoid_quote_update'):
            return
        if hasattr(quote_or_service, 'quote'):
            quote = quote_or_service.quote
        elif isinstance(quote_or_service, Quote):
            quote = quote_or_service
        else:
            return

        if hasattr(quote_or_service, "avoid_sync_paxvariants"):
            quote.avoid_sync_paxvariants = True

        date_from = None
        date_to = None
        for service in quote.quote_services.all():
            # date_from
            if service.datetime_from is not None:
                if date_from is None or (date_from > service.datetime_from):
                    date_from = service.datetime_from
            # date_to
            if service.datetime_to is not None:
                if date_to is None or (date_to < service.datetime_to):
                    date_to = service.datetime_to
        fields = []
        if quote.date_from != date_from:
            fields.append('date_from')
            quote.date_from = date_from
        if quote.date_to != date_to:
            fields.append('date_to')
            quote.date_to = date_to
        if fields:
            quote.save(update_fields=fields)

    @classmethod
    def sync_quotepackage_services(cls, quote_package):
        if hasattr(quote_package, "avoid_sync_services"):
            return

        services = list(
            QuotePackageService.objects.filter(quote_package_id=quote_package.id).all())
        if services:
            return

        package = quote_package.service
        # create bookingallotment list
        for package_allotment in PackageAllotment.objects.filter(package_id=package.id).all():
            quote_package_allotment = QuotePackageAllotment()
            quote_package_allotment.quote_package = quote_package
            quote_package_allotment.conf_number = '< confirm number >'
            # cost_amount
            # cost_comment
            # price_amount
            # price_comment
            # provider_invoice

            # name auto
            # service_type auto
            cls._copy_package_info(
                dst_package=quote_package_allotment, src_package=package_allotment)
            quote_package_allotment.room_type = package_allotment.room_type
            quote_package_allotment.board_type = package_allotment.board_type
            quote_package_allotment.save()

        # create bookingtransfer list
        for package_transfer in PackageTransfer.objects.filter(package_id=package.id).all():
            quote_package_transfer = QuotePackageTransfer()
            quote_package_transfer.quote_package = quote_package
            quote_package_transfer.conf_number = '< confirm number >'
            # cost_amount
            # cost_comment
            # price_amount
            # price_comment
            # provider_invoice
            # name auto
            # service_type auto
            cls._copy_package_info(
                dst_package=quote_package_transfer, src_package=package_transfer)
            # time
            # quantity auto
            quote_package_transfer.location_from = package_transfer.location_from
            # place_from
            # schedule_from
            # pickup
            quote_package_transfer.location_to = package_transfer.location_to
            # place_to
            # schedule_to
            # dropoff
            quote_package_transfer.save()

        # create bookingextra list
        for package_extra in PackageExtra.objects.filter(package_id=package.id).all():
            quote_package_extra = QuotePackageExtra()
            quote_package_extra.quote_package = quote_package
            quote_package_extra.conf_number = '< confirm number >'
            # cost_amount
            # cost_comment
            # price_amount
            # price_comment
            # provider_invoice
            # name auto
            # service_type auto
            cls._copy_package_info(
                dst_package=quote_package_extra, src_package=package_extra)
            quote_package_extra.addon = package_extra.addon
            quote_package_extra.time = package_extra.time
            quote_package_extra.quantity = package_extra.quantity
            quote_package_extra.parameter = package_extra.parameter
            quote_package_extra.save()


    @classmethod
    def find_quote_amounts(
            cls, quote, variant_list, inline_allotment_list=None, inline_transfer_list=None, inline_extra_list=None, inline_package_list=None):
        agency = quote.agency
        result = list()

        if not variant_list:
            return 3, 'Pax Variants Missing', None

        allotment_list = inline_allotment_list
        if not allotment_list:
            allotment_list = list(QuoteAllotment.objects.filter(
                quote=quote.id).exclude(
                    status=constants.SERVICE_STATUS_CANCELLED
                ).all())
        transfer_list = inline_transfer_list
        if not transfer_list:
            transfer_list = list(QuoteTransfer.objects.filter(
                quote=quote.id).exclude(
                    status=constants.SERVICE_STATUS_CANCELLED
                ).all())
        extra_list = inline_extra_list
        if not extra_list:
            extra_list = list(QuoteExtra.objects.filter(
                quote=quote.id).exclude(
                    status=constants.SERVICE_STATUS_CANCELLED
                ).all())
        package_list = inline_package_list
        if not package_list:
            package_list = list(QuotePackage.objects.filter(
                quote=quote.id).exclude(
                    status=constants.SERVICE_STATUS_CANCELLED
                ).all())

        if (
                (not allotment_list) and
                (not transfer_list) and
                (not extra_list) and
                (not package_list)):
            return 2, 'Services Missing', None

        for pax_variant in variant_list:
            variant_dict = dict()
            variant_dict.update({'paxes': pax_variant.pax_quantity})

            cost_1, cost_1_msg, price_1, price_1_msg, \
            cost_2, cost_2_msg, price_2, price_2_msg, \
            cost_3, cost_3_msg, price_3, price_3_msg = cls._find_quote_pax_variant_amounts(
                pax_variant, allotment_list, transfer_list, extra_list, package_list,
                agency, variant_dict)

            variant_dict.update({'total': cls._quote_amounts_dict(
                cost_1, cost_1_msg, price_1, price_1_msg,
                cost_2, cost_2_msg, price_2, price_2_msg,
                cost_3, cost_3_msg, price_3, price_3_msg)})

            result.append(variant_dict)

        return 0, '', result


    @classmethod
    def _find_quote_pax_variant_amounts(
            cls, pax_variant, allotment_list, transfer_list, extra_list, package_list,
            agency, variant_dict=None):
        cost_1, cost_1_msg, price_1, price_1_msg = 0, '', 0, ''
        cost_2, cost_2_msg, price_2, price_2_msg = 0, '', 0, ''
        cost_3, cost_3_msg, price_3, price_3_msg = 0, '', 0, ''

        if allotment_list:
            counter = 0
            for allotment in allotment_list:
                if allotment.status == constants.SERVICE_STATUS_CANCELLED:
                    continue
                key = '%s' % counter
                if not hasattr(allotment, 'service'):
                    if variant_dict:
                        variant_dict.update({key: cls._no_service_dict()})
                else:
                    c1, c1_msg, p1, p1_msg, \
                    c2, c2_msg, p2, p2_msg, \
                    c3, c3_msg, p3, p3_msg = cls._find_amounts_for_quoteservice(
                        quote_pax_variant=pax_variant, quoteservice=allotment, agency=agency,
                        manuals=True)

                    # service amounts
                    if variant_dict:
                        variant_dict.update({key: cls._quote_amounts_dict(
                            c1, c1_msg, p1, p1_msg,
                            c2, c2_msg, p2, p2_msg,
                            c3, c3_msg, p3, p3_msg
                        )})
                    # variants totals
                    cost_1, cost_1_msg, price_1, price_1_msg, \
                    cost_2, cost_2_msg, price_2, price_2_msg, \
                    cost_3, cost_3_msg, price_3, price_3_msg = cls._variant_totals(
                        cost_1, cost_1_msg, c1, c1_msg, price_1, price_1_msg, p1, p1_msg,
                        cost_2, cost_2_msg, c2, c2_msg, price_2, price_2_msg, p2, p2_msg,
                        cost_3, cost_3_msg, c3, c3_msg, price_3, price_3_msg, p3, p3_msg)
                counter = counter + 1

        if transfer_list:
            counter = 0
            for transfer in transfer_list:
                if transfer.status == constants.SERVICE_STATUS_CANCELLED:
                    continue
                key = '2-%s' % counter
                if not hasattr(transfer, 'service'):
                    if variant_dict:
                        variant_dict.update({key: cls._no_service_dict()})
                else:
                    c1, c1_msg, p1, p1_msg, \
                    c2, c2_msg, p2, p2_msg, \
                    c3, c3_msg, p3, p3_msg = cls._find_amounts_for_quoteservice(
                        quote_pax_variant=pax_variant, quoteservice=transfer, agency=agency,
                        manuals=True)

                    # service amounts
                    if variant_dict:
                        variant_dict.update({key: cls._quote_amounts_dict(
                            c1, c1_msg, p1, p1_msg,
                            c2, c2_msg, p2, p2_msg,
                            c3, c3_msg, p3, p3_msg
                        )})
                    # variants totals
                    cost_1, cost_1_msg, price_1, price_1_msg, \
                    cost_2, cost_2_msg, price_2, price_2_msg, \
                    cost_3, cost_3_msg, price_3, price_3_msg = cls._variant_totals(
                        cost_1, cost_1_msg, c1, c1_msg, price_1, price_1_msg, p1, p1_msg,
                        cost_2, cost_2_msg, c2, c2_msg, price_2, price_2_msg, p2, p2_msg,
                        cost_3, cost_3_msg, c3, c3_msg, price_3, price_3_msg, p3, p3_msg)
                counter = counter + 1

        if extra_list:
            counter = 0
            for extra in extra_list:
                if extra.status == constants.SERVICE_STATUS_CANCELLED:
                    continue
                key = '3-%s' % counter
                if not hasattr(extra, 'service'):
                    if variant_dict:
                        variant_dict.update({key: cls._no_service_dict()})
                else:
                    c1, c1_msg, p1, p1_msg, \
                    c2, c2_msg, p2, p2_msg, \
                    c3, c3_msg, p3, p3_msg = cls._find_amounts_for_quoteservice(
                        quote_pax_variant=pax_variant, quoteservice=extra, agency=agency,
                        manuals=True)

                    # service amounts
                    if variant_dict:
                        variant_dict.update({key: cls._quote_amounts_dict(
                            c1, c1_msg, p1, p1_msg,
                            c2, c2_msg, p2, p2_msg,
                            c3, c3_msg, p3, p3_msg
                        )})
                    # variants totals
                    cost_1, cost_1_msg, price_1, price_1_msg, \
                    cost_2, cost_2_msg, price_2, price_2_msg, \
                    cost_3, cost_3_msg, price_3, price_3_msg = cls._variant_totals(
                        cost_1, cost_1_msg, c1, c1_msg, price_1, price_1_msg, p1, p1_msg,
                        cost_2, cost_2_msg, c2, c2_msg, price_2, price_2_msg, p2, p2_msg,
                        cost_3, cost_3_msg, c3, c3_msg, price_3, price_3_msg, p3, p3_msg)
                counter = counter + 1

        if package_list:
            counter = 0
            for package in package_list:
                if package.status == constants.SERVICE_STATUS_CANCELLED:
                    continue
                key = '4-%s' % counter
                if not hasattr(package, 'service'):
                    if variant_dict:
                        variant_dict.update({key: cls._no_service_dict()})
                else:
                    c1, c1_msg, p1, p1_msg, \
                    c2, c2_msg, p2, p2_msg, \
                    c3, c3_msg, p3, p3_msg = cls._find_quotepackage_amounts(
                        quote_pax_variant=pax_variant, package=package, agency=agency,
                        manuals=True)

                    # service amounts
                    if variant_dict:
                        variant_dict.update({key: cls._quote_amounts_dict(
                            c1, c1_msg, p1, p1_msg,
                            c2, c2_msg, p2, p2_msg,
                            c3, c3_msg, p3, p3_msg
                        )})
                    # variants totals
                    cost_1, cost_1_msg, price_1, price_1_msg, \
                    cost_2, cost_2_msg, price_2, price_2_msg, \
                    cost_3, cost_3_msg, price_3, price_3_msg = cls._variant_totals(
                        cost_1, cost_1_msg, c1, c1_msg, price_1, price_1_msg, p1, p1_msg,
                        cost_2, cost_2_msg, c2, c2_msg, price_2, price_2_msg, p2, p2_msg,
                        cost_3, cost_3_msg, c3, c3_msg, price_3, price_3_msg, p3, p3_msg)
                counter = counter + 1

        return cost_1, cost_1_msg, price_1, price_1_msg, \
            cost_2, cost_2_msg, price_2, price_2_msg, \
            cost_3, cost_3_msg, price_3, price_3_msg


    @classmethod
    def find_quoteservice_amounts(
            cls, quoteservice, variant_list):
        result = list()

        if not variant_list:
            return 3, 'Pax Variants Missing', None

        counter = 0
        for pax_variant in variant_list:

            key = '%s' % counter

            cost_1 = 0
            cost_2 = 0
            cost_3 = 0
            price_1 = 0
            price_2 = 0
            price_3 = 0
            cost_1_msg = ''
            cost_2_msg = ''
            cost_3_msg = ''
            price_1_msg = ''
            price_2_msg = ''
            price_3_msg = ''

            variant_dict = dict()

            if isinstance(quoteservice, (QuoteAllotment, QuoteTransfer, QuoteExtra, QuotePackage, QuoteService)):
                variant_dict.update({'quote_pax_variant': pax_variant.quote_pax_variant.id})
            else:
                variant_dict.update({'quotepackage_pax_variant': pax_variant.quotepackage_pax_variant.id})
            if not hasattr(quoteservice, 'service'):
                variant_dict.update({'total': cls._no_service_dict()})
            else:
                if isinstance(quoteservice, QuotePackage):
                    c1, c1_msg, p1, p1_msg, \
                    c2, c2_msg, p2, p2_msg, \
                    c3, c3_msg, p3, p3_msg = cls._find_quotepackage_amounts(
                        quote_pax_variant=pax_variant.quote_pax_variant,
                        package=quoteservice,
                        agency=quoteservice.quote.agency,
                        service_pax_variant=pax_variant,
                        manuals=True)
                else:
                    if isinstance(quoteservice, (QuoteAllotment, QuoteTransfer, QuoteExtra, QuoteService)):
                        quote_pax_variant = pax_variant.quote_pax_variant
                        agency = quoteservice.quote.agency
                        service_pax_variant = pax_variant
                    else:
                        quote_pax_variant = pax_variant.quotepackage_pax_variant.quote_pax_variant
                        agency = quoteservice.quote_package.quote.agency
                        service_pax_variant = pax_variant.quotepackage_pax_variant

                    c1, c1_msg, p1, p1_msg, \
                    c2, c2_msg, p2, p2_msg, \
                    c3, c3_msg, p3, p3_msg = cls._find_amounts_for_quoteservice(
                        quote_pax_variant=quote_pax_variant,
                        quoteservice=quoteservice,
                        agency=agency,
                        service_pax_variant=service_pax_variant)

                # variants totals
                cost_1, cost_1_msg, price_1, price_1_msg, \
                cost_2, cost_2_msg, price_2, price_2_msg, \
                cost_3, cost_3_msg, price_3, price_3_msg = cls._variant_totals(
                    cost_1, cost_1_msg, c1, c1_msg, price_1, price_1_msg, p1, p1_msg,
                    cost_2, cost_2_msg, c2, c2_msg, price_2, price_2_msg, p2, p2_msg,
                    cost_3, cost_3_msg, c3, c3_msg, price_3, price_3_msg, p3, p3_msg)

                variant_dict.update({'total': cls._quote_amounts_dict(
                    cost_1, cost_1_msg, price_1, price_1_msg,
                    cost_2, cost_2_msg, price_2, price_2_msg,
                    cost_3, cost_3_msg, price_3, price_3_msg)})

            counter = counter + 1

            result.append(variant_dict)

        return 0, '', result


    @classmethod
    def package_price(
            cls, service_id, date_from, date_to, price_groups, agency):
        service = Package.objects.get(pk=service_id)

        if date_from is None and date_to is None:
            return None, 'Both Dates are Missing'
        if date_from is None:
            date_from = date_to
        if date_to is None:
            date_to = date_from

        # agency price
        # obtain details order by date_from asc, date_to desc
        if price_groups is None and service.amounts_type == constants.PACKAGE_AMOUNTS_BY_PAX:
            price = None
            price_message = 'Paxes Missing'
        elif agency is None:
            price = None
            price_message = 'Agency Not Found'
        else:
            if service.has_pax_range:
                price = 0
                price_message = ''
                # each group can have different details
                for group in price_groups:
                    paxes = group[0] + group[1]
                    queryset = cls._get_agency_queryset(
                        AgencyPackageDetail.objects,
                        agency.id, service_id, date_from, date_to)
                    # pax range filtering
                    queryset = queryset.filter(
                        (Q(pax_range_min=0) & Q(pax_range_max__gte=paxes)) |
                        (Q(pax_range_min__lte=paxes) & Q(pax_range_max__gte=paxes)) |
                        (Q(pax_range_min__lte=paxes) & Q(pax_range_max=0)) |
                        (Q(pax_range_min=0) & Q(pax_range_max=0))
                    )
                    detail_list = list(queryset)
                    group_price, group_price_message = cls._find_package_group_price(
                        service, date_from, date_to, group, detail_list
                    )
                    if group_price:
                        price += group_price
                        price_message = group_price_message
                    else:
                        price = None
                        price_message = group_price_message
                        break
            else:
                queryset = cls._get_agency_queryset(
                    AgencyPackageDetail.objects,
                    agency.id, service_id, date_from, date_to)

                detail_list = list(queryset)

                price, price_message = cls._find_package_groups_price(
                    service, date_from, date_to, price_groups, detail_list
                )

        return price, price_message


    @classmethod
    def update_booking(cls, booking_or_bookingservice):

        if hasattr(booking_or_bookingservice, 'avoid_booking_update'):
            return
        if hasattr(booking_or_bookingservice, 'booking'):
            booking = booking_or_bookingservice.booking
        elif isinstance(booking_or_bookingservice, Booking):
            booking = booking_or_bookingservice
        else:
            return

        cost = 0
        price = 0
        date_from = None
        date_to = None
        status = constants.BOOKING_STATUS_COORDINATED
        services = False
        cancelled = True
        for service in booking.booking_services.all():
            services = True
            # process only non cancelled services
            if service.status != constants.SERVICE_STATUS_CANCELLED:
                # set not all cancelled
                cancelled = False
                # date_from
                if (service.datetime_from is not None
                        and (date_from is None or date_from > service.datetime_from)):
                    date_from = service.datetime_from
                # date_to
                if service.datetime_to is None:
                    service.datetime_to = service.datetime_from
                if (service.datetime_to is not None
                        and (date_to is None or date_to < service.datetime_to)):
                    date_to = service.datetime_to
                # cost
                if cost is not None:
                    if service.cost_amount is None:
                        cost = None
                    else:
                        cost += service.cost_amount
                # price
                if price is not None:
                    if service.price_amount is None:
                        price = None
                    else:
                        price += service.price_amount
                # status
                # pending sets always pending
                if service.status == constants.SERVICE_STATUS_PENDING:
                    status = constants.BOOKING_STATUS_PENDING
                # requested sets requested when not pending
                elif (service.status == constants.SERVICE_STATUS_REQUEST) and (
                        status != constants.BOOKING_STATUS_PENDING):
                    status = constants.BOOKING_STATUS_REQUEST
                # phone confirmed sets requested when not pending
                elif (service.status == constants.SERVICE_STATUS_PHONE_CONFIRMED) and (
                        status != constants.BOOKING_STATUS_PENDING):
                    status = constants.BOOKING_STATUS_REQUEST
                # confirmed sets confirmed when not requested and not pending
                elif (service.status == constants.SERVICE_STATUS_CONFIRMED) and (
                        status != constants.BOOKING_STATUS_PENDING) and (
                            status != constants.BOOKING_STATUS_REQUEST):
                    status = constants.BOOKING_STATUS_CONFIRMED

        # verify that have services and all cancelled
        if services:
            if cancelled:
                # status cancelled
                status = constants.BOOKING_STATUS_CANCELLED
        else:
            status = constants.BOOKING_STATUS_PENDING
        # verify package prices
        if booking.is_package_price:
            price, price_msg = cls._find_booking_package_price(booking)

        fields = []
        if booking.date_from != date_from:
            fields.append('date_from')
            booking.date_from = date_from
        if booking.date_to != date_to:
            fields.append('date_to')
            booking.date_to = date_to
        if booking.status != status:
            fields.append('status')
            booking.status = status
        if not cls._equals_amounts(booking.cost_amount, cost):
            fields.append('cost_amount')
            booking.cost_amount = cost
        if not cls._equals_amounts(booking.price_amount, price):
            fields.append('price_amount')
            booking.price_amount = price

        if fields:
            booking.save(update_fields=fields)


    @classmethod
    def find_groups(cls, booking_service, service, for_cost):
        if booking_service is None:
            return None, None
        pax_list = list(
            BookingServicePax.objects.filter(booking_service=booking_service.id))
        return cls.find_bookingservice_paxes_groups(pax_list, service, for_cost)


    @classmethod
    def find_bookingservice_paxes_groups(cls, pax_list, service, for_cost):
        if service.grouping:
            groups = dict()
            for pax in pax_list:
                if pax.booking_pax_id is not None and pax.group is not None:
                    if not groups.__contains__(pax.group):
                        groups[pax.group] = dict()
                        groups[pax.group][0] = 0 # adults count
                        groups[pax.group][1] = 0 # child count
                    if for_cost and pax.is_cost_free:
                        continue
                    if not for_cost and pax.is_price_free:
                        continue
                    if pax.booking_pax.pax_age is None:
                        groups[pax.group][0] += 1
                    else:
                        if service.child_age is None:
                            if service.infant_age is None:
                                groups[pax.group][0] += 1
                            else:
                                if pax.booking_pax.pax_age > service.infant_age:
                                    groups[pax.group][0] += 1
                        else:
                            if pax.booking_pax.pax_age > service.child_age:
                                groups[pax.group][0] += 1
                            else:
                                if service.infant_age is None:
                                    groups[pax.group][1] += 1
                                else:
                                    if pax.booking_pax.pax_age > service.infant_age:
                                        groups[pax.group][1] += 1
            return groups.values()
        else:
            adults = 0
            children = 0
            for pax in pax_list:
                if pax.booking_pax_id is not None:
                    if for_cost and pax.is_cost_free:
                        continue
                    if not for_cost and pax.is_price_free:
                        continue
                    if pax.booking_pax.pax_age is None:
                        adults += 1
                    else:
                        if service.child_age is None:
                            if service.infant_age is None:
                                adults += 1
                            else:
                                if pax.booking_pax.pax_age > service.infant_age:
                                    adults += 1
                        else:
                            if pax.booking_pax.pax_age > service.child_age:
                                adults += 1
                            else:
                                if service.infant_age is None:
                                    children += 1
                                else:
                                    if pax.booking_pax.pax_age > service.infant_age:
                                        children += 1
            return ({0: adults, 1: children},)


    @classmethod
    def update_bookingpackage(cls, bookingpackage_or_bookingpackageservice):

        if hasattr(bookingpackage_or_bookingpackageservice, 'avoid_bookingpackage_update'):
            return
        if hasattr(bookingpackage_or_bookingpackageservice, 'booking_package'):
            bookingpackage = bookingpackage_or_bookingpackageservice.booking_package
        elif isinstance(bookingpackage_or_bookingpackageservice, BookingPackage):
            bookingpackage = bookingpackage_or_bookingpackageservice
        else:
            return

        cost = 0
        price = 0
        date_from = None
        date_to = None
        status = constants.BOOKING_STATUS_COORDINATED
        services = False
        cancelled = True
        for service in bookingpackage.bookingpackage_services.all():
            services = True
            # process only non cancelled services
            if service.status != constants.SERVICE_STATUS_CANCELLED:
                # set not all cancelled
                cancelled = False
                # date_from
                if (service.datetime_from is not None
                        and (date_from is None or date_from > service.datetime_from)):
                    date_from = service.datetime_from
                # date_to
                if service.datetime_to is None:
                    service.datetime_to = service.datetime_from
                if (service.datetime_to is not None
                        and (date_to is None or date_to < service.datetime_to)):
                    date_to = service.datetime_to
                # cost
                if cost is not None:
                    if service.cost_amount is None:
                        cost = None
                    else:
                        cost += service.cost_amount
                # price
                if price is not None:
                    if service.price_amount is None:
                        price = None
                    else:
                        price += service.price_amount
                # status
                # pending sets always pending
                if service.status == constants.SERVICE_STATUS_PENDING:
                    status = constants.BOOKING_STATUS_PENDING
                # requested sets requested when not pending
                elif (service.status == constants.SERVICE_STATUS_REQUEST) and (
                        status != constants.BOOKING_STATUS_PENDING):
                    status = constants.BOOKING_STATUS_REQUEST
                # phone confirmed sets requested when not pending
                elif (service.status == constants.SERVICE_STATUS_PHONE_CONFIRMED) and (
                        status != constants.BOOKING_STATUS_PENDING):
                    status = constants.BOOKING_STATUS_REQUEST
                # confirmed sets confirmed when not requested and not pending
                elif (service.status == constants.SERVICE_STATUS_CONFIRMED) and (
                        status != constants.BOOKING_STATUS_PENDING) and (
                            status != constants.BOOKING_STATUS_REQUEST):
                    status = constants.BOOKING_STATUS_CONFIRMED

        # verify that have services and all cancelled
        if services:
            if cancelled:
                # status cancelled
                status = constants.BOOKING_STATUS_CANCELLED
        else:
            status = constants.BOOKING_STATUS_PENDING

        fields = []
        if bookingpackage.datetime_from != date_from:
            fields.append('datetime_from')
            bookingpackage.datetime_from = date_from
        if bookingpackage.datetime_to != date_to:
            fields.append('datetime_to')
            bookingpackage.datetime_to = date_to
        if bookingpackage.status != status:
            fields.append('status')
            bookingpackage.status = status
        if not cls._equals_amounts(bookingpackage.cost_amount, cost):
            fields.append('cost_amount')
            bookingpackage.cost_amount = cost
        if not cls._equals_amounts(bookingpackage.price_amount, price):
            fields.append('price_amount')
            bookingpackage.price_amount = price

        if fields:
            bookingpackage.save(update_fields=fields)


    @classmethod
    def update_bookingservice_description(cls, booking_service):
        CLASSES = {
            'T': BookingTransfer,
            'E': BookingExtra,
            'A': BookingAllotment,
            'P': BookingPackage,
        }
        service = CLASSES[booking_service.service_type].objects.get(id=booking_service.id)
        #service = getattr(CLASSES, booking_service.service_type).objects.get(
        #    id=booking_service.id)
        service.description = service.build_description()
        service.save()

    @classmethod
    def process_agencies_amounts(cls, agencies, is_update):
        """
        process_agencies_amounts
        """
        cls.generate_agencies_amounts(agencies, is_update)
        return

        # from multiprocessing import Process
        # if __name__ == 'config.services':
        #    p = Process(target=cls.generate_agencies_amounts, args=(agencies))
        #    p.start()
        #    p.join()


    @classmethod
    def generate_agencies_amounts(cls, agencies, is_update):
        """
        generate_agencies_amounts
        """
        # load source agency

        from reservas.custom_settings import AGENCY_FOR_AMOUNTS

        try:
            src_agency = Agency.objects.get(id=AGENCY_FOR_AMOUNTS)
        except Agency.DoesNotExist as ex:
            print(ex)
            # 'Source Agency not Found'
            return
        for dst_agency in agencies:
            cls.copy_agency_amounts(src_agency, dst_agency, is_update)


    @classmethod
    def copy_agency_amounts(cls, src_agency, dst_agency, is_update):
        """
        copy_agency_amounts
        """
        ConfigServices.copy_agency_amounts(src_agency, dst_agency, is_update)
        cls._copy_packages(src_agency, dst_agency, is_update)


    @classmethod
    def _find_package_groups_price(
            cls, service, date_from, date_to, groups, detail_list):

        groups_amount = 0
        groups_message = ''
        for group in groups:
            amount, message = cls._find_package_group_price(
                service, date_from, date_to, group, detail_list)
            if amount is None:
                return None, message
            groups_amount += amount
            groups_message = message

        return groups_amount, groups_message


    @classmethod
    def _find_package_group_price(cls, service, date_from, date_to, group, detail_list):
        adults, children = group[0], group[1]
        if adults + children == 0:
            return 0, ''
        message = ''
        stop = False
        solved = False
        current_date = date_from
        amount = 0
        details = list(detail_list)
        # continue until solved or empty details list
        while not stop:
            # verify list not empty
            if details:
                # working with first detail
                detail = details[0]

                detail_date_from = detail.agency_service.date_from
                detail_date_to = detail.agency_service.date_to

                if current_date >= detail_date_from:
                    # verify final date included
                    end_date = detail_date_to + timedelta(days=1)
                    if end_date >= date_to:
                        # full date range
                        result = cls._get_package_price(
                            service, detail, current_date, date_to,
                            adults, children)
                        if result is not None and result >= 0:
                            amount += result
                            solved = True
                            stop = True
                    else:
                        result = cls._get_package_price(
                            service, detail, current_date,
                            datetime(year=end_date.year, month=end_date.month, day=end_date.day),
                            adults, children)
                        if result is not None and result >= 0:
                            amount += result
                            current_date = datetime(
                                year=end_date.year, month=end_date.month, day=end_date.day)
                # remove detail from list
                details.remove(detail)
            else:
                # empty list, no solved all days
                stop = True
                message = 'Amount Not Found for date %s' % current_date
        if not solved:
            amount = None

        if amount is not None and amount >= 0:
            return amount, message
        else:
            return None, message


    @classmethod
    def _get_package_price(
            cls, service, detail, date_from, date_to, adults, children):
        if (service.cost_type == constants.PACKAGE_AMOUNTS_FIXED and
                detail.ad_1_amount is not None):
            return detail.ad_1_amount
        if service.cost_type == constants.PACKAGE_AMOUNTS_BY_PAX:
            if not service.grouping:
                adult_amount = 0
                if adults > 0:
                    if detail.ad_1_amount is None:
                        return None
                    adult_amount = adults * detail.ad_1_amount
                children_amount = 0
                if children > 0:
                    if detail.ch_1_ad_1_amount is None:
                        return None
                    children_amount = children * detail.ch_1_ad_1_amount
                amount = adult_amount + children_amount
            else:
                amount = ConfigServices.find_detail_amount(detail, adults, children)
            if amount is not None and amount >= 0:
                return amount
        return None


    @classmethod
    def _find_service_pax_variant(cls, service, quote_pax_variant, service_pax_variant):
        if service_pax_variant is None:
            if isinstance(service, QuotePackageService):
                try:
                    return QuoteServicePaxVariant.objects.get(
                        quote_service=service.quote_package.id,
                        quote_pax_variant=quote_pax_variant.id)
                except Exception as ex:
                    result = QuoteServicePaxVariant()
                    result.quote_service = service.quote_package
                    result.quote_pax_variant = quote_pax_variant
                    result.free_cost_single = quote_pax_variant.free_cost_single
                    result.free_cost_double = quote_pax_variant.free_cost_single
                    result.free_cost_triple = quote_pax_variant.free_cost_single
                    return result
            else:
                try:
                    return QuoteServicePaxVariant.objects.get(
                        quote_service=service.id,
                        quote_pax_variant=quote_pax_variant.id)
                except Exception as ex:
                    result = QuoteServicePaxVariant()
                    result.quote_service = service
                    result.quote_pax_variant = quote_pax_variant

                    return result
        else:
            return service_pax_variant


    @classmethod
    def _find_quotepackage_amounts(
            cls, quote_pax_variant, package, agency, service_pax_variant=None, manuals=False):
        cost_1 = 0
        cost_2 = 0
        cost_3 = 0
        price_1 = 0
        price_2 = 0
        price_3 = 0
        cost_1_msg = ''
        cost_2_msg = ''
        cost_3_msg = ''
        price_1_msg = ''
        price_2_msg = ''
        price_3_msg = ''

        service_pax_variant = cls._find_service_pax_variant(
            package, quote_pax_variant, service_pax_variant)

        # for saved ones use saved quote package services

        if hasattr(package, 'id') and package.id:
            if isinstance(package, QuoteService):
                package = QuotePackage.objects.get(pk=package.id)
            allotment_list = list(
                QuotePackageAllotment.objects.filter(
                    quote_package=package.id).exclude(
                        status=constants.SERVICE_STATUS_CANCELLED).all())
            transfer_list = list(
                QuotePackageTransfer.objects.filter(
                    quote_package=package.id).exclude(
                        status=constants.SERVICE_STATUS_CANCELLED).all())
            extra_list = list(
                QuotePackageExtra.objects.filter(
                    quote_package=package.id).exclude(
                        status=constants.SERVICE_STATUS_CANCELLED).all())
        else:
            allotment_list = list(
                PackageAllotment.objects.filter(package=package.service_id).all())
            transfer_list = list(
                PackageTransfer.objects.filter(package=package.service_id).all())
            extra_list = list(
                PackageExtra.objects.filter(package=package.service_id).all())

        if not hasattr(package, 'price_by_package_catalogue'):
            package.price_by_package_catalogue = False

        if package.price_by_package_catalogue:

            date_from = package.datetime_from
            date_to = package.datetime_to

            price_1, price_1_msg, \
            price_2, price_2_msg, \
            price_3, price_3_msg = cls._find_quote_package_prices(
                pax_quantity=quote_pax_variant.pax_quantity,
                service=package.service,
                date_from=date_from,
                date_to=date_to,
                agency=agency,
                service_pax_variant=service_pax_variant)

        if allotment_list:
            for allotment in allotment_list:
                if hasattr(allotment, 'service'):
                    provider = package.provider
                    if provider is None:
                        provider = allotment.provider
                    date_from = None
                    date_to = None
                    if isinstance(allotment, QuotePackageAllotment):
                        date_from = allotment.datetime_from
                        date_to = allotment.datetime_to
                        quoteservice_paxvariant = QuoteServicePaxVariant.objects.get(
                            quote_pax_variant=service_pax_variant.quote_pax_variant_id,
                            quote_service=allotment.quote_package_id)
                        try:
                            packageservice_paxvariant = QuotePackageServicePaxVariant.objects.get(
                                quotepackage_pax_variant=quoteservice_paxvariant.id,
                                quotepackage_service=allotment.id)
                        except QuotePackageServicePaxVariant.DoesNotExist as ex:
                            continue
                    if isinstance(allotment, PackageAllotment):
                        days_after = allotment.days_after
                        if days_after is None:
                            days_after = 0
                        if not package.datetime_from is None:
                            date_from = package.datetime_from + timedelta(days=days_after)
                            days_duration = allotment.days_duration
                            if days_duration is None:
                                days_duration = 0
                            date_to = date_from + timedelta(days=days_duration)
                        packageservice_paxvariant = QuotePackageServicePaxVariant()
                    if package.price_by_package_catalogue:
                        c1, c1_msg, c2, c2_msg, c3, c3_msg = cls._find_quoteservice_costs(
                            pax_quantity=quote_pax_variant.pax_quantity,
                            quoteservice=allotment,
                            date_from=date_from,
                            date_to=date_to,
                            provider=provider,
                            service_pax_variant=packageservice_paxvariant,
                            manuals=manuals)
                        # service amounts
                        cost_1, cost_1_msg, \
                        cost_2, cost_2_msg, \
                        cost_3, cost_3_msg = cls._variant_cost_totals(
                            cost_1, cost_1_msg, c1, c1_msg,
                            cost_2, cost_2_msg, c2, c2_msg,
                            cost_3, cost_3_msg, c3, c3_msg)
                    else:
                        c1, c1_msg, p1, p1_msg, \
                        c2, c2_msg, p2, p2_msg, \
                        c3, c3_msg, p3, p3_msg = cls._find_quoteservice_amounts(
                            pax_quantity=quote_pax_variant.pax_quantity,
                            quoteservice=allotment,
                            date_from=date_from,
                            date_to=date_to,
                            provider=provider,
                            agency=agency,
                            service_pax_variant=packageservice_paxvariant,
                            manuals=manuals)
                        # service amounts
                        cost_1, cost_1_msg, price_1, price_1_msg, \
                        cost_2, cost_2_msg, price_2, price_2_msg, \
                        cost_3, cost_3_msg, price_3, price_3_msg = cls._variant_totals(
                            cost_1, cost_1_msg, c1, c1_msg, price_1, price_1_msg, p1, p1_msg,
                            cost_2, cost_2_msg, c2, c2_msg, price_2, price_2_msg, p2, p2_msg,
                            cost_3, cost_3_msg, c3, c3_msg, price_3, price_3_msg, p3, p3_msg)

        if transfer_list:
            for transfer in transfer_list:
                if hasattr(transfer, 'service'):
                    provider = package.provider
                    if provider is None:
                        provider = transfer.provider
                    date_from = None
                    date_to = None
                    if isinstance(transfer, QuotePackageTransfer):
                        date_from = transfer.datetime_from
                        date_to = transfer.datetime_to
                        quoteservice_paxvariant = QuoteServicePaxVariant.objects.get(
                            quote_pax_variant=service_pax_variant.quote_pax_variant_id,
                            quote_service=transfer.quote_package_id)
                        try:
                            packageservice_paxvariant = QuotePackageServicePaxVariant.objects.get(
                                quotepackage_pax_variant=quoteservice_paxvariant.id,
                                quotepackage_service=transfer.id)
                        except QuotePackageServicePaxVariant.DoesNotExist as ex:
                            continue
                    if isinstance(transfer, PackageTransfer):
                        days_after = transfer.days_after
                        if days_after is None:
                            days_after = 0
                        if not package.datetime_from is None:
                            date_from = package.datetime_from + timedelta(days=days_after)
                            days_duration = transfer.days_duration
                            if days_duration is None:
                                days_duration = 0
                            date_to = date_from + timedelta(days=days_duration)
                        packageservice_paxvariant = QuotePackageServicePaxVariant()
                    if package.price_by_package_catalogue:
                        c1, c1_msg, c2, c2_msg, c3, c3_msg = cls._find_quoteservice_costs(
                            pax_quantity=quote_pax_variant.pax_quantity,
                            quoteservice=transfer,
                            date_from=date_from,
                            date_to=date_to,
                            provider=provider,
                            service_pax_variant=packageservice_paxvariant,
                            manuals=manuals)
                        # service amounts
                        cost_1, cost_1_msg, \
                        cost_2, cost_2_msg, \
                        cost_3, cost_3_msg = cls._variant_cost_totals(
                            cost_1, cost_1_msg, c1, c1_msg,
                            cost_2, cost_2_msg, c2, c2_msg,
                            cost_3, cost_3_msg, c3, c3_msg)
                    else:
                        c1, c1_msg, p1, p1_msg, \
                        c2, c2_msg, p2, p2_msg, \
                        c3, c3_msg, p3, p3_msg = cls._find_quoteservice_amounts(
                            pax_quantity=quote_pax_variant.pax_quantity,
                            quoteservice=transfer,
                            date_from=date_from,
                            date_to=date_to,
                            provider=provider,
                            agency=agency,
                            service_pax_variant=packageservice_paxvariant,
                            manuals=manuals)
                        # service amounts
                        cost_1, cost_1_msg, price_1, price_1_msg, \
                        cost_2, cost_2_msg, price_2, price_2_msg, \
                        cost_3, cost_3_msg, price_3, price_3_msg = cls._variant_totals(
                            cost_1, cost_1_msg, c1, c1_msg, price_1, price_1_msg, p1, p1_msg,
                            cost_2, cost_2_msg, c2, c2_msg, price_2, price_2_msg, p2, p2_msg,
                            cost_3, cost_3_msg, c3, c3_msg, price_3, price_3_msg, p3, p3_msg)
        if extra_list:
            for extra in extra_list:
                if hasattr(extra, 'service'):
                    provider = package.provider
                    if provider is None:
                        provider = extra.provider
                    date_from = None
                    date_to = None
                    if isinstance(extra, QuotePackageExtra):
                        date_from = extra.datetime_from
                        date_to = extra.datetime_to
                        quoteservice_paxvariant = QuoteServicePaxVariant.objects.get(
                            quote_pax_variant=service_pax_variant.quote_pax_variant_id,
                            quote_service=extra.quote_package_id)
                        try:
                            packageservice_paxvariant = QuotePackageServicePaxVariant.objects.get(
                                quotepackage_pax_variant=quoteservice_paxvariant.id,
                                quotepackage_service=extra.id)
                        except QuotePackageServicePaxVariant.DoesNotExist as ex:
                            continue
                    if isinstance(extra, PackageExtra):
                        days_after = extra.days_after
                        if days_after is None:
                            days_after = 0
                        if not package.datetime_from is None:
                            date_from = package.datetime_from + timedelta(days=days_after)
                            days_duration = extra.days_duration
                            if days_duration is None:
                                days_duration = 0
                            date_to = date_from + timedelta(days=days_duration)
                        packageservice_paxvariant = QuotePackageServicePaxVariant()
                    if package.price_by_package_catalogue:
                        c1, c1_msg, c2, c2_msg, c3, c3_msg = cls._find_quoteservice_costs(
                            pax_quantity=quote_pax_variant.pax_quantity,
                            quoteservice=extra,
                            date_from=date_from,
                            date_to=date_to,
                            provider=provider,
                            service_pax_variant=packageservice_paxvariant,
                            manuals=manuals)
                        # service amounts
                        cost_1, cost_1_msg, \
                        cost_2, cost_2_msg, \
                        cost_3, cost_3_msg = cls._variant_cost_totals(
                            cost_1, cost_1_msg, c1, c1_msg,
                            cost_2, cost_2_msg, c2, c2_msg,
                            cost_3, cost_3_msg, c3, c3_msg)
                    else:
                        c1, c1_msg, p1, p1_msg, \
                        c2, c2_msg, p2, p2_msg, \
                        c3, c3_msg, p3, p3_msg = cls._find_quoteservice_amounts(
                            pax_quantity=quote_pax_variant.pax_quantity,
                            quoteservice=extra,
                            date_from=date_from,
                            date_to=date_to,
                            provider=provider,
                            agency=agency,
                            service_pax_variant=packageservice_paxvariant,
                            manuals=manuals)
                        # service amounts
                        cost_1, cost_1_msg, price_1, price_1_msg, \
                        cost_2, cost_2_msg, price_2, price_2_msg, \
                        cost_3, cost_3_msg, price_3, price_3_msg = cls._variant_totals(
                            cost_1, cost_1_msg, c1, c1_msg, price_1, price_1_msg, p1, p1_msg,
                            cost_2, cost_2_msg, c2, c2_msg, price_2, price_2_msg, p2, p2_msg,
                            cost_3, cost_3_msg, c3, c3_msg, price_3, price_3_msg, p3, p3_msg)

        return cost_1, cost_1_msg, price_1, price_1_msg, \
            cost_2, cost_2_msg, price_2, price_2_msg, \
            cost_3, cost_3_msg, price_3, price_3_msg


    @classmethod
    def _quote_amounts_dict(
            cls,
            cost_1, cost_1_msg, price_1, price_1_msg,
            cost_2, cost_2_msg, price_2, price_2_msg,
            cost_3, cost_3_msg, price_3, price_3_msg):
        return {
            'cost_1': cost_1,
            'cost_1_msg': cost_1_msg,
            'price_1': price_1,
            'price_1_msg': price_1_msg,
            'cost_2': cost_2,
            'cost_2_msg': cost_2_msg,
            'price_2': price_2,
            'price_2_msg': price_2_msg,
            'cost_3': cost_3,
            'cost_3_msg': cost_3_msg,
            'price_3': price_3,
            'price_3_msg': price_3_msg,
        }


    @classmethod
    def _no_service_dict(cls):
        return cls._quote_amounts_dict(
            None, 'No Service', None, 'No Service', None, 'No Service',
            None, 'No Service', None, 'No Service', None, 'No Service'
        )


    @classmethod
    def _variant_cost_totals(
            cls,
            cost_1, cost_1_msg, c1, c1_msg,
            cost_2, cost_2_msg, c2, c2_msg,
            cost_3, cost_3_msg, c3, c3_msg):
        rc1, rc1_msg = cls._merge_costs(cost_1, cost_1_msg, c1, c1_msg)
        rc2, rc2_msg = cls._merge_costs(cost_2, cost_2_msg, c2, c2_msg)
        rc3, rc3_msg = cls._merge_costs(cost_3, cost_3_msg, c3, c3_msg)

        return rc1, rc1_msg, rc2, rc2_msg, rc3, rc3_msg


    @classmethod
    def _variant_totals(
            cls,
            cost_1, cost_1_msg, c1, c1_msg, price_1, price_1_msg, p1, p1_msg,
            cost_2, cost_2_msg, c2, c2_msg, price_2, price_2_msg, p2, p2_msg,
            cost_3, cost_3_msg, c3, c3_msg, price_3, price_3_msg, p3, p3_msg):
        rc1, rc1_msg = cls._merge_costs(cost_1, cost_1_msg, c1, c1_msg)
        rp1, rp1_msg = cls._merge_prices(price_1, price_1_msg, p1, p1_msg)
        rc2, rc2_msg = cls._merge_costs(cost_2, cost_2_msg, c2, c2_msg)
        rp2, rp2_msg = cls._merge_prices(price_2, price_2_msg, p2, p2_msg)
        rc3, rc3_msg = cls._merge_costs(cost_3, cost_3_msg, c3, c3_msg)
        rp3, rp3_msg = cls._merge_prices(price_3, price_3_msg, p3, p3_msg)

        return rc1, rc1_msg, rp1, rp1_msg, rc2, rc2_msg, rp2, rp2_msg, rc3, rc3_msg, rp3, rp3_msg


    @classmethod
    def _merge_costs(
            cls, prev_cost, prev_msg, cost, msg):
        if prev_cost is None:
            return None, prev_msg
        elif cost is None:
            return None, msg
        else:
            return cls._round_cost(float(prev_cost) + float(cost)), msg


    @classmethod
    def _merge_prices(
            cls, prev_price, prev_msg, price, msg):
        if prev_price is None:
            return None, prev_msg
        elif price is None:
            return None, msg
        else:
            return cls._round_price(float(prev_price) + float(price)), msg


    @classmethod
    def _find_bookingservice(cls, booking_service, manager):
        bookingservice = list(manager.filter(pk=booking_service.pk))
        if not bookingservice:
            return None
        return bookingservice[0]


    @classmethod
    def _save_booking_service_amounts(cls, booking_service, cost, price):
        fields = []
        if not cls._equals_amounts(booking_service.cost_amount, cost):
            fields.append('cost_amount')
            booking_service.cost_amount = cost
        if not cls._equals_amounts(booking_service.price_amount, price):
            fields.append('price_amount')
            booking_service.price_amount = price

        if fields:
            booking_service.save(update_fields=fields)
            # done on signals
            #if isinstance(booking_service, (BookingAllotment, BookingTransfer, BookingExtra)):
            #    cls.update_booking_amounts(booking_service)
            #else:
            #    cls.update_bookingpackage_amounts(booking_service)


    @classmethod
    def _find_bookingservice_pax_list(cls, bookingservice):
        if isinstance(
            bookingservice, (
                BookingAllotment, BookingTransfer, BookingExtra, BookingPackage, BookingService)):
            return list(BookingServicePax.objects.filter(booking_service=bookingservice.id).all())
        return list(
            BookingServicePax.objects.filter(
                booking_service=bookingservice.booking_package.id).all())


    @classmethod
    def _verify_booking_service_manuals(cls, booking_service):
        if booking_service.manual_cost is None:
            booking_service.manual_cost = False
        if booking_service.manual_price is None:
            booking_service.manual_price = False
        return booking_service.manual_cost and booking_service.manual_price


    @classmethod
    def _bookingpackageservice_amounts(cls, bookingpackage_service, pax_list=None):
        if not pax_list:
            pax_list = cls._find_bookingservice_pax_list(bookingpackage_service.booking_package)

        cost_groups = BookingServices.find_bookingservice_paxes_groups(
            pax_list, bookingpackage_service.booking_package.service, True)
        price_groups = BookingServices.find_bookingservice_paxes_groups(
            pax_list, bookingpackage_service.booking_package.service, False)

        service_provider = bookingpackage_service.booking_package.provider
        if service_provider is None:
            service_provider = bookingpackage_service.provider

        cost, price = None, None
        if isinstance(bookingpackage_service, BookingPackageAllotment):
            cost, cost_msg, price, price_msg = ConfigServices.allotment_amounts(
                bookingpackage_service.service,
                bookingpackage_service.datetime_from, bookingpackage_service.datetime_to,
                cost_groups, price_groups, service_provider,
                bookingpackage_service.booking_package.booking.agency,
                bookingpackage_service.board_type, bookingpackage_service.room_type_id,
                bookingpackage_service.service_addon_id)
        if isinstance(bookingpackage_service, BookingPackageTransfer):
            cost, cost_msg, price, price_msg = ConfigServices.transfer_amounts(
                bookingpackage_service.service,
                bookingpackage_service.datetime_from, bookingpackage_service.datetime_to,
                cost_groups, price_groups, service_provider,
                bookingpackage_service.booking_package.booking.agency,
                bookingpackage_service.location_from_id, bookingpackage_service.location_to_id,
                bookingpackage_service.service_addon_id,
                bookingpackage_service.quantity)
        if isinstance(bookingpackage_service, BookingPackageExtra):
            cost, cost_msg, price, price_msg = ConfigServices.extra_amounts(
                bookingpackage_service.service,
                bookingpackage_service.datetime_from, bookingpackage_service.datetime_to,
                cost_groups, price_groups, service_provider,
                bookingpackage_service.booking_package.booking.agency,
                bookingpackage_service.service_addon_id,
                bookingpackage_service.quantity, bookingpackage_service.parameter)

        return cost, price


    @classmethod
    def _copy_packages(cls, src_agency, dst_agency, is_update):
        # find agencyservice list
        src_agency_services = list(AgencyPackageService.objects.filter(agency=src_agency.id))
        # for each agencyservice create agencyservice
        for src_agency_service in src_agency_services:
            dst_agency_service, created = AgencyPackageService.objects.get_or_create(
                agency_id=dst_agency.id,
                date_from=src_agency_service.date_from,
                date_to=src_agency_service.date_to,
                service_id=src_agency_service.service_id
            )
            # find details
            details = list(
                AgencyPackageDetail.objects.filter(agency_service=src_agency_service))
            # for each src agency detail create dst agency detail
            for detail in details:
                if is_update:
                    # update - dont modify if exists
                    agency_detail, created = AgencyPackageDetail.objects.get_or_create(
                        agency_service_id=dst_agency_service.id,
                        pax_range_min=detail.pax_range_min,
                        pax_range_max=detail.pax_range_max,
                        defaults=ConfigServices.calculate_default_amounts(
                            detail, src_agency.gain_percent, dst_agency.gain_percent)
                    )
                else:
                    # rewrite - modify if exists
                    agency_detail, created = AgencyPackageDetail.objects.update_or_create(
                        agency_service_id=dst_agency_service.id,
                        pax_range_min=detail.pax_range_min,
                        pax_range_max=detail.pax_range_max,
                        defaults=ConfigServices.calculate_default_amounts(
                            detail, src_agency.gain_percent, dst_agency.gain_percent)
                    )


    @classmethod
    def _get_agency_queryset(
            cls, manager, agency_id, package_id, date_from, date_to):
        if date_from is None:
            return manager.none()
        if date_to is None:
            return manager.none()
        return manager.select_related(
            'agency_service__service'
            ).filter(
                agency_service__agency_id=agency_id
            ).filter(
                agency_service__service_id=package_id
            ).filter(
                agency_service__date_to__gte=date_from,
                agency_service__date_from__lte=date_to
            ).order_by(
                'agency_service__date_from', '-agency_service__date_to'
            )


    @classmethod
    def _find_pax_quantity_for_booking_rooming(cls, rooming):
        pax_qtty = 0
        for pax in rooming:
            if pax['pax_name'] and pax['pax_group']:
                pax_qtty += 1
        return pax_qtty


    @classmethod
    def _find_quote_paxvariant_for_booking_rooming(cls, quote, rooming):
        pax_qtty = cls._find_pax_quantity_for_booking_rooming(rooming)

        variants = list(
            QuotePaxVariant.objects.filter(quote=quote.id).all().order_by('pax_quantity'))
        if variants:
            result = variants[0]
            for variant in variants:
                if variant.pax_quantity <= pax_qtty:
                    result = variant
            return result
        return None


    @classmethod
    def _find_quoteservice_paxvariant_for_bookingservice(cls, quoteservice, quote_pax_variant):
        service_pax_variants = list(
            QuoteServicePaxVariant.objects.all().filter(
                quote_service=quoteservice.id,
                quote_pax_variant=quote_pax_variant.id))
        if service_pax_variants:
            return service_pax_variants[0]
        return None


    @classmethod
    def _copy_service_info(cls, dst_service, src_service):
        dst_service.description = src_service.description
        dst_service.datetime_from = src_service.datetime_from
        dst_service.datetime_to = src_service.datetime_to
        dst_service.status = constants.SERVICE_STATUS_PENDING
        dst_service.provider = src_service.provider
        dst_service.service = src_service.service


    @classmethod
    def _copy_package_info(cls, dst_package, src_package):
        dst_package.description = src_package.description

        days_after = src_package.days_after
        if days_after is None:
            days_after = 0
        if hasattr(dst_package, 'quote_package'):
            dst_package.datetime_from = dst_package.quote_package.datetime_from + timedelta(
                days=days_after)
        if hasattr(dst_package, 'booking_package'):
            dst_package.datetime_from = dst_package.booking_package.datetime_from + timedelta(
                days=days_after)
        days_duration = src_package.days_duration
        if days_duration is None:
            days_duration = 0
        dst_package.datetime_to = dst_package.datetime_from + timedelta(days=days_duration)
        dst_package.status = constants.SERVICE_STATUS_PENDING
        dst_package.provider = src_package.provider
        dst_package.service = src_package.service
        dst_package.service_addon = src_package.service_addon


    @classmethod
    def _find_free_paxes(cls, quoteservice_pax_variant):
        if isinstance(quoteservice_pax_variant, QuotePackageServicePaxVariant):
            service_pax_variant = quoteservice_pax_variant.quotepackage_pax_variant
        else:
            service_pax_variant = quoteservice_pax_variant

        free_cost_single, free_cost_double, free_cost_triple = 0, 0, 0
        free_price_single, free_price_double, free_price_triple = 0, 0, 0

        if service_pax_variant.free_cost_single:
            free_cost_single = service_pax_variant.free_cost_single
        if service_pax_variant.free_cost_double:
            free_cost_double = service_pax_variant.free_cost_double
        if service_pax_variant.free_cost_triple:
            free_cost_triple = service_pax_variant.free_cost_triple
        if service_pax_variant.free_price_single:
            free_price_single = service_pax_variant.free_price_single
        if service_pax_variant.free_price_double:
            free_price_double = service_pax_variant.free_price_double
        if service_pax_variant.free_price_triple:
            free_price_triple = service_pax_variant.free_price_triple

        total_free_cost = free_cost_single + free_cost_double + free_cost_triple
        total_free_price = free_price_single + free_price_double + free_price_triple
        return total_free_cost, total_free_price


    @classmethod
    def _adjust_group_free_amounts(
            cls, amount_single, amount_double, amount_triple,
            pax_quantity, quoteservice_pax_variant, for_cost):

        if isinstance(quoteservice_pax_variant, QuotePackageServicePaxVariant):
            service_pax_variant = quoteservice_pax_variant.quotepackage_pax_variant
        else:
            service_pax_variant = quoteservice_pax_variant

        a1, a2, a3 = amount_single, amount_double, amount_triple
        a1_msg, a2_msg, a3_msg = None, None, None

        if for_cost:
            if a1:
                a1 = cls._round_cost(float(a1))
            if a2:
                a2 = cls._round_cost(float(a2) / 2.0)
            if a3:
                a3 = cls._round_cost(float(a3) / 3.0)
            free1 = service_pax_variant.free_cost_single
            free2 = service_pax_variant.free_cost_double
            free3 = service_pax_variant.free_cost_triple
            if not free1:
                free1 = 0
            if not free2:
                free2 = 0
            if not free3:
                free3 = 0
            paxes_paying = pax_quantity - free1 - free2 - free3
            if paxes_paying < 1:
                return None, "No Paxes to Split", None, "No Paxes to Split", None, "No Paxes to Split"
            if a1:
                a1 = cls._round_cost(paxes_paying * float(a1) / pax_quantity)
            if a2:
                a2 = cls._round_cost(paxes_paying * float(a2) / pax_quantity)
            if a3:
                a3 = cls._round_cost(paxes_paying * float(a3) / pax_quantity)
        else:
            if a1:
                a1 = cls._round_price(float(a1))
            if a2:
                a2 = cls._round_price(float(a2) / 2.0)
            if a3:
                a3 = cls._round_price(float(a3) / 3.0)
            free1 = service_pax_variant.free_price_single
            free2 = service_pax_variant.free_price_double
            free3 = service_pax_variant.free_price_triple
            if not free1:
                free1 = 0
            if not free2:
                free2 = 0
            if not free3:
                free3 = 0
            if a1 is None and free1:
                if a2:
                    a2, a2_msg = None, "Need Single Amount for Free Pax in Single"
                if a3:
                    a3, a3_msg = None, "Need Single Amount for Free Pax in Single"
            elif a2 is None and free2:
                if a1:
                    a1, a1_msg = None, "Need Double Amount for Free Pax in Double"
                if a3:
                    a3, a3_msg = None, "Need Double Amount for Free Pax in Double"
            elif a3 is None and free3:
                if a1:
                    a1, a1_msg = None, "Need Triple Amount for Free Pax in Triple"
                if a2:
                    a2, a2_msg = None, "Need Triple Amount for Free Pax in Triple"

            free_amount = cls._calculate_group_free_amount(
                a1, a2, a3, service_pax_variant, for_cost)

            paxes_paying = pax_quantity - free1 - free2 - free3
            if paxes_paying < 1:
                return None, "No Paxes to Split", None, "No Paxes to Split", None, "No Paxes to Split"

            if free_amount:
                extra_amount = free_amount
            else:
                extra_amount = 0.0

            if a1:
                a1 = cls._round_price(float(a1) + float(extra_amount) / pax_quantity)
            if a2:
                a2 = cls._round_price(float(a2) + float(extra_amount) / pax_quantity)
            if a3:
                a3 = cls._round_price(float(a3) + float(extra_amount) / pax_quantity)

        return a1, a1_msg, a2, a2_msg, a3, a3_msg


    @classmethod
    def _calculate_group_free_amount(
            cls, amount1, amount2, amount3, service_pax_variant, for_cost):
        if amount1 is None or amount2 is None or amount3 is None:
            return None
        amount = 0.0
        if for_cost:
            if service_pax_variant.free_cost_single:
                amount += float(amount1) * float(service_pax_variant.free_cost_single)
            if service_pax_variant.free_cost_double:
                amount += float(amount2) * float(service_pax_variant.free_cost_double)
            if service_pax_variant.free_cost_triple:
                amount += float(amount3) * float(service_pax_variant.free_cost_triple)
        else:
            if service_pax_variant.free_price_single:
                amount += float(amount1) * float(service_pax_variant.free_price_single)
            if service_pax_variant.free_price_double:
                amount += float(amount2) * float(service_pax_variant.free_price_double)
            if service_pax_variant.free_price_triple:
                amount += float(amount3) * float(service_pax_variant.free_price_triple)

        return amount


    @classmethod
    def _find_amounts_for_quoteservice(
            cls, quote_pax_variant, quoteservice, agency, service_pax_variant=None, manuals=False):
        service_pax_variant = cls._find_service_pax_variant(
            quoteservice, quote_pax_variant, service_pax_variant)

        return cls._find_quoteservice_amounts(
            pax_quantity=quote_pax_variant.pax_quantity,
            quoteservice=quoteservice,
            date_from=quoteservice.datetime_from,
            date_to=quoteservice.datetime_to,
            provider=quoteservice.provider,
            agency=agency,
            service_pax_variant=service_pax_variant,
            manuals=manuals,
            quote_pax_variant=quote_pax_variant)


    @classmethod
    def _quoteservice_amounts(
            cls, quoteservice, date_from, date_to, cost_groups, price_groups, provider, agency):
        if isinstance(quoteservice, (QuoteAllotment, QuotePackageAllotment)):
            c, c_msg, p, p_msg = ConfigServices.allotment_amounts(
                quoteservice.service, date_from, date_to, cost_groups, price_groups,
                provider, agency,
                quoteservice.board_type, quoteservice.room_type_id,
                quoteservice.service_addon_id)
            return c, c_msg, p, p_msg
        if isinstance(quoteservice, (QuoteTransfer, QuotePackageTransfer)):
            c, c_msg, p, p_msg = ConfigServices.transfer_amounts(
                quoteservice.service, date_from, date_to, cost_groups, price_groups,
                provider, agency,
                quoteservice.location_from_id, quoteservice.location_to_id,
                quoteservice.service_addon_id,
                quoteservice.quantity)
            return c, c_msg, p, p_msg
        if isinstance(quoteservice, (QuoteExtra, QuotePackageExtra)):
            c, c_msg, p, p_msg = ConfigServices.extra_amounts(
                quoteservice.service, date_from, date_to, cost_groups, price_groups,
                provider, agency,
                quoteservice.service_addon_id, quoteservice.quantity, quoteservice.parameter)
            return c, c_msg, p, p_msg
        return None, "Unknown Service", None, "Unknown Service"


    @classmethod
    def _quoteservice_costs(
            cls, quoteservice, date_from, date_to, cost_groups, provider):
        if isinstance(quoteservice, (QuoteAllotment, QuotePackageAllotment)):
            return ConfigServices.allotment_costs(
                quoteservice.service, date_from, date_to, cost_groups, provider,
                quoteservice.board_type, quoteservice.room_type_id)
        if isinstance(quoteservice, (QuoteTransfer, QuotePackageTransfer)):
            return ConfigServices.transfer_costs(
                quoteservice.service, date_from, date_to, cost_groups, provider,
                quoteservice.location_from_id, quoteservice.location_to_id,
                quoteservice.quantity)
        if isinstance(quoteservice, (QuoteExtra, QuotePackageExtra)):
            return ConfigServices.extra_costs(
                quoteservice.service, date_from, date_to, cost_groups, provider,
                quoteservice.addon_id, quoteservice.quantity, quoteservice.parameter)
        return None, "Unknown Service"


    @classmethod
    def _quoteservice_prices(
            cls, quoteservice, date_from, date_to, price_groups, agency):
        if isinstance(quoteservice, (QuoteAllotment, QuotePackageAllotment)):
            return ConfigServices.allotment_prices(
                quoteservice.service, date_from, date_to, price_groups, agency,
                quoteservice.board_type, quoteservice.room_type_id)
        if isinstance(quoteservice, (QuoteTransfer, QuotePackageTransfer)):
            return ConfigServices.transfer_prices(
                quoteservice.service, date_from, date_to, price_groups, agency,
                quoteservice.location_from_id, quoteservice.location_to_id,
                quoteservice.quantity)
        if isinstance(quoteservice, (QuoteExtra, QuotePackageExtra)):
            return ConfigServices.extra_prices(
                quoteservice.service, date_from, date_to, price_groups, agency,
                quoteservice.addon_id, quoteservice.quantity, quoteservice.parameter)
        return None, "Unknown Service"


    @classmethod
    def _find_quoteservice_amounts(
            cls, pax_quantity, quoteservice, date_from, date_to,
            provider, agency, service_pax_variant, manuals=False, quote_pax_variant=None):
        if service_pax_variant is None:
            return None, "Service Pax Variant Not Found", \
                None, "Service Pax Variant Not Found", \
                None, "Service Pax Variant Not Found", \
                None, "Service Pax Variant Not Found", \
                None, "Service Pax Variant Not Found", \
                None, "Service Pax Variant Not Found"
        auto_cost, auto_price = True, True
        if manuals:
            if service_pax_variant.manual_costs:
                auto_cost = False
                if service_pax_variant.cost_single_amount:
                    c1, c1_msg = service_pax_variant.cost_single_amount, None
                else:
                    c1, c1_msg = None, "Missing Manual Cost for Single"
                if service_pax_variant.cost_double_amount:
                    c2, c2_msg = service_pax_variant.cost_double_amount, None
                else:
                    c2, c2_msg = None, "Missing Manual Cost for Double"
                if service_pax_variant.cost_triple_amount:
                    c3, c3_msg = service_pax_variant.cost_triple_amount, None
                else:
                    c3, c3_msg = None, "Missing Manual Cost for Triple"
                if service_pax_variant.manual_prices:
                    if service_pax_variant.price_single_amount:
                        p1, p1_msg = service_pax_variant.price_single_amount, None
                    else:
                        p1, p1_msg = None, "Missing Manual Price for Single"
                    if service_pax_variant.price_double_amount:
                        p2, p2_msg = service_pax_variant.price_double_amount, None
                    else:
                        p2, p2_msg = None, "Missing Manual Price for Double"
                    if service_pax_variant.price_triple_amount:
                        p3, p3_msg = service_pax_variant.price_triple_amount, None
                    else:
                        p3, p3_msg = None, "Missing Manual Price for Triple"
                    return c1, c1_msg, p1, p1_msg, c2, c2_msg, p2, p2_msg, c3, c3_msg, p3, p3_msg
            elif service_pax_variant.manual_prices:
                auto_price = False
                if service_pax_variant.price_single_amount:
                    p1, p1_msg = service_pax_variant.price_single_amount, None
                else:
                    p1, p1_msg = None, "Missing Manual Price for Single"
                if service_pax_variant.price_double_amount:
                    p2, p2_msg = service_pax_variant.price_double_amount, None
                else:
                    p2, p2_msg = None, "Missing Manual Price for Double"
                if service_pax_variant.price_triple_amount:
                    p3, p3_msg = service_pax_variant.price_triple_amount, None
                else:
                    p3, p3_msg = None, "Missing Manual Price for Triple"
        if auto_cost and auto_price:
            if quoteservice.service.grouping:
                # grouping means passing 1,2,3 as pax quantity
                c1, c1_msg, p1, p1_msg = cls._quoteservice_amounts(
                    quoteservice, date_from, date_to, ({0:1, 1:0},), ({0:1, 1:0},), provider, agency)
                c2, c2_msg, p2, p2_msg = cls._quoteservice_amounts(
                    quoteservice, date_from, date_to, ({0:2, 1:0},), ({0:2, 1:0},), provider, agency)
                c3, c3_msg, p3, p3_msg = cls._quoteservice_amounts(
                    quoteservice, date_from, date_to, ({0:3, 1:0},), ({0:3, 1:0},), provider, agency)

                c1, c1_msg, c2, c2_msg, c3, c3_msg = cls._adjust_group_free_amounts(
                    c1, c2, c3, pax_quantity, service_pax_variant, True)
                p1, p1_msg, p2, p2_msg, p3, p3_msg = cls._adjust_group_free_amounts(
                    p1, p2, p3, pax_quantity, service_pax_variant, False)
            else:
                # no grouping means passing total pax quantity
                total_free_cost, total_free_price = cls._find_free_paxes(service_pax_variant)
                c1, c1_msg, p1, p1_msg = cls._quoteservice_amounts(
                    quoteservice, date_from, date_to,
                    ({0:pax_quantity, 1:0},),
                    ({0:pax_quantity, 1:0},),
                    provider, agency)
                if c1:
                    c1 = cls._round_cost(cls._adjust_cost(c1, pax_quantity, total_free_cost))
                if p1:
                    p1 = cls._round_price(cls._adjust_price(p1, pax_quantity, total_free_price))
                c2, c2_msg, p2, p2_msg = c1, c1_msg, p1, p1_msg
                c3, c3_msg, p3, p3_msg = c1, c1_msg, p1, p1_msg
        elif auto_cost:
            c1, c1_msg, c2, c2_msg, c3, c3_msg = cls._find_quoteservice_costs(
                pax_quantity, quoteservice, date_from, date_to, provider, service_pax_variant)
        elif auto_price:
            p1, p1_msg, p2, p2_msg, p3, p3_msg = cls._find_quoteservice_prices(
                pax_quantity, quoteservice, date_from, date_to, agency, service_pax_variant)

        if not quote_pax_variant:
            if isinstance(service_pax_variant, QuoteServicePaxVariant):
                quote_pax_variant = service_pax_variant.quote_pax_variant
            else:
                quote_pax_variant = service_pax_variant.quotepackage_pax_variant.quote_pax_variant

        if quote_pax_variant.price_percent and auto_price:
            if service_pax_variant.manual_costs:
                if service_pax_variant.cost_single_amount:
                    p1 = cls._round_price(
                        cls._apply_percent(
                            service_pax_variant.cost_single_amount, quote_pax_variant.price_percent))
                    p1_msg = None
                else:
                    p1, p1_msg = None, 'Cost SGL for % is empty'
                if service_pax_variant.cost_double_amount:
                    p2 = cls._round_price(
                        cls._apply_percent(
                            service_pax_variant.cost_double_amount, quote_pax_variant.price_percent))
                    p2_msg = None
                else:
                    p2, p2_msg = None, 'Cost DBL for % is empty'
                if service_pax_variant.cost_triple_amount:
                    p3 = cls._round_price(
                        cls._apply_percent(
                            service_pax_variant.cost_triple_amount, quote_pax_variant.price_percent))
                    p3_msg = None
                else:
                    p3, p3_msg = None, 'Cost TPL for % is empty'
            else:
                if c1 is None:
                    p1, p1_msg = None, 'Cost SGL for % is empty'
                else:
                    p1 = cls._round_price(cls._apply_percent(c1, quote_pax_variant.price_percent))
                    p1_msg = None
                if c2 is None:
                    p2, p2_msg = None, 'Cost DBL for % is empty'
                else:
                    p2 = cls._round_price(cls._apply_percent(c2, quote_pax_variant.price_percent))
                    p2_msg = None
                if c3 is None:
                    p3, p3_msg = None, 'Cost TPL for % is empty'
                else:
                    p3 = cls._round_price(cls._apply_percent(c3, quote_pax_variant.price_percent))
                    p3_msg = None

        return c1, c1_msg, p1, p1_msg, c2, c2_msg, p2, p2_msg, c3, c3_msg, p3, p3_msg


    @classmethod
    def _find_quoteservice_costs(
            cls, pax_quantity, quoteservice, date_from, date_to,
            provider, service_pax_variant, manuals=False):
        if service_pax_variant is None:
            return None, "Service Pax Variant Not Found", \
                None, "Service Pax Variant Not Found", \
                None, "Service Pax Variant Not Found"

        if manuals:
            if service_pax_variant.manual_costs:
                if service_pax_variant.cost_single_amount:
                    c1, c1_msg = service_pax_variant.cost_single_amount, None
                if service_pax_variant.cost_double_amount:
                    c2, c2_msg = service_pax_variant.cost_double_amount, None
                if service_pax_variant.cost_triple_amount:
                    c3, c3_msg = service_pax_variant.cost_triple_amount, None
                return c1, c1_msg, c2, c2_msg, c3, c3_msg
        if quoteservice.service.grouping:
            # grouping means passing 1,2,3 as pax quantity
            c1, c1_msg = cls._quoteservice_costs(
                quoteservice, date_from, date_to, ({0:1, 1:0},), provider)
            c2, c2_msg = cls._quoteservice_costs(
                quoteservice, date_from, date_to, ({0:2, 1:0},), provider)
            c3, c3_msg = cls._quoteservice_costs(
                quoteservice, date_from, date_to, ({0:3, 1:0},), provider)

            c1, c1_msg, c2, c2_msg, c3, c3_msg = cls._adjust_group_free_amounts(
                c1, c2, c3, pax_quantity, service_pax_variant, True)

        else:
            # no grouping means passing total pax quantity
            total_free_cost, total_free_price = cls._find_free_paxes(service_pax_variant)
                
            c1, c1_msg = cls._quoteservice_costs(
                quoteservice, date_from, date_to,
                ({0:pax_quantity, 1:0},),
                provider)
            if c1:
                c1 = cls._round_cost(cls._adjust_cost(c1, pax_quantity, total_free_cost))
            c2, c2_msg, c3, c3_msg = c1, c1_msg, c1, c1_msg
        return c1, c1_msg, c2, c2_msg, c3, c3_msg


    @classmethod
    def _find_quoteservice_prices(
            cls, pax_quantity, quoteservice, date_from, date_to,
            agency, service_pax_variant, manuals=False, quotepackageservice_pax_variant=None):
        if service_pax_variant is None:
            return None, "Service Pax Variant Not Found", \
                None, "Service Pax Variant Not Found", \
                None, "Service Pax Variant Not Found"

        if manuals:
            if quotepackageservice_pax_variant and quotepackageservice_pax_variant.manual_prices:
                if quotepackageservice_pax_variant.price_single_amount:
                    p1, p1_msg = quotepackageservice_pax_variant.price_single_amount, None
                if quotepackageservice_pax_variant.price_double_amount:
                    p2, p2_msg = quotepackageservice_pax_variant.price_double_amount, None
                if quotepackageservice_pax_variant.price_triple_amount:
                    p3, p3_msg = quotepackageservice_pax_variant.price_triple_amount, None
                return p1, p1_msg, p2, p2_msg, p3, p3_msg
            if service_pax_variant.manual_prices:
                if service_pax_variant.price_single_amount:
                    p1, p1_msg = service_pax_variant.price_single_amount, None
                if service_pax_variant.price_double_amount:
                    p2, p2_msg = service_pax_variant.price_double_amount, None
                if service_pax_variant.price_triple_amount:
                    p3, p3_msg = service_pax_variant.price_triple_amount, None
                return p1, p1_msg, p2, p2_msg, p3, p3_msg
        if quoteservice.service.grouping:
            # grouping means passing 1,2,3 as pax quantity
            p1, p1_msg = cls._quoteservice_prices(
                quoteservice, date_from, date_to, ({0:1, 1:0},), agency)
            p2, p2_msg = cls._quoteservice_prices(
                quoteservice, date_from, date_to, ({0:2, 1:0},), agency)
            p3, p3_msg = cls._quoteservice_prices(
                quoteservice, date_from, date_to, ({0:3, 1:0},), agency)

            p1, p1_msg, p2, p2_msg, p3, p3_msg = cls._adjust_group_free_amounts(
                p1, p2, p3, pax_quantity, service_pax_variant, False)
        else:
            # no grouping means passing total pax quantity
            total_free_cost, total_free_price = cls._find_free_paxes(service_pax_variant)
                
            p1, p1_msg = cls._quoteservice_prices(
                quoteservice, date_from, date_to,
                ({0:pax_quantity, 1:0},),
                agency)
            if p1:
                p1 = cls._round_price(cls._adjust_price(p1, pax_quantity, total_free_price))
            p2, p2_msg, p3, p3_msg = p1, p1_msg, p1, p1_msg
        return p1, p1_msg, p2, p2_msg, p3, p3_msg


    @classmethod
    def _find_quote_package_prices(
            cls, pax_quantity, service, date_from, date_to, agency, service_pax_variant):
        total_free_cost, total_free_price = cls._find_free_paxes(service_pax_variant)
        p1, p1_msg = cls.package_price(
            service, date_from, date_to, ({0:pax_quantity, 1:0},), agency)
        if p1:
            p1 = cls._round_price(cls._adjust_price(p1, pax_quantity, total_free_price))
        p2, p2_msg, p3, p3_msg = p1, p1_msg, p1, p1_msg
        return p1, p1_msg, p2, p2_msg, p3, p3_msg


    @classmethod
    def _adjust_cost(cls, cost, total_paxes, free_paxes):
        return (1.0 - float(free_paxes) / total_paxes) * float(cost) / total_paxes


    @classmethod
    def _adjust_price(cls, price, total_paxes, free_paxes):
        return (1.0 + float(free_paxes) / total_paxes) * float(price) / total_paxes


    @classmethod
    def _round_cost(cls, cost):
        if cost is None:
            return None
        return round(float(cost), 2)


    @classmethod
    def _round_price(cls, price):
        if price is None:
            return None
        return round(0.499999 + float(price))


    @classmethod
    def _get_package_price(
            cls, package, detail, date_from, date_to, adults, children):
        adult_price = 0
        if adults > 0:
            if detail.ad_1_amount is None:
                return None
            adult_price = adults * detail.ad_1_amount
        children_price = 0
        if children > 0:
            if detail.ch_1_ad_1_amount is None:
                return None
            children_price = children * detail.ch_1_ad_1_amount
        price = adult_price + children_price
        if price and price >= 0:
            return price
        return None


    @classmethod
    def sync_quote_paxvariants(cls, quote, user=None):
        if hasattr(quote, "avoid_sync_paxvariants"):
            return 
        # verify on all services if pax variant exists
        quote_services = list(QuoteService.objects.all().filter(
            quote=quote.id))
        quote_pax_variants = list(QuotePaxVariant.objects.all().filter(
            quote=quote.id))

        for quote_pax_variant in quote_pax_variants:
            cls._sync_quote_children_paxvariants(quote_pax_variant, quote_services, user)

    @classmethod
    def sync_quote_children_paxvariants(cls, quote_pax_variant, user=None):
        quote = quote_pax_variant.quote
        # verify on all services if pax variant exists
        quote_services = list(QuoteService.objects.all().filter(
            quote=quote.id))
        cls._sync_quote_children_paxvariants(quote_pax_variant, quote_services, user)


    @classmethod
    def _sync_quote_children_paxvariants(cls, quote_pax_variant, quote_services, user=None):
        for quote_service in quote_services:
            try:
                quote_service_pax_variant, created = QuoteServicePaxVariant.objects.get_or_create(
                    quote_pax_variant_id=quote_pax_variant.id,
                    quote_service_id=quote_service.id,
                )
                if not created and cls.setup_paxvariant_amounts(quote_service_pax_variant):
                    quote_service_pax_variant.code_updated = True
                    quote_service_pax_variant.save()
                cls.update_quote_paxvariant_amounts(quote_service_pax_variant, user)

                if quote_service.service_type == constants.SERVICE_CATEGORY_PACKAGE:
                    # verify on all services if pax variant exists
                    quotepackage_services = list(QuotePackageService.objects.all().filter(
                        quote_package=quote_service.id))

                    for quotepackage_service in quotepackage_services:
                        quotepackage_service_pax_variant, created = QuotePackageServicePaxVariant.objects.update_or_create(
                            quotepackage_pax_variant_id=quote_service_pax_variant.id,
                            quotepackage_service_id=quotepackage_service.id,
                        )
                        if created:
                            cls.update_quotepackage_paxvariant_amounts(
                                quotepackage_service_pax_variant, user)
                        elif cls.setup_paxvariant_amounts(quotepackage_service_pax_variant):
                            quotepackage_service_pax_variant.code_updated = True
                            quotepackage_service_pax_variant.save()

                        cls.update_quote_paxvariant_amounts(quotepackage_service_pax_variant, user)

            except Exception as ex:
                print('booking service 2660 : ' + ex.__str__())


    @classmethod
    def sync_quotepackage_paxvariants(cls, quotepackage):
        cls.sync_quote_paxvariants(quotepackage.quote)

        quotepackage_services = list(QuotePackageService.objects.all().filter(
            quote_package=quotepackage.id))
        quotepackage_paxvariants = list(QuoteServicePaxVariant.objects.all().filter(
            quote_service=quotepackage.id))

        for quotepackage_paxvariant in quotepackage_paxvariants:
            cls._sync_quotepackage_children_paxvariants(
                quotepackage_paxvariant, quotepackage_services)
            cls.update_quotepackage_paxvariant_amounts(quotepackage_paxvariant)
        

    @classmethod
    def sync_quotepackage_children_paxvariants(cls, quotepackage_pax_variant):
        quotepackage = quotepackage_pax_variant.quote_service
        # verify on all services if pax variant exists
        quotepackage_services = list(QuotePackageService.objects.all().filter(
            quote_package=quotepackage.id))
        cls._sync_quotepackage_children_paxvariants(quotepackage_pax_variant, quotepackage_services)


    @classmethod
    def _sync_quotepackage_children_paxvariants(
            cls, quotepackage_pax_variant, quotepackage_services):
        for quotepackage_service in quotepackage_services:
            try:
                quotepackage_service_pax_variant, created = QuotePackageServicePaxVariant.objects.get_or_create(
                    quotepackage_pax_variant_id=quotepackage_pax_variant.id,
                    quotepackage_service_id=quotepackage_service.id,
                )
                if created:
                    cls.update_quotepackage_paxvariant_amounts(quotepackage_service_pax_variant)
                elif cls.setup_paxvariant_amounts(quotepackage_service_pax_variant):
                    quotepackage_service_pax_variant.code_updated = True
                    quotepackage_service_pax_variant.save()
                    cls.update_quotepackage_paxvariant_amounts(quotepackage_service_pax_variant)

            except Exception as ex:
                print('booking service 2707 : ' + ex)


    @classmethod
    def update_quotepackage_paxvariants_amounts(cls, quotepackage_service):
        quote_package = quotepackage_service.quote_package
        quotepackage_paxvariants = list(QuoteServicePaxVariant.objects.all().filter(
            quote_service=quote_package.id))

        for quotepackage_paxvariant in quotepackage_paxvariants:
            try:
                cls.update_quotepackage_paxvariant_amounts(quotepackage_paxvariant)
            except Exception as ex:
                print('booking service 2720 : ' + ex)


    @classmethod
    def _equals_amounts(cls, amount1, amount2):
        if amount1 is None and amount2 is None:
            return True
        if amount1 is None or amount2 is None:
            return False
        return float(amount1) == float(amount2)


    @classmethod
    def update_quoteservice_paxvariants_amounts(cls, quote_service):
        if hasattr(quote_service, "avoid_sync_paxvariants"):
            return

        quote = quote_service.quote
        # find quote pax variants
        quote_pax_variants = list(QuotePaxVariant.objects.all().filter(quote=quote.id))
        # for each quote pax variant get or create
        for quote_pax_variant in quote_pax_variants:
            defaults = cls._calculate_default_paxvariant_amounts(
                quote_service,
                quote_pax_variant)
            try:
                obj = QuoteServicePaxVariant.objects.get(
                    quote_service_id=quote_service.id,
                    quote_pax_variant_id=quote_pax_variant.id)
                if obj.manual_costs and obj.manual_prices:
                    continue
                fields = []
                if not obj.manual_costs:
                    if not cls._equals_amounts(obj.cost_single_amount, defaults['cost_single_amount']):
                        fields.append('cost_single_amount')
                        obj.cost_single_amount = defaults['cost_single_amount']

                    if not cls._equals_amounts(obj.cost_double_amount, defaults['cost_double_amount']):
                        fields.append('cost_double_amount')
                        obj.cost_double_amount = defaults['cost_double_amount']

                    if not cls._equals_amounts(obj.cost_triple_amount, defaults['cost_triple_amount']):
                        fields.append('cost_triple_amount')
                        obj.cost_triple_amount = defaults['cost_triple_amount']

                if not obj.manual_prices:
                    if not cls._equals_amounts(obj.price_single_amount, defaults['price_single_amount']):
                        fields.append('price_single_amount')
                        obj.price_single_amount = defaults['price_single_amount']

                    if not cls._equals_amounts(obj.price_double_amount, defaults['price_double_amount']):
                        fields.append('price_double_amount')
                        obj.price_double_amount = defaults['price_double_amount']

                    if not cls._equals_amounts(obj.price_triple_amount, defaults['price_triple_amount']):
                        fields.append('price_triple_amount')
                        obj.price_triple_amount = defaults['price_triple_amount']

                if fields:
                    obj.save(update_fields=fields)
                    cls.update_quote_paxvariant_amounts(quote_pax_variant)

            except QuoteServicePaxVariant.DoesNotExist:
                new_values = {
                    'quote_service_id': quote_service.id,
                    'quote_pax_variant_id': quote_pax_variant.id}
                new_values.update(defaults)
                obj = QuoteServicePaxVariant(**new_values)
                obj.save()
                cls.update_quote_paxvariant_amounts(quote_pax_variant)


    @classmethod
    def update_quotepackageservice_paxvariants_amounts(cls, quotepackage_service):
        if hasattr(quotepackage_service, "avoid_sync_paxvariants"):
            return

        quote_package = quotepackage_service.quote_package
        # find pax variants
        quotepackage_pax_variants = list(QuoteServicePaxVariant.objects.all().filter(quote_service=quote_package.id))
        # for each quote pax variant get or create
        for quotepackage_pax_variant in quotepackage_pax_variants:
            defaults = cls._calculate_default_paxvariant_amounts(
                quotepackage_service,
                quotepackage_pax_variant)
            try:
                obj = QuotePackageServicePaxVariant.objects.get(
                    quotepackage_service_id=quotepackage_service.id,
                    quotepackage_pax_variant_id=quotepackage_pax_variant.id)
                if obj.manual_costs and obj.manual_prices:
                    continue
                fields = []
                if not obj.manual_costs:
                    if not cls._equals_amounts(obj.cost_single_amount, defaults['cost_single_amount']):
                        fields.append('cost_single_amount')
                        obj.cost_single_amount = defaults['cost_single_amount']

                    if not cls._equals_amounts(obj.cost_double_amount, defaults['cost_double_amount']):
                        fields.append('cost_double_amount')
                        obj.cost_double_amount = defaults['cost_double_amount']

                    if not cls._equals_amounts(obj.cost_triple_amount, defaults['cost_triple_amount']):
                        fields.append('cost_triple_amount')
                        obj.cost_triple_amount = defaults['cost_triple_amount']

                if not obj.manual_prices:
                    if not cls._equals_amounts(obj.price_single_amount, defaults['price_single_amount']):
                        fields.append('price_single_amount')
                        obj.price_single_amount = defaults['price_single_amount']

                    if not cls._equals_amounts(obj.price_double_amount, defaults['price_double_amount']):
                        fields.append('price_double_amount')
                        obj.price_double_amount = defaults['price_double_amount']

                    if not cls._equals_amounts(obj.price_triple_amount, defaults['price_triple_amount']):
                        fields.append('price_triple_amount')
                        obj.price_triple_amount = defaults['price_triple_amount']

                if fields:
                    obj.save(update_fields=fields)
                    cls.update_quotepackage_paxvariant_amounts(quotepackage_pax_variant)

            except QuotePackageServicePaxVariant.DoesNotExist:
                new_values = {
                    'quotepackage_service_id': quotepackage_service.id,
                    'quotepackage_pax_variant_id': quotepackage_pax_variant.id}
                new_values.update(defaults)
                obj = QuotePackageServicePaxVariant(**new_values)
                obj.save()
                cls.update_quotepackage_paxvariant_amounts(quotepackage_pax_variant)
                cls.update_quote_paxvariant_amounts(quotepackage_pax_variant.quote_pax_variant)


    @classmethod
    def _find_paxvariant_amounts(cls, service, pax_variant, for_update=False):
        if isinstance(pax_variant, QuotePaxVariant):
            quote_pax_variant = pax_variant
            service_pax_variant = None
        elif isinstance(pax_variant, QuoteServicePaxVariant):
            quote_pax_variant = pax_variant.quote_pax_variant
            service_pax_variant = pax_variant
        elif isinstance(pax_variant, QuotePackageServicePaxVariant):
            quote_pax_variant = pax_variant.quotepackage_pax_variant.quote_pax_variant
            service_pax_variant = pax_variant.quotepackage_pax_variant
        else:
            return None, "Unknow Pax Variant", None, "Unknow Pax Variant", \
                None, "Unknow Pax Variant", None, "Unknow Pax Variant", \
                None, "Unknow Pax Variant", None, "Unknow Pax Variant"

        if isinstance(service, (QuoteAllotment, QuoteTransfer, QuoteExtra)):
            c1, c1_msg, p1, p1_msg, \
            c2, c2_msg, p2, p2_msg, \
            c3, c3_msg, p3, p3_msg = cls._find_amounts_for_quoteservice(
                quote_pax_variant=quote_pax_variant,
                quoteservice=service,
                agency=service.quote.agency,
                service_pax_variant=service_pax_variant)
        elif isinstance(service, QuotePackage):
            return cls._find_quotepackage_amounts(
                quote_pax_variant=quote_pax_variant,
                package=service,
                agency=service.quote.agency,
                service_pax_variant=service_pax_variant,
                manuals=for_update)
        if isinstance(service, (QuotePackageAllotment, QuotePackageTransfer, QuotePackageExtra)):
            c1, c1_msg, p1, p1_msg, \
            c2, c2_msg, p2, p2_msg, \
            c3, c3_msg, p3, p3_msg = cls._find_amounts_for_quoteservice(
                quote_pax_variant=quote_pax_variant,
                quoteservice=service,
                agency=service.quote_package.quote.agency,
                service_pax_variant=service_pax_variant)
        elif isinstance(service, QuoteService):
            if service.service_type == constants.SERVICE_CATEGORY_ALLOTMENT:
                service = QuoteAllotment.objects.get(pk=service.id)
            elif service.service_type == constants.SERVICE_CATEGORY_TRANSFER:
                service = QuoteTransfer.objects.get(pk=service.id)
            elif service.service_type == constants.SERVICE_CATEGORY_EXTRA:
                service = QuoteExtra.objects.get(pk=service.id)
            elif service.service_type == constants.SERVICE_CATEGORY_PACKAGE:
                service = QuotePackage.objects.get(pk=service.id)
                return cls._find_quotepackage_amounts(
                    quote_pax_variant=quote_pax_variant,
                    package=service,
                    agency=service.quote.agency,
                    service_pax_variant=service_pax_variant,
                    manuals=for_update)
            else:
                return None, "Unknow Service", None, "Unknow Service", \
                    None, "Unknow Service", None, "Unknow Service", \
                    None, "Unknow Service", None, "Unknow Service"
            c1, c1_msg, p1, p1_msg, \
            c2, c2_msg, p2, p2_msg, \
            c3, c3_msg, p3, p3_msg = cls._find_amounts_for_quoteservice(
                quote_pax_variant=quote_pax_variant,
                quoteservice=service,
                agency=service.quote.agency,
                service_pax_variant=service_pax_variant)
        elif isinstance(service, QuotePackageService):
            if service.service_type == constants.SERVICE_CATEGORY_ALLOTMENT:
                service = QuotePackageAllotment.objects.get(pk=service.id)
            elif service.service_type == constants.SERVICE_CATEGORY_TRANSFER:
                service = QuotePackageTransfer.objects.get(pk=service.id)
            elif service.service_type == constants.SERVICE_CATEGORY_EXTRA:
                service = QuotePackageExtra.objects.get(pk=service.id)
            else:
                return None, "Unknow Service", None, "Unknow Service", \
                    None, "Unknow Service", None, "Unknow Service", \
                    None, "Unknow Service", None, "Unknow Service"
            c1, c1_msg, p1, p1_msg, \
            c2, c2_msg, p2, p2_msg, \
            c3, c3_msg, p3, p3_msg = cls._find_amounts_for_quoteservice(
                quote_pax_variant=quote_pax_variant,
                quoteservice=service,
                agency=service.quote_package.quote.agency,
                service_pax_variant=service_pax_variant)
        else:
            return None, "Unknow Service", None, "Unknow Service", \
                None, "Unknow Service", None, "Unknow Service", \
                None, "Unknow Service", None, "Unknow Service"

        if for_update:
            if hasattr(pax_variant, 'manual_costs') and pax_variant.manual_costs:
                c1, c1_msg = pax_variant.cost_single_amount, None
                c2, c2_msg = pax_variant.cost_double_amount, None
                c3, c3_msg = pax_variant.cost_triple_amount, None
            if hasattr(pax_variant, 'manual_prices') and pax_variant.manual_prices:
                p1, p1_msg = pax_variant.price_single_amount, None
                p2, p2_msg = pax_variant.price_double_amount, None
                p3, p3_msg = pax_variant.price_triple_amount, None

        return c1, c1_msg, p1, p1_msg, c2, c2_msg, p2, p2_msg, c3, c3_msg, p3, p3_msg

    @classmethod
    def _calculate_default_paxvariant_amounts(cls, service, pax_variant, for_update=True):

        c1, c1_msg, p1, p1_msg, \
        c2, c2_msg, p2, p2_msg, \
        c3, c3_msg, p3, p3_msg = cls._find_paxvariant_amounts(service, pax_variant, for_update)

        return {
            'cost_single_amount': c1,
            'cost_double_amount': c2,
            'cost_triple_amount': c3,
            'price_single_amount': p1,
            'price_double_amount': p2,
            'price_triple_amount': p3,
        }


    @classmethod
    def update_quotepackage_service_pax_variants_amounts(cls, quotepackage_service):
        quote_package = quotepackage_service.quote_package
        # find quote package pax variants
        quotepackage_pax_variants = list(QuoteServicePaxVariant.objects.all().filter(quote_service=quote_package.id))
        # for each quotepackage pax variant get or create
        for quotepackage_pax_variant in quotepackage_pax_variants:
            defaults = cls._calculate_default_paxvariant_amounts(
                quotepackage_service,
                quotepackage_pax_variant)
            try:
                obj = QuotePackageServicePaxVariant.objects.get(
                    quotepackage_service_id=quotepackage_service.id,
                    quotepackage_pax_variant_id=quotepackage_pax_variant.id)
                if obj.manual_costs and obj.manual_prices:
                    continue
                fields = []
                if not obj.manual_costs:
                    if not cls._equals_amounts(obj.cost_single_amount, defaults['cost_single_amount']):
                        fields.append('cost_single_amount')
                        obj.cost_single_amount = defaults['cost_single_amount']

                    if not cls._equals_amounts(obj.cost_double_amount, defaults['cost_double_amount']):
                        fields.append('cost_double_amount')
                        obj.cost_double_amount = defaults['cost_double_amount']

                    if not cls._equals_amounts(obj.cost_triple_amount, defaults['cost_triple_amount']):
                        fields.append('cost_triple_amount')
                        obj.cost_triple_amount = defaults['cost_triple_amount']

                if not obj.manual_prices:
                    if not cls._equals_amounts(obj.price_single_amount, defaults['price_single_amount']):
                        fields.append('price_single_amount')
                        obj.price_single_amount = defaults['price_single_amount']

                    if not cls._equals_amounts(obj.price_double_amount, defaults['price_double_amount']):
                        fields.append('price_double_amount')
                        obj.price_double_amount = defaults['price_double_amount']

                    if not cls._equals_amounts(obj.price_triple_amount, defaults['price_triple_amount']):
                        fields.append('price_triple_amount')
                        obj.price_triple_amount = defaults['price_triple_amount']

                if fields:
                    obj.save(update_fields=fields)
                    cls.update_quotepackage_paxvariant_amounts(obj)

            except QuotePackageServicePaxVariant.DoesNotExist:
                new_values = {
                    'quotepackage_service_id': quotepackage_service.id,
                    'quotepackage_pax_variant_id': quotepackage_pax_variant.id}
                new_values.update(defaults)
                obj = QuotePackageServicePaxVariant(**new_values)
                obj.save()
                cls.update_quotepackage_paxvariant_amounts(obj)


    @classmethod
    def update_quote_paxvariants_amounts(cls, quote_or_service):
        if isinstance(quote_or_service, Quote):
            quote = quote_or_service
        else:
            quote = quote_or_service.quote
        quote_pax_variants = list(
            QuotePaxVariant.objects.all().filter(quote=quote.id))

        for quote_pax_variant in quote_pax_variants:
            cls.update_quote_paxvariant_amounts(quote_pax_variant)

    @classmethod
    def update_quote_paxvariant_amounts(cls, pax_variant, user=None):
        if isinstance(pax_variant, QuotePackageServicePaxVariant):
            quote_pax_variant = pax_variant.quotepackage_pax_variant.quote_pax_variant
        elif isinstance(pax_variant, QuoteServicePaxVariant):
            quote_pax_variant = pax_variant.quote_pax_variant
        else:
            quote_pax_variant = pax_variant

        quoteservice_pax_variants = list(
            QuoteServicePaxVariant.objects.all().filter(
                quote_pax_variant=quote_pax_variant.id).exclude(
                    quote_service__status=constants.SERVICE_STATUS_CANCELLED))

        c1, c2, c3, p1, p2, p3 = cls._totalize_pax_variants(quoteservice_pax_variants)

        fields = cls._build_pax_variant_fields(quote_pax_variant, c1, c2, c3, p1, p2, p3)
        if fields:
            quote_pax_variant.code_updated = True
            quote_pax_variant.save(update_fields=fields)


    @classmethod
    def _apply_percent(cls, amount, percent):
        return float(amount) * (1.0 + float(percent) / 100.0)

    @classmethod
    def update_quotepackage_paxvariants_amounts(cls, service):
        quote_package = service.quote_package
        quotepackage_pax_variants = list(
            QuoteServicePaxVariant.objects.all().filter(quote_service=quote_package.id))

        for quotepackage_pax_variant in quotepackage_pax_variants:
            cls.update_quotepackage_paxvariant_amounts(quotepackage_pax_variant)


    @classmethod
    def update_quotepackage_paxvariant_amounts(cls, pax_variant):
        if isinstance(pax_variant, QuotePackageServicePaxVariant):
            quotepackage_pax_variant = pax_variant.quotepackage_pax_variant
        else:
            quotepackage_pax_variant = pax_variant

        c1, c1_msg, p1, p1_msg, \
        c2, c2_msg, p2, p2_msg, \
        c3, c3_msg, p3, p3_msg = cls._find_quotepackage_amounts(
            quote_pax_variant=quotepackage_pax_variant.quote_pax_variant,
            package=quotepackage_pax_variant.quote_service,
            agency=quotepackage_pax_variant.quote_pax_variant.quote.agency,
            service_pax_variant=quotepackage_pax_variant,
            manuals=True)

        fields = cls._build_pax_variant_fields(quotepackage_pax_variant, c1, c2, c3, p1, p2, p3)
        if fields:
            quotepackage_pax_variant.code_updated = True
            quotepackage_pax_variant.save(update_fields=fields)
            cls.update_quote_paxvariant_amounts(quotepackage_pax_variant)



    @classmethod
    def _totalize_pax_variants(cls, pax_variants):
        if pax_variants:
            c1, c2, c3, p1, p2, p3 = 0, 0, 0, 0, 0, 0
            for pax_variant in pax_variants:
                c1 = cls.totalize(c1, pax_variant.cost_single_amount)
                c2 = cls.totalize(c2, pax_variant.cost_double_amount)
                c3 = cls.totalize(c3, pax_variant.cost_triple_amount)
                p1 = cls.totalize(p1, pax_variant.price_single_amount)
                p2 = cls.totalize(p2, pax_variant.price_double_amount)
                p3 = cls.totalize(p3, pax_variant.price_triple_amount)
            return  cls._round_cost(c1), cls._round_cost(c2), cls._round_cost(c3), \
                cls._round_price(p1), cls._round_price(p2), cls._round_price(p3)
        return None, None, None, None, None, None

    @classmethod
    def _build_pax_variant_fields(cls, pax_variant, c1, c2, c3, p1, p2, p3):
        fields = []
        if not cls._equals_amounts(pax_variant.cost_single_amount, c1):
            fields.append('cost_single_amount')
            pax_variant.cost_single_amount = c1

        if not cls._equals_amounts(pax_variant.cost_double_amount, c2):
            fields.append('cost_double_amount')
            pax_variant.cost_double_amount = c2

        if not cls._equals_amounts(pax_variant.cost_triple_amount, c3):
            fields.append('cost_triple_amount')
            pax_variant.cost_triple_amount = c3

        extra = 0.0
        if isinstance(pax_variant, QuotePaxVariant):
            extra = cls._round_price(pax_variant.extra_single_amount)
        if p1 is None:
            if not pax_variant.price_single_amount is None:
                fields.append('price_single_amount')
                pax_variant.price_single_amount = None
        else:
            if not cls._equals_amounts(pax_variant.price_single_amount, p1 + extra):
                fields.append('price_single_amount')
                pax_variant.price_single_amount = p1 + extra

        if isinstance(pax_variant, QuotePaxVariant):
            extra = cls._round_price(float(pax_variant.extra_double_amount))
        if p2 is None:
            if not pax_variant.price_double_amount is None:
                fields.append('price_double_amount')
                pax_variant.price_double_amount = None
        else:
            if not cls._equals_amounts(pax_variant.price_double_amount, p2 + extra):
                fields.append('price_double_amount')
                pax_variant.price_double_amount = p2 + extra

        if isinstance(pax_variant, QuotePaxVariant):
            extra = cls._round_price(float(pax_variant.extra_triple_amount))
        if p3 is None:
            if not pax_variant.price_triple_amount is None:
                fields.append('price_triple_amount')
                pax_variant.price_triple_amount = None
        else:
            if not cls._equals_amounts(pax_variant.price_triple_amount, p3 + extra):
                fields.append('price_triple_amount')
                pax_variant.price_triple_amount = p3 + extra
        return fields


    @classmethod
    def totalize(cls, total, increment):
        if total is None or increment is None:
            return None
        return total + increment


    @classmethod
    def update_quotepackage(cls, quotepackage_service):

        quote_package = quotepackage_service.quote_package

        date_from = None
        date_to = None
        for service in quote_package.quotepackage_services.all():
            if not service.status is constants.SERVICE_STATUS_CANCELLED:
                # date_from
                if service.datetime_from is not None:
                    if date_from is None or (date_from > service.datetime_from):
                        date_from = service.datetime_from
                # date_to
                if service.datetime_to is not None:
                    if date_to is None or (date_to < service.datetime_to):
                        date_to = service.datetime_to
        fields = []
        if quote_package.datetime_from != date_from:
            fields.append('datetime_from')
            quote_package.datetime_from = date_from
        if quote_package.datetime_to != date_to:
            fields.append('datetime_to')
            quote_package.datetime_to = date_to
        if fields:
            quote_package.code_updated = True
            quote_package.save(update_fields=fields)


    @classmethod
    def setup_paxvariant_amounts(cls, pax_variant):
        if pax_variant.manual_costs is None:
            pax_variant.manual_costs = False
        if pax_variant.manual_prices is None:
           pax_variant.manual_prices = False

        if pax_variant.manual_costs and pax_variant.manual_prices:
            return False

        if isinstance(pax_variant, QuoteServicePaxVariant):
            service = pax_variant.quote_service
        elif isinstance(pax_variant, QuotePackageServicePaxVariant):
            service = pax_variant.quotepackage_service
        else:
            return False

        c1, c1_msg, p1, p1_msg, \
        c2, c2_msg, p2, p2_msg, \
        c3, c3_msg, p3, p3_msg = cls._find_paxvariant_amounts(
            service,
            pax_variant,
            True)

        modified = False

        if not pax_variant.manual_costs:

            if not cls._equals_amounts(pax_variant.cost_single_amount, c1):
                modified = True
                pax_variant.cost_single_amount = c1

            if not cls._equals_amounts(pax_variant.cost_double_amount, c2):
                modified = True
                pax_variant.cost_double_amount = c2

            if not cls._equals_amounts(pax_variant.cost_triple_amount, c3):
                modified = True
                pax_variant.cost_triple_amount = c3

        if not pax_variant.manual_prices:

            if not cls._equals_amounts(pax_variant.price_single_amount, p1):
                modified = True
                pax_variant.price_single_amount = p1

            if not cls._equals_amounts(pax_variant.price_double_amount, p2):
                modified = True
                pax_variant.price_double_amount = p2

            if not cls._equals_amounts(pax_variant.price_triple_amount, p3):
                modified = True
                pax_variant.price_triple_amount = p3

        return modified


    @classmethod
    def find_booking_amounts(cls, booking, pax_list):
        agency = booking.agency

        allotment_list = list(BookingAllotment.objects.filter(
            booking=booking.id).exclude(
                status=constants.SERVICE_STATUS_CANCELLED
            ).all())
        transfer_list = list(BookingTransfer.objects.filter(
            booking=booking.id).exclude(
                status=constants.SERVICE_STATUS_CANCELLED
            ).all())
        extra_list = list(BookingExtra.objects.filter(
            booking=booking.id).exclude(
                status=constants.SERVICE_STATUS_CANCELLED
            ).all())
        package_list = list(BookingPackage.objects.filter(
            booking=booking.id).exclude(
                status=constants.SERVICE_STATUS_CANCELLED
            ).all())

        if (
                (not allotment_list) and
                (not transfer_list) and
                (not extra_list) and
                (not package_list)):
            return None, 'Services Missing', None, 'Services Missing'

        cost, cost_msg, price, price_msg = 0, '', 0, ''

        if allotment_list:
            for allotment in allotment_list:
                if allotment.status == constants.SERVICE_STATUS_CANCELLED:
                    continue
                if not hasattr(allotment, 'service'):
                    return None, "Missing Allotment Service", None, "Missing Allotment Service"
                c, c_msg, p, p_msg = cls._find_bookingservice_update_amounts(
                    bookingservice=allotment, agency=booking.agency)
                cost, cost_msg = cls._merge_costs(cost, cost_msg, c, c_msg)
                price, price_msg = cls._merge_prices(price, price_msg, p, p_msg, )
                if cost is None and price is None:
                    return cost, cost_msg, price, price_msg

        if transfer_list:
            for transfer in transfer_list:
                if transfer.status == constants.SERVICE_STATUS_CANCELLED:
                    continue
                if not hasattr(transfer, 'service'):
                    return None, "Missing Transfer Service", None, "Missing Transfer Service"
                c, c_msg, p, p_msg = cls._find_bookingservice_update_amounts(
                    bookingservice=transfer, agency=booking.agency)
                cost, cost_msg = cls._merge_costs(cost, cost_msg, c, c_msg)
                price, price_msg = cls._merge_prices(price, price_msg, p, p_msg, )
                if cost is None and price is None:
                    return cost, cost_msg, price, price_msg

        if extra_list:
            for extra in extra_list:
                if extra.status == constants.SERVICE_STATUS_CANCELLED:
                    continue
                if not hasattr(extra, 'service'):
                    return None, "Missing Extra Service", None, "Missing Extra Service"
                c, c_msg, p, p_msg = cls._find_bookingservice_update_amounts(
                    bookingservice=extra, agency=booking.agency)
                cost, cost_msg = cls._merge_costs(cost, cost_msg, c, c_msg)
                price, price_msg = cls._merge_prices(price, price_msg, p, p_msg, )
                if cost is None and price is None:
                    return cost, cost_msg, price, price_msg

        if package_list:
            for package in package_list:
                if package.status == constants.SERVICE_STATUS_CANCELLED:
                    continue
                if not hasattr(package, 'service'):
                    return None, "Missing Extra Service", None, "Missing Extra Service"
                c, c_msg, p, p_msg = cls._find_bookingservice_update_amounts(
                    bookingservice=package, agency=booking.agency)
                cost, cost_msg = cls._merge_costs(cost, cost_msg, c, c_msg)
                price, price_msg = cls._merge_prices(price, price_msg, p, p_msg, )
                if cost is None and price is None:
                    return cost, cost_msg, price, price_msg

        if booking.is_package_price:
            price, price_msg = cls._find_booking_package_price(booking, pax_list)

        return cost, cost_msg, price, price_msg


    @classmethod
    def _find_bookingpackageservice_provider(cls, bookingpackageservice):
        service_provider = bookingpackageservice.booking_package.provider
        if service_provider is None:
            return bookingpackageservice.provider
        return service_provider


    @classmethod
    def find_bookingservice_amounts(cls, bookingservice, pax_list=None, agency=None, manuals=False):
        if isinstance(bookingservice, BookingPackage):
            return cls.find_bookingpackage_update_amounts(bookingservice, agency, manuals)

        if not pax_list:
            pax_list = cls._find_bookingservice_pax_list(bookingservice)

        cost_groups = BookingServices.find_bookingservice_paxes_groups(
            pax_list, bookingservice.service, True)
        price_groups = BookingServices.find_bookingservice_paxes_groups(
            pax_list, bookingservice.service, False)
        return cls._find_bookingservice_amounts(
            bookingservice, cost_groups, price_groups, agency)


    @classmethod
    def find_bookingservice_cost(cls, bookingservice, pax_list=None):
        if isinstance(bookingservice, BookingPackage):
            return cls.find_bookingpackage_update_cost(bookingservice)

        if not pax_list:
            pax_list = cls._find_bookingservice_pax_list(bookingservice)

        cost_groups = BookingServices.find_bookingservice_paxes_groups(
            pax_list, bookingservice.service, True)
        return cls._find_bookingservice_cost(bookingservice, cost_groups)


    @classmethod
    def find_bookingservice_update_cost(cls, bookingservice, pax_list=None):
        if isinstance(bookingservice, BookingPackage):
            return cls.find_bookingpackage_update_cost(bookingservice)

        if not pax_list:
            pax_list = cls._find_bookingservice_pax_list(bookingservice)

        cost_groups = BookingServices.find_bookingservice_paxes_groups(
            pax_list, bookingservice.service, True)
        return cls._find_bookingservice_update_cost(bookingservice, cost_groups)


    @classmethod
    def find_bookingservice_price(cls, bookingservice, pax_list=None, agency=None):
        if isinstance(bookingservice, BookingPackage):
            return cls.find_bookingpackage_update_price(bookingservice, agency)

        if not pax_list:
            pax_list = cls._find_bookingservice_pax_list(bookingservice)

        price_groups = BookingServices.find_bookingservice_paxes_groups(
            pax_list, bookingservice.service, False)
        return cls._find_bookingservice_price(bookingservice, price_groups, agency)


    @classmethod
    def find_bookingservice_update_price(cls, bookingservice, pax_list=None, agency=None):
        if isinstance(bookingservice, BookingPackage):
            return cls.find_bookingpackage_update_price(bookingservice, agency)

        if not pax_list:
            pax_list = cls._find_bookingservice_pax_list(bookingservice)

        price_groups = BookingServices.find_bookingservice_paxes_groups(
            pax_list, bookingservice.service, False)
        return cls._find_bookingservice_update_price(bookingservice, price_groups, agency)


    @classmethod
    def _find_bookingservice_amounts(
            cls, bookingservice, cost_groups, price_groups, agency=None):
        if isinstance(bookingservice, BookingAllotment):
            if not agency:
                agency = bookingservice.booking.agency
            cost, cost_msg, price, price_msg = ConfigServices.allotment_amounts(
                bookingservice.service_id,
                bookingservice.datetime_from, bookingservice.datetime_to,
                cost_groups, price_groups,
                bookingservice.provider, agency,
                bookingservice.board_type, bookingservice.room_type_id,
                bookingservice.service_addon_id)
        elif isinstance(bookingservice, BookingTransfer):
            if not agency:
                agency = bookingservice.booking.agency
            cost, cost_msg, price, price_msg = ConfigServices.transfer_amounts(
                bookingservice.service_id,
                bookingservice.datetime_from, bookingservice.datetime_to,
                cost_groups, price_groups,
                bookingservice.provider, agency,
                bookingservice.location_from_id, bookingservice.location_to_id,
                bookingservice.service_addon_id,
                bookingservice.quantity)
        elif isinstance(bookingservice, BookingExtra):
            if not agency:
                agency = bookingservice.booking.agency
            cost, cost_msg, price, price_msg = ConfigServices.extra_amounts(
                bookingservice.service_id,
                bookingservice.datetime_from, bookingservice.datetime_to,
                cost_groups, price_groups,
                bookingservice.provider, agency,
                bookingservice.service_addon_id, bookingservice.quantity, bookingservice.parameter)
        elif isinstance(bookingservice, BookingPackageAllotment):
            if not agency:
                agency = bookingservice.booking_package.booking.agency
            service_provider = cls._find_bookingpackageservice_provider(bookingservice)
            cost, cost_msg, price, price_msg = ConfigServices.allotment_amounts(
                bookingservice.service,
                bookingservice.datetime_from, bookingservice.datetime_to,
                cost_groups, price_groups,
                service_provider, agency,
                bookingservice.board_type, bookingservice.room_type_id,
                bookingservice.service_addon_id)
        elif isinstance(bookingservice, BookingPackageTransfer):
            if not agency:
                agency = bookingservice.booking_package.booking.agency
            service_provider = cls._find_bookingpackageservice_provider(bookingservice)
            cost, cost_msg, price, price_msg = ConfigServices.transfer_amounts(
                bookingservice.service,
                bookingservice.datetime_from, bookingservice.datetime_to,
                cost_groups, price_groups,
                service_provider, agency,
                bookingservice.location_from_id, bookingservice.location_to_id,
                bookingservice.service_addon_id,
                bookingservice.quantity)
        elif isinstance(bookingservice, BookingPackageExtra):
            if not agency:
                agency = bookingservice.booking_package.booking.agency
            service_provider = cls._find_bookingpackageservice_provider(bookingservice)
            cost, cost_msg, price, price_msg = ConfigServices.extra_amounts(
                bookingservice.service,
                bookingservice.datetime_from, bookingservice.datetime_to,
                cost_groups, price_groups,
                service_provider, agency,
                bookingservice.service_addon_id, bookingservice.quantity, bookingservice.parameter)
        elif isinstance(bookingservice, BookingPackage):
            if not agency:
                agency = bookingservice.booking.agency
            cost, cost_msg, price, price_msg = cls._bookingpackage_amounts(
                bookingservice, cost_groups, price_groups, agency)
        return cost, cost_msg, price, price_msg


    @classmethod
    def _find_bookingservice_cost(cls, bookingservice, cost_groups):
        if isinstance(bookingservice, BookingAllotment):
            cost, cost_msg = ConfigServices.allotment_costs(
                bookingservice.service_id,
                bookingservice.datetime_from, bookingservice.datetime_to,
                cost_groups,
                bookingservice.provider,
                bookingservice.board_type, bookingservice.room_type_id,
                bookingservice.service_addon_id)
        elif isinstance(bookingservice, BookingTransfer):
            cost, cost_msg = ConfigServices.transfer_costs(
                bookingservice.service_id,
                bookingservice.datetime_from, bookingservice.datetime_to,
                cost_groups,
                bookingservice.provider,
                bookingservice.location_from_id, bookingservice.location_to_id,
                bookingservice.service_addon_id,
                bookingservice.quantity)
        elif isinstance(bookingservice, BookingExtra):
            cost, cost_msg = ConfigServices.extra_costs(
                bookingservice.service_id,
                bookingservice.datetime_from, bookingservice.datetime_to,
                cost_groups,
                bookingservice.provider,
                bookingservice.service_addon_id, bookingservice.quantity, bookingservice.parameter)
        elif isinstance(bookingservice, BookingPackageAllotment):
            service_provider = cls._find_bookingpackageservice_provider(bookingservice)
            cost, cost_msg = ConfigServices.allotment_costs(
                bookingservice.service,
                bookingservice.datetime_from, bookingservice.datetime_to,
                cost_groups,
                service_provider,
                bookingservice.board_type, bookingservice.room_type_id,
                bookingservice.service_addon_id)
        elif isinstance(bookingservice, BookingPackageTransfer):
            service_provider = cls._find_bookingpackageservice_provider(bookingservice)
            cost, cost_msg = ConfigServices.transfer_costs(
                bookingservice.service,
                bookingservice.datetime_from, bookingservice.datetime_to,
                cost_groups,
                service_provider,
                bookingservice.location_from_id, bookingservice.location_to_id,
                bookingservice.service_addon_id,
                bookingservice.quantity)
        elif isinstance(bookingservice, BookingPackageExtra):
            service_provider = cls._find_bookingpackageservice_provider(bookingservice)
            cost, cost_msg = ConfigServices.extra_costs(
                bookingservice.service,
                bookingservice.datetime_from, bookingservice.datetime_to,
                cost_groups,
                service_provider,
                bookingservice.service_addon_id, bookingservice.quantity, bookingservice.parameter)
        elif isinstance(bookingservice, BookingPackage):
            cost, cost_msg = cls._bookingpackage_costs(bookingservice, pax_list)
        return cost, cost_msg


    @classmethod
    def _find_bookingservice_price(cls, bookingservice, price_groups, agency=None):
        if isinstance(bookingservice, BookingAllotment):
            if not agency:
                agency = bookingservice.booking.agency
            price, price_msg = ConfigServices.allotment_prices(
                bookingservice.service_id,
                bookingservice.datetime_from, bookingservice.datetime_to,
                price_groups,
                agency,
                bookingservice.board_type, bookingservice.room_type_id,
                bookingservice.service_addon_id)
        elif isinstance(bookingservice, BookingTransfer):
            if not agency:
                agency = bookingservice.booking.agency
            price, price_msg = ConfigServices.transfer_prices(
                bookingservice.service_id,
                bookingservice.datetime_from, bookingservice.datetime_to,
                price_groups,
                agency,
                bookingservice.location_from_id, bookingservice.location_to_id,
                bookingservice.service_addon_id,
                bookingservice.quantity)
        elif isinstance(bookingservice, BookingExtra):
            if not agency:
                agency = bookingservice.booking.agency
            price, price_msg = ConfigServices.extra_prices(
                bookingservice.service_id,
                bookingservice.datetime_from, bookingservice.datetime_to,
                price_groups,
                agency,
                bookingservice.service_addon_id, bookingservice.quantity, bookingservice.parameter)
        elif isinstance(bookingservice, BookingPackageAllotment):
            if not agency:
                agency = bookingservice.booking_package.booking.agency
            price, price_msg = ConfigServices.allotment_prices(
                bookingservice.service,
                bookingservice.datetime_from, bookingservice.datetime_to,
                price_groups,
                agency,
                bookingservice.board_type, bookingservice.room_type_id,
                bookingservice.service_addon_id)
        elif isinstance(bookingservice, BookingPackageTransfer):
            if not agency:
                agency = bookingservice.booking_package.booking.agency
            price, price_msg = ConfigServices.transfer_prices(
                bookingservice.service,
                bookingservice.datetime_from, bookingservice.datetime_to,
                price_groups,
                agency,
                bookingservice.location_from_id, bookingservice.location_to_id,
                bookingservice.service_addon_id,
                bookingservice.quantity)
        elif isinstance(bookingservice, BookingPackageExtra):
            if not agency:
                agency = bookingservice.booking_package.booking.agency
            price, price_msg = ConfigServices.extra_prices(
                bookingservice.service,
                bookingservice.datetime_from, bookingservice.datetime_to,
                price_groups,
                agency,
                bookingservice.service_addon_id, bookingservice.quantity, bookingservice.parameter)
        elif isinstance(bookingservice, BookingPackage):
            if not agency:
                agency = bookingservice.booking.agency
            price, price_msg = cls._bookingpackage_prices(bookingservice, pax_list, agency)
        return price, price_msg


    @classmethod
    def _find_booking_service(cls, bookingservice):
        if isinstance(bookingservice, BookingService):
            if bookingservice.service_type == constants.SERVICE_CATEGORY_ALLOTMENT:
                bookingservice = cls._find_bookingservice(bookingservice, BookingAllotment.objects)
            elif bookingservice.service_type == constants.SERVICE_CATEGORY_TRANSFER:
                bookingservice = cls._find_bookingservice(bookingservice, BookingTransfer.objects)
            elif bookingservice.service_type == constants.SERVICE_CATEGORY_EXTRA:
                bookingservice = cls._find_bookingservice(bookingservice, BookingExtra.objects)
            elif bookingservice.service_type == constants.SERVICE_CATEGORY_PACKAGE:
                bookingservice = cls._find_bookingservice(bookingservice, BookingPackage.objects)

        if isinstance(bookingservice, BookingPackageService):
            if bookingservice.service_type == constants.SERVICE_CATEGORY_ALLOTMENT:
                bookingservice = cls._find_bookingservice(
                    bookingservice, BookingPackageAllotment.objects)
            elif bookingservice.service_type == constants.SERVICE_CATEGORY_TRANSFER:
                bookingservice = cls._find_bookingservice(
                    bookingservice, BookingPackageTransfer.objects)
            elif bookingservice.service_type == constants.SERVICE_CATEGORY_EXTRA:
                bookingservice = cls._find_bookingservice(
                    bookingservice, BookingPackageExtra.objects)

        return bookingservice


    @classmethod
    def _find_bookingservice_update_amounts(cls, bookingservice, pax_list=None, agency=None):

        bookingservice = cls._find_booking_service(bookingservice)

        if not bookingservice:
            return None, "Service Not Found", None, "Service Not Found"

        if isinstance(bookingservice, BookingPackage):
            return cls.find_bookingpackage_update_amounts(bookingservice, pax_list, agency, True)

        if bookingservice.manual_cost is None:
            bookingservice.manual_cost = False
        if bookingservice.manual_price is None:
            bookingservice.manual_price = False

        if bookingservice.manual_cost and bookingservice.manual_price:
            cost = bookingservice.cost_amount
            price = bookingservice.price_amount
            cost_msg, price_msg = None, None
            if cost is None:
                cost_msg = "Missing Manual Cost"
            if price is None:
                price_msg = "Missing Manual Price"
            return cost, cost_msg, price, price_msg

        if not pax_list:
            pax_list = cls._find_bookingservice_pax_list(bookingservice)

        if bookingservice.manual_cost:
            cost_msg = None
            cost = bookingservice.cost_amount
            if cost is None:
                cost_msg = "Missing Manual Cost"
            price, price_msg = cls.find_bookingservice_price(bookingservice, pax_list, agency)
        elif bookingservice.manual_price:
            cost, cost_msg = cls.find_bookingservice_cost(bookingservice, pax_list)
            price_msg = None
            price = bookingservice.price_amount
            if price is None:
                price_msg = "Missing Manual Price"
        else:
            cost, cost_msg, price, price_msg = cls.find_bookingservice_amounts(
                bookingservice, pax_list, agency)
        return cost, cost_msg, price, price_msg


    @classmethod
    def find_bookingservice_update_cost(cls, bookingservice, pax_list=None):

        bookingservice = cls._find_booking_service(bookingservice)

        if not bookingservice:
            return None, "Service Not Found"

        if isinstance(bookingservice, BookingPackage):
            return cls.find_bookingpackage_update_cost(bookingservice, pax_list)

        if bookingservice.manual_cost is None:
            bookingservice.manual_cost = False

        if bookingservice.manual_cost:
            cost = bookingservice.cost_amount
            cost_msg = None
            if cost is None:
                cost_msg = "Missing Manual Cost"
            return cost, cost_msg

        if not pax_list:
            pax_list = cls._find_bookingservice_pax_list(bookingservice)

        cost, cost_msg = cls.find_bookingservice_cost(bookingservice, pax_list)
        return cost, cost_msg


    @classmethod
    def find_bookingservice_update_price(cls, bookingservice, pax_list=None, agency=None):

        bookingservice = cls._find_booking_service(bookingservice)

        if not bookingservice:
            return None, "Service Not Found"

        if isinstance(bookingservice, BookingPackage):
            return cls.find_bookingpackage_update_price(bookingservice, pax_list, agency)

        if bookingservice.manual_price is None:
            bookingservice.manual_price = False

        if bookingservice.manual_price:
            price = bookingservice.price_amount
            price_msg = None
            if price is None:
                price_msg = "Missing Manual Price"
            return price, price_msg

        if not pax_list:
            pax_list = cls._find_bookingservice_pax_list(bookingservice)

        price, price_msg = cls.find_bookingservice_price(bookingservice, pax_list, agency)
        return price, price_msg


    @classmethod
    def setup_bookingservice_amounts_from_quote(cls, bookingservice, service_paxvariant, pax_list):
        groups = cls._find_groups(pax_list)
        cost, price = 0, 0
        for pax_qtty in groups:
            if pax_qtty == 1:
                if service_paxvariant.cost_single_amount is None:
                    cost = None
                if not cost is None:
                    cost, cost_msg = cls._merge_costs(
                        cost, None, service_paxvariant.cost_single_amount, None)
                if service_paxvariant.price_single_amount is None:
                    price = None
                if not price is None:
                    price, price_msg = cls._merge_prices(
                        price, None, service_paxvariant.price_single_amount, None)
            elif pax_qtty == 2:
                if service_paxvariant.cost_double_amount is None:
                    cost = None
                if not cost is None:
                    cost, cost_msg = cls._merge_costs(
                        cost, None, 2 * service_paxvariant.cost_double_amount, None)
                if service_paxvariant.price_double_amount is None:
                    price = None
                if not price is None:
                    price, price_msg = cls._merge_prices(
                        price, None, 2 * service_paxvariant.price_double_amount, None)
            elif pax_qtty == 3:
                if service_paxvariant.cost_triple_amount is None:
                    cost = None
                if not cost is None:
                    cost, cost_msg = cls._merge_costs(
                        cost, None, 3 * service_paxvariant.cost_triple_amount, None)
                if service_paxvariant.price_triple_amount is None:
                    price = None
                if not price is None:
                    price, price_msg = cls._merge_prices(
                        price, None, 2 * service_paxvariant.price_triple_amount, None)
            else:
                cost, price = None, None
        bookingservice.cost_amount = cost
        bookingservice.price_amount = price
        bookingservice.manual_cost = service_paxvariant.manual_costs
        bookingservice.manual_price = service_paxvariant.manual_prices


    @classmethod
    def setup_bookingservice_amounts(cls, bookingservice, pax_list=None, agency=None):
        if hasattr(bookingservice, 'avoid_update'):
            return
        if bookingservice.manual_cost is None:
            bookingservice.manual_cost = False
        if bookingservice.manual_price is None:
            bookingservice.manual_price = False

        if bookingservice.manual_cost and bookingservice.manual_price:
            return False

        if not pax_list:
            pax_list = cls._find_bookingservice_pax_list(bookingservice)

        modified = False

        if not bookingservice.manual_cost:
            if not bookingservice.manual_price:
                cost, cost_msg, price, price_msg = cls.find_bookingservice_amounts(
                    bookingservice, pax_list)
                if not cls._equals_amounts(bookingservice.cost_amount, cost):
                    modified = True
                    bookingservice.cost_amount = cost
                if not cls._equals_amounts(bookingservice.price_amount, price):
                    modified = True
                    bookingservice.price_amount = price
            else:
                cost, cost_msg = cls.find_bookingservice_cost(
                    bookingservice, pax_list)
                if not cls._equals_amounts(bookingservice.cost_amount, cost):
                    modified = True
                    bookingservice.cost_amount = cost
        else:
            price, price_msg = cls.find_bookingservice_price(
                bookingservice, pax_list)
            if not cls._equals_amounts(bookingservice.price_amount, price):
                modified = True
                bookingservice.price_amount = price

        return modified


    # removed automatic update from booking to services
    # @classmethod
    # def update_bookingservices_amounts(cls, obj):
    #     if isinstance(obj, BookingPax):
    #         booking = obj.booking
    #     else:
    #         booking = obj
    #     allotment_list = list(BookingAllotment.objects.filter(
    #         booking=booking.id).exclude(status=constants.SERVICE_STATUS_CANCELLED).all())
    #     transfer_list = list(BookingTransfer.objects.filter(
    #         booking=booking.id).exclude(status=constants.SERVICE_STATUS_CANCELLED).all())
    #     extra_list = list(BookingExtra.objects.filter(
    #         booking=booking.id).exclude(status=constants.SERVICE_STATUS_CANCELLED).all())
    #     package_list = list(BookingPackage.objects.filter(
    #         booking=booking.id).exclude(status=constants.SERVICE_STATUS_CANCELLED).all())
    #     if allotment_list:
    #         for allotment in allotment_list:
    #             cls.update_bookingservice_amounts(allotment)
    #     if transfer_list:
    #         for transfer in transfer_list:
    #             cls.update_bookingservice_amounts(transfer)
    #     if extra_list:
    #         for extra in extra_list:
    #             cls.update_bookingservice_amounts(extra)
    #     if package_list:
    #         for package in package_list:
    #             cls.update_bookingservice_amounts(package)


    @classmethod
    def update_bookingservice_amounts(cls, booking_service):
        if hasattr(booking_service, 'avoid_update'):
            return
        if isinstance(booking_service, (
                BookingAllotment, BookingTransfer, BookingExtra,
                BookingPackageAllotment, BookingPackageTransfer, BookingPackageExtra)):
            cost, cost_msg, price, price_msg = cls._find_bookingservice_update_amounts(
                booking_service)
            cls._save_booking_service_amounts(booking_service, cost, price)
        elif isinstance(booking_service, BookingPackage):
            cls.update_bookingpackage_amounts(booking_service)
        elif isinstance(booking_service, BookingService):
            if booking_service.service_type == constants.SERVICE_CATEGORY_ALLOTMENT:
                bookingallotment = cls._find_bookingservice(
                    booking_service, BookingAllotment.objects)
                if not bookingallotment:
                    return
                cost, cost_msg, price, price_msg = cls._find_bookingservice_update_amounts(
                    bookingallotment)
                cls._save_booking_service_amounts(bookingallotment, cost, price)
                booking_service.cost_amount = bookingallotment.cost_amount
                booking_service.price_amount = bookingallotment.price_amount
            elif booking_service.service_type == constants.SERVICE_CATEGORY_TRANSFER:
                bookingtransfer = cls._find_bookingservice(
                    booking_service, BookingTransfer.objects)
                if not bookingtransfer:
                    return
                cost, cost_msg, price, price_msg = cls._find_bookingservice_update_amounts(
                    bookingtransfer)
                cls._save_booking_service_amounts(bookingtransfer, cost, price)
                booking_service.cost_amount = bookingtransfer.cost_amount
                booking_service.price_amount = bookingtransfer.price_amount
            elif booking_service.service_type == constants.SERVICE_CATEGORY_EXTRA:
                bookingextra = cls._find_bookingservice(booking_service, BookingExtra.objects)
                if not bookingextra:
                    return
                cost, cost_msg, price, price_msg = cls._find_bookingservice_update_amounts(
                    bookingextra)
                cls._save_booking_service_amounts(bookingextra, cost, price)
                booking_service.cost_amount = bookingextra.cost_amount
                booking_service.price_amount = bookingextra.price_amount
            elif booking_service.service_type == constants.SERVICE_CATEGORY_PACKAGE:
                bookingpackage = cls._find_bookingservice(booking_service, BookingPackage.objects)
                if not bookingpackage:
                    return
                cls.update_bookingpackage_amounts(bookingpackage, True)
                booking_service.cost_amount = bookingpackage.cost_amount
                booking_service.price_amount = bookingpackage.price_amount
        elif isinstance(booking_service, BookingPackageService):
            if booking_service.service_type == constants.SERVICE_CATEGORY_ALLOTMENT:
                bookingpackageallotment = cls._find_bookingservice(
                    booking_service, BookingPackageAllotment.objects)
                if not bookingpackageallotment:
                    return
                cost, cost_msg, price, price_msg = cls._find_bookingservice_update_amounts(
                    bookingpackageallotment)
                cls._save_booking_service_amounts(bookingpackageallotment, cost, price)
                booking_service.cost_amount = bookingpackageallotment.cost_amount
                booking_service.price_amount = bookingpackageallotment.price_amount
            elif booking_service.service_type == constants.SERVICE_CATEGORY_TRANSFER:
                bookingpackagetransfer = cls._find_bookingservice(
                    booking_service, BookingPackageTransfer.objects)
                if not bookingpackagetransfer:
                    return
                cost, cost_msg, price, price_msg = cls._find_bookingservice_update_amounts(
                    bookingpackagetransfer)
                cls._save_booking_service_amounts(bookingpackagetransfer, cost, price)
                booking_service.cost_amount = bookingpackagetransfer.cost_amount
                booking_service.price_amount = bookingpackagetransfer.price_amount
            elif booking_service.service_type == constants.SERVICE_CATEGORY_EXTRA:
                bookingpackageextra = cls._find_bookingservice(
                    booking_service, BookingPackageExtra.objects)
                if not bookingpackageextra:
                    return
                cost, cost_msg, price, price_msg = cls._find_bookingservice_update_amounts(
                    bookingpackageextra)
                cls._save_booking_service_amounts(bookingpackageextra, cost, price)
                booking_service.cost_amount = bookingpackageextra.cost_amount
                booking_service.price_amount = bookingpackageextra.price_amount


    @classmethod
    def _totalize_services(cls, services, update_services=False):
        if services:
            cost, price = 0, 0
            for service in services:
                if update_services:
                    cls.update_bookingservice_amounts(service)
                cost = cls.totalize(cost, service.cost_amount)
                price = cls.totalize(price, service.price_amount)
            return  cls._round_cost(cost), cls._round_price(price)
        return None, None


    @classmethod
    def update_booking_amounts(cls, obj):
        if isinstance(obj, Booking):
            booking = obj
        else:
            booking = obj.booking
        booking_services = list(
            BookingService.objects.all().filter(
                booking=booking.id).exclude(
                    status=constants.SERVICE_STATUS_CANCELLED))

        cost, price = cls._totalize_services(booking_services)

        if booking.is_package_price:
            price, price_msg = cls._find_booking_package_price(booking)

        fields = []
        if not cls._equals_amounts(booking.cost_amount, cost):
            fields.append('cost_amount')
            booking.cost_amount = cost
        if not cls._equals_amounts(booking.price_amount, price):
            fields.append('price_amount')
            booking.price_amount = price
        if fields:
            booking.code_updated = True
            booking.save(update_fields=fields)


    @classmethod
    def update_bookingpackage_amounts(cls, obj, update_services=False):
        if isinstance(obj, BookingPackage):
            bookingpackage = obj
        else:
            bookingpackage = obj.booking_package
            
        bookingpackage_services = list(
            BookingPackageService.objects.all().filter(
                booking_package=bookingpackage.id).exclude(
                    status=constants.SERVICE_STATUS_CANCELLED))

        cost, price = cls._totalize_services(bookingpackage_services, update_services)

        if bookingpackage.price_by_package_catalogue:
            price_groups = cls.find_groups(bookingpackage, bookingpackage.service, False)
            price, price_msg = cls.package_price(
                bookingpackage.service.id,
                bookingpackage.datetime_from, bookingpackage.datetime_to,
                price_groups,
                bookingpackage.booking.agency)

        if bookingpackage.manual_price:
            price = bookingpackage.bookingpackage.price_amount
            price_msg = None
            if price is None:
                price_msg = "Manual Price Missing"

        fields = []
        if not cls._equals_amounts(bookingpackage.cost_amount, cost):
            fields.append('cost_amount')
            bookingpackage.cost_amount = cost
        if not cls._equals_amounts(bookingpackage.price_amount, price):
            fields.append('price_amount')
            bookingpackage.price_amount = price
        if fields:
            bookingpackage.code_updated = True
            bookingpackage.save(update_fields=fields)
            cls.update_booking_amounts(bookingpackage.booking)


    @classmethod
    def find_bookingpackage_update_amounts(cls, obj, pax_list=None, agency=None, manuals=False):
        if isinstance(obj, BookingPackage):
            bookingpackage = obj
        else:
            bookingpackage = obj.booking_package

        cost, cost_msg, price, price_msg = 0, None, 0, None

        if not agency:
            agency = bookingpackage.booking.agency
        if agency is None:
            price, price_msg = None, "Missing Agency"

        allotment_list = list(BookingPackageAllotment.objects.filter(
            booking_package=bookingpackage.id).exclude(
                status=constants.SERVICE_STATUS_CANCELLED).all())
        transfer_list = list(BookingPackageTransfer.objects.filter(
            booking_package=bookingpackage.id).exclude(
                status=constants.SERVICE_STATUS_CANCELLED).all())
        extra_list = list(BookingPackageExtra.objects.filter(
            booking_package=bookingpackage.id).exclude(
                status=constants.SERVICE_STATUS_CANCELLED).all())
        if ((not allotment_list) and (not transfer_list) and (not extra_list)):
            return None, "Booking Package Empty", None, "Booking Package Empty"

        if agency and bookingpackage.price_by_package_catalogue:
            if manuals and bookingpackage.manual_price:
                if bookingpackage.price_amount is None:
                    price, price_msg = None, "Missing Manual Price"
                else:
                    price, price_msg = bookingpackage.price_amount, None
            else:
                price, price_msg = BookingServices.package_price(
                    bookingpackage.service_id,
                    bookingpackage.datetime_from, bookingpackage.datetime_to,
                    cls.find_groups(bookingpackage, bookingpackage.service, False),
                    agency)
            if allotment_list:
                for allotment in allotment_list:
                    c, c_msg = cls.find_bookingservice_update_cost(allotment)
                    cost, cost_msg = cls._merge_costs(cost, cost_msg, c, c_msg)
                    if cost is None:
                        return cost, cost_msg, price, price_msg
            if transfer_list:
                for transfer in transfer_list:
                    c, c_msg = cls.find_bookingservice_update_cost(transfer)
                    cost, cost_msg = cls._merge_costs(cost, cost_msg, c, c_msg)
                    if cost is None:
                        return cost, cost_msg, price, price_msg
            if extra_list:
                for extra in extra_list:
                    c, c_msg = cls.find_bookingservice_update_cost(extra)
                    cost, cost_msg = cls._merge_costs(cost, cost_msg, c, c_msg)
                    if cost is None:
                        return cost, cost_msg, price, price_msg
        else:
            if allotment_list:
                for allotment in allotment_list:
                    c, c_msg, p, p_msg = cls._find_bookingservice_update_amounts(allotment)
                    cost, cost_msg = cls._merge_costs(cost, cost_msg, c, c_msg)
                    price, price_msg = cls._merge_prices(price, price_msg, p, p_msg)
                    if cost is None and price is None:
                        return cost, cost_msg, price, price_msg
            if transfer_list:
                for transfer in transfer_list:
                    c, c_msg, p, p_msg = cls._find_bookingservice_update_amounts(transfer)
                    cost, cost_msg = cls._merge_costs(cost, cost_msg, c, c_msg)
                    price, price_msg = cls._merge_prices(price, price_msg, p, p_msg)
                    if cost is None and price is None:
                        return cost, cost_msg, price, price_msg
            if extra_list:
                for extra in extra_list:
                    c, c_msg, p, p_msg = cls._find_bookingservice_update_amounts(extra)
                    cost, cost_msg = cls._merge_costs(cost, cost_msg, c, c_msg)
                    price, price_msg = cls._merge_prices(price, price_msg, p, p_msg)
                    if cost is None and price is None:
                        return cost, cost_msg, price, price_msg
        return cost, cost_msg, price, price_msg


    @classmethod
    def find_bookingpackage_update_cost(cls, obj):
        cost, cost_msg, price, price_msg = cls.find_bookingpackage_update_amounts(obj)
        return cost, cost_msg


    @classmethod
    def find_bookingpackage_update_price(cls, obj):
        cost, cost_msg, price, price_msg = cls.find_bookingpackage_update_amounts(obj)
        return price, price_msg


    @classmethod
    def sync_bookingpackage_services(cls, bookingpackage):
        if not isinstance(bookingpackage, BookingPackage):
            return False

        avoid_package_services = None
        if hasattr(bookingpackage, 'avoid_package_services'):
            avoid_package_services = bookingpackage.avoid_package_services
        if avoid_package_services:
            return False
        services = list(
            BookingPackageService.objects.filter(booking_package_id=bookingpackage.id).all())
        if services:
            return False

        package = bookingpackage.service
        if bookingpackage.time is None and not package.time is None:
            bookingpackage.refresh_from_db(fields=['version'])
            bookingpackage.time = package.time
            bookingpackage.save(update_fields=['time'])
        # create bookingallotment list
        for package_allotment in PackageAllotment.objects.filter(package_id=package.id).all():
            booking_package_allotment = BookingPackageAllotment()
            booking_package_allotment.booking_package = bookingpackage
            booking_package_allotment.conf_number = '< confirm number >'
            cls._copy_package_info(
                dst_package=booking_package_allotment, src_package=package_allotment)
            booking_package_allotment.room_type = package_allotment.room_type
            booking_package_allotment.board_type = package_allotment.board_type
            cls.setup_bookingservice_amounts(booking_package_allotment)
            booking_package_allotment.save()

        # create bookingtransfer list
        for package_transfer in PackageTransfer.objects.filter(package_id=package.id).all():
            booking_package_transfer = BookingPackageTransfer()
            booking_package_transfer.booking_package = bookingpackage
            booking_package_transfer.conf_number = '< confirm number >'
            cls._copy_package_info(
                dst_package=booking_package_transfer, src_package=package_transfer)
            # time
            # quantity auto
            booking_package_transfer.location_from = package_transfer.location_from
            booking_package_transfer.place_from = package_transfer.place_from
            booking_package_transfer.schedule_from = package_transfer.schedule_from
            booking_package_transfer.pickup = package_transfer.pickup
            booking_package_transfer.location_to = package_transfer.location_to
            booking_package_transfer.place_to = package_transfer.place_to
            booking_package_transfer.schedule_to = package_transfer.schedule_to
            booking_package_transfer.dropoff = package_transfer.dropoff
            cls.setup_bookingservice_amounts(booking_package_transfer)
            booking_package_transfer.save()

        # create bookingextra list
        for package_extra in PackageExtra.objects.filter(package_id=package.id).all():
            booking_package_extra = BookingPackageExtra()
            booking_package_extra.booking_package = bookingpackage
            booking_package_extra.conf_number = '< confirm number >'
            cls._copy_package_info(
                dst_package=booking_package_extra, src_package=package_extra)
            booking_package_extra.addon = package_extra.addon
            booking_package_extra.time = package_extra.time
            booking_package_extra.quantity = package_extra.quantity
            booking_package_extra.parameter = package_extra.parameter
            cls.setup_bookingservice_amounts(booking_package_extra)
            booking_package_extra.save()
        return True


    @classmethod
    def update_bookingpackageservices_amounts(cls, obj):
        if isinstance(obj, BookingServicePax):
            bookingpackage = obj.booking_service
        else:
            bookingpackage = obj

        if not cls.sync_bookingpackage_services(bookingpackage):
            allotment_list = list(BookingPackageAllotment.objects.filter(
                booking_package=bookingpackage.id).exclude(
                    status=constants.SERVICE_STATUS_CANCELLED).all())
            transfer_list = list(BookingPackageTransfer.objects.filter(
                booking_package=bookingpackage.id).exclude(
                    status=constants.SERVICE_STATUS_CANCELLED).all())
            extra_list = list(BookingPackageExtra.objects.filter(
                booking_package=bookingpackage.id).exclude(
                    status=constants.SERVICE_STATUS_CANCELLED).all())
            if allotment_list:
                for allotment in allotment_list:
                    cls.update_bookingservice_amounts(allotment)
            if transfer_list:
                for transfer in transfer_list:
                    cls.update_bookingservice_amounts(transfer)
            if extra_list:
                for extra in extra_list:
                    cls.update_bookingservice_amounts(extra)

    @classmethod
    def update_bookingpackage(cls, obj):
        if hasattr(obj, 'avoid_bookingpackage_update'):
            return

        if isinstance(obj, BookingPackage):
            bookingpackage = obj
        else:
            bookingpackage = obj.booking_package

        date_from = None
        date_to = None
        status = constants.BOOKING_STATUS_COORDINATED
        services = False
        cancelled = True
        for service in bookingpackage.booking_package_services.all():
            services = True
            # process only non cancelled services
            if service.status != constants.SERVICE_STATUS_CANCELLED:
                # set not all cancelled
                cancelled = False
                # date_from
                if service.datetime_from is not None:
                    if date_from is None or (date_from > service.datetime_from):
                        date_from = service.datetime_from
                # date_to
                if service.datetime_to is not None:
                    if date_to is None or (date_to < service.datetime_to):
                        date_to = service.datetime_to
                # status
                # pending sets always pending
                if service.status == constants.SERVICE_STATUS_PENDING:
                    status = constants.BOOKING_STATUS_PENDING
                # requested sets requested when not pending
                elif (service.status == constants.SERVICE_STATUS_REQUEST) and (
                        status != constants.BOOKING_STATUS_PENDING):
                    status = constants.BOOKING_STATUS_REQUEST
                # phone confirmed sets requested when not pending
                elif (service.status == constants.SERVICE_STATUS_PHONE_CONFIRMED) and (
                        status != constants.BOOKING_STATUS_PENDING):
                    status = constants.BOOKING_STATUS_REQUEST
                # confirmed sets confirmed when not requested and not pending
                elif (service.status == constants.SERVICE_STATUS_CONFIRMED) and (
                        status != constants.BOOKING_STATUS_PENDING) and (
                            status != constants.BOOKING_STATUS_REQUEST):
                    status = constants.BOOKING_STATUS_CONFIRMED
        # verify that have services and all cancelled
        if services:
            if cancelled:
                # status cancelled
                status = constants.BOOKING_STATUS_CANCELLED
        else:
            status = constants.BOOKING_STATUS_PENDING
        fields = []
        if bookingpackage.datetime_from != date_from:
            fields.append('datetime_from')
            bookingpackage.datetime_from = date_from
        if bookingpackage.datetime_to != date_to:
            fields.append('datetime_to')
            bookingpackage.datetime_to = date_to
        if bookingpackage.status != status:
            fields.append('status')
            bookingpackage.status = status

        if fields:
            bookingpackage.save(update_fields=fields)
            cls.update_booking(bookingpackage)


    @classmethod
    def update_booking(cls, booking_or_bookingservice):

        if hasattr(booking_or_bookingservice, 'avoid_booking_update'):
            return
        if hasattr(booking_or_bookingservice, 'booking'):
            booking = booking_or_bookingservice.booking
        elif isinstance(booking_or_bookingservice, Booking):
            booking = booking_or_bookingservice
        else:
            return

        cost = 0
        price = 0
        date_from = None
        date_to = None
        status = constants.BOOKING_STATUS_COORDINATED
        services = False
        cancelled = True
        for service in booking.booking_services.all():
            services = True
            # process only non cancelled services
            if service.status != constants.SERVICE_STATUS_CANCELLED:
                # set not all cancelled
                cancelled = False
                # date_from
                if (service.datetime_from is not None
                        and (date_from is None or date_from > service.datetime_from)):
                    date_from = service.datetime_from
                # date_to
                if service.datetime_to is None:
                    service.datetime_to = service.datetime_from
                if (service.datetime_to is not None
                        and (date_to is None or date_to < service.datetime_to)):
                    date_to = service.datetime_to
                # cost
                if not cost is None:
                    if service.cost_amount is None:
                        cost = None
                    else:
                        cost += service.cost_amount
                # price
                if not price is None:
                    if service.price_amount is None:
                        price = None
                    else:
                        price += service.price_amount
                # status
                # pending sets always pending
                if service.status == constants.SERVICE_STATUS_PENDING:
                    status = constants.BOOKING_STATUS_PENDING
                # requested sets requested when not pending
                elif (service.status == constants.SERVICE_STATUS_REQUEST) and (
                        status != constants.BOOKING_STATUS_PENDING):
                    status = constants.BOOKING_STATUS_REQUEST
                # phone confirmed sets requested when not pending
                elif (service.status == constants.SERVICE_STATUS_PHONE_CONFIRMED) and (
                        status != constants.BOOKING_STATUS_PENDING):
                    status = constants.BOOKING_STATUS_REQUEST
                # confirmed sets confirmed when not requested and not pending
                elif (service.status == constants.SERVICE_STATUS_CONFIRMED) and (
                        status != constants.BOOKING_STATUS_PENDING) and (
                            status != constants.BOOKING_STATUS_REQUEST):
                    status = constants.BOOKING_STATUS_CONFIRMED

        # verify that have services and all cancelled
        if services:
            if cancelled:
                # status cancelled
                status = constants.BOOKING_STATUS_CANCELLED
        else:
            status = constants.BOOKING_STATUS_PENDING
        # verify package prices
        if booking.is_package_price:
            price, price_msg = cls._find_booking_package_price(booking)

        fields = []
        if booking.date_from != date_from:
            fields.append('date_from')
            booking.date_from = date_from
        if booking.date_to != date_to:
            fields.append('date_to')
            booking.date_to = date_to
        if booking.status != status:
            fields.append('status')
            booking.status = status
        if not cls._equals_amounts(booking.cost_amount, cost):
            fields.append('cost_amount')
            booking.cost_amount = cost
        if not cls._equals_amounts(booking.price_amount, price):
            fields.append('price_amount')
            booking.price_amount = price

        if fields:
            booking.save(update_fields=fields)


    @classmethod
    def _find_groups(cls, pax_list):
        groups = dict()
        for pax in pax_list:
            if isinstance(pax, BookingPax):
                if pax.pax_group is None:
                    continue
                if not groups.__contains__(pax.pax_group):
                    groups[pax.pax_group] = 0
                groups[pax.pax_group] += 1
            else:
                if pax.group is None:
                    continue
                if not groups.__contains__(pax.group):
                    groups[pax.group] = 0
                groups[pax.group] += 1
        return groups.values()


    @classmethod
    def _find_booking_groups(cls, booking, pax_list=None):
        if not pax_list:
            pax_list = list(BookingPax.objects.filter(booking=booking.id))
        return cls._find_groups(pax_list)


    @classmethod
    def _find_booking_pricepackage_groups(cls, booking, pax_list=None):
        if not pax_list:
            pax_list = list(BookingPax.objects.filter(booking=booking.id))
        groups = dict()
        for pax in pax_list:
            if pax.pax_group is None:
                continue
            if not groups.__contains__(pax.pax_group):
                groups[pax.pax_group] = dict()
                groups[pax.pax_group]['qtty'] = 0
                groups[pax.pax_group]['free'] = 0
            groups[pax.pax_group]['qtty'] += 1
            if pax.is_price_free:
                groups[pax.pax_group]['free'] += 1
        return groups.values()


    @classmethod
    def _find_booking_package_price(cls, booking, pax_list=None):
        groups = cls._find_booking_pricepackage_groups(booking, pax_list)
        price, price_msg = 0, None
        for group in groups:
            if group['qtty'] == 1:
                if group['free'] < 1:
                    if not booking.package_sgl_price_amount is None:
                        price += booking.package_sgl_price_amount
                    else:
                        return None, "Package Price Missing Single Amount"
            elif group['qtty'] == 2:
                if group['free'] < 2:
                    if not booking.package_dbl_price_amount is None:
                        if group['free'] == 0:
                            price += 2 * booking.package_dbl_price_amount
                        else:
                            price += booking.package_dbl_price_amount
                    else:
                        return None, "Package Price Missing Double Amount"
            elif group['qtty'] == 3:
                if group['free'] < 3:
                    if not booking.package_tpl_price_amount is None:
                        if group['free'] == 0:
                            price += 3 * booking.package_tpl_price_amount
                        elif group['free'] == 1:
                            price += 2 * booking.package_tpl_price_amount
                        else:
                            price += booking.package_tpl_price_amount
                    else:
                        return None, "Package Price Missing Triple Amount"
            else:
                return None, "Package Price Unsupported Pax Quantity (%s)" % group['qtty']
        return price, price_msg


    @classmethod
    def find_bookingservices_with_different_amounts(cls, booking):
        agency = booking.agency
        bookingservices = list(BookingService.objects.all().filter(
            booking=booking.id).exclude(
                status=constants.SERVICE_STATUS_CANCELLED).order_by('datetime_from', 'datetime_to'))
        services = list()
        for bookingservice in bookingservices:
            cost, c_msg, price, p_msg = cls._find_bookingservice_update_amounts(
                bookingservice=bookingservice, agency=agency)
            if not cls._equals_amounts(cost, bookingservice.cost_amount) \
                    or not cls._equals_amounts(price, bookingservice.price_amount):
                bookingservice.update_cost_amount = cost
                bookingservice.update_price_amount = price
                services.append(bookingservice)
        return services


    @classmethod
    def update_bookingservices_amounts(cls, services):
        for service in services:
            cls.update_bookingservice_amounts(service)


    @classmethod
    def find_providers(cls, bookingservice):
        if bookingservice.service:
            qs = Provider.objects.all()
            if bookingservice.service_addon:
                addon = bookingservice.service_addon
            else:
                addon = ADDON_FOR_NO_ADDON

            if isinstance(bookingservice, (BookingAllotment, BookingPackageallotment)) \
                    and bookingservice.room_type and bookingservice.board_type:
                qs = qs.filter(
                    providerallotmentservice__service=bookingservice.service,
                    providerallotmentservice__providerallotmentdetail__room_type=bookingservice.room_type,
                    providerallotmentservice__providerallotmentdetail__board_type=bookingservice.board_type,
                    providerallotmentservice__providerallotmentdetail__addon=addon,
                )
            elif isinstance(bookingservice, (BookingTransfer, BookingPackageTransfer)) \
                    and bookingservice.location_from and bookingservice.location_to:
                qs = qs.filter(
                    Q(providertransferservice__service=bookingservice.service)
                    &
                    Q(providerallotmentservice__providerallotmentdetail__addon=addon)
                    &
                    (
                        (
                            Q(providertransferservice__providertransferdetail__p_location_from=bookingservice.location_from)
                            & Q(providertransferservice__providertransferdetail__p_location_to=bookingservice.location_to)
                        )
                        |
                        (
                            Q(providertransferservice__providertransferdetail__p_location_from=bookingservice.location_to)
                            & Q(providertransferservice__providertransferdetail__p_location_to=bookingservice.location_from)
                        )
                    )
                )
            elif isinstance(bookingservice, (BookingExtra, BookingPackageExtra)):
                qs = qs.filter(
                    providerextraservice__service=bookingservice.service,
                    providerextraservice__providerextradetail__addon=addon,
                )
            else:
                return Provider.objects.none()
            return list(qs)
        return Provider.objects.none()
    

    @classmethod
    def list_providers_costs(cls, bookingservice, pax_list):
        providers = cls.find_providers(bookingservice)
        for provider in providers:
            bookingservice.provider = provider
            cost, cost_msg = cls._find_bookingservice_cost(bookingservice, pax_list)
            provider.cost = cost
            provider.cost_msg = cost_msg
        return providers

    @classmethod
    def clone_quote_services(cls, old_quote_id, new_quote):
        new_quote.avoid_all = True

        old_quote = Quote.objects.get(pk=old_quote_id)

        allotments = list(QuoteAllotment.objects.filter(
            quote=old_quote))
        for service in allotments:
            cls._clone_quote_service(service, new_quote)

        transfers = list(QuoteTransfer.objects.filter(
            quote=old_quote))
        for service in transfers:
            cls._clone_quote_service(service, new_quote)

        extras = list(QuoteExtra.objects.filter(
            quote=old_quote))
        for service in extras:
            cls._clone_quote_service(service, new_quote)

        packages = list(QuotePackage.objects.filter(
            quote=old_quote))
        for service in packages:
            package_pk = service.pk
            service.avoid_sync_services = True
            cls._clone_quote_service(service, new_quote)

            # package services
            allotments = list(QuotePackageAllotment.objects.filter(
                quote_package=package_pk))
            for package_service in allotments:
                cls._clone_quotepackage_service(package_service, service)

            transfers = list(QuotePackageTransfer.objects.filter(
                quote_package=package_pk))
            for package_service in transfers:
                cls._clone_quotepackage_service(package_service, service)

            extras = list(QuotePackageExtra.objects.filter(
                quote_package=package_pk))
            for package_service in extras:
                cls._clone_quotepackage_service(package_service, service)

        cls.update_quote(new_quote)
        cls.update_quote_paxvariants_amounts(new_quote)

    @classmethod
    def _clone_quote_service(cls, quote_service, quote):
        pax_variants = list(QuoteServicePaxVariant.objects.filter(
            quote_service=quote_service))
        quote_service.pk = None
        quote_service.id = None
        quote_service.quote = quote
        quote_service.quote_id = quote.pk
        quote_service.avoid_all = True
        quote_service.save()
        for pax_variant in pax_variants:
            cls._clone_quoteservice_paxvariant(pax_variant, quote_service)

    @classmethod
    def _clone_quotepackage_service(cls, package_service, package):
        pax_variants = list(QuotePackageServicePaxVariant.objects.filter(
            quotepackage_service=package_service))
        package_service.pk = None
        package_service.id = None
        package_service.quote_package = package
        package_service.quote_package_id = package.pk
        package_service.avoid_all = True
        package_service.save()
        for pax_variant in pax_variants:
            cls._clone_quotepackageservice_paxvariant(pax_variant, package_service)

    @classmethod
    def _clone_quoteservice_paxvariant(cls, pax_variant, quote_service):
        pax_variant.pk = None
        pax_variant.id = None
        pax_variant.quote_service = quote_service
        pax_variant.quote_service_id = quote_service.pk
        quote_pax_variant = cls._find_quote_paxvariant(pax_variant, quote_service.quote)
        pax_variant.quote_pax_variant = quote_pax_variant
        pax_variant.quote_pax_variant_id = quote_pax_variant.pk
        pax_variant.avoid_all = True
        pax_variant.save()

    @classmethod
    def _find_quote_paxvariant(cls, pax_variant, quote):
        pax_variants = list(QuotePaxVariant.objects.filter(
            quote=quote.id, pax_quantity=pax_variant.quote_pax_variant.pax_quantity))
        return pax_variants[0]

    @classmethod
    def _clone_quotepackageservice_paxvariant(cls, pax_variant, package_service):
        pax_variant.pk = None
        pax_variant.id = None
        pax_variant.quotepackage_service = package_service
        pax_variant.quotepackage_service_id = package_service.pk
        quotepackage_pax_variant = cls._find_quotepackage_paxvariant(
            pax_variant, package_service.quote_package)
        pax_variant.quotepackage_pax_variant = quotepackage_pax_variant
        pax_variant.quotepackage_pax_variant_id = quotepackage_pax_variant.pk
        pax_variant.avoid_all = True
        pax_variant.save()

    @classmethod
    def _find_quotepackage_paxvariant(cls, pax_variant, quote_package):
        pax_variants = list(QuoteServicePaxVariant.objects.filter(
            quote_service=quote_package.id,
            quote_pax_variant__pax_quantity=pax_variant.quotepackage_pax_variant.quote_pax_variant.pax_quantity))
        return pax_variants[0]


    @classmethod
    def add_paxes_to_booking(cls, booking, pax_list, bookingservice_ids):
        with transaction.atomic(savepoint=False):
            for pax in pax_list:
                booking_pax = BookingPax()
                booking_pax.booking = booking
                booking_pax.pax_name = pax['pax_name']
                booking_pax.pax_group = pax['pax_group']
                booking_pax.pax_age = pax['pax_age']
                booking_pax.is_price_free = pax['is_price_free']
                booking_pax.avoid_booking_update = True
                booking_pax.save()

                cls._add_bookingpax_to_bookingservices(booking_pax, bookingservice_ids)


    @classmethod
    def _add_bookingpax_to_bookingservices(cls, booking_pax, bookingservice_ids):
        for bookingservice_id in bookingservice_ids:
            bookingservice = BookingService.objects.get(pk=bookingservice_id)
            bookingservice_pax = BookingServicePax()
            bookingservice_pax.booking_service = bookingservice
            bookingservice_pax.booking_pax = booking_pax
            bookingservice_pax.group = booking_pax.pax_group
            bookingservice_pax.save()


    @classmethod
    def next_year_package_prices(cls, agency_service_ids, percent=None, amount=None):
        for agency_service_id in agency_service_ids:
            try:
                agency_service = AgencyPackageService.objects.get(agency_service_id)
                ConfigServices.next_year_price(
                    AgencyPackageDetail.objects, agency_service, percent, amount)
            except Error as ex:
                print(ex)


    @classmethod
    def list_package_details(cls, package, agency, date_from, date_to):
        qs = AgencyPackageDetail.objects.all()
        qs = qs.filter(
            agency_service__agency=agency,
            agency_service__service=package.id)
        if date_from:
            qs = qs.filter(agency_service__date_to__gte=date_from)
        if date_to:
            qs = qs.filter(agency_service__date_from__lte=date_to)
        qs = qs.order_by(
            'pax_range_min', '-pax_range_max',
            'agency_service__date_from', '-agency_service__date_to')
        return list(qs)


    @classmethod
    def find_bookingservice_providers_costs(cls, bookingservice, pax_list=None):
        if not pax_list:
            pax_list = cls._find_bookingservice_pax_list(bookingservice)

        if isinstance(bookingservice, (BookingAllotment, BookingPackageAllotment)):
            detail_list = list(details_allotment_queryset(
                bookingservice.service,
                bookingservice.datetime_from,
                bookingservice.datetime_to,
                bookingservice.room_type,
                bookingservice.board_type,
                bookingservice.service_addon))
        elif isinstance(bookingservice, (BookingTransfer, BookingPackageTransfer)):
            detail_list = list(details_transfer_queryset(
                bookingservice.service,
                bookingservice.datetime_from,
                bookingservice.datetime_to,
                bookingservice.location_from,
                bookingservice.location_to,
                bookingservice.service_addon))
        elif isinstance(bookingservice, (BookingExtra, BookingPackageExtra)):
            detail_list = list(details_extra_queryset(
                bookingservice.service,
                bookingservice.datetime_from,
                bookingservice.datetime_to,
                bookingservice.service_addon))
        else:
            return list()

        result = list()
        for detail in detail_list:
            result.append({
                'provider_id': detail.provider_service.provider.id,
                'provider_name': detail.provider_service.provider.name,
                'date_from': detail.provider_service.date_from,
                'date_to': detail.provider_service.date_to,
                'sgl_cost': detail.ad_1_amount,
                'dbl_cost': detail.ad_2_amount,
                'tpl_cost': detail.ad_3_amount,})
        return result

def details_allotment_queryset(
        service, date_from=None, date_to=None, room_type=None, board_type=None, addon=None):
    if not service:
        return ProviderAllotmentDetail.objects.none()

    qs = ProviderAllotmentDetail.objects.all().distinct().filter(
        provider_service__service=service,
        provider_service__provider__enabled=True)

    if date_from:
        qs = qs.filter(provider_service__date_to__gte=date_from)
    if date_to:
        qs = qs.filter(provider_service__date_from__lte=date_to)
    if room_type:
        qs = qs.filter(room_type=room_type)
    if board_type:
        qs = qs.filter(board_type=board_type)
    if addon:
        qs = qs.filter(addon=addon)
    else:
        qs = qs.filter(addon=ADDON_FOR_NO_ADDON)
    qs = qs.order_by(
        'provider_service__provider',
        'provider_service__date_from',
        'provider_service__date_to',
        'board_type', 'room_type', 'addon')
    return qs[:50]

def details_transfer_queryset(
        service, date_from=None, date_to=None, location_from=None, location_to=None, addon=None):
    if not service:
        return ProviderTransferDetail.objects.none()

    qs = ProviderTransferDetail.objects.all().distinct().filter(
        provider_service__service=service,
        provider_service__provider__enabled=True)

    if date_from:
        qs = qs.filter(provider_service__date_to__gte=date_from)
    if date_to:
        qs = qs.filter(provider_service__date_from__lte=date_to)
    if location_from:
        if location_to:
            qs = qs.filter(
                (Q(p_location_from=location_from)
                & Q(p_location_to=location_to))
                |
                (Q(p_location_from=location_to)
                & Q(p_location_to=location_from)))
        else:
            qs = qs.filter(
                Q(p_location_from=location_from)
                |
                Q(p_location_to=location_from))
    else:
        if location_to:
            qs = qs.filter(
                Q(p_location_from=location_to)
                |
                Q(p_location_to=location_to))
    if addon:
        qs = qs.filter(addon=addon)
    else:
        qs = qs.filter(addon=ADDON_FOR_NO_ADDON)
    qs = qs.order_by(
        'provider_service__provider',
        'provider_service__date_from',
        'provider_service__date_to',
        'p_location_from', 'p_location_to', 'addon')
    return qs[:50]


def details_extra_queryset(service, date_from=None, date_to=None, addon=None):
    if not service:
        return ProviderExtraDetail.objects.none()

    qs = ProviderExtraDetail.objects.all().distinct().filter(
        provider_service__service=service,
        provider_service__provider__enabled=True)

    if date_from:
        qs = qs.filter(provider_service__date_to__gte=date_from)
    if date_to:
        qs = qs.filter(provider_service__date_from__lte=date_to)
    if addon:
        qs = qs.filter(addon=addon)
    else:
        qs = qs.filter(addon=ADDON_FOR_NO_ADDON)
    qs = qs.order_by(
        'provider_service__provider',
        'provider_service__date_from',
        'provider_service__date_to',
        'addon')
    return qs[:50]
