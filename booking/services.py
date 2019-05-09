# -*- coding: utf-8 -*-
from __future__ import unicode_literals

"""
Booking Service
"""
from datetime import datetime, timedelta

from django.db import transaction
from django.db.models import Q

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
    BookingInvoice, BookingInvoiceLine, BookingInvoicePartial)

from config.services import ConfigServices

from finance.constants import STATUS_CANCELLED, STATUS_READY
from finance.services import FinanceService
from finance.models import Agency


class BookingServices(object):
    """
    Booking Services
    """

    @classmethod
    def booking_to_invoice(cls, user, booking, force=False):
        with transaction.atomic(savepoint=False):
            invoice = booking.invoice
            new_invoice = False
            if invoice is None:
                new_invoice = True
                invoice = BookingInvoice()
            else:
                if force:
                    invoice.status = STATUS_CANCELLED
                    FinanceService.save_agency_invoice(user, invoice)
                    new_invoice = True
                    invoice = BookingInvoice()

            invoice.agency = booking.agency
            invoice.currency = booking.currency
            invoice.amount = booking.price_amount
            invoice.status = STATUS_READY

            invoice.booking_name = booking.name
            invoice.reference = booking.reference
            invoice.date_from = booking.date_from
            invoice.date_to = booking.date_to

            FinanceService.save_agency_invoice(user, invoice)

            # obtain lines
            booking_service_list = BookingService.objects.filter(
                booking=booking.id).all()
            for booking_service in booking_service_list:
                invoice_line = BookingInvoiceLine()
                invoice_line.invoice = invoice
                invoice_line.date_from = booking_service.datetime_from
                invoice_line.date_to = booking_service.datetime_to
                invoice_line.bookingservice_name = booking_service.name
                invoice_line.service_name = booking_service.service.name
                invoice_line.price = booking_service.price_amount

                invoice_line.save()

            # obtain partials
            booking_pax_list = BookingPax.objects.filter(booking=booking.id).all()
            for booking_pax in booking_pax_list:
                invoice_partial = BookingInvoicePartial()
                invoice_partial.invoice = invoice
                invoice_partial.pax_name = booking_pax.pax_name

                invoice_partial.save()

            # verify if new invoice to save booking
            if new_invoice:
                booking.agency_invoice = invoice
                booking.save()


    @classmethod
    def build_bookingservice_paxes(cls, bookingservice, pax_list):
        for service_pax in pax_list:
            bookingservice_pax = BookingServicePax()
            bookingservice_pax.booking_service = bookingservice
            bookingservice_pax.booking_pax = service_pax.booking_pax
            bookingservice_pax.group = service_pax.group

            bookingservice_pax.avoid_booking_update = True
            bookingservice_pax.save()


    @classmethod
    def build_booking(cls, quote_id, rooming):
        quote = list(Quote.objects.filter(pk=quote_id).all())
        if not quote:
            return None, 'Quote Not Found'
        quote = quote[0]
        try:
            with transaction.atomic(savepoint=False):
                # create booking
                booking = Booking()
                booking.name = '< booking name >'
                booking.agency = quote.agency
                booking.reference = '< reference> '
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
                pax_variant = cls._find_pax_variant(quote, rooming)
                booking.package_sgl_price_amount = pax_variant.price_single_amount
                if booking.package_sgl_price_amount is None:
                    booking.package_sgl_price_amount = 0
                booking.package_dbl_price_amount = pax_variant.price_double_amount
                if booking.package_dbl_price_amount is None:
                    booking.package_dbl_price_amount = 0
                booking.package_tpl_price_amount = pax_variant.price_triple_amount
                if booking.package_tpl_price_amount is None:
                    booking.package_tpl_price_amount = 0

                booking.save()
                service_pax_list = list()
                # create pax list
                pax_list = list()
                for pax in rooming:
                    if pax['pax_name'] and pax['pax_group']:

                        booking_pax = BookingPax()
                        booking_pax.booking = booking
                        booking_pax.pax_name = pax['pax_name']
                        booking_pax.pax_age = pax['pax_age']
                        booking_pax.pax_group = pax['pax_group']

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

                    cls.set_bookingservice_amounts(booking_allotment, pax_list)

                    booking_allotment.avoid_booking_update = True
                    booking_allotment.save()

                    # create bookingservicepax list
                    cls.build_bookingservice_paxes(booking_allotment, pax_list)

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

                    cls.set_bookingservice_amounts(booking_transfer, pax_list)

                    booking_transfer.avoid_booking_update = True
                    booking_transfer.save()

                    # create bookingservicepax list
                    cls.build_bookingservice_paxes(booking_transfer, pax_list)

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

                    cls.set_bookingservice_amounts(booking_extra, pax_list)

                    booking_extra.avoid_booking_update = True
                    booking_extra.save()

                    # create bookingservicepax list
                    cls.build_bookingservice_paxes(booking_extra, pax_list)

                # create bookingpackage list
                for quote_package in QuotePackage.objects.filter(quote_id=quote.id).all():
                    booking_package = BookingPackage()
                    booking_package.booking = booking
                    booking_package.conf_number = '< confirm number >'
                    booking_package.name = quote_package.name
                    cls._copy_service_info(
                        dst_service=booking_package, src_service=quote_package)

                    cls.set_bookingservice_amounts(booking_package, pax_list)

                    booking_package.avoid_package_services = True
                    booking_package.avoid_booking_update = True
                    booking_package.save()

                    # create bookingservicepax list
                    cls.build_bookingservice_paxes(booking_package, pax_list)

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

                        bookingpackage_allotment.avoid_booking_update = True
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

                        bookingpackage_transfer.avoid_booking_update = True
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

                        bookingpackage_extra.avoid_booking_update = True
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
    def update_quote_package(cls, quote_package):

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
                pax_variant, allotment_list, transfer_list, extra_list, package_list, agency)

            variant_dict.update({'total': cls._quote_amounts_dict(
                cost_1, cost_1_msg, price_1, price_1_msg,
                cost_2, cost_2_msg, price_2, price_2_msg,
                cost_3, cost_3_msg, price_3, price_3_msg)})

            result.append(variant_dict)

        return 0, '', result


    @classmethod
    def _find_quote_pax_variant_amounts(
            cls, pax_variant, allotment_list=None, transfer_list=None, extra_list=None, package_list=None,
            agency=None, variant_dict=None):
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
                    c3, c3_msg, p3, p3_msg = cls._find_quoteallotment_amounts(
                        pax_variant=pax_variant, allotment=allotment, agency=agency)

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
                    c3, c3_msg, p3, p3_msg = cls._find_quotetransfer_amounts(
                        pax_variant=pax_variant, transfer=transfer, agency=agency)

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
                    c3, c3_msg, p3, p3_msg = cls._find_quoteextra_amounts(
                        pax_variant=pax_variant, extra=extra, agency=agency)

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
                        pax_variant=pax_variant, package=package, agency=agency)

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

        if not pax_variant.price_percent is None:
            if cost_1 is None:
                price_1, price_1_msg = None, 'Cost for % is empty'
            else:
                price_1, price_1_msg = round(0.499999 + float(cost_1) * (1.0 + float(pax_variant.price_percent) / 100.0)), None
            if cost_2 is None:
                price_2, price_2_msg = None, 'Cost for % is empty'
            else:
                price_2, price_2_msg = round(0.499999 + float(cost_2) * (1.0 + float(pax_variant.price_percent) / 100.0)), None
            if cost_3 is None:
                price_3, price_3_msg = None, 'Cost for % is empty'
            else:
                price_3, price_3_msg = round(0.499999 + float(cost_3) * (1.0 + float(pax_variant.price_percent) / 100.0)), None

        return cost_1, cost_1_msg, price_1, price_1_msg, \
            cost_2, cost_2_msg, price_2, price_2_msg, \
            cost_3, cost_3_msg, price_3, price_3_msg


    @classmethod
    def find_quoteallotment_amounts(
            cls, quoteallotment, variant_list):
        result = list()

        if not variant_list:
            return 3, 'Pax Variants Missing', None

        counter = 0
        for pax_variant in variant_list:
            variant_dict = dict()
            variant_dict.update({'quote_pax_variant': pax_variant.quote_pax_variant.id})

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

            key = '%s' % counter
            if not hasattr(quoteallotment, 'service'):
                variant_dict.update({'total': cls._no_service_dict()})
            else:
                c1, c1_msg, p1, p1_msg, \
                c2, c2_msg, p2, p2_msg, \
                c3, c3_msg, p3, p3_msg = cls._find_quoteallotment_amounts(
                    pax_variant=pax_variant.quote_pax_variant,
                    allotment=quoteallotment,
                    agency=quoteallotment.quote.agency)

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
    def find_quotepackageallotment_amounts(
            cls, quotepackageallotment, packagevariant_list):
        result = list()

        if not packagevariant_list:
            return 3, 'Pax Variants Missing', None

        counter = 0
        for pax_variant in packagevariant_list:
            variant_dict = dict()
            variant_dict.update({'quotepackage_pax_variant': pax_variant.quotepackage_pax_variant.id})

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

            key = '%s' % counter
            if not hasattr(quotepackageallotment, 'service'):
                variant_dict.update({'total': cls._no_service_dict()})
            else:
                c1, c1_msg, p1, p1_msg, \
                c2, c2_msg, p2, p2_msg, \
                c3, c3_msg, p3, p3_msg = cls._find_quoteallotment_amounts(
                    pax_variant=pax_variant.quotepackage_pax_variant.quote_pax_variant,
                    allotment=quotepackageallotment,
                    agency=quotepackageallotment.quote_package.quote.agency)

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
    def find_quotetransfer_amounts(
            cls, quotetransfer, variant_list):
        result = list()

        if not variant_list:
            return 3, 'Pax Variants Missing', None

        counter = 0
        for pax_variant in variant_list:
            variant_dict = dict()
            variant_dict.update({'quote_pax_variant': pax_variant.quote_pax_variant.id})

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

            key = '%s' % counter
            if not hasattr(quotetransfer, 'service'):
                variant_dict.update({'total': cls._no_service_dict()})
            else:
                c1, c1_msg, p1, p1_msg, \
                c2, c2_msg, p2, p2_msg, \
                c3, c3_msg, p3, p3_msg = cls._find_quotetransfer_amounts(
                    pax_variant=pax_variant.quote_pax_variant,
                    transfer=quotetransfer,
                    agency=quotetransfer.quote.agency)

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
    def find_quotepackagetransfer_amounts(
            cls, quotepackagetransfer, packagevariant_list):
        result = list()

        if not packagevariant_list:
            return 3, 'Pax Variants Missing', None

        counter = 0
        for pax_variant in packagevariant_list:
            variant_dict = dict()
            variant_dict.update({'quotepackage_pax_variant': pax_variant.quotepackage_pax_variant.id})

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

            key = '%s' % counter
            if not hasattr(quotepackagetransfer, 'service'):
                variant_dict.update({'total': cls._no_service_dict()})
            else:
                c1, c1_msg, p1, p1_msg, \
                c2, c2_msg, p2, p2_msg, \
                c3, c3_msg, p3, p3_msg = cls._find_quotetransfer_amounts(
                    pax_variant=pax_variant.quotepackage_pax_variant.quote_pax_variant,
                    transfer=quotepackagetransfer,
                    agency=quotepackagetransfer.quote_package.quote.agency)

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
    def find_quoteextra_amounts(
            cls, quoteextra, variant_list):
        result = list()

        if not variant_list:
            return 3, 'Pax Variants Missing', None

        counter = 0
        for pax_variant in variant_list:
            variant_dict = dict()
            variant_dict.update({'quote_pax_variant': pax_variant.quote_pax_variant.id})

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

            key = '%s' % counter
            if not hasattr(quoteextra, 'service'):
                variant_dict.update({'total': cls._no_service_dict()})
            else:
                c1, c1_msg, p1, p1_msg, \
                c2, c2_msg, p2, p2_msg, \
                c3, c3_msg, p3, p3_msg = cls._find_quoteextra_amounts(
                    pax_variant=pax_variant.quote_pax_variant, extra=quoteextra, agency=quoteextra.quote.agency)

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
    def find_quotepackageextra_amounts(
            cls, quotepackageextra, packagevariant_list):
        result = list()

        if not packagevariant_list:
            return 3, 'Pax Variants Missing', None

        counter = 0
        for pax_variant in packagevariant_list:
            variant_dict = dict()
            variant_dict.update({'quotepackage_pax_variant': pax_variant.quotepackage_pax_variant.id})

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

            key = '%s' % counter
            if not hasattr(quotepackageextra, 'service'):
                variant_dict.update({'total': cls._no_service_dict()})
            else:
                c1, c1_msg, p1, p1_msg, \
                c2, c2_msg, p2, p2_msg, \
                c3, c3_msg, p3, p3_msg = cls._find_quoteextra_amounts(
                    pax_variant=pax_variant.quotepackage_pax_variant.quote_pax_variant,
                    extra=quotepackageextra,
                    agency=quotepackageextra.quote_package.quote.agency)

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
    def find_quotepackage_amounts(
            cls, quotepackage, variant_list):
        result = list()

        if not variant_list:
            return 3, 'Pax Variants Missing', None

        counter = 0
        for pax_variant in variant_list:
            variant_dict = dict()
            variant_dict.update({'quote_pax_variant': pax_variant.quote_pax_variant_id})

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

            key = '%s' % counter
            if not hasattr(quotepackage, 'service'):
                variant_dict.update({'total': cls._no_service_dict()})
            else:
                c1, c1_msg, p1, p1_msg, \
                c2, c2_msg, p2, p2_msg, \
                c3, c3_msg, p3, p3_msg = cls._find_quotepackage_amounts(
                    pax_variant=pax_variant.quote_pax_variant, package=quotepackage, agency=quotepackage.quote.agency)

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
                        (Q(pax_range_min__isnull=True) & Q(pax_range_max__gte=paxes)) |
                        (Q(pax_range_min__lte=paxes) & Q(pax_range_max__gte=paxes)) |
                        (Q(pax_range_min__lte=paxes) & Q(pax_range_max__isnull=True))
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
            groups = cls.find_booking_groups(booking)
            price = 0
            for pax_qtty in groups:
                if pax_qtty == 1:
                    price += booking.package_sgl_price_amount
                elif pax_qtty == 2:
                    price += 2 * booking.package_dbl_price_amount
                elif pax_qtty == 3:
                    price += 3 * booking.package_tpl_price_amount

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
        if booking.cost_amount != cost:
            fields.append('cost_amount')
            booking.cost_amount = cost
        if booking.price_amount != price:
            fields.append('price_amount')
            booking.price_amount = price

        if fields:
            booking.save(update_fields=fields)


    @classmethod
    def find_booking_groups(cls, booking):
        pax_list = list(BookingPax.objects.filter(booking=booking.id))
        groups = dict()
        for pax in pax_list:
            if not groups.__contains__(pax.pax_group):
                groups[pax.pax_group] = 0
            groups[pax.pax_group] += 1
        return groups.values()


    @classmethod
    def find_groups(cls, booking_service, service, for_cost):
        if booking_service is None:
            return None, None
        pax_list = list(
            BookingServicePax.objects.filter(booking_service=booking_service.id))
        return cls.find_paxes_groups(pax_list, service, for_cost)


    @classmethod
    def find_paxes_groups(cls, pax_list, service, for_cost):
        if service.grouping:
            groups = dict()
            for pax in pax_list:
                if not pax.booking_pax_id is None and not pax.group is None:
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
                if not pax.booking_pax_id is None:
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
    def update_booking_package(cls, booking_package):
        if not isinstance(booking_package, BookingPackage):
            return

        avoid_package_services = None
        if hasattr(booking_package, 'avoid_package_services'):
            avoid_package_services = booking_package.avoid_package_services
        if avoid_package_services:
            return

        services = list(
            BookingPackageService.objects.filter(booking_package_id=booking_package.id).all())
        if services:
            return

        package = booking_package.service
        # create bookingallotment list
        for package_allotment in PackageAllotment.objects.filter(package_id=package.id).all():
            booking_package_allotment = BookingPackageAllotment()
            booking_package_allotment.booking_package = booking_package
            booking_package_allotment.conf_number = '< confirm number >'
            # cost_amount
            # cost_comment
            # price_amount
            # price_comment
            # provider_invoice

            # name auto
            # service_type auto
            cls._copy_package_info(
                dst_package=booking_package_allotment, src_package=package_allotment)
            booking_package_allotment.room_type = package_allotment.room_type
            booking_package_allotment.board_type = package_allotment.board_type

            cls.set_bookingservice_amounts(booking_package_allotment)
            booking_package_allotment.save()

        # create bookingtransfer list
        for package_transfer in PackageTransfer.objects.filter(package_id=package.id).all():
            booking_package_transfer = BookingPackageTransfer()
            booking_package_transfer.booking_package = booking_package
            booking_package_transfer.conf_number = '< confirm number >'
            # cost_amount
            # cost_comment
            # price_amount
            # price_comment
            # provider_invoice
            # name auto
            # service_type auto
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

            cls.set_bookingservice_amounts(booking_package_transfer)
            booking_package_transfer.save()

        # create bookingextra list
        for package_extra in PackageExtra.objects.filter(package_id=package.id).all():
            booking_package_extra = BookingPackageExtra()
            booking_package_extra.booking_package = booking_package
            booking_package_extra.conf_number = '< confirm number >'
            # cost_amount
            # cost_comment
            # price_amount
            # price_comment
            # name auto
            # service_type auto
            cls._copy_package_info(
                dst_package=booking_package_extra, src_package=package_extra)
            booking_package_extra.addon = package_extra.addon
            booking_package_extra.time = package_extra.time
            booking_package_extra.quantity = package_extra.quantity
            booking_package_extra.parameter = package_extra.parameter

            cls.set_bookingservice_amounts(booking_package_extra)
            booking_package_extra.save()

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
    def update_bookingservice_amounts(cls, booking_service):
        if booking_service.service_type == constants.SERVICE_CATEGORY_ALLOTMENT:
            bookingallotment = cls._find_bookingservice(booking_service, BookingAllotment.objects)
            if not bookingallotment:
                return
            cost, price = cls._bookingallotment_amounts(bookingallotment)
            cls._save_booking_service_amounts(bookingallotment, cost, price)

        if booking_service.service_type == constants.SERVICE_CATEGORY_TRANSFER:
            bookingtransfer = cls._find_bookingservice(booking_service, BookingTransfer.objects)
            if not bookingtransfer:
                return
            cost, price = cls._bookingtransfer_amounts(bookingtransfer)
            cls._save_booking_service_amounts(bookingtransfer, cost, price)

        if booking_service.service_type == constants.SERVICE_CATEGORY_EXTRA:
            bookingextra = cls._find_bookingservice(booking_service, BookingExtra.objects)
            if not bookingextra:
                return
            cost, price = cls._bookingextra_amounts(bookingextra)
            cls._save_booking_service_amounts(bookingextra, cost, price)

        if booking_service.service_type == constants.SERVICE_CATEGORY_PACKAGE:
            bookingpackage = cls._find_bookingservice(booking_service, BookingPackage.objects)
            if not bookingpackage:
                return

            # update package services
            pax_list = cls._find_pax_list(bookingpackage)

            for bookingpackage_allotment in BookingPackageAllotment.objects.filter(
                    booking_package=bookingpackage.id).all():
                cost, price = cls._bookingpackageservice_amounts(
                    bookingpackage_allotment, pax_list)
                cost, price = cls._bookingservice_manual_amounts(
                    bookingpackage_allotment, cost, price)
                cls._save_booking_service_amounts(bookingpackage_allotment, cost, price)

            for bookingpackage_transfer in BookingPackageTransfer.objects.filter(
                    booking_package=bookingpackage.id).all():
                cost, price = cls._bookingpackageservice_amounts(
                    bookingpackage_transfer, pax_list)
                cost, price = cls._bookingservice_manual_amounts(
                    bookingpackage_transfer, cost, price)
                cls._save_booking_service_amounts(bookingpackage_transfer, cost, price)

            for bookingpackage_extra in BookingPackageExtra.objects.filter(
                    booking_package=bookingpackage.id).all():
                cost, price = cls._bookingpackageservice_amounts(
                    bookingpackage_extra, pax_list)
                cost, price = cls._bookingservice_manual_amounts(
                    bookingpackage_extra, cost, price)
                cls._save_booking_service_amounts(bookingpackage_extra, cost, price)

            cost, price = cls._bookingpackage_amounts(bookingpackage, pax_list)
            cls._save_booking_service_amounts(bookingpackage, cost, price)


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
    def bookingpackage_amounts(
            cls, bookingpackage, pax_list):
        cost_groups = BookingServices.find_paxes_groups(pax_list, bookingpackage.service, True)
        price_groups = BookingServices.find_paxes_groups(pax_list, bookingpackage.service, False)

        pck_cost = 0
        pck_cost_msg = ''
        pck_price = 0
        pck_price_msg = ''

        agency = bookingpackage.booking.agency

        if bookingpackage.price_by_package_catalogue:
            pck_price, pck_price_msg = cls.package_price(
                service_id=bookingpackage.service_id,
                date_from=bookingpackage.datetime_from,
                date_to=bookingpackage.datetime_to,
                price_groups=price_groups,
                agency=agency)

        bookingpackageallotment_list = list(BookingPackageAllotment.objects.filter(
                booking_package=bookingpackage.id).exclude(
                    status=constants.SERVICE_STATUS_CANCELLED).all())
        if bookingpackageallotment_list:
            for bookingpackageallotment in bookingpackageallotment_list:
                if bookingpackageallotment.manual_cost:
                    cost, cost_msg = bookingpackageallotment.cost_amount, bookingpackageallotment.cost_comments
                    if not bookingpackage.price_by_package_catalogue:
                        if bookingpackageallotment.manual_price:
                            price, price_msg = bookingpackageallotment.price_amount, bookingpackageallotment.price_comments
                        else:
                            price, price_msg = ConfigServices.allotment_prices(
                                bookingpackageallotment.service_id,
                                bookingpackageallotment.datetime_from, bookingpackageallotment.datetime_to,
                                price_groups,
                                agency,
                                bookingpackageallotment.board_type, bookingpackageallotment.room_type_id,
                            )
                        pck_price, pck_price_msg = cls._merge_amounts(
                            price, price_msg, pck_price, pck_price_msg)
                else:
                    provider = bookingpackage.provider
                    if provider is None:
                        provider = bookingpackageallotment.provider
                    cost_groups = BookingServices.find_paxes_groups(pax_list, bookingpackageallotment.service, True)
                    cost, cost_msg = ConfigServices.allotment_costs(
                        bookingpackageallotment.service_id,
                        bookingpackageallotment.datetime_from, bookingpackageallotment.datetime_to,
                        cost_groups,
                        provider,
                        bookingpackageallotment.board_type, bookingpackageallotment.room_type_id,
                    )
                    if not bookingpackage.price_by_package_catalogue:
                        if bookingpackageallotment.manual_price:
                            price, price_msg = bookingpackageallotment.price_amount, bookingpackageallotment.price_comments
                        else:
                            price, price_msg = ConfigServices.allotment_prices(
                                bookingpackageallotment.service_id,
                                bookingpackageallotment.datetime_from, bookingpackageallotment.datetime_to,
                                price_groups,
                                agency,
                                bookingpackageallotment.board_type, bookingpackageallotment.room_type_id,
                            )
                        pck_price, pck_price_msg = cls._merge_amounts(
                            price, price_msg, pck_price, pck_price_msg)
                pck_cost, pck_cost_msg = cls._merge_amounts(cost, cost_msg, pck_cost, pck_cost_msg)

        bookingpackagetransfer_list = list(BookingPackageTransfer.objects.filter(
                booking_package=bookingpackage.id).exclude(
                    status=constants.SERVICE_STATUS_CANCELLED).all())
        if bookingpackagetransfer_list:
            for bookingpackagetransfer in bookingpackagetransfer_list:
                if bookingpackagetransfer.manual_cost:
                    cost, cost_msg = bookingpackagetransfer.cost_amount, bookingpackagetransfer.cost_comments
                    if not bookingpackage.price_by_package_catalogue:
                        if bookingpackagetransfer.manual_price:
                            price, price_msg = bookingpackagetransfer.price_amount, bookingpackagetransfer.price_comments
                        else:
                            price, price_msg = ConfigServices.transfer_prices(
                                bookingpackagetransfer.service_id,
                                bookingpackagetransfer.datetime_from, bookingpackagetransfer.datetime_to,
                                price_groups,
                                agency,
                                bookingpackagetransfer.location_from_id, bookingpackagetransfer.location_to_id,
                                bookingpackagetransfer.quantity
                            )
                        pck_price, pck_price_msg = cls._merge_amounts(
                            price, price_msg, pck_price, pck_price_msg)
                else:
                    provider = bookingpackage.provider
                    if provider is None:
                        provider = bookingpackagetransfer.provider
                    cost_groups = BookingServices.find_paxes_groups(pax_list, bookingpackagetransfer.service, True)
                    cost, cost_msg = ConfigServices.transfer_costs(
                        bookingpackagetransfer.service_id,
                        bookingpackagetransfer.datetime_from, bookingpackagetransfer.datetime_to,
                        cost_groups,
                        provider,
                        bookingpackagetransfer.location_from_id, bookingpackagetransfer.location_to_id,
                        bookingpackagetransfer.quantity
                    )
                    if not bookingpackage.price_by_package_catalogue:
                        if bookingpackagetransfer.manual_price:
                            price, price_msg = bookingpackagetransfer.price_amount, bookingpackagetransfer.price_comments
                        else:
                            price, price_msg = ConfigServices.transfer_prices(
                                bookingpackagetransfer.service_id,
                                bookingpackagetransfer.datetime_from, bookingpackagetransfer.datetime_to,
                                price_groups,
                                agency,
                                bookingpackagetransfer.location_from_id, bookingpackagetransfer.location_to_id,
                                bookingpackagetransfer.quantity
                            )
                        pck_price, pck_price_msg = cls._merge_amounts(
                            price, price_msg, pck_price, pck_price_msg)
                pck_cost, pck_cost_msg = cls._merge_amounts(cost, cost_msg, pck_cost, pck_cost_msg)

        bookingpackageextra_list = list(BookingPackageExtra.objects.filter(
                booking_package=bookingpackage.id).exclude(
                    status=constants.SERVICE_STATUS_CANCELLED).all())
        if bookingpackageextra_list:
            for bookingpackageextra in bookingpackageextra_list:
                if bookingpackageextra.manual_cost:
                    cost, cost_msg = bookingpackageextra.cost_amount, bookingpackageextra.cost_comments
                    if not bookingpackage.price_by_package_catalogue:
                        if bookingpackageextra.manual_price:
                            price, price_msg = bookingpackageextra.price_amount, bookingpackageextra.price_comments
                        else:
                            price, price_msg = ConfigServices.extra_prices(
                                bookingpackageextra.service_id,
                                bookingpackageextra.datetime_from, bookingpackageextra.datetime_to,
                                price_groups,
                                agency,
                                bookingpackageextra.addon_id, bookingpackageextra.quantity, bookingpackageextra.parameter
                            )
                        pck_price, pck_price_msg = cls._merge_amounts(
                            price, price_msg, pck_price, pck_price_msg)
                else:
                    provider = bookingpackage.provider
                    if provider is None:
                        provider = bookingpackageextra.provider
                    cost_groups = BookingServices.find_paxes_groups(pax_list, bookingpackageextra.service, True)
                    cost, cost_msg = ConfigServices.extra_costs(
                        bookingpackageextra.service_id,
                        bookingpackageextra.datetime_from, bookingpackageextra.datetime_to,
                        cost_groups,
                        provider,
                        bookingpackageextra.addon_id, bookingpackageextra.quantity, bookingpackageextra.parameter
                    )
                    if not bookingpackage.price_by_package_catalogue:
                        if bookingpackageextra.manual_price:
                            price, price_msg = bookingpackageextra.price_amount, bookingpackageextra.price_comments
                        else:
                            price, price_msg = ConfigServices.extra_prices(
                                bookingpackageextra.service_id,
                                bookingpackageextra.datetime_from, bookingpackageextra.datetime_to,
                                price_groups,
                                agency,
                                bookingpackageextra.addon_id, bookingpackageextra.quantity, bookingpackageextra.parameter
                            )
                        pck_price, pck_price_msg = cls._merge_amounts(
                            price, price_msg, pck_price, pck_price_msg)
                pck_cost, pck_cost_msg = cls._merge_amounts(cost, cost_msg, pck_cost, pck_cost_msg)

        return ConfigServices.build_amounts_result(
            pck_cost, pck_cost_msg, pck_price, pck_price_msg)


    @classmethod
    def set_bookingservice_amounts(cls, bookingservice, pax_list=None):
        if bookingservice.manual_cost is None:
            bookingservice.manual_cost = False
        if bookingservice.manual_price is None:
            bookingservice.manual_price = False
        if not bookingservice.manual_cost or not bookingservice.manual_price:
            cost, price = None, None

            if isinstance(bookingservice, BookingAllotment):
                cost, price = cls._bookingallotment_amounts(bookingservice, pax_list)
            if isinstance(bookingservice, BookingTransfer):
                cost, price = cls._bookingtransfer_amounts(bookingservice, pax_list)
            if isinstance(bookingservice, BookingExtra):
                cost, price = cls._bookingextra_amounts(bookingservice, pax_list)
            if isinstance(bookingservice, BookingPackage):
                cost, price = cls._bookingpackage_amounts(bookingservice, pax_list)
            if isinstance(bookingservice, (
                    BookingPackageAllotment, BookingPackageTransfer, BookingPackageExtra)):
                cost, price = cls._bookingpackageservice_amounts(bookingservice, pax_list)

            if not bookingservice.manual_cost:
                bookingservice.cost_amount = cost
            if not bookingservice.manual_price:
                bookingservice.price_amount = price


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
    def _find_quotepackage_amounts(cls, pax_variant, package, agency):
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

        # for saved ones use saved quote package services

        if hasattr(package, 'id') and package.id:
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

        if package.price_by_package_catalogue:

            date_from = package.datetime_from
            date_to = package.datetime_to

            price_1, price_1_msg, \
            price_2, price_2_msg, \
            price_3, price_3_msg = cls._find_quote_package_prices(
                pax_variant=pax_variant,
                service=package.service,
                date_from=date_from,
                date_to=date_to,
                agency=agency)

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
                    if package.price_by_package_catalogue:
                        c1, c1_msg, c2, c2_msg, c3, c3_msg = cls._find_quote_service_allotment_costs(
                            pax_variant=pax_variant,
                            service=allotment.service,
                            date_from=date_from,
                            date_to=date_to,
                            room_type_id=allotment.room_type_id,
                            board_type=allotment.board_type,
                            provider=provider)
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
                        c3, c3_msg, p3, p3_msg = cls._find_quote_service_allotment_amounts(
                            pax_variant=pax_variant,
                            service=allotment.service,
                            date_from=date_from,
                            date_to=date_to,
                            room_type_id=allotment.room_type_id,
                            board_type=allotment.board_type,
                            provider=provider,
                            agency=agency)
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
                    if package.price_by_package_catalogue:
                        c1, c1_msg, c2, c2_msg, c3, c3_msg = cls._find_quote_service_transfer_costs(
                            pax_variant=pax_variant,
                            service=transfer.service,
                            date_from=date_from,
                            date_to=date_to,
                            location_from_id=transfer.location_from_id,
                            location_to_id=transfer.location_to_id,
                            quantity=transfer.quantity,
                            provider=provider)
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
                        c3, c3_msg, p3, p3_msg = cls._find_quote_service_transfer_amounts(
                            pax_variant=pax_variant,
                            service=transfer.service,
                            date_from=date_from,
                            date_to=date_to,
                            location_from_id=transfer.location_from_id,
                            location_to_id=transfer.location_to_id,
                            quantity=transfer.quantity,
                            provider=provider,
                            agency=agency)
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
                    if package.price_by_package_catalogue:
                        c1, c1_msg, c2, c2_msg, c3, c3_msg = cls._find_quote_service_extra_costs(
                            pax_variant=pax_variant,
                            service=extra.service,
                            date_from=date_from,
                            date_to=date_to,
                            addon_id=extra.addon_id,
                            quantity=extra.quantity,
                            parameter=extra.parameter,
                            provider=provider)
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
                        c3, c3_msg, p3, p3_msg = cls._find_quote_service_extra_amounts(
                            pax_variant=pax_variant,
                            service=extra.service,
                            date_from=date_from,
                            date_to=date_to,
                            addon_id=extra.addon_id,
                            quantity=extra.quantity,
                            parameter=extra.parameter,
                            provider=provider,
                            agency=agency)
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
        rc1, rc1_msg = cls._merge_amounts(cost_1, cost_1_msg, c1, c1_msg)
        rc2, rc2_msg = cls._merge_amounts(cost_2, cost_2_msg, c2, c2_msg)
        rc3, rc3_msg = cls._merge_amounts(cost_3, cost_3_msg, c3, c3_msg)

        return rc1, rc1_msg, rc2, rc2_msg, rc3, rc3_msg


    @classmethod
    def _variant_totals(
            cls,
            cost_1, cost_1_msg, c1, c1_msg, price_1, price_1_msg, p1, p1_msg,
            cost_2, cost_2_msg, c2, c2_msg, price_2, price_2_msg, p2, p2_msg,
            cost_3, cost_3_msg, c3, c3_msg, price_3, price_3_msg, p3, p3_msg):
        rc1, rc1_msg = cls._merge_amounts(cost_1, cost_1_msg, c1, c1_msg)
        rp1, rp1_msg = cls._merge_amounts(price_1, price_1_msg, p1, p1_msg)
        rc2, rc2_msg = cls._merge_amounts(cost_2, cost_2_msg, c2, c2_msg)
        rp2, rp2_msg = cls._merge_amounts(price_2, price_2_msg, p2, p2_msg)
        rc3, rc3_msg = cls._merge_amounts(cost_3, cost_3_msg, c3, c3_msg)
        rp3, rp3_msg = cls._merge_amounts(price_3, price_3_msg, p3, p3_msg)

        return rc1, rc1_msg, rp1, rp1_msg, rc2, rc2_msg, rp2, rp2_msg, rc3, rc3_msg, rp3, rp3_msg


    @classmethod
    def _merge_amounts(
            cls,
            prev_amount, prev_msg, amount, msg, round_digits=2):
        if prev_amount is None:
            return None, prev_msg
        elif amount is None:
            return None, msg
        else:
            return round(float(prev_amount) + float(amount), round_digits), msg


    @classmethod
    def _update_bookingpackageservice_amounts(cls, bookingpackage_service):
        if not bookingpackage_service:
            return
        cost, price = cls._bookingpackageservice_amounts(bookingpackage_service)
        cls._save_booking_service_amounts(bookingpackage_service, cost, price)


    @classmethod
    def _find_bookingservice(cls, booking_service, manager):
        bookingservice = list(manager.filter(pk=booking_service.pk))
        if not bookingservice:
            return None
        return bookingservice[0]


    @classmethod
    def _save_booking_service_amounts(cls, booking_service, cost, price):
        fields = []
        if booking_service.cost_amount != cost:
            fields.append('cost_amount')
            booking_service.cost_amount = cost
        if booking_service.price_amount != price:
            fields.append('price_amount')
            booking_service.price_amount = price

        if fields:
            booking_service.save(update_fields=fields)


    @classmethod
    def _find_pax_list(cls, booking_service):
        return list(BookingServicePax.objects.filter(booking_service=booking_service.id).all())


    @classmethod
    def _bookingservice_manual_amounts(cls, booking_service, cost, price):
        cost_result, price_result = cost, price
        if booking_service.manual_cost:
            cost_result = booking_service.cost_amount
        if booking_service.manual_price:
            price_result = booking_service.price_amount

        return cost_result, price_result 


    @classmethod
    def _verify_booking_service_manuals(cls, booking_service):
        if booking_service.manual_cost is None:
            booking_service.manual_cost = False
        if booking_service.manual_price is None:
            booking_service.manual_price = False
        return booking_service.manual_cost and booking_service.manual_price


    @classmethod
    def _bookingallotment_amounts(cls, bookingallotment, pax_list=None):
        if cls._verify_booking_service_manuals(bookingallotment):
            return bookingallotment.cost_amount, bookingallotment.price_amount

        if not pax_list:
            pax_list = cls._find_pax_list(bookingallotment)

        cost_groups = BookingServices.find_paxes_groups(pax_list, bookingallotment.service, True)
        price_groups = BookingServices.find_paxes_groups(pax_list, bookingallotment.service, False)

        code, message, cost, cost_msg, price, price_msg = ConfigServices.allotment_amounts(
            bookingallotment.service_id,
            bookingallotment.datetime_from, bookingallotment.datetime_to,
            cost_groups, price_groups,
            bookingallotment.provider, bookingallotment.booking.agency,
            bookingallotment.board_type, bookingallotment.room_type_id)

        return cls._bookingservice_manual_amounts(bookingallotment, cost, price)


    @classmethod
    def _bookingtransfer_amounts(cls, bookingtransfer, pax_list=None):
        if cls._verify_booking_service_manuals(bookingtransfer):
            return bookingtransfer.cost_amount, bookingtransfer.price_amount

        if not pax_list:
            pax_list = cls._find_pax_list(bookingtransfer)

        cost_groups = BookingServices.find_paxes_groups(pax_list, bookingtransfer.service, True)
        price_groups = BookingServices.find_paxes_groups(pax_list, bookingtransfer.service, False)

        code, message, cost, cost_msg, price, price_msg = ConfigServices.transfer_amounts(
            bookingtransfer.service_id, bookingtransfer.datetime_from, bookingtransfer.datetime_to, cost_groups, price_groups,
            bookingtransfer.provider, bookingtransfer.booking.agency,
            bookingtransfer.location_from_id, bookingtransfer.location_to_id, bookingtransfer.quantity)

        return cls._bookingservice_manual_amounts(bookingtransfer, cost, price)


    @classmethod
    def _bookingextra_amounts(cls, bookingextra, pax_list=None):
        if cls._verify_booking_service_manuals(bookingextra):
            return bookingextra.cost_amount, bookingextra.price_amount

        if not pax_list:
            pax_list = cls._find_pax_list(bookingextra)

        cost_groups = BookingServices.find_paxes_groups(pax_list, bookingextra.service, True)
        price_groups = BookingServices.find_paxes_groups(pax_list, bookingextra.service, False)

        code, message, cost, cost_msg, price, price_msg = ConfigServices.extra_amounts(
            bookingextra.service_id, bookingextra.datetime_from, bookingextra.datetime_to, cost_groups, price_groups,
            bookingextra.provider, bookingextra.booking.agency,
            bookingextra.addon_id, bookingextra.quantity, bookingextra.parameter)

        return cls._bookingservice_manual_amounts(bookingextra, cost, price)


    @classmethod
    def _bookingpackage_amounts(cls, bookingpackage, pax_list=None):
        if cls._verify_booking_service_manuals(bookingpackage):
            return bookingpackage.cost_amount, bookingpackage.price_amount

        if not pax_list:
            pax_list = cls._find_pax_list(bookingpackage)

        code, msg, pck_cost, pck_cost_msg, pck_price, pck_price_msg = cls.bookingpackage_amounts(
            bookingpackage, pax_list)

        return cls._bookingservice_manual_amounts(bookingpackage, pck_cost, pck_price)


    @classmethod
    def _bookingpackageservice_amounts(cls, bookingpackage_service, pax_list=None):
        if not pax_list:
            pax_list = cls._find_pax_list(bookingpackage_service.booking_package)

        cost_groups = BookingServices.find_paxes_groups(
            pax_list, bookingpackage_service.booking_package.service, True)
        price_groups = BookingServices.find_paxes_groups(
            pax_list, bookingpackage_service.booking_package.service, False)

        service_provider = bookingpackage_service.booking_package.provider
        if service_provider is None:
            service_provider = bookingpackage_service.provider

        cost, price = None, None
        if isinstance(bookingpackage_service, BookingPackageAllotment):
            code, msg, cost, cost_msg, price, price_msg = ConfigServices.allotment_amounts(
                bookingpackage_service.service,
                bookingpackage_service.datetime_from, bookingpackage_service.datetime_to,
                cost_groups, price_groups, service_provider,
                bookingpackage_service.booking_package.booking.agency,
                bookingpackage_service.board_type, bookingpackage_service.room_type_id)
        if isinstance(bookingpackage_service, BookingPackageTransfer):
            code, msg, cost, cost_msg, price, price_msg = ConfigServices.transfer_amounts(
                bookingpackage_service.service,
                bookingpackage_service.datetime_from, bookingpackage_service.datetime_to,
                cost_groups, price_groups, service_provider,
                bookingpackage_service.booking_package.booking.agency,
                bookingpackage_service.location_from_id, bookingpackage_service.location_to_id,
                bookingpackage_service.quantity)
        if isinstance(bookingpackage_service, BookingPackageExtra):
            code, msg, cost, cost_msg, price, price_msg = ConfigServices.extra_amounts(
                bookingpackage_service.service,
                bookingpackage_service.datetime_from, bookingpackage_service.datetime_to,
                cost_groups, price_groups, service_provider,
                bookingpackage_service.booking_package.booking.agency,
                bookingpackage_service.addon_id,
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
    def _find_pax_variant(cls, quote, rooming):
        pax_qtty = 0
        for pax in rooming:
            if pax['pax_name'] and pax['pax_group']:
                pax_qtty += 1
        variants = list(
            QuotePaxVariant.objects.filter(quote=quote.id).all().order_by('pax_quantity'))
        result = variants[0]
        for variant in variants:
            if variant.pax_quantity < pax_qtty:
                result = variant
        return result


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


    @classmethod
    def _find_quoteallotment_amounts(cls, pax_variant, allotment, agency):
        return cls._find_quote_service_allotment_amounts(
            pax_variant=pax_variant,
            service=allotment.service,
            date_from=allotment.datetime_from,
            date_to=allotment.datetime_to,
            room_type_id=allotment.room_type_id,
            board_type=allotment.board_type,
            provider=allotment.provider,
            agency=agency)


    @classmethod
    def _find_quote_service_allotment_amounts(
            cls, pax_variant, service, date_from, date_to,
            room_type_id, board_type, provider, agency):
        if service.grouping:
            # grouping means passing 1,2,3 as pax quantity
            code, msg, c1, c1_msg, p1, p1_msg = ConfigServices.allotment_amounts(
                service, date_from, date_to, ({0:1, 1:0},), ({0:1, 1:0},), provider, agency,
                board_type, room_type_id)
            if c1:
                c1 = round(float(c1), 2)
            if p1:
                p1 = round(0.499999 + float(p1))
            code, msg, c2, c2_msg, p2, p2_msg = ConfigServices.allotment_amounts(
                service, date_from, date_to, ({0:2, 1:0},), ({0:2, 1:0},), provider, agency,
                board_type, room_type_id)
            if c2:
                c2 = round(float(c2) / 2, 2)
            if p2:
                p2 = round(0.499999 + float(p2) / 2)
            code, msg, c3, c3_msg, p3, p3_msg = ConfigServices.allotment_amounts(
                service, date_from, date_to, ({0:3, 1:0},), ({0:3, 1:0},), provider, agency,
                board_type, room_type_id)
            if c3:
                c3 = round(float(c3) / 3, 2)
            if p3:
                p3 = round(0.499999 + float(p3) / 3)
        else:
            # no grouping means passing total pax quantity
            code, msg, c1, c1_msg, p1, p1_msg = ConfigServices.allotment_amounts(
                service, date_from, date_to,
                ({0:pax_variant.pax_quantity, 1:0},), ({0:pax_variant.pax_quantity, 1:0},),
                provider, agency,
                board_type, room_type_id)
            if c1:
                c1 = round(float(c1) / pax_variant.pax_quantity, 2)
            if p1:
                p1 = round(0.499999 + float(p1) / pax_variant.pax_quantity)
            c2, c2_msg, p2, p2_msg = c1, c1_msg, p1, p1_msg
            c3, c3_msg, p3, p3_msg = c1, c1_msg, p1, p1_msg
        return c1, c1_msg, p1, p1_msg, c2, c2_msg, p2, p2_msg, c3, c3_msg, p3, p3_msg


    @classmethod
    def _find_quote_service_allotment_costs(
            cls, pax_variant, service, date_from, date_to,
            room_type_id, board_type, provider):
        if service.grouping:
            # grouping means passing 1,2,3 as pax quantity
            c1, c1_msg = ConfigServices.allotment_costs(
                service, date_from, date_to, ({0:1, 1:0},), provider, board_type, room_type_id)
            if c1:
                c1 = round(float(c1), 2)
            c2, c2_msg = ConfigServices.allotment_costs(
                service, date_from, date_to, ({0:2, 1:0},), provider, board_type, room_type_id)
            if c2:
                c2 = round(float(c2) / 2, 2)
            c3, c3_msg = ConfigServices.allotment_costs(
                service, date_from, date_to, ({0:3, 1:0},),provider, board_type, room_type_id)
            if c3:
                c3 = round(float(c3) / 3, 2)
        else:
            # no grouping means passing total pax quantity
            c1, c1_msg = ConfigServices.allotment_costs(
                service, date_from, date_to, ({0:pax_variant.pax_quantity, 1:0},),
                provider, board_type, room_type_id)
            if c1:
                c1 = round(float(c1) / pax_variant.pax_quantity, 2)
            c2, c2_msg, c3, c3_msg = c1, c1_msg, c1, c1_msg
        return c1, c1_msg, c2, c2_msg, c3, c3_msg


    @classmethod
    def _find_quotetransfer_amounts(cls, pax_variant, transfer, agency):
        return cls._find_quote_service_transfer_amounts(
            pax_variant=pax_variant,
            service=transfer.service,
            date_from=transfer.datetime_from,
            date_to=transfer.datetime_to,
            location_from_id=transfer.location_from_id,
            location_to_id=transfer.location_to_id,
            quantity=transfer.quantity,
            provider=transfer.provider,
            agency=agency)


    @classmethod
    def _find_quote_service_transfer_amounts(
            cls, pax_variant, service, date_from, date_to,
            location_from_id, location_to_id, quantity, provider, agency):
        if service.grouping:
            # grouping means passing 1,2,3 as pax quantity
            code, msg, c1, c1_msg, p1, p1_msg = ConfigServices.transfer_amounts(
                service, date_from, date_to, ({0:1, 1:0},), ({0:1, 1:0},), provider, agency,
                location_from_id, location_to_id, quantity)
            if c1:
                c1 = round(float(c1), 2)
            if p1:
                p1 = round(0.499999 + float(p1))
            code, msg, c2, c2_msg, p2, p2_msg = ConfigServices.transfer_amounts(
                service, date_from, date_to, ({0:2, 1:0},), ({0:2, 1:0},), provider, agency,
                location_from_id, location_to_id, quantity)
            if c2:
                c2 = round(float(c2) / 2, 2)
            if p2:
                p2 = round(0.499999 + float(p2) / 2)
            code, msg, c3, c3_msg, p3, p3_msg = ConfigServices.transfer_amounts(
                service, date_from, date_to, ({0:3, 1:0},), ({0:3, 1:0},), provider, agency,
                location_from_id, location_to_id, quantity)
            if c3:
                c3 = round(float(c3) / 3, 2)
            if p3:
                p3 = round(0.499999 + float(p3) / 3)
        else:
            # no grouping means passing total pax quantity
            code, msg, c1, c1_msg, p1, p1_msg = ConfigServices.transfer_amounts(
                service, date_from, date_to,
                ({0:pax_variant.pax_quantity, 1:0},), ({0:pax_variant.pax_quantity, 1:0},),
                provider, agency,
                location_from_id, location_to_id, quantity)
            if c1:
                c1 = round(float(c1) / pax_variant.pax_quantity, 2)
            if p1:
                p1 = round(0.499999 + float(p1) / pax_variant.pax_quantity)
            c2, c2_msg, p2, p2_msg = c1, c1_msg, p1, p1_msg
            c3, c3_msg, p3, p3_msg = c1, c1_msg, p1, p1_msg
        return c1, c1_msg, p1, p1_msg, c2, c2_msg, p2, p2_msg, c3, c3_msg, p3, p3_msg


    @classmethod
    def _find_quote_service_transfer_costs(
            cls, pax_variant, service, date_from, date_to,
            location_from_id, location_to_id, quantity, provider):
        if service.grouping:
            # grouping means passing 1,2,3 as pax quantity
            c1, c1_msg = ConfigServices.transfer_costs(
                service, date_from, date_to, ({0:1, 1:0},), provider,
                location_from_id, location_to_id, quantity)
            if c1:
                c1 = round(float(c1), 2)
            c2, c2_msg = ConfigServices.transfer_costs(
                service, date_from, date_to, ({0:2, 1:0},), provider,
                location_from_id, location_to_id, quantity)
            if c2:
                c2 = round(float(c2) / 2, 2)
            c3, c3_msg = ConfigServices.transfer_costs(
                service, date_from, date_to, ({0:3, 1:0},), provider,
                location_from_id, location_to_id, quantity)
            if c3:
                c3 = round(float(c3) / 3, 2)
        else:
            # no grouping means passing total pax quantity
            c1, c1_msg = ConfigServices.transfer_costs(
                service, date_from, date_to,
                ({0:pax_variant.pax_quantity, 1:0},), provider,
                location_from_id, location_to_id, quantity)
            if c1:
                c1 = round(float(c1) / pax_variant.pax_quantity, 2)
            c2, c2_msg, c3, c3_msg = c1, c1_msg, c1, c1_msg
        return c1, c1_msg, c2, c2_msg, c3, c3_msg


    @classmethod
    def _find_quoteextra_amounts(cls, pax_variant, extra, agency):
        return cls._find_quote_service_extra_amounts(
            pax_variant=pax_variant,
            service=extra.service,
            date_from=extra.datetime_from,
            date_to=extra.datetime_to,
            addon_id=extra.addon_id,
            quantity=extra.quantity,
            parameter=extra.parameter,
            provider=extra.provider,
            agency=agency)


    @classmethod
    def _find_quote_service_extra_amounts(
            cls, pax_variant, service, date_from, date_to,
            addon_id, quantity, parameter, provider, agency):
        if service.grouping:
            # grouping means passing 1,2,3 as pax quantity
            code, msg, c1, c1_msg, p1, p1_msg = ConfigServices.extra_amounts(
                service, date_from, date_to, ({0:1, 1:0},), ({0:1, 1:0},), provider, agency,
                addon_id, quantity, parameter)
            if c1:
                c1 = round(float(c1), 2)
            if p1:
                p1 = round(0.499999 + float(p1))
            code, msg, c2, c2_msg, p2, p2_msg = ConfigServices.extra_amounts(
                service, date_from, date_to, ({0:2, 1:0},), ({0:2, 1:0},), provider, agency,
                addon_id, quantity, parameter)
            if c2:
                c2 = round(float(c2) / 2, 2)
            if p2:
                p2 = round(0.499999 + float(p2))
            code, msg, c3, c3_msg, p3, p3_msg = ConfigServices.extra_amounts(
                service, date_from, date_to, ({0:3, 1:0},), ({0:3, 1:0},), provider, agency,
                addon_id, quantity, parameter)
            if c3:
                c3 = round(float(c3) / 2, 2)
            if p3:
                p3 = round(0.499999 + float(p3))
        else:
            # no grouping means passing total pax quantity
            code, msg, c1, c1_msg, p1, p1_msg = ConfigServices.extra_amounts(
                service, date_from, date_to,
                ({0:pax_variant.pax_quantity, 1:0},), ({0:pax_variant.pax_quantity, 1:0},),
                provider, agency,
                addon_id, quantity, parameter)
            if c1:
                c1 = round(float(c1) / pax_variant.pax_quantity, 2)
            if p1:
                p1 = round(0.499999 + float(p1) / pax_variant.pax_quantity)
            c2, c2_msg, p2, p2_msg = c1, c1_msg, p1, p1_msg
            c3, c3_msg, p3, p3_msg = c1, c1_msg, p1, p1_msg
        return c1, c1_msg, p1, p1_msg, c2, c2_msg, p2, p2_msg, c3, c3_msg, p3, p3_msg


    @classmethod
    def _find_quote_service_extra_costs(
            cls, pax_variant, service, date_from, date_to,
            addon_id, quantity, parameter, provider):
        if service.grouping:
            # grouping means passing 1,2,3 as pax quantity
            c1, c1_msg = ConfigServices.extra_costs(
                service, date_from, date_to, ({0:1, 1:0},), provider,
                addon_id, quantity, parameter)
            if c1:
                c1 = round(float(c1), 2)
            c2, c2_msg = ConfigServices.extra_costs(
                service, date_from, date_to, ({0:2, 1:0},), provider,
                addon_id, quantity, parameter)
            if c2:
                c2 = round(float(c2) / 2, 2)
            c3, c3_msg = ConfigServices.extra_costs(
                service, date_from, date_to, ({0:3, 1:0},), provider,
                addon_id, quantity, parameter)
            if c3:
                c3 = round(float(c3) / 2, 2)
        else:
            # no grouping means passing total pax quantity
            c1, c1_msg = ConfigServices.extra_costs(
                service, date_from, date_to,
                ({0:pax_variant.pax_quantity, 1:0},), provider,
                addon_id, quantity, parameter)
            if c1:
                c1 = round(float(c1) / pax_variant.pax_quantity, 2)
            c2, c2_msg, c3, c3_msg = c1, c1_msg, c1, c1_msg
        return c1, c1_msg, c2, c2_msg, c3, c3_msg


    @classmethod
    def _find_quote_package_prices(
        cls, pax_variant, service, date_from, date_to, agency):
        p1, p1_msg = cls.package_price(
            service, date_from, date_to, ({0:pax_variant.pax_quantity, 1:0},), agency)
        if p1:
            p1 = round(0.499999 + float(p1) / pax_variant.pax_quantity)
        p2, p2_msg, p3, p3_msg = p1, p1_msg, p1, p1_msg
        return p1, p1_msg, p2, p2_msg, p3, p3_msg


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
    def sync_pax_variants(cls, view_quote_pax_variant):
        if isinstance(view_quote_pax_variant, Quote):
            quote = view_quote_pax_variant
        else:
            quote = view_quote_pax_variant.quote
        # verify on all services if pax variant exists
        quote_services = list(QuoteService.objects.all().filter(
            quote=quote))
        quote_pax_variants = list(QuotePaxVariant.objects.all().filter(
            quote=quote))

        for quote_service in quote_services:
            for quote_pax_variant in quote_pax_variants:
                try:
                    quote_service_pax_variant, created = QuoteServicePaxVariant.objects.update_or_create(
                        quote_pax_variant_id=quote_pax_variant.id,
                        quote_service_id=quote_service.id,
                        defaults=cls._calculate_default_service_pax_variant_amounts(
                            quote_service, quote_pax_variant, True)
                    )
                    if quote_service.service_type == constants.SERVICE_CATEGORY_PACKAGE:
                        # verify on all services if pax variant exists
                        quotepackage_services = list(QuotePackageService.objects.all().filter(
                            quote_package=quote_service.id))

                        for quotepackage_service in quotepackage_services:
                            quotepackage_service_pax_variant, created = QuotePackageServicePaxVariant.objects.update_or_create(
                                quotepackage_pax_variant_id=quote_service_pax_variant.id,
                                quotepackage_service_id=quotepackage_service.id,
                                defaults=cls._calculate_default_service_pax_variant_amounts(
                                    quotepackage_service, quote_service_pax_variant, True)
                                )
                except Exception as ex:
                    print(ex)
        return


    @classmethod
    def update_service_pax_variants_amounts(cls, quote_service):
        quote = quote_service.quote
        # find quote pax variants
        quote_pax_variants = list(QuotePaxVariant.objects.all().filter(quote=quote.id))
        # for each quote pax variant get or create
        for quote_pax_variant in quote_pax_variants:
            defaults = cls._calculate_default_service_pax_variant_amounts(
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
                    if obj.cost_single_amount != defaults['cost_single_amount']:
                        fields.append('cost_single_amount')
                        obj.cost_single_amount = defaults['cost_single_amount']

                    if obj.cost_double_amount != defaults['cost_double_amount']:
                        fields.append('cost_double_amount')
                        obj.cost_double_amount = defaults['cost_double_amount']

                    if obj.cost_triple_amount != defaults['cost_triple_amount']:
                        fields.append('cost_triple_amount')
                        obj.cost_triple_amount = defaults['cost_triple_amount']

                if not obj.manual_prices:
                    if obj.price_single_amount != defaults['price_single_amount']:
                        fields.append('price_single_amount')
                        obj.price_single_amount = defaults['price_single_amount']

                    if obj.price_double_amount != defaults['price_double_amount']:
                        fields.append('price_double_amount')
                        obj.price_double_amount = defaults['price_double_amount']

                    if obj.price_triple_amount != defaults['price_triple_amount']:
                        fields.append('price_triple_amount')
                        obj.price_triple_amount = defaults['price_triple_amount']

                if fields:
                    obj.save(update_fields=fields)
                    cls.update_quote_pax_variant_amounts(quote_pax_variant)

            except QuoteServicePaxVariant.DoesNotExist:
                new_values = {
                    'quote_service_id': quote_service.id,
                    'quote_pax_variant_id': quote_pax_variant.id}
                new_values.update(defaults)
                obj = QuoteServicePaxVariant(**new_values)
                obj.save()
                cls.update_quote_pax_variant_amounts(quote_pax_variant)


    @classmethod
    def _find_quoteservice_pax_variant_amounts(cls, in_quote_service, quote_pax_variant, for_update=False):
        if isinstance(in_quote_service, QuoteService):
            if in_quote_service.service_type == constants.SERVICE_CATEGORY_ALLOTMENT:
                quote_service = QuoteAllotment.objects.get(pk=in_quote_service.id)
            elif in_quote_service.service_type == constants.SERVICE_CATEGORY_TRANSFER:
                quote_service = QuoteTransfer.objects.get(pk=in_quote_service.id)
            elif in_quote_service.service_type == constants.SERVICE_CATEGORY_EXTRA:
                quote_service = QuoteExtra.objects.get(pk=in_quote_service.id)
            elif in_quote_service.service_type == constants.SERVICE_CATEGORY_PACKAGE:
                quote_service = QuotePackage.objects.get(pk=in_quote_service.id)
            else:
                return None, "Unknow Service", None, "Unknow Service", None, "Unknow Service", None, "Unknow Service", None, "Unknow Service", None, "Unknow Service"
        else:
            quote_service = in_quote_service

        if isinstance(quote_service, QuoteAllotment):
            c1, c1_msg, p1, p1_msg, \
            c2, c2_msg, p2, p2_msg, \
            c3, c3_msg, p3, p3_msg = cls._find_quoteallotment_amounts(
                pax_variant=quote_pax_variant, allotment=quote_service, agency=quote_service.quote.agency)
        elif isinstance(quote_service, QuoteTransfer):
            c1, c1_msg, p1, p1_msg, \
            c2, c2_msg, p2, p2_msg, \
            c3, c3_msg, p3, p3_msg = cls._find_quotetransfer_amounts(
                pax_variant=quote_pax_variant, transfer=quote_service, agency=quote_service.quote.agency)
        elif isinstance(quote_service, QuoteExtra):
            c1, c1_msg, p1, p1_msg, \
            c2, c2_msg, p2, p2_msg, \
            c3, c3_msg, p3, p3_msg = cls._find_quoteextra_amounts(
                pax_variant=quote_pax_variant, extra=quote_service, agency=quote_service.quote.agency)
        elif isinstance(quote_service, QuotePackage):
            return cls._find_quotepackage_amounts(
                pax_variant=quote_pax_variant, package=quote_service, agency=quote_service.quote.agency)
        else:
            return None, "Unknow Service", None, "Unknow Service", None, "Unknow Service", None, "Unknow Service", None, "Unknow Service", None, "Unknow Service"
        if for_update:
            try:
                quoteservice_pax_variant = QuoteServicePaxVariant.objects.get(
                    quote_service_id=quote_service.id,
                    quote_pax_variant_id=quote_pax_variant.id)
                if quoteservice_pax_variant.manual_costs:
                    c1, c1_msg = quoteservice_pax_variant.cost_single_amount, None
                    c2, c2_msg = quoteservice_pax_variant.cost_double_amount, None
                    c3, c3_msg = quoteservice_pax_variant.cost_triple_amount, None
                if quoteservice_pax_variant.manual_prices:
                    p1, p1_msg = quoteservice_pax_variant.price_single_amount, None
                    p2, p2_msg = quoteservice_pax_variant.price_double_amount, None
                    p3, p3_msg = quoteservice_pax_variant.price_triple_amount, None

            except QuoteServicePaxVariant.DoesNotExist:
                pass

        return c1, c1_msg, p1, p1_msg, c2, c2_msg, p2, p2_msg, c3, c3_msg, p3, p3_msg

    @classmethod
    def _calculate_default_service_pax_variant_amounts(cls, quote_service, quote_pax_variant, for_update=True):

        c1, c1_msg, p1, p1_msg, \
        c2, c2_msg, p2, p2_msg, \
        c3, c3_msg, p3, p3_msg = cls._find_quoteservice_pax_variant_amounts(
                quote_service, quote_pax_variant, for_update)

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
            defaults = cls._calculate_default_service_pax_variant_amounts(
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
                    if obj.cost_single_amount != defaults['cost_single_amount']:
                        fields.append('cost_single_amount')
                        obj.cost_single_amount = defaults['cost_single_amount']

                    if obj.cost_double_amount != defaults['cost_double_amount']:
                        fields.append('cost_double_amount')
                        obj.cost_double_amount = defaults['cost_double_amount']

                    if obj.cost_triple_amount != defaults['cost_triple_amount']:
                        fields.append('cost_triple_amount')
                        obj.cost_triple_amount = defaults['cost_triple_amount']

                if not obj.manual_prices:
                    if obj.price_single_amount != defaults['price_single_amount']:
                        fields.append('price_single_amount')
                        obj.price_single_amount = defaults['price_single_amount']

                    if obj.price_double_amount != defaults['price_double_amount']:
                        fields.append('price_double_amount')
                        obj.price_double_amount = defaults['price_double_amount']

                    if obj.price_triple_amount != defaults['price_triple_amount']:
                        fields.append('price_triple_amount')
                        obj.price_triple_amount = defaults['price_triple_amount']

                if fields:
                    obj.save(update_fields=fields)
                    cls.update_quotepackage_pax_variant_amounts(obj)

            except QuotePackageServicePaxVariant.DoesNotExist:
                new_values = {
                    'quotepackage_service_id': quotepackage_service.id,
                    'quotepackage_pax_variant_id': quotepackage_pax_variant.id}
                new_values.update(defaults)
                obj = QuotePackageServicePaxVariant(**new_values)
                obj.save()
                cls.update_quotepackage_pax_variant_amounts(obj)


    @classmethod
    def update_quote_pax_variant_amounts(cls, quoteservice_pax_variant):
        if isinstance(quoteservice_pax_variant, QuotePaxVariant):
            quote_pax_variant = quoteservice_pax_variant
        else:
            quote_pax_variant = QuotePaxVariant.objects.get(
                pk=quoteservice_pax_variant.quote_pax_variant.id)

        quoteservice_pax_variants = list(
            QuoteServicePaxVariant.objects.all().filter(
                quote_pax_variant=quote_pax_variant.id).exclude(
                    quote_service__status=constants.SERVICE_STATUS_CANCELLED))

        if quoteservice_pax_variants:
            cost_single_amount, cost_double_amount, cost_triple_amount = 0, 0, 0
            price_single_amount, price_double_amount, price_triple_amount = 0, 0, 0
            for quoteservice_pax_variant in quoteservice_pax_variants:
                cost_single_amount = cls.totalize(
                    cost_single_amount, quoteservice_pax_variant.cost_single_amount)
                cost_double_amount = cls.totalize(
                    cost_double_amount, quoteservice_pax_variant.cost_double_amount)
                cost_triple_amount = cls.totalize(
                    cost_triple_amount, quoteservice_pax_variant.cost_triple_amount)
                price_single_amount = cls.totalize(
                    price_single_amount, quoteservice_pax_variant.price_single_amount)
                price_double_amount = cls.totalize(
                    price_double_amount, quoteservice_pax_variant.price_double_amount)
                price_triple_amount = cls.totalize(
                    price_triple_amount, quoteservice_pax_variant.price_triple_amount)
        else:
            cost_single_amount, cost_double_amount, cost_triple_amount = None, None, None
            price_single_amount, price_double_amount, price_triple_amount = None, None, None

        fields = []
        if quote_pax_variant.cost_single_amount != cost_single_amount:
            fields.append('cost_single_amount')
            quote_pax_variant.cost_single_amount = cost_single_amount

        if quote_pax_variant.cost_double_amount != cost_double_amount:
            fields.append('cost_double_amount')
            quote_pax_variant.cost_double_amount = cost_double_amount

        if quote_pax_variant.cost_triple_amount != cost_triple_amount:
            fields.append('cost_triple_amount')
            quote_pax_variant.cost_triple_amount = cost_triple_amount

        if quote_pax_variant.price_single_amount != price_single_amount:
            fields.append('price_single_amount')
            quote_pax_variant.price_single_amount = price_single_amount

        if quote_pax_variant.price_double_amount != price_double_amount:
            fields.append('price_double_amount')
            quote_pax_variant.price_double_amount = price_double_amount

        if quote_pax_variant.price_triple_amount != price_triple_amount:
            fields.append('price_triple_amount')
            quote_pax_variant.price_triple_amount = price_triple_amount

        if fields:
            quote_pax_variant.save(update_fields=fields)


    @classmethod
    def update_quotepackage_pax_variant_amounts(cls, quotepackageservice_pax_variant):
        if isinstance(quotepackageservice_pax_variant, QuoteServicePaxVariant):
            quotepackage_pax_variant = quotepackageservice_pax_variant
        else:
            quotepackage_pax_variant = quotepackageservice_pax_variant.quotepackage_pax_variant

        quotepackageservices_pax_variants = list(
            QuotePackageServicePaxVariant.objects.all().filter(
                quotepackage_pax_variant=quotepackage_pax_variant.id).exclude(
                    quotepackage_service__status=constants.SERVICE_STATUS_CANCELLED))

        if quotepackageservices_pax_variants:
            cost_single_amount, cost_double_amount, cost_triple_amount = 0, 0, 0
            price_single_amount, price_double_amount, price_triple_amount = 0, 0, 0
            for quotepackageservice_pax_variant in quotepackageservices_pax_variants:
                cost_single_amount = cls.totalize(
                    cost_single_amount, quotepackageservice_pax_variant.cost_single_amount)
                cost_double_amount = cls.totalize(
                    cost_double_amount, quotepackageservice_pax_variant.cost_double_amount)
                cost_triple_amount = cls.totalize(
                    cost_triple_amount, quotepackageservice_pax_variant.cost_triple_amount)
                price_single_amount = cls.totalize(
                    price_single_amount, quotepackageservice_pax_variant.price_single_amount)
                price_double_amount = cls.totalize(
                    price_double_amount, quotepackageservice_pax_variant.price_double_amount)
                price_triple_amount = cls.totalize(
                    price_triple_amount, quotepackageservice_pax_variant.price_triple_amount)
        else:
            cost_single_amount, cost_double_amount, cost_triple_amount = None, None, None
            price_single_amount, price_double_amount, price_triple_amount = None, None, None

        fields = []
        if quotepackage_pax_variant.cost_single_amount != cost_single_amount:
            fields.append('cost_single_amount')
            quotepackage_pax_variant.cost_single_amount = cost_single_amount

        if quotepackage_pax_variant.cost_double_amount != cost_double_amount:
            fields.append('cost_double_amount')
            quotepackage_pax_variant.cost_double_amount = cost_double_amount

        if quotepackage_pax_variant.cost_triple_amount != cost_triple_amount:
            fields.append('cost_triple_amount')
            quotepackage_pax_variant.cost_triple_amount = cost_triple_amount

        if quotepackage_pax_variant.price_single_amount != price_single_amount:
            fields.append('price_single_amount')
            quotepackage_pax_variant.price_single_amount = price_single_amount

        if quotepackage_pax_variant.price_double_amount != price_double_amount:
            fields.append('price_double_amount')
            quotepackage_pax_variant.price_double_amount = price_double_amount

        if quotepackage_pax_variant.price_triple_amount != price_triple_amount:
            fields.append('price_triple_amount')
            quotepackage_pax_variant.price_triple_amount = price_triple_amount

        if fields:
            quotepackage_pax_variant.save(update_fields=fields)
            cls.update_quote_pax_variant_amounts(quotepackage_pax_variant)


    @classmethod
    def totalize(cls, total, increment):
        if total is None or increment is None:
            return None
        return total + increment


    @classmethod
    def update_quotepackage(cls, quotepackage_or_service):

        if hasattr(quotepackage_or_service, 'avoid_quotepackage_update'):
            return
        if hasattr(quotepackage_or_service, 'quote_package'):
            quote_package = quotepackage_or_service.quote_package
        elif isinstance(quotepackage_or_service, QuotePackage):
            quote_package = quotepackage_or_service
        else:
            return

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
            quote_package.save(update_fields=fields)
