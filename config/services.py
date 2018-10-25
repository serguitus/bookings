"""
Config Service
"""

from config.constants import (
    SERVICE_CATEGORY_EXTRA, SERVICE_CATEGORY_ALLOTMENT, SERVICE_CATEGORY_TRANSFER,
    TRANSFER_COST_TYPE_FIXED, TRANSFER_COST_TYPE_BY_PAX,
    EXTRA_COST_TYPE_FIXED, EXTRA_COST_TYPE_BY_PAX,
    EXTRA_PARAMETER_TYPE_HOURS, EXTRA_PARAMETER_TYPE_DAYS,
    ERROR_INVALID_SERVICE_CATEGORY)
from config.models import (
    Allotment,
    ProviderAllotmentService, ProviderAllotmentDetail,
    AgencyAllotmentService, AgencyAllotmentDetail,
    Transfer,
    ProviderTransferService, ProviderTransferDetail,
    AgencyTransferService, AgencyTransferDetail,
    Extra,
    ProviderExtraService, ProviderExtraDetail,
    AgencyExtraService, AgencyExtraDetail,
)

class ConfigService(object):
    """
    Config Service
    """
    @classmethod
    def allotment_amounts(cls, service_id, date_from, date_to, adults, children, provider, agency,
        board_type, room_type_id):
        pass

    @classmethod
    def transfer_amounts(cls, service_id, date_from, date_to, adults, children, provider, agency,
        location_from, location_to):
        pass

    @classmethod
    def extra_amounts(cls, service_id, date_from, date_to, adults, children, provider, agency,
        quantity, parameter):
        
        service = Extra.objects.get(pk=service_id)

        # provider cost
        # obtain details order by date_from asc, date_to desc
        detail_list = list(
            ProviderExtraDetail.objects.select_related(
                'provider_service__service'
            ).filter(
                provider_service__provider__eq=provider.id
            ).filter(
                provider_service__provider_service__eq=service.id
            ).filter(
                provider_service__date_to__gte=date_from,
                provider_service__date_from__lte=date_to
            ).order_by(
                ['provider_service__date_from', '-provider_service__date_to']
            )
        )
        cost, cost_message = cls.find_amount(
            True, service, date_from, date_to, adults, children,
            quantity, parameter, detail_list
        )

        # agency price
        # obtain details order by date_from asc, date_to desc
        detail_list = list(
            AgencyExtraDetail.objects.select_related(
                'agency_service__service'
            ).filter(
                agency_service__agency__eq=agency.id
            ).filter(
                agency_service__agency_service__eq=service.id
            ).filter(
                agency_service__date_to__gte=date_from,
                agency_service__date_from__lte=date_to
            ).order_by(
                ['agency_service__date_from', '-agency_service__date_to']
            )
        )
        price, price_message = cls.find_amount(
            False, service, date_from, date_to, adults, children,
            quantity, parameter, detail_list
        )
        return _get_result(cost, cost_message, price, price_message)

    @classmethod
    def _get_result(cls, cost, cost_message, price, price_message):
        if cost >= 0:
            if price >= 0:
                code = "0"
                message = "Provider Cost and Agency Price Found: %s - %s" % (
                    cost_message, price_message
                )
            else:
                code = "1"
                message = "Only Provider Cost Found: %s - %s" % (
                    cost_message, price_message
                )
        else:
            if price >= 0:
                code = "2"
                message = "Only Agency Price Found: %s - %s" % (
                    cost_message, price_message
                )
            else:
                code = "3"
                message = "Provider Cost and Agency Price NOT Found: %s - %s" % (
                    cost_message, price_message
                )
                
        return code, message, cost, price

    @classmethod
    def find_amount(cls, amount_for_provider, service, date_from, date_to, adults, children,
        quantity, parameter, detail_list):

        message = ''
        stop = False
        solved = False
        current_date = date_from
        amount = 0
        # continue until solved or empty details list
        while not stop:
            # verify list not empty
            if len(detail_list) > 0:
                # working with first detail
                detail = detail_list[0]
                # verify current dat included
                if amount_for_provider:
                    detail_date_from = detail.provider_servide.date_from
                    detail_date_to = detail.provider_servide.date_to
                else:
                    detail_date_from = detail.agency_servide.date_from
                    detail_date_to = detail.agency_servide.date_to
                    
                if current_date >= detail_date_from:
                    # verify final date included
                    if detail_date_to >= date_to:
                        # full date range
                        result = cls._get_service_amount(
                            service, detail, current_date, date_to,
                            adults, children,
                            quantity, parameter)
                        if result >= 0:
                            amount += result
                            solved = True
                            stop = True
                    else:
                        result = cls._get_service_amount(
                            service, detail, current_date, detail_date_to,
                            adults, children,
                            quantity, parameter)
                        if result >= 0:
                            amount += result
                            # TODO add 1 day
                            current_date = detail_date_to + 1
                # remove detail from list
                detail_list.remove(detail)
            else:
                # empty list, no solved all days
                stop = True
                message = 'Price Not Found for date %s' % current_date
        if not solved:
            amount = -1

        return amount, message

    @classmethod
    def _get_service_amount(
        cls, service, detail, date_from, date_to, adults, children, quantity, parameter):
        if isinstance(service, Allotment):
            return cls._get_allotment_amount(
                service, detail, date_from, date_to, adults, children, quantity, parameter)
        if isinstance(service, Transfer):
            return cls._get_transfer_amount(
                service, detail, date_from, date_to, adults, children, quantity, parameter)
        if isinstance(service, Extra):
            return cls._get_extra_amount(
                service, detail, date_from, date_to, adults, children, quantity, parameter)
        return -1

    @classmethod
    def _get_allotment_amount(
        cls, service, detail, date_from, date_to, adults, children, quantity, parameter):
        # TODO
        days = date_to - date_from
        amount = cls._find_detail_amount(detail, adults, children)
        if amount >= 0:
           return amount * days
        return -1

    @classmethod
    def _get_transfer_amount(
        cls, service, detail, date_from, date_to, adults, children, quantity, parameter):
        if service.cost_type == TRANSFER_COST_TYPE_FIXED and detail.ad_1_amount:
            return detail.ad_1_amount
        if service.cost_type == TRANSFER_COST_TYPE_BY_PAX:
            amount = cls._find_detail_amount(detail, adults, children)
            if amount >= 0:
                return amount
        return -1

    @classmethod
    def _get_extra_amount(cls, service, detail, date_from, date_to, adults, children, quantity, parameter):
        if service.parameter_type == EXTRA_PARAMETER_TYPE_DAYS:
            # TODO
            days = date_to - date_from
            parameter = days
        if service.cost_type == EXTRA_COST_TYPE_FIXED and detail.ad_1_amount:
            return detail.ad_1_amount * quantity * parameter
        if service.cost_type == EXTRA_COST_TYPE_BY_PAX:
            price = cls._find_detail_amount(detail, adults, children)
            if price >= 0:
                return price * quantity * parameter
        return -1

    @classmethod
    def _find_detail_amount(cls, detail, adults, children):
        if adults == 0:
            if children == 1 and detail.ch_1_ad_0_amount:
                return 1 * detail.ch_1_ad_0_amount
            if children == 2 and detail.ch_2_ad_0_amount:
                return 2 * detail.ch_2_ad_0_amount
            if children == 3 and detail.ch_3_ad_0_amount:
                return 3 * detail.ch_3_ad_0_amount
        if adults == 1 and detail.ad_1_amount:
            if children == 0:
                return 1 * detail.ad_1_amount
            if children == 1 and detail.ch_1_ad_1_amount:
                return 1 * detail.ad_1_amount + 1 * detail.ch_1_ad_1_amount 
            if children == 2 and detail.ch_2_ad_1_amount:
                return 1 * detail.ad_1_amount + 2 * detail.ch_2_ad_1_amount
            if children == 3 and detail.ch_3_ad_1_amount:
                return 1 * detail.ad_1_amount + 3 * detail.ch_3_ad_1_amount
        if adults == 2 and detail.ad_2_amount:
            if children == 0:
                return 2 * detail.ad_2_amount
            if children == 1 and detail.ch_1_ad_2_amount:
                return 2 * detail.ad_2_amount + 1 * detail.ch_1_ad_2_amount
            if children == 2 and detail.ch_2_ad_2_amount:
                return 2 * detail.ad_2_amount + 2 * detail.ch_2_ad_2_amount
            if children == 3 and detail.ch_3_ad_2_amount:
                return 2 * detail.ad_2_amount + 3 * detail.ch_3_ad_2_amount
        if adults == 3 and detail.ad_3_amount:
            if children == 0:
                return 3 * detail.ad_3_amount
            if children == 1 and detail.ch_1_ad_3_amount:
                return 3 * detail.ad_3_amount + 1 * detail.ch_1_ad_3_amount
            if children == 2 and detail.ch_2_ad_3_amount:
                return 3 * detail.ad_3_amount + 2 * detail.ch_2_ad_3_amount
            if children == 3 and detail.ch_3_ad_3_amount:
                return 3 * detail.ad_3_amount + 3 * detail.ch_3_ad_3_amount
        if adults == 4 and detail.ad_4_amount:
            if children == 0:
                return 4 * detail.ad_4_amount
            if children == 1 and detail.ch_1_ad_4_amount:
                return 4 * detail.ad_4_amount + 1 * detail.ch_1_ad_4_amount
            if children == 2 and detail.ch_2_ad_4_amount:
                return 4 * detail.ad_4_amount + 2 * detail.ch_2_ad_4_amount
            if children == 3 and detail.ch_3_ad_4_amount:
                return 4 * detail.ad_4_amount + 3 * detail.ch_3_ad_4_amount
        return -1
    
