# -*- coding: utf-8 -*-
from __future__ import unicode_literals

"""
Copy Booking Data Utils
"""

from booking.models import (
    BookServiceData, DateInterval, CostData, PriceData,
    BaseBookingService,
    BookAllotmentData, BookTransferData, BookExtraData,
)


class CopyBookingDataUtils(object):
    """
    Copy Booking Data Utils
    """
    @classmethod
    def copy_BookServiceData_data(cls, dst_service: BookServiceData, src_service: BookServiceData):
        dst_service.name = src_service.name
        dst_service.description = src_service.description
        dst_service.base_service = src_service.base_service
        dst_service.base_location = src_service.base_location
        dst_service.provider = src_service.provider
        dst_service.service_addon = src_service.service_addon
        dst_service.time = src_service.time


    @classmethod
    def copy_DateInterval_data(cls, dst_service: DateInterval, src_service: DateInterval):
        dst_service.datetime_from = src_service.datetime_from
        dst_service.datetime_to = src_service.datetime_to


    @classmethod
    def copy_CostData_data(cls, dst_service: CostData, src_service: CostData):
        dst_service.cost_amount = src_service.cost_amount
        dst_service.cost_comments = src_service.cost_comments


    @classmethod
    def copy_PriceData_data(cls, dst_service: PriceData, src_service: PriceData):
        dst_service.price_amount = src_service.price_amount
        dst_service.price_comments = src_service.price_comments


    @classmethod
    def copy_BaseBookingService_data(cls, dst_service: BaseBookingService, src_service: BaseBookingService):
        dst_service.booking = src_service.booking
        dst_service.contract_code = src_service.contract_code
        dst_service.status = src_service.status
        dst_service.conf_number = src_service.conf_number
        dst_service.p_notes = src_service.p_notes
        dst_service.new_v_notes = src_service.new_v_notes
        dst_service.provider_notes = src_service.provider_notes
        dst_service.manual_cost = src_service.manual_cost
        dst_service.manual_price = src_service.manual_price
        dst_service.cost_amount_to_pay = src_service.cost_amount_to_pay
        dst_service.cost_amount_paid = src_service.cost_amount_paid
        dst_service.has_payment = src_service.has_payment

        cls.copy_BookServiceData_data(dst_service, src_service)
        cls.copy_DateInterval_data(dst_service, src_service)
        cls.copy_CostData_data(dst_service, src_service)
        cls.copy_PriceData_data(dst_service, src_service)


    @classmethod
    def copy_BookAllotmentData_data(cls, dst_service: BookAllotmentData, src_service: BookAllotmentData):
        dst_service.room_type = src_service.room_type
        dst_service.board_type = src_service.board_type


    @classmethod
    def copy_BookTransferData_data(cls, dst_service: BookTransferData, src_service: BookTransferData):
        dst_service.location_from = src_service.location_from
        dst_service.location_to = src_service.location_to
        dst_service.quantity = src_service.quantity
        dst_service.place_from = src_service.place_from
        dst_service.schedule_from = src_service.schedule_from
        dst_service.pickup = src_service.pickup
        dst_service.place_to = src_service.place_to
        dst_service.schedule_to = src_service.schedule_to
        dst_service.dropoff = src_service.dropoff
        dst_service.schedule_time_from = src_service.schedule_time_from
        dst_service.schedule_time_to = src_service.schedule_time_to


    @classmethod
    def copy_BookExtraData_data(cls, dst_service: BookExtraData, src_service: BookExtraData):
        dst_service.quantity = src_service.quantity
        dst_service.parameter = src_service.parameter
        dst_service.pickup_office = src_service.pickup_office
        dst_service.dropoff_office = src_service.dropoff_office
