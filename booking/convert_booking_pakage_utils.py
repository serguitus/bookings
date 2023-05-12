# -*- coding: utf-8 -*-
from __future__ import unicode_literals

"""
Convert Booking Package to Extra Utils
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


class ConvertBookingPackageUtils(object):
    """
    Convert Booking Package to Extra Utils
    """

    @classmethod
    def create_bookingallotmentdetail_from_bookingallotment(cls, booking_allotment: BookingProvidedAllotment, parent_service: BookingProvidedService):
        with transaction.atomic(savepoint=False):
            # new allotment detail
            booking_detail = BookingBookDetailAllotment()
            # copy data from service
            CopyBookingDataUtils.copy_BaseBookingService_data(booking_detail, booking_allotment)
            CopyBookingDataUtils.copy_BookAllotmentData_data(booking_detail, booking_allotment)
            booking_detail.booking_service = parent_service
            booking_detail.save()


    @classmethod
    def create_bookingtransferdetail_from_bookingtransfer(cls, booking_transfer: BookingProvidedTransfer, parent_service: BookingProvidedService):
            # new transfer detail
            booking_detail = BookingBookDetailTransfer()
            # copy data from service
            CopyBookingDataUtils.copy_BaseBookingService_data(booking_detail, booking_transfer)
            CopyBookingDataUtils.copy_BookTransferData_data(booking_detail, booking_transfer)
            booking_detail.booking_service = parent_service
            booking_detail.save()


    @classmethod
    def create_bookingextradetail_from_bookingextra(cls, booking_extra: BookingProvidedExtra, parent_service: BookingProvidedService):
            # new extra detail
            booking_detail = BookingBookDetailExtra()
            # copy data from service
            CopyBookingDataUtils.copy_BaseBookingService_data(booking_detail, booking_extra)
            CopyBookingDataUtils.copy_BookExtraData_data(booking_detail, booking_extra)
            booking_detail.booking_service = parent_service
            booking_detail.save()


    @classmethod
    def create_bookingextra_with_details_from_bookingpackage(cls, booking_package: BookingExtraPackage):
        """ creates a BookingProvidedExtra to replace a package in a booking """
        with transaction.atomic(savepoint=False):
            # new extra service
            booking_extra = BookingProvidedExtra()
            # copy data from package
            CopyBookingDataUtils.copy_BaseBookingService_data(booking_extra, booking_package)
            # data in BookingProvidedService
            booking_extra.cost_by_catalog = False
            booking_extra.price_by_catalog = False
            booking_extra.booking_package = None
            # booking_package.voucher_detail
            booking_extra.save()

            # create details
            # create booking service details (allotments)
            services = BookingProvidedAllotment.objects.filter(booking_package=booking_package)
            for service in services:
                cls.create_bookingallotmentdetail_from_bookingservice(service, booking_extra)

            # create booking service details (transfers)
            services = BookingProvidedTransfer.objects.filter(booking_package=booking_package)
            for service in services:
                cls.create_bookingtransferdetail_from_bookingservice(service, booking_extra)

            # create booking service details (extras)
            services = BookingProvidedExtra.objects.filter(booking_package=booking_package)
            for service in services:
                cls.create_bookingextradetail_from_bookingservice(service, booking_extra)


    @classmethod
    def convert_bookingpackage_into_bookingextra_with_details(cls, package_id):
        """ creates a BookingProvidedExtra to replace a package in a booking """
        try:
            # obtain package
            booking_package = BookingExtraPackage.objects.get(id=package_id)
        except Exception:
            return None, "Error: Not Found booking package"

        # TODO validate conversion preconditions
        if 1 == 1:
            return None, "Error: Validation Failed"

        with transaction.atomic(savepoint=False):
            # create extra
            cls.create_bookingextra_with_details_from_bookingpackage(booking_package)
            # delete package
            DeleteBookingDataUtils.delete_bookingpackage(booking_package)

