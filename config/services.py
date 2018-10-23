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
    Extra, ProviderExtraService, ProviderExtraDetail, AgencyExtraService, AgencyExtraDetail,
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

        # TODO provider cost
        cost = None

        # agency price
        # obtain details order by date_from asc, date_to desc
        agency_detail_list = list(
            AgencyExtraDetail.objects.select_related(
                'agency_service__service'
            ).filter(
                agency_service__agency__eq=agency
            ).filter(
                agency_service__agency_service__eq=service
            ).filter(
                agency_service__date_to__gte=date_from,
                agency_service__date_from__lte=date_to
            ).order_by(
                ['agency_service__date_from', '-agency_service__date_to']
            )
        )
        stop = False
        solved = False
        current_date = date_from
        price= 0
        # continue until solved or empty details list
        while not stop:
            # verify list not empty
            if len(agency_detail_list) > 0:
                # working with first detail
                detail = agency_detail_list[0]
                # verify current dat included
                if current_date >= detail.agency_servide.date_from:
                    # verify final date included
                    if detail.agency_servide.date_to >= date_to:
                        # full date range
                        price += cls._get_extra_price(
                            service, detail, current_date, date_to,
                            adults, children,
                            quantity, parameter)
                        solved = True
                        stop = True
                    else:
                        price += cls._get_extra_price(
                            service, detail, current_date, detail.agency_servide.date_to,
                            adults, children,
                            quantity, parameter)
                        current_date = detail.agency_servide.date_to + 1
                # remove detail from list
                agency_detail_list.remove(detail)
            else:
                # empty list, no solved all days
                stop = True
                message = 'No Price Found for date %s' % current_date
        if not solved:
            price = None

        code = ''

        return code, message, cost, price

    @classmethod
    def _get_extra_price(
        cls, service, detail, current_date, date_to, adults, children, quantity, parameter):
        if service.cost_type == EXTRA_COST_TYPE_FIXED:
            return detail.ad_1_amount * quantity * parameter
        if service.cost_type == EXTRA_COST_TYPE_BY_PAX:
            if adults == 0:
                if children == 1 and detail.ch_1_ad_0_amount:
                    return 1 * detail.ch_1_ad_0_amount * quantity * parameter
                if children == 2 and detail.ch_2_ad_0_amount:
                    return 2 * detail.ch_2_ad_0_amount * quantity * parameter
                if children == 3 and detail.ch_3_ad_0_amount:
                    return 3 * detail.ch_3_ad_0_amount * quantity * parameter
            if adults == 1 and detail.ad_1_amount:
                if children == 0:
                    return 1 * detail.ad_1_amount * quantity * parameter
                if children == 1 and detail.ch_1_ad_1_amount:
                    return (1 * detail.ad_1_amount + 1 * detail.ch_1_ad_1_amount) * quantity * parameter
                if children == 2 and detail.ch_2_ad_1_amount:
                    return (1 * detail.ad_1_amount + 2 * detail.ch_2_ad_1_amount) * quantity * parameter
                if children == 3 and detail.ch_3_ad_1_amount:
                    return (1 * detail.ad_1_amount + 3 * detail.ch_3_ad_1_amount) * quantity * parameter
            if adults == 2 and detail.ad_2_amount:
                if children == 0:
                    return 2 * detail.ad_2_amount * quantity * parameter
                if children == 1 and detail.ch_1_ad_2_amount:
                    return (2 * detail.ad_2_amount + 1 * detail.ch_1_ad_2_amount) * quantity * parameter
                if children == 2 and detail.ch_2_ad_2_amount:
                    return (2 * detail.ad_2_amount + 2 * detail.ch_2_ad_2_amount) * quantity * parameter
                if children == 3 and detail.ch_3_ad_2_amount:
                    return (2 * detail.ad_2_amount + 3 * detail.ch_3_ad_2_amount) * quantity * parameter
            if adults == 3 and detail.ad_3_amount:
                if children == 0:
                    return 3 * detail.ad_3_amount * quantity * parameter
                if children == 1 and detail.ch_1_ad_3_amount:
                    return (3 * detail.ad_3_amount + 1 * detail.ch_1_ad_3_amount) * quantity * parameter
                if children == 2 and detail.ch_2_ad_3_amount:
                    return (3 * detail.ad_3_amount + 2 * detail.ch_2_ad_3_amount) * quantity * parameter
                if children == 3 and detail.ch_3_ad_3_amount:
                    return (3 * detail.ad_3_amount + 3 * detail.ch_3_ad_3_amount) * quantity * parameter
            if adults == 4 and detail.ad_4_amount:
                if children == 0:
                    return 4 * detail.ad_4_amount * quantity * parameter
                if children == 1 and detail.ch_1_ad_4_amount:
                    return (4 * detail.ad_4_amount + 1 * detail.ch_1_ad_4_amount) * quantity * parameter
                if children == 2 and detail.ch_2_ad_4_amount:
                    return (4 * detail.ad_4_amount + 2 * detail.ch_2_ad_4_amount) * quantity * parameter
                if children == 3 and detail.ch_3_ad_4_amount:
                    return (4 * detail.ad_4_amount + 3 * detail.ch_3_ad_4_amount) * quantity * parameter
        return -1
