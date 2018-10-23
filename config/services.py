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
                            service, detail, current_date, date_to, quantity, parameter)
                        solved = True
                        stop = True
                    else:
                        price += cls._get_extra_price(
                            service, detail, current_date, detail.agency_servide.date_to, quantity, parameter)
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
        cls, service, detail, current_date, date_to, quantity, parameter):
        if service.cost_type == EXTRA_COST_TYPE_FIXED:
            return detail.ad_1_amount * quantity * parameter
        if service.cost_type == EXTRA_COST_TYPE_BY_PAX:
            adults, children = cls._findPaxex()
            return detail.ad_1_amount * quantity * parameter
            
        return 0
