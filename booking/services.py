"""
Booking Service
"""

from booking import constants
from booking.models import BookingServicePax


class BookingService(object):
    """
    Booking Service
    """

    @classmethod
    def update_order(cls, order):
        date_from = None
        date_to = None
        for service in order.orderservice_set:
            # date_from
            if date_from is None or (date_from > service.date_from):
                date_from = service.date_from
            # date_to
            if date_to is None or (date_to < service.date_to):
                date_to = service.date_to
            # cost
            #cost += service.cost_amount
            # price
            #price += service.price_amount
            # status
            # pending sets always pending
            #if service.status == constants.SERVICE_STATUS_PENDING:
            #    status = constants.BOOKING_STATUS_PENDING
            # requested sets requested when not pending
            #elif (service.status == constants.SERVICE_STATUS_REQUEST) and (
            #        status != constants.BOOKING_STATUS_PENDING):
            #    status = constants.BOOKING_STATUS_REQUEST
            # phone confirmed sets requested when not pending
            #elif (service.status == constants.SERVICE_STATUS_PHONE_CONFIRMED) and (
            #        status != constants.BOOKING_STATUS_PENDING):
            #    status = constants.BOOKING_STATUS_REQUEST
            # confirmed sets confirmed when not requested and not pending
            #elif (service.status == constants.SERVICE_STATUS_CONFIRMED) and (
            #        status != constants.BOOKING_STATUS_PENDING) and (
            #            status != constants.BOOKING_STATUS_REQUEST):
            #    status = constants.BOOKING_STATUS_CONFIRMED

        fields = []
        if order.date_from != date_from:
            fields.append('date_from')
            order.date_from = date_from
        if order.date_to != date_to:
            fields.append('date_to')
            order.date_to = date_to
        #if order.status != status:
        #    fields.append('status')
        #    order.status = status

        if fields:
            order.save(update_fields=fields)


    @classmethod
    def update_paxvariants(cls, order):
        for variant in order.orderpaxvariant_set:
            cost_single = 0
            cost_double = 0
            cost_triple = 0
            price_single = 0
            price_double = 0
            price_triple = 0
            for service in order.orderservice_set:
                pass


    @classmethod
    def update_booking(cls, booking):
        cost = 0
        price = 0
        date_from = None
        date_to = None
        status = constants.BOOKING_STATUS_COORDINATED
        services = False
        cancelled = True
        need_save = False
        for service in booking.bookingservice_set:
            services = True
            # process only non cancelled services
            if service.status != constants.SERVICE_STATUS_CANCELLED:
                # set not all cancelled
                cancelled = False
                # date_from
                if date_from is None or (date_from > service.date_from):
                    date_from = service.date_from
                # date_to
                if date_to is None or (date_to < service.date_to):
                    date_to = service.date_to
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
        if service.grouping:
            groups = dict()
            for pax in pax_list:
                if not groups.__contains__(pax.group):
                    groups[pax.group] = dict()
                    groups[pax.group][0] = 0
                    groups[pax.group][1] = 0
                if service.child_age is None or (pax.booking_pax.pax_age > service.child_age):
                    groups[pax.group][0] += 1
                else:
                    groups[pax.group][1] += 1
            return groups.values()
        else:
            if service.child_age is None:
                return list({0: len(pax_list), 1: 0})
            adults = 0
            children = 0
            for pax in pax_list:
                if pax.pax_age > service.child_age:
                    adults += 1
                else:
                    children += 1
            return list({0: adults, 1: children})

