# -*- coding: utf-8 -*-
from __future__ import unicode_literals

"""
Delete Booking Data Utils
"""

from django.db import transaction

from booking.models import (
    BookingExtraPackage,
    BookingProvidedService, BookingProvidedAllotment, BookingProvidedTransfer, BookingProvidedExtra,
    BookingBookDetailAllotment, BookingBookDetailTransfer, BookingBookDetailExtra,
)

from common.filters import parse_date


class DeleteBookingDataUtils(object):
    """
    Delete Booking Data Utils
    """

    @classmethod
    def delete_bookingservice_details(cls, booking_service: BookingProvidedService):
        with transaction.atomic(savepoint=False):
            # delete booking service details (allotments)
            details = BookingBookDetailAllotment.objects.filter(booking_service=booking_service);
            for detail in details:
                detail.delete()

            # delete booking service details (transfers)
            details = BookingBookDetailTransfer.objects.filter(booking_service=booking_service);
            for detail in details:
                detail.delete()

            # delete booking service details (extras)
            details = BookingBookDetailExtra.objects.filter(booking_service=booking_service);
            for detail in details:
                detail.delete()


    @classmethod
    def delete_bookingservice(cls, booking_service: BookingProvidedService):
        with transaction.atomic(savepoint=False):
            # delete booking service details
            cls.delete_bookingservice_details(booking_service)
            # delete booking service
            booking_service.delete()


    @classmethod
    def delete_bookingpackage_services(cls, booking_package: BookingExtraPackage):
        with transaction.atomic(savepoint=False):
            # delete booking package allotments
            services = BookingProvidedAllotment.objects.filter(booking_package=booking_package);
            for service in services:
                cls.delete_bookingservice(service)

            # delete booking package transfers
            services = BookingProvidedTransfer.objects.filter(booking_package=booking_package);
            for service in services:
                cls.delete_bookingservice(service)

            # delete booking package extras
            services = BookingProvidedExtra.objects.filter(booking_package=booking_package);
            for service in services:
                cls.delete_bookingservice(service)


    @classmethod
    def delete_bookingpackage(cls, booking_package: BookingExtraPackage):
        with transaction.atomic(savepoint=False):
            # delete booking package services
            cls.delete_bookingpackage_services(booking_package)
            # delete booking package
            booking_package.delete()
