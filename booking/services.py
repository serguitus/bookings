"""
Booking Service
"""
from datetime import date, timedelta

from django.db import transaction

from booking import constants
from booking.models import (
    Quote,
    QuoteAllotment, QuoteTransfer, QuoteExtra, QuotePackage,
    QuotePackageAllotment, QuotePackageTransfer, QuotePackageExtra,
    Package, PackageAllotment, PackageTransfer, PackageExtra,
    Booking, BookingService, BookingPax, BookingServicePax,
    BookingAllotment, BookingTransfer, BookingExtra,
    BookingInvoice, BookingInvoiceLine, BookingInvoicePartial)

from config.services import ConfigService

from finance.constants import STATUS_CANCELLED, STATUS_READY
from finance.services import FinanceService


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
                booking.save()
                # create bookingpax list
                booking_pax_list = list()
                for pax in rooming:
                    if pax['pax_name'] and pax['pax_group']:
                        booking_pax = BookingPax()
                        booking_pax.booking = booking
                        booking_pax.pax_name = pax['pax_name']
                        booking_pax.pax_age = pax['pax_age']
                        booking_pax.pax_group = pax['pax_group']
                        booking_pax.save()
                        booking_pax_list.append(booking_pax)
                # create bookingallotment list
                for quote_allotment in QuoteAllotment.objects.filter(quote_id=quote.id).all():
                    booking_allotment = BookingAllotment()
                    booking_allotment.booking = booking
                    booking_allotment.conf_number = '< confirm number >'
                    # cost_amount
                    # cost_comment
                    # price_amount
                    # price_comment
                    # provider_invoice
                    booking_allotment.name = quote_allotment.name
                    # service_type auto
                    cls.copy_service_info(
                        dst_service=booking_allotment, src_service=quote_allotment)
                    booking_allotment.room_type = quote_allotment.room_type
                    booking_allotment.board_type = quote_allotment.board_type
                    booking_allotment.save()
                    # create bookingservicepax list
                    for booking_pax in booking_pax_list:
                        bookingservice_pax = BookingServicePax()
                        bookingservice_pax.booking_service = booking_allotment
                        bookingservice_pax.booking_pax = booking_pax
                        bookingservice_pax.group = booking_pax.pax_group
                        bookingservice_pax.save()

                # create bookingtransfer list
                for quote_transfer in QuoteTransfer.objects.filter(quote_id=quote.id).all():
                    booking_transfer = BookingTransfer()
                    booking_transfer.booking = booking
                    booking_transfer.conf_number = '< confirm number >'
                    # cost_amount
                    # cost_comment
                    # price_amount
                    # price_comment
                    # provider_invoice
                    booking_transfer.name = quote_transfer.name
                    # service_type auto
                    cls.copy_service_info(dst_service=booking_transfer, src_service=quote_transfer)
                    # time
                    booking_transfer.quantity = ConfigService.get_service_quantity(
                        booking_transfer.service, len(booking_pax_list))
                    booking_transfer.location_from = quote_transfer.location_from
                    # place_from
                    # schedule_from
                    # pickup
                    booking_transfer.location_to = quote_transfer.location_to
                    # place_to
                    # schedule_to
                    # dropoff
                    booking_transfer.save()

                    # create bookingservicepax list
                    for booking_pax in booking_pax_list:
                        bookingservice_pax = BookingServicePax()
                        bookingservice_pax.booking_service = booking_transfer
                        bookingservice_pax.booking_pax = booking_pax
                        bookingservice_pax.group = booking_pax.pax_group
                        bookingservice_pax.save()

                # create bookingextra list
                for quote_extra in QuoteExtra.objects.filter(quote_id=quote.id).all():
                    booking_extra = BookingExtra()
                    booking_extra.booking = booking
                    booking_extra.conf_number = '< confirm number >'
                    # cost_amount
                    # cost_comment
                    # price_amount
                    # price_comment
                    # provider_invoice
                    booking_extra.name = quote_extra.name
                    # service_type auto
                    cls.copy_service_info(dst_service=booking_extra, src_service=quote_extra)
                    booking_extra.addon = quote_extra.addon
                    booking_extra.time = quote_extra.time
                    booking_extra.quantity = quote_extra.quantity
                    booking_extra.parameter = quote_extra.parameter
                    booking_extra.save()

                    # create bookingservicepax list
                    for booking_pax in booking_pax_list:
                        bookingservice_pax = BookingServicePax()
                        bookingservice_pax.booking_service = booking_extra
                        bookingservice_pax.booking_pax = booking_pax
                        bookingservice_pax.group = booking_pax.pax_group
                        bookingservice_pax.save()

                # update booking
                cls.update_booking(booking)
                return booking, 'Booking Succesfully Created'
        except Exception as ex:
            return None, 'Error on Booking Building : %s' % (ex)
        return None, 'Error on Booking Building'

    @classmethod
    def update_quote(cls, quote):
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
        print ('ENTRANDO B for de allotment')
        package = quote_package.service
        # create bookingallotment list
        print ('ENTRANDO A for de allotment')
        for package_allotment in PackageAllotment.objects.filter(package_id=package.id).all():
            print ('EN for de allotment')
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
            cls.copy_package_info(
                dst_package=quote_package_allotment, src_package=package_allotment)
            quote_package_allotment.room_type = package_allotment.room_type
            quote_package_allotment.board_type = package_allotment.board_type
            quote_package_allotment.save()

        # create bookingtransfer list
        print ('ENTRANDO A for de transfer')
        for package_transfer in PackageTransfer.objects.filter(package_id=package.id).all():
            print ('EN for de transfer')
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
            cls.copy_package_info(
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
            cls.copy_package_info(
                dst_package=quote_package_extra, src_package=package_extra)
            quote_package_extra.addon = package_extra.addon
            quote_package_extra.time = package_extra.time
            quote_package_extra.quantity = package_extra.quantity
            quote_package_extra.parameter = package_extra.parameter
            quote_package_extra.save()


    @classmethod
    def copy_service_info(cls, dst_service, src_service):
        dst_service.description = src_service.description
        dst_service.datetime_from = src_service.datetime_from
        dst_service.datetime_to = src_service.datetime_to
        dst_service.status = constants.SERVICE_STATUS_PENDING
        dst_service.provider = src_service.provider
        dst_service.service = src_service.service


    @classmethod
    def copy_package_info(cls, dst_package, src_package):
        dst_package.description = src_package.description

        days_after = src_package.days_after
        if days_after is None:
            days_after = 0
        dst_package.datetime_from = dst_package.quote_package.datetime_from + timedelta(
                days=days_after)
        days_duration = src_package.days_duration
        if days_duration is None:
            days_duration = 0
        dst_package.datetime_to = dst_package.datetime_from + timedelta(days=days_duration)
        dst_package.status = constants.SERVICE_STATUS_PENDING
        dst_package.provider = src_package.provider
        dst_package.service = src_package.service


    @classmethod
    def find_quote_amounts(cls, agency, variant_list, allotment_list, transfer_list, extra_list):
        result = list()

        if not variant_list:
            return 3, 'Pax Variants Missing', None
        if (not allotment_list) and (not transfer_list) and (not extra_list):
            return 2, 'Services Missing', None

        for pax_variant in variant_list:
            variant_dict = dict()
            variant_dict.update({'paxes': pax_variant.pax_quantity})

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

            if allotment_list:
                counter = 0
                for quote_allotment in allotment_list:
                    key = '%s' % counter
                    if not hasattr(quote_allotment, 'service'):
                        variant_dict.update({key: cls._no_service_dict()})
                    else:
                        if quote_allotment.service.grouping:
                            # grouping means passing 1,2,3 as pax quantity
                            code, msg, c1, c1_msg, p1, p1_msg = ConfigService.allotment_amounts(
                                quote_allotment.service,
                                quote_allotment.datetime_from, quote_allotment.datetime_to,
                                ({0:1, 1:0},),
                                quote_allotment.provider, agency,
                                quote_allotment.board_type, quote_allotment.room_type_id)
                            if c1:
                                c1 = round(float(c1), 2)
                            if p1:
                                p1 = round(0.499999 + float(p1))
                            code, msg, c2, c2_msg, p2, p2_msg = ConfigService.allotment_amounts(
                                quote_allotment.service,
                                quote_allotment.datetime_from, quote_allotment.datetime_to,
                                ({0:2, 1:0},),
                                quote_allotment.provider, agency,
                                quote_allotment.board_type, quote_allotment.room_type_id)
                            if c2:
                                c2 = round(float(c2) / 2, 2)
                            if p2:
                                p2 = round(0.499999 + float(p2) / 2)
                            code, msg, c3, c3_msg, p3, p3_msg = ConfigService.allotment_amounts(
                                quote_allotment.service,
                                quote_allotment.datetime_from, quote_allotment.datetime_to,
                                ({0:3, 1:0},),
                                quote_allotment.provider, agency,
                                quote_allotment.board_type, quote_allotment.room_type_id)
                            if c3:
                                c3 = round(float(c3) / 3, 2)
                            if p3:
                                p3 = round(0.499999 + float(p3) / 3)
                        else:
                            # no grouping means passing total pax quantity
                            code, msg, c1, c1_msg, p1, p1_msg = ConfigService.allotment_amounts(
                                quote_allotment.service,
                                quote_allotment.datetime_from, quote_allotment.datetime_to,
                                ({0:pax_variant.pax_quantity, 1:0},),
                                quote_allotment.provider, agency,
                                quote_allotment.board_type, quote_allotment.room_type_id)
                            if c1:
                                c1 = round(float(c1) / pax_variant.pax_quantity, 2)
                            if p1:
                                p1 = round(0.499999 + float(p1) / pax_variant.pax_quantity)
                            c2, c2_msg, p2, p2_msg = c1, c1_msg, p1, p1_msg
                            c3, c3_msg, p3, p3_msg = c1, c1_msg, p1, p1_msg
                        # service amounts
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
                for quote_transfer in transfer_list:
                    key = '2-%s' % counter
                    if not hasattr(quote_transfer, 'service'):
                        variant_dict.update({key: cls._no_service_dict()})
                    else:
                        if quote_transfer.service.grouping:
                            # grouping means passing 1,2,3 as pax quantity
                            code, msg, c1, c1_msg, p1, p1_msg = ConfigService.transfer_amounts(
                                quote_transfer.service,
                                quote_transfer.datetime_from, quote_transfer.datetime_to,
                                ({0:1, 1:0},),
                                quote_transfer.provider, agency,
                                quote_transfer.location_from_id, quote_transfer.location_to_id,
                                quote_transfer.quantity)
                            if c1:
                                c1 = round(float(c1), 2)
                            if p1:
                                p1 = round(0.499999 + float(p1))
                            code, msg, c2, c2_msg, p2, p2_msg = ConfigService.transfer_amounts(
                                quote_transfer.service,
                                quote_transfer.datetime_from, quote_transfer.datetime_to,
                                ({0:2, 1:0},),
                                quote_transfer.provider, agency,
                                quote_transfer.location_from_id, quote_transfer.location_to_id,
                                quote_transfer.quantity)
                            if c2:
                                c2 = round(float(c2) / 2, 2)
                            if p2:
                                p2 = round(0.499999 + float(p2) / 2)
                            code, msg, c3, c3_msg, p3, p3_msg = ConfigService.transfer_amounts(
                                quote_transfer.service,
                                quote_transfer.datetime_from, quote_transfer.datetime_to,
                                ({0:3, 1:0},),
                                quote_transfer.provider, agency,
                                quote_transfer.location_from_id, quote_transfer.location_to_id,
                                quote_transfer.quantity)
                            if c3:
                                c3 = round(float(c3) / 3, 2)
                            if p2:
                                p3 = round(0.499999 + float(p3) / 3)
                        else:
                            # no grouping means passing total pax quantity
                            code, msg, c1, c1_msg, p1, p1_msg = ConfigService.transfer_amounts(
                                quote_transfer.service,
                                quote_transfer.datetime_from, quote_transfer.datetime_to,
                                ({0:pax_variant.pax_quantity, 1:0},),
                                quote_transfer.provider, agency,
                                quote_transfer.location_from_id, quote_transfer.location_to_id,
                                quote_transfer.quantity)
                            if c1:
                                c1 = round(float(c1) / pax_variant.pax_quantity, 2)
                            if p1:
                                p1 = round(0.499999 + float(p1) / pax_variant.pax_quantity)
                            c2, c2_msg, p2, p2_msg = c1, c1_msg, p1, p1_msg
                            c3, c3_msg, p3, p3_msg = c1, c1_msg, p1, p1_msg
                        # service amounts
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
                for quote_extra in extra_list:
                    key = '3-%s' % counter
                    if not hasattr(quote_extra, 'service'):
                        variant_dict.update({key: cls._no_service_dict()})
                    else:
                        if quote_extra.service.grouping:
                            # grouping means passing 1,2,3 as pax quantity
                            code, msg, c1, c1_msg, p1, p1_msg = ConfigService.extra_amounts(
                                quote_extra.service,
                                quote_extra.datetime_from, quote_extra.datetime_to,
                                ({0:1, 1:0},),
                                quote_extra.provider, agency,
                                quote_extra.addon_id,
                                quote_extra.quantity, quote_extra.parameter)
                            if c1:
                                c1 = round(float(c1), 2)
                            if p1:
                                p1 = round(0.499999 + float(p1))
                            code, msg, c2, c2_msg, p2, p2_msg = ConfigService.extra_amounts(
                                quote_extra.service,
                                quote_extra.datetime_from, quote_extra.datetime_to,
                                ({0:2, 1:0},),
                                quote_extra.provider, agency,
                                quote_extra.addon_id,
                                quote_extra.quantity, quote_extra.parameter)
                            if c2:
                                c2 = round(float(c2) / 2, 2)
                            if p2:
                                p2 = round(0.499999 + float(p2))
                            code, msg, c3, c3_msg, p3, p3_msg = ConfigService.extra_amounts(
                                quote_extra.service,
                                quote_extra.datetime_from, quote_extra.datetime_to,
                                ({0:3, 1:0},),
                                quote_extra.provider, agency,
                                quote_extra.addon_id,
                                quote_extra.quantity, quote_extra.parameter)
                            if c3:
                                c3 = round(float(c3) / 2, 2)
                            if p3:
                                p3 = round(0.499999 + float(p3))

                        else:
                            # no grouping means passing total pax quantity
                            code, msg, c1, c1_msg, p1, p1_msg = ConfigService.extra_amounts(
                                quote_extra.service,
                                quote_extra.datetime_from, quote_extra.datetime_to,
                                ({0:pax_variant.pax_quantity, 1:0},),
                                quote_extra.provider, agency,
                                quote_extra.addon_id,
                                quote_extra.quantity, quote_extra.parameter)
                            if c1:
                                c1 = round(float(c1) / pax_variant.pax_quantity, 2)
                            if p1:
                                p1 = round(0.499999 + float(p1) / pax_variant.pax_quantity)
                            c2, c2_msg, p2, p2_msg = c1, c1_msg, p1, p1_msg
                            c3, c3_msg, p3, p3_msg = c1, c1_msg, p1, p1_msg
                        # service amounts
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

            variant_dict.update({'total': cls._quote_amounts_dict(
                cost_1, cost_1_msg, price_1, price_1_msg,
                cost_2, cost_2_msg, price_2, price_2_msg,
                cost_3, cost_3_msg, price_3, price_3_msg)})

            result.append(variant_dict)

        return 0, '', result

    @classmethod
    def _quote_amounts_dict(
            cls,
            cost_1, cost_1_msg, price_1, price_1_msg,
            cost_2, cost_2_msg, price_2, price_2_msg,
            cost_3, cost_3_msg, price_3, price_3_msg,
            ):
        return {
            'cost_1': cost_1,
            'cost_1_msg': cost_1_msg,
            'price_1': price_1,
            'price_1_msg': price_1_msg,
            'cost_2': cost_2,
            'price_2': price_2,
            'price_2_msg': price_2_msg,
            'cost_2_msg': cost_2_msg,
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
            prev_amount, prev_msg, amount, msg):
        if prev_amount is None:
            return None, prev_msg
        elif amount is None:
            return None, msg
        else:
            return float(prev_amount) + float(amount), msg

    @classmethod
    def update_booking(cls, booking):
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
                cost += service.cost_amount
                # price
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
        if services and cancelled:
            # status cancelled
            status = constants.BOOKING_STATUS_CANCELLED

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
    def find_groups(cls, booking_service, service):
        if booking_service is None:
            return None, None
        pax_list = list(
            BookingServicePax.objects.filter(booking_service=booking_service.id))
        return cls.find_paxes_groups(pax_list, service)

    @classmethod
    def find_paxes_groups(cls, pax_list, service):
        if service.grouping:
            groups = dict()
            for pax in pax_list:
                if pax.booking_pax_id and pax.group:
                    if not groups.__contains__(pax.group):
                        groups[pax.group] = dict()
                        groups[pax.group][0] = 0 # adults count
                        groups[pax.group][1] = 0 # child count
                    if (service.child_age is None) or (pax.booking_pax.pax_age is None) or (
                            pax.booking_pax.pax_age > service.child_age):
                        groups[pax.group][0] += 1
                    else:
                        groups[pax.group][1] += 1
            return groups.values()
        else:
            adults = 0
            if service.child_age is None:
                for pax in pax_list:
                    if pax.booking_pax_id:
                        adults += 1
                return ({0: adults, 1: 0},)
            children = 0
            for pax in pax_list:
                if pax.booking_pax_id:
                    if pax.pax_age > service.child_age:
                        adults += 1
                    else:
                        children += 1
            return ({0: adults, 1: children},)

    @classmethod
    def _quote_allotment_amounts(
            cls,
            cost, cost_msg, price, price_msg,
            service, date_from, date_to, adults, board_type, room_type_id, quantity,
            provider, agency):
        groups = ({0:adults, 1:0},)
        if cost is None:
            if price is None:
                return None, cost_msg, None, price_msg
            else:
                code, msg, c, c_msg, p, p_msg = ConfigService.allotment_amounts(
                    service, date_from, date_to, groups,
                    None, agency,
                    board_type, room_type_id, quantity)
        else:
            if price is None:
                code, msg, c, c_msg, p, p_msg = ConfigService.allotment_amounts(
                    service, date_from, date_to, groups,
                    provider, None,
                    board_type, room_type_id, quantity)
            else:
                code, msg, c, c_msg, p, p_msg = ConfigService.allotment_amounts(
                    service, date_from, date_to, groups,
                    provider, agency,
                    board_type, room_type_id, quantity)
        return cls._quote_results(adults, cost, cost_msg, price, price_msg, c, c_msg, p, p_msg)

    @classmethod
    def _quote_transfer_amounts(
            cls,
            cost, cost_msg, price, price_msg,
            service, date_from, date_to, adults, location_from_id, location_to_id, quantity,
            provider, agency):
        groups = ({0:adults, 1:0},)
        if cost is None:
            if price is None:
                return None, cost_msg, None, price_msg
            else:
                code, msg, c, c_msg, p, p_msg = ConfigService.transfer_amounts(
                    service, date_from, date_to, groups,
                    None, agency,
                    location_from_id, location_to_id, quantity)
        else:
            if price is None:
                code, msg, c, c_msg, p, p_msg = ConfigService.transfer_amounts(
                    service, date_from, date_to, groups,
                    provider, None,
                    location_from_id, location_to_id, quantity)
            else:
                code, msg, c, c_msg, p, p_msg = ConfigService.transfer_amounts(
                    service, date_from, date_to, groups,
                    provider, agency,
                    location_from_id, location_to_id, quantity)
            return cls._quote_results(adults, cost, cost_msg, price, price_msg, c, c_msg, p, p_msg)

    @classmethod
    def _quote_extra_amounts(
            cls,
            cost, cost_msg, price, price_msg,
            service, date_from, date_to, adults, addon_id, quantity, parameter,
            provider, agency):
        groups = ({0:adults, 1:0},)
        if cost is None:
            if price is None:
                return None, cost_msg, None, price_msg
            else:
                code, msg, c, c_msg, p, p_msg = ConfigService.extra_amounts(
                    service, date_from, date_to, groups,
                    None, agency,
                    addon_id, quantity, parameter)
        else:
            if price is None:
                code, msg, c, c_msg, p, p_msg = ConfigService.extra_amounts(
                    service, date_from, date_to, groups,
                    provider, None,
                    addon_id, quantity, parameter)
            else:
                code, msg, c, c_msg, p, p_msg = ConfigService.extra_amounts(
                    service, date_from, date_to, groups,
                    provider, agency,
                    addon_id, quantity, parameter)
            return cls._quote_results(adults, cost, cost_msg, price, price_msg, c, c_msg, p, p_msg)

    @classmethod
    def _quote_results(cls, adults, cost, cost_msg, price, price_msg, c, c_msg, p, p_msg):
        if cost is None:
            if price is None:
                return None, cost_msg, None, price_msg
            else:
                if p is None:
                    return None, cost_msg, None, p_msg
                else:
                    return None, cost_msg, price + round(0.499999 + float(p / adults)), p_msg
        else:
            if price is None:
                if c is None:
                    return None, c_msg, None, price_msg
                else:
                    return cost + round(float(c / adults), 2), c_msg, None, price_msg
            else:
                if c is None:
                    if p is None:
                        return None, c_msg, None, p_msg
                    else:
                        return None, c_msg, price + round(0.499999 + float(p / adults)), p_msg
                else:
                    if p is None:
                        return cost + round(float(c / adults), 2), c_msg, None, p_msg
                    else:
                        return cost + round(float(c / adults), 2), c_msg, price + round(0.499999 + float(p / adults)), p_msg
