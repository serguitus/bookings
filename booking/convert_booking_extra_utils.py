# -*- coding: utf-8 -*-
from __future__ import unicode_literals

"""
Convert Booking Extra to Package Utils
"""

from django.db import transaction

from booking.copy_booking_data_utils import CopyBookingDataUtils
from booking.delete_booking_data_utils import DeleteBookingDataUtils
from booking.models import (
    BookingExtraPackage,
    BookingProvidedService, BookingProvidedAllotment, BookingProvidedTransfer, BookingProvidedExtra,
    BookingBookDetailAllotment, BookingBookDetailTransfer, BookingBookDetailExtra,
)

from common.filters import parse_date


class ConvertBookingExtraUtils(object):
    """
    Convert Booking Extra to Package Utils
    """

    @classmethod
    def create_bookingallotment_from_bookingdetail(cls, booking_detail_allotment: BookingBookDetailAllotment, parent_package: BookingExtraPackage):
        with transaction.atomic(savepoint=False):
            # new booking allotment
            booking_service = BookingProvidedAllotment()
            # copy data from detail
            CopyBookingDataUtils.copy_BaseBookingService_data(booking_service, booking_detail_allotment)
            CopyBookingDataUtils.copy_BookAllotmentData_data(booking_service, booking_detail_allotment)
            booking_service.booking_package = parent_package
            booking_service.save()


    @classmethod
    def create_bookingtransferdetail_from_bookingtransfer(cls, booking_detail_transfer: BookingBookDetailTransfer, parent_package: BookingExtraPackage):
            # new transfer detail
            booking_service = BookingProvidedTransfer()
            # copy data from service
            CopyBookingDataUtils.copy_BaseBookingService_data(booking_service, booking_detail_transfer)
            CopyBookingDataUtils.copy_BookTransferData_data(booking_service, booking_detail_transfer)
            booking_service.booking_package = parent_package
            booking_service.save()


    @classmethod
    def create_bookingextradetail_from_bookingextra(cls, booking_detail_extra: BookingBookDetailExtra, parent_package: BookingExtraPackage):
            # new extra detail
            booking_service = BookingProvidedExtra()
            # copy data from service
            CopyBookingDataUtils.copy_BaseBookingService_data(booking_service, booking_detail_extra)
            CopyBookingDataUtils.copy_BookExtraData_data(booking_service, booking_detail_extra)
            booking_service.booking_package = parent_package
            booking_service.save()


    @classmethod
    def create_bookingpackage_from_bookingextra(cls, booking_extra: BookingProvidedExtra):
        """ creates a BookingExtraPackage to replace an extra in a booking """
        with transaction.atomic(savepoint=False):
            # new package service
            booking_package = BookingExtraPackage()
            # copy data from extra
            CopyBookingDataUtils.copy_BaseBookingService_data(booking_package, booking_extra)
            CopyBookingDataUtils.copy_BookExtraData_data(booking_package, booking_extra)
            # data in BookingExtraPackage
            booking_package.service = booking_extra.base_service
            booking_package.price_by_catalog = False
            booking_package.save()

            # create services
            # create allotments
            details = BookingBookDetailAllotment.objects.filter(booking_service=booking_extra)
            for detail in details:
                cls.create_bookingallotment_from_bookingdetail(detail, booking_package)

            # create transfers
            details = BookingBookDetailTransfer.objects.filter(booking_service=booking_extra)
            for detail in details:
                cls.create_bookingtransfer_from_bookingdetail(detail, booking_package)

            # create extras
            details = BookingBookDetailExtra.objects.filter(booking_service=booking_extra)
            for detail in details:
                cls.create_bookingextra_from_bookingdetail(detail, booking_package)


    @classmethod
    def convert_bookingextra_to_bookingpackage(cls, extra_id):
        """ creates a BookingExtraPackage to replace an extra in a booking """
        try:
            # obtain extra
            booking_extra = BookingProvidedExtra.objects.get(id=extra_id)
        except Exception:
            return None, "Error: Not Found booking extra"

        # TODO validate conversion preconditions
        if 1 == 1:
            return None, "Error: Validation Failed"

        with transaction.atomic(savepoint=False):
            # create extra
            cls.create_bookingpackage_from_bookingextra(booking_extra)
            # delete extra
            DeleteBookingDataUtils.delete_bookingservice(booking_extra)

