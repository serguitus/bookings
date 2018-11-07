"""
Booking Service
"""

from booking import constants
from booking.models import BookingServicePax

from config.constants import (
    SERVICE_CATEGORY_ALLOTMENT, SERVICE_CATEGORY_TRANSFER, SERVICE_CATEGORY_EXTRA
)
from config.services import ConfigService


class BookingService(object):
    """
    Booking Service
    """

    @classmethod
    def update_quote(cls, quote):
        date_from = None
        date_to = None
        for service in quote.quoteservice_set:
            # date_from
            if date_from is None or (date_from > service.date_from):
                date_from = service.date_from
            # date_to
            if date_to is None or (date_to < service.date_to):
                date_to = service.date_to
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
    def find_quote_amounts(cls, quote):
        result = dict()
        for pax_variant in quote.quote_paxvariants:
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
            for qservice in quote.quote_services:
                service_type = qservice.service.category
                if service_type == SERVICE_CATEGORY_ALLOTMENT:
                    if qservice.service.grouping:
                        cost_1, cost_1_msg, price_1, price_1_msg = cls._quote_allotment_amounts(
                            cost_1, cost_1_msg, price_1, price_1_msg,
                            qservice.service, qservice.date_from, qservice.date_to,
                            list((1, 0)),
                            qservice.board_type, qservice.room_type_id,
                            qservice.quantity,
                            qservice.provider, quote.agency)
                        cost_2, cost_2_msg, price_2, price_2_msg = cls._quote_allotment_amounts(
                            cost_2, cost_2_msg, price_2, price_2_msg,
                            qservice.service, qservice.date_from, qservice.date_to,
                            list((2, 0)),
                            qservice.board_type, qservice.room_type_id,
                            qservice.quantity,
                            qservice.provider, quote.agency)
                        cost_3, cost_3_msg, price_3, price_3_msg = cls._quote_allotment_amounts(
                            cost_3, cost_3_msg, price_3, price_3_msg,
                            qservice.service, qservice.date_from, qservice.date_to,
                            list((3, 0)),
                            qservice.board_type, qservice.room_type_id,
                            qservice.quantity,
                            qservice.provider, quote.agency)
                    else:
                        cost_1, cost_1_msg, price_1, price_1_msg = cls._quote_allotment_amounts(
                            cost_1, cost_1_msg, price_1, price_1_msg,
                            qservice.service, qservice.date_from, qservice.date_to,
                            list((pax_variant.pax_quantity, 0)),
                            qservice.board_type, qservice.room_type_id,
                            qservice.quantity,
                            qservice.provider, quote.agency)
                        cost_2, cost_2_msg = cost_1, cost_1_msg
                        price_2, price_2_msg = price_1, price_1_msg
                        cost_3, cost_3_msg = cost_1, cost_1_msg
                        price_3, price_3_msg = price_1, price_1_msg
                if service_type == SERVICE_CATEGORY_TRANSFER:
                    if qservice.service.grouping:
                        cost_1, cost_1_msg, price_1, price_1_msg = cls._quote_transfer_amounts(
                            cost_1, cost_1_msg, price_1, price_1_msg,
                            qservice.service, qservice.date_from, qservice.date_to,
                            list((1, 0)),
                            qservice.location_from_id, qservice.location_to_id,
                            qservice.quantity,
                            qservice.provider, quote.agency)
                        cost_2, cost_2_msg, price_2, price_2_msg = cls._quote_transfer_amounts(
                            cost_2, cost_2_msg, price_2, price_2_msg,
                            qservice.service, qservice.date_from, qservice.date_to,
                            list((2, 0)),
                            qservice.location_from_id, qservice.location_to_id,
                            qservice.quantity,
                            qservice.provider, quote.agency)
                        cost_3, cost_3_msg, price_3, price_3_msg = cls._quote_transfer_amounts(
                            cost_3, cost_3_msg, price_3, price_3_msg,
                            qservice.service, qservice.date_from, qservice.date_to,
                            list((3, 0)),
                            qservice.location_from_id, qservice.location_to_id,
                            qservice.quantity,
                            qservice.provider, quote.agency)
                    else:
                        cost_1, cost_1_msg, price_1, price_1_msg = cls._quote_transfer_amounts(
                            cost_1, cost_1_msg, price_1, price_1_msg,
                            qservice.service, qservice.date_from, qservice.date_to,
                            list((pax_variant.pax_quantity, 0)),
                            qservice.location_from_id, qservice.location_to_id,
                            qservice.quantity,
                            qservice.provider, quote.agency)
                        cost_2, cost_2_msg = cost_1, cost_1_msg
                        price_2, price_2_msg = price_1, price_1_msg
                        cost_3, cost_3_msg = cost_1, cost_1_msg
                        price_3, price_3_msg = price_1, price_1_msg
                if service_type == SERVICE_CATEGORY_EXTRA:
                    if qservice.service.grouping:
                        cost_1, cost_1_msg, price_1, price_1_msg = cls._quote_extra_amounts(
                            cost_1, cost_1_msg, price_1, price_1_msg,
                            qservice.service, qservice.date_from, qservice.date_to,
                            list((1, 0)),
                            qservice.quantity, qservice.parameter,
                            qservice.provider, quote.agency)
                        cost_2, cost_2_msg, price_2, price_2_msg = cls._quote_extra_amounts(
                            cost_2, cost_2_msg, price_2, price_2_msg,
                            qservice.service, qservice.date_from, qservice.date_to,
                            list((2, 0)),
                            qservice.quantity, qservice.parameter,
                            qservice.provider, quote.agency)
                        cost_3, cost_3_msg, price_3, price_3_msg = cls._quote_extra_amounts(
                            cost_3, cost_3_msg, price_3, price_3_msg,
                            qservice.service, qservice.date_from, qservice.date_to,
                            list((3, 0)),
                            qservice.quantity, qservice.parameter,
                            qservice.provider, quote.agency)
                    else:
                        cost_1, cost_1_msg, price_1, price_1_msg = cls._quote_extra_amounts(
                            cost_1, cost_1_msg, price_1, price_1_msg,
                            qservice.service, qservice.date_from, qservice.date_to,
                            list((pax_variant.pax_quantity, 0)),
                            qservice.quantity, qservice.parameter,
                            qservice.provider, quote.agency)
                        cost_2, cost_2_msg = cost_1, cost_1_msg
                        price_2, price_2_msg = price_1, price_1_msg
                        cost_3, cost_3_msg = cost_1, cost_1_msg
                        price_3, price_3_msg = price_1, price_1_msg
            result.update({
                pax_variant.pax_quantity: {
                    cost_1: cost_1,
                    cost_1_msg: cost_1_msg,
                    cost_2: cost_2,
                    cost_2_msg: cost_2_msg,
                    cost_3: cost_3,
                    cost_3_msg: cost_3_msg,
                    price_1: price_1,
                    price_1_msg: price_1_msg,
                    price_2: price_2,
                    price_2_msg: price_2_msg,
                    price_3: price_3,
                    price_3_msg: price_3_msg,
                }
            })
            return result

    @classmethod
    def _quote_allotment_amounts(
            cls,
            cost, cost_msg, price, price_msg,
            service, date_from, date_to, adults, board_type, room_type_id, quantity,
            provider, agency):
        if cost is None:
            if price is None:
                return None, cost_msg, None, price_msg
            else:
                code, msg, c, c_msg, p, p_msg = ConfigService.allotment_amounts(
                    service, date_from, date_to, ((adults, 0)),
                    None, agency,
                    board_type, room_type_id, quantity)
        else:
            if price is None:
                code, msg, c, c_msg, p, p_msg = ConfigService.allotment_amounts(
                    service, date_from, date_to, ((adults, 0)),
                    provider, None,
                    board_type, room_type_id, quantity)
            else:
                code, msg, c, cost_msg, price, price_msg = ConfigService.allotment_amounts(
                    service, date_from, date_to, ((adults, 0)),
                    provider, agency,
                    board_type, room_type_id, quantity)
            return cls._quote_results(adults, cost, cost_msg, price, price_msg, c, c_msg, p, p_msg)

    @classmethod
    def _quote_transfer_amounts(
            cls,
            cost, cost_msg, price, price_msg,
            service, date_from, date_to, adults, location_from_id, location_to_id, quantity,
            provider, agency):
        if cost is None:
            if price is None:
                return None, cost_msg, None, price_msg
            else:
                code, msg, c, c_msg, p, p_msg = ConfigService.transfer_amounts(
                    service, date_from, date_to, ((adults, 0)),
                    None, agency,
                    location_from_id, location_to_id, quantity)
        else:
            if price is None:
                code, msg, c, c_msg, p, p_msg = ConfigService.transfer_amounts(
                    service, date_from, date_to, ((adults, 0)),
                    provider, None,
                    location_from_id, location_to_id, quantity)
            else:
                code, msg, c, cost_msg, price, price_msg = ConfigService.transfer_amounts(
                    service, date_from, date_to, ((adults, 0)),
                    provider, agency,
                    location_from_id, location_to_id, quantity)
            return cls._quote_results(adults, cost, cost_msg, price, price_msg, c, c_msg, p, p_msg)

    @classmethod
    def _quote_extra_amounts(
            cls,
            cost, cost_msg, price, price_msg,
            service, date_from, date_to, adults, quantity, parameter,
            provider, agency):
        if cost is None:
            if price is None:
                return None, cost_msg, None, price_msg
            else:
                code, msg, c, c_msg, p, p_msg = ConfigService.extra_amounts(
                    service, date_from, date_to, ((adults, 0)),
                    None, agency,
                    quantity, parameter)
        else:
            if price is None:
                code, msg, c, c_msg, p, p_msg = ConfigService.extra_amounts(
                    service, date_from, date_to, ((adults, 0)),
                    provider, None,
                    quantity, parameter)
            else:
                code, msg, c, cost_msg, price, price_msg = ConfigService.extra_amounts(
                    service, date_from, date_to, ((adults, 0)),
                    provider, agency,
                    quantity, parameter)
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
                    return None, cost_msg, price + round(0.999999 + p / adults), p_msg
        else:
            if price is None:
                if c is None:
                    return None, c_msg, None, price_msg
                else:
                    return cost + round(0.999999 + c / adults), c_msg, None, price_msg
            else:
                if c is None:
                    if p is None:
                        return None, c_msg, None, p_msg
                    else:
                        return None, c_msg, price + round(0.999999 + p / adults), p_msg
                else:
                    if p is None:
                        return cost + round(0.999999 + c / adults), c_msg, None, p_msg
                    else:
                        return cost + round(0.999999 + c / adults), c_msg, price + round(0.999999 + p / adults), p_msg

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

