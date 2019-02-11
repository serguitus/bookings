"""
config services
"""
from datetime import datetime, timedelta

from django.db.models import Q

from config.constants import (
    SERVICE_CATEGORY_EXTRA, SERVICE_CATEGORY_ALLOTMENT, SERVICE_CATEGORY_TRANSFER,
    TRANSFER_COST_TYPE_FIXED, TRANSFER_COST_TYPE_BY_PAX,
    EXTRA_COST_TYPE_FIXED, EXTRA_COST_TYPE_BY_PAX,
    EXTRA_PARAMETER_TYPE_HOURS, EXTRA_PARAMETER_TYPE_DAYS,
    EXTRA_PARAMETER_TYPE_NIGHTS, EXTRA_PARAMETER_TYPE_STAY,
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
    ConfigService
    """

    @classmethod
    def process_agency_allotments_amounts(
            cls, agency, allotments_ids, gain_percent):
        """
        process_agency_allotments_amounts
        """

        from multiprocessing import Process

        if __name__ == '__main__':
            p = Process(
                target=cls.generate_agency_allotments_amounts,
                args=(agency, allotments_ids, gain_percent,))
            p.start()
            p.join()



    @classmethod
    def generate_agency_allotments_amounts(
            cls, agency_id, allotments_ids, gain_percent):
        """
        generate_agency_amounts
        """
        # for each service
        for service_id in allotments_ids:
            # find providerservice list
            provider_services = list(ProviderAllotmentService.objects.filter(service=service_id))
            # for each providerservice create agencyservice
            for provider_service in provider_services:
                agency_service, created = AgencyAllotmentService.objects.get_or_create(
                    agency_id=agency_id,
                    date_from=provider_service.date_from,
                    date_to=provider_service.date_to,
                    service=provider_service.service
                )
                # find details
                details = list(
                    ProviderAllotmentDetail.objects.filter(provider_service=provider_service))
                # for each providerdetail create agencydetail
                for detail in details:
                    agency_detail, created = AgencyAllotmentDetail.objects.get_or_create(
                        agency_service=agency_service,
                        room_type=detail.room_type,
                        board_type=detail.board_type,
                        defaults=cls._default_amounts(detail, gain_percent)
                    )
                    # if already exists ensure higher amounts
                    if not created:
                        cls._ensure_higher_amounts(agency_detail, detail)
        # finally fix agency allotments amounts
        cls.fix_agency_allotments_amounts(agency_id)

    @classmethod
    def fix_agency_allotments_amounts(cls, agency_id):
        """
        fix_agency_allotments_amounts
        """
        # get all agency services sorted by service, date_from asc, date_to desc
        agency_services = list()
        prev_agency_service = None
        for agency_service in agency_services:
            if prev_agency_service is not None:
                # verify date overlap
                if agency_service.date_from <= prev_agency_service.date_to:
                    pass



            prev_agency_service = agency_service

    @classmethod
    def _default_amounts(cls, detail, gain_percent):
        return {
            'ad_1_amount': cls._calculate_price(detail.ad_1_amount, gain_percent),
            'ad_2_amount': cls._calculate_price(detail.ad_2_amount, gain_percent),
            'ad_3_amount': cls._calculate_price(detail.ad_3_amount, gain_percent),
            'ad_4_amount': cls._calculate_price(detail.ad_4_amount, gain_percent),
            'ch_1_ad_0_amount': cls._calculate_price(
                detail.ch_1_ad_0_amount, gain_percent),
            'ch_1_ad_1_amount': cls._calculate_price(
                detail.ch_1_ad_1_amount, gain_percent),
            'ch_1_ad_2_amount': cls._calculate_price(
                detail.ch_1_ad_2_amount, gain_percent),
            'ch_1_ad_3_amount': cls._calculate_price(
                detail.ch_1_ad_3_amount, gain_percent),
            'ch_1_ad_4_amount': cls._calculate_price(
                detail.ch_1_ad_4_amount, gain_percent),
            'ch_2_ad_0_amount': cls._calculate_price(
                detail.ch_2_ad_0_amount, gain_percent),
            'ch_2_ad_1_amount': cls._calculate_price(
                detail.ch_2_ad_1_amount, gain_percent),
            'ch_2_ad_2_amount': cls._calculate_price(
                detail.ch_2_ad_2_amount, gain_percent),
            'ch_2_ad_3_amount': cls._calculate_price(
                detail.ch_2_ad_3_amount, gain_percent),
            'ch_2_ad_4_amount': cls._calculate_price(
                detail.ch_2_ad_4_amount, gain_percent),
            'ch_3_ad_0_amount': cls._calculate_price(
                detail.ch_3_ad_0_amount, gain_percent),
            'ch_3_ad_1_amount': cls._calculate_price(
                detail.ch_3_ad_1_amount, gain_percent),
            'ch_3_ad_2_amount': cls._calculate_price(
                detail.ch_3_ad_2_amount, gain_percent),
            'ch_3_ad_3_amount': cls._calculate_price(
                detail.ch_3_ad_3_amount, gain_percent),
            'ch_3_ad_4_amount': cls._calculate_price(
                detail.ch_3_ad_4_amount, gain_percent)
        }

    @classmethod
    def _ensure_higher_amounts(cls, agency_detail, detail):
        modified = False
        if cls._need_update(agency_detail.ad_1_amount, detail.ad_1_amount):
            agency_detail.ad_1_amount = detail.ad_1_amount
            modified = True
        if cls._need_update(agency_detail.ad_2_amount, detail.ad_2_amount):
            agency_detail.ad_2_amount = detail.ad_2_amount
            modified = True
        if cls._need_update(agency_detail.ad_3_amount, detail.ad_3_amount):
            agency_detail.ad_3_amount = detail.ad_3_amount
            modified = True
        if cls._need_update(agency_detail.ad_4_amount, detail.ad_4_amount):
            agency_detail.ad_4_amount = detail.ad_4_amount
            modified = True
        if cls._need_update(
                agency_detail.ch_1_ad_0_amount, detail.ch_1_ad_0_amount):
            agency_detail.ch_1_ad_0_amount = detail.ch_1_ad_0_amount
            modified = True
        if cls._need_update(
                agency_detail.ch_1_ad_1_amount, detail.ch_1_ad_1_amount):
            agency_detail.ch_1_ad_1_amount = detail.ch_1_ad_1_amount
            modified = True
        if cls._need_update(
                agency_detail.ch_1_ad_2_amount, detail.ch_1_ad_2_amount):
            agency_detail.ch_1_ad_2_amount = detail.ch_1_ad_2_amount
            modified = True
        if cls._need_update(
                agency_detail.ch_1_ad_3_amount, detail.ch_1_ad_3_amount):
            agency_detail.ch_1_ad_3_amount = detail.ch_1_ad_3_amount
            modified = True
        if cls._need_update(
                agency_detail.ch_1_ad_4_amount, detail.ch_1_ad_4_amount):
            agency_detail.ch_1_ad_4_amount = detail.ch_1_ad_4_amount
            modified = True
        if cls._need_update(
                agency_detail.ch_2_ad_0_amount, detail.ch_2_ad_0_amount):
            agency_detail.ch_2_ad_0_amount = detail.ch_2_ad_0_amount
            modified = True
        if cls._need_update(
                agency_detail.ch_2_ad_1_amount, detail.ch_2_ad_1_amount):
            agency_detail.ch_2_ad_1_amount = detail.ch_2_ad_1_amount
            modified = True
        if cls._need_update(
                agency_detail.ch_2_ad_2_amount, detail.ch_2_ad_2_amount):
            agency_detail.ch_2_ad_2_amount = detail.ch_2_ad_2_amount
            modified = True
        if cls._need_update(
                agency_detail.ch_2_ad_3_amount, detail.ch_2_ad_3_amount):
            agency_detail.ch_2_ad_3_amount = detail.ch_2_ad_3_amount
            modified = True
        if cls._need_update(
                agency_detail.ch_2_ad_4_amount, detail.ch_2_ad_4_amount):
            agency_detail.ch_2_ad_4_amount = detail.ch_2_ad_4_amount
            modified = True
        if cls._need_update(
                agency_detail.ch_3_ad_0_amount, detail.ch_3_ad_0_amount):
            agency_detail.ch_3_ad_0_amount = detail.ch_3_ad_0_amount
            modified = True
        if cls._need_update(
                agency_detail.ch_3_ad_1_amount, detail.ch_3_ad_1_amount):
            agency_detail.ch_3_ad_1_amount = detail.ch_3_ad_1_amount
            modified = True
        if cls._need_update(
                agency_detail.ch_3_ad_2_amount, detail.ch_3_ad_2_amount):
            agency_detail.ch_3_ad_2_amount = detail.ch_3_ad_2_amount
            modified = True
        if cls._need_update(
                agency_detail.ch_3_ad_3_amount, detail.ch_3_ad_3_amount):
            agency_detail.ch_3_ad_3_amount = detail.ch_3_ad_3_amount
            modified = True
        if cls._need_update(
                agency_detail.ch_3_ad_4_amount, detail.ch_3_ad_4_amount):
            agency_detail.ch_3_ad_4_amount = detail.ch_3_ad_4_amount
            modified = True
        if modified:
            agency_detail.save()

    @classmethod
    def _calculate_price(cls, cost, gain_percent):
        if cost is None:
            return None
        if gain_percent is None:
            return cost
        return round(0.499999 + float(cost) * (1.0 + float(gain_percent) / 100.0))

    @classmethod
    def _need_update(cls, old_value, new_value):
        return new_value is not None and (old_value is None or old_value < new_value)

    @classmethod
    def allotment_amounts(
            cls, service_id, date_from, date_to, groups, provider, agency,
            board_type, room_type_id, quantity=None):

        if groups is None:
            return 3, 'Paxes Missing', None, None

        service = Allotment.objects.get(pk=service_id)

        # provider cost
        # obtain details order by date_from asc, date_to desc
        if provider is None:
            cost = None
            cost_message = 'Provider Not Found'
        else:
            queryset = cls._get_provider_queryset(
                ProviderAllotmentDetail.objects,
                provider.id, service_id, date_from, date_to)
            detail_list = list(
                queryset.filter(
                    board_type=board_type
                ).filter(
                    room_type_id=room_type_id
                )
            )
            cost, cost_message = cls.find_groups_amount(
                True, service, date_from, date_to, groups,
                quantity, None, detail_list
            )

        # agency price
        # obtain details order by date_from asc, date_to desc
        if agency is None:
            price = None
            price_message = 'Agency Not Found'
        else:
            if room_type_id is None:
                price = None
                price_message = 'Room Type Not Found'
            else:
                queryset = cls._get_agency_queryset(
                    AgencyAllotmentDetail.objects,
                    agency.id, service_id, date_from, date_to)
                detail_list = list(
                    queryset.filter(
                        board_type=board_type
                    ).filter(
                        room_type_id=room_type_id
                    )
                )
                price, price_message = cls.find_groups_amount(
                    False, service, date_from, date_to, groups,
                    quantity, None, detail_list
                )

        return cls._get_result(cost, cost_message, price, price_message)

    @classmethod
    def transfer_amounts(
            cls, service_id, date_from, date_to, groups, provider, agency,
            location_from_id, location_to_id, quantity=None):
        service = Transfer.objects.get(pk=service_id)

        if service.cost_type == TRANSFER_COST_TYPE_BY_PAX and (groups is None):
            return 3, 'Paxes Missing', None, None

        # provider cost
        # obtain details order by date_from asc, date_to desc
        if provider is None:
            cost = None
            cost_message = 'Provider Not Found'
        else:
            queryset = cls._get_provider_queryset(
                ProviderTransferDetail.objects,
                provider.id, service_id, date_from, date_to)
            detail_list = list(
                queryset.filter(
                    p_location_from_id=location_from_id
                ).filter(
                    p_location_to_id=location_to_id
                )
            )
            cost, cost_message = cls.find_groups_amount(
                True, service, date_from, date_to, groups,
                quantity, None, detail_list
            )

        # agency price
        # obtain details order by date_from asc, date_to desc
        if agency is None:
            price = None
            price_message = 'Agency Not Found'
        else:
            queryset = cls._get_agency_queryset(
                AgencyTransferDetail.objects,
                agency.id, service_id, date_from, date_to)
            detail_list = list(
                queryset.filter(
                    a_location_from_id=location_from_id
                ).filter(
                    a_location_to_id=location_to_id
                )
            )
            price, price_message = cls.find_groups_amount(
                False, service, date_from, date_to, groups,
                quantity, None, detail_list
            )

        return cls._get_result(cost, cost_message, price, price_message)

    @classmethod
    def extra_amounts(
            cls, service_id, date_from, date_to, groups, provider, agency,
            addon_id, quantity, parameter):
        service = Extra.objects.get(pk=service_id)

        if service.cost_type == EXTRA_COST_TYPE_BY_PAX and (groups is None):
            return 3, 'Paxes Missing', None, None

        # provider cost
        # obtain details order by date_from asc, date_to desc
        if provider is None:
            cost = None
            cost_message = 'Provider Not Found'
        else:
            if service.has_pax_range:
                cost = 0
                cost_message = ''
                # each group can have different details
                for group in groups:
                    paxes = group[0] + group[1]
                    queryset = cls._get_provider_queryset(
                        ProviderExtraDetail.objects,
                        provider.id, service_id, date_from, date_to)
                    # pax range filtering
                    queryset = queryset.filter(
                        (Q(pax_range_min__isnull=True) & Q(pax_range_max__gte=paxes)) |
                        (Q(pax_range_min__lte=paxes) & Q(pax_range_max__gte=paxes)) |
                        (Q(pax_range_min__lte=paxes) & Q(pax_range_max__isnull=True))
                    )
                    # addon filtering
                    if addon_id:
                        queryset = queryset.filter(addon_id=addon_id)
                    else:
                        queryset = queryset.filter(addon_id__isnull=True)

                    detail_list = list(queryset)

                    group_cost, group_cost_message = cls.find_group_amount(
                        True, service, date_from, date_to, group,
                        quantity, parameter, detail_list
                    )
                    if group_cost:
                        cost += group_cost
                        cost_message = group_cost_message
                    else:
                        cost = None
                        cost_message = group_cost_message
                        break
            else:
                queryset = cls._get_provider_queryset(
                    ProviderExtraDetail.objects,
                    provider.id, service_id, date_from, date_to)
                # addon filtering
                if addon_id:
                    queryset = queryset.filter(addon_id=addon_id)
                else:
                    queryset = queryset.filter(addon_id__isnull=True)

                detail_list = list(queryset)

                cost, cost_message = cls.find_groups_amount(
                    True, service, date_from, date_to, groups,
                    quantity, parameter, detail_list
                )

        # agency price
        # obtain details order by date_from asc, date_to desc
        if agency is None:
            price = None
            price_message = 'Agency Not Found'
        else:
            if service.has_pax_range:
                price = 0
                price_message = ''
                # each group can have different details
                for group in groups:
                    paxes = group[0] + group[1]
                    queryset = cls._get_agency_queryset(
                        AgencyExtraDetail.objects,
                        agency.id, service_id, date_from, date_to)
                    # pax range filtering
                    queryset = queryset.filter(
                        (Q(pax_range_min__isnull=True) & Q(pax_range_max__gte=paxes)) |
                        (Q(pax_range_min__lte=paxes) & Q(pax_range_max__gte=paxes)) |
                        (Q(pax_range_min__lte=paxes) & Q(pax_range_max__isnull=True))
                    )
                    # addon filtering
                    if addon_id:
                        queryset = queryset.filter(addon_id=addon_id)
                    else:
                        queryset = queryset.filter(addon_id__isnull=True)

                    detail_list = list(queryset)
                    group_price, group_price_message = cls.find_group_amount(
                        False, service, date_from, date_to, group,
                        quantity, parameter, detail_list
                    )
                    if group_price:
                        price += group_price
                        price_message = group_price_message
                    else:
                        price = None
                        price_message = group_price_message
                        break
            else:
                queryset = cls._get_agency_queryset(
                    AgencyExtraDetail.objects,
                    agency.id, service_id, date_from, date_to)
                # addon filtering
                if addon_id:
                    queryset = queryset.filter(addon_id=addon_id)
                else:
                    queryset = queryset.filter(addon_id__isnull=True)

                detail_list = list(queryset)

                price, price_message = cls.find_groups_amount(
                    False, service, date_from, date_to, groups,
                    quantity, parameter, detail_list
                )

        return cls._get_result(cost, cost_message, price, price_message)

    @classmethod
    def _get_result(cls, cost, cost_message, price, price_message):
        if cost and cost >= 0:
            if price and price >= 0:
                code = "0"
                message = "Provider Cost and Agency Price Found: %s - %s" % (
                    cost_message, price_message
                )
            else:
                code = "2"
                message = "Only Provider Cost Found: %s - %s" % (
                    cost_message, price_message
                )
        else:
            if price and price >= 0:
                code = "1"
                message = "Only Agency Price Found: %s - %s" % (
                    cost_message, price_message
                )
            else:
                code = "3"
                message = "Provider Cost and Agency Amounts NOT Found: %s - %s" % (
                    cost_message, price_message
                )
        return code, message, cost, cost_message, price, price_message

    @classmethod
    def find_groups_amount(
            cls, amount_for_provider, service, date_from, date_to, groups,
            quantity, parameter, detail_list):

        groups_amount = 0
        groups_message = ''
        for group in groups:
            amount, message = cls.find_group_amount(
                amount_for_provider, service, date_from, date_to, group,
                quantity, parameter, detail_list)
            if amount is None:
                return None, message
            groups_amount += amount
            groups_message = message

        return groups_amount, groups_message

    @classmethod
    def find_group_amount(
            cls, amount_for_provider, service, date_from, date_to, group,
            quantity, parameter, detail_list):

        amount, message = cls.find_amount(
            amount_for_provider, service, date_from, date_to, group[0], group[1],
            quantity, parameter, detail_list)
        if amount is not None and amount >= 0:
            return amount, message
        else:
            return None, message

    @classmethod
    def find_amount(
            cls, amount_for_provider, service, date_from, date_to, adults, children,
            quantity, parameter, detail_list):
        message = ''
        stop = False
        solved = False
        current_date = date_from
        amount = 0
        details = list(detail_list)
        # continue until solved or empty details list
        while not stop:
            # verify list not empty
            if details:
                # working with first detail
                detail = details[0]

                # verify current dat included
                if amount_for_provider:
                    detail_date_from = detail.provider_service.date_from
                    detail_date_to = detail.provider_service.date_to
                else:
                    detail_date_from = detail.agency_service.date_from
                    detail_date_to = detail.agency_service.date_to

                if current_date >= detail_date_from:
                    # verify final date included
                    end_date = detail_date_to + timedelta(days=1)
                    if end_date >= date_to:
                        # full date range
                        result = cls._get_service_amount(
                            service, detail, current_date, date_to,
                            adults, children,
                            quantity, parameter)
                        if result is not None and result >= 0:
                            amount += result
                            solved = True
                            stop = True
                    else:
                        result = cls._get_service_amount(
                            service, detail, current_date,
                            datetime(year=end_date.year, month=end_date.month, day=end_date.day),
                            adults, children,
                            quantity, parameter)
                        if result is not None and result >= 0:
                            amount += result
                            current_date = datetime(
                                year=end_date.year, month=end_date.month, day=end_date.day)
                # remove detail from list
                details.remove(detail)
            else:
                # empty list, no solved all days
                stop = True
                message = 'Amount Not Found for date %s' % current_date
        if not solved:
            amount = None

        return amount, message

    @classmethod
    def _get_service_amount(
            cls, service, detail, date_from, date_to, adults, children, quantity, parameter):
        if isinstance(service, Allotment):
            interval = date_to - date_from
            return cls._get_allotment_amount(
                service, detail, interval.days, adults, children, quantity)
        if isinstance(service, Transfer):
            return cls._get_transfer_amount(
                service, detail, adults, children, quantity)
        if isinstance(service, Extra):
            return cls._get_extra_amount(
                service, detail, date_from, date_to, adults, children, quantity, parameter)
        return None

    @classmethod
    def _get_allotment_amount(
            cls, service, detail, days, adults, children, quantity):
        if quantity is None or (quantity < 1):
            quantity = 1
        if service.grouping:
            amount = cls._find_detail_amount(detail, adults, children)
        else:
            adult_amount = 0
            if adults > 0:
                if detail.ad_1_amount is None:
                    return None
                adult_amount = adults * detail.ad_1_amount
            children_amount = 0
            if children > 0:
                if detail.ch_1_ad_1_amount is None:
                    return None
                children_amount = children * detail.ch_1_ad_1_amount
            amount = adult_amount + children_amount
        if amount and amount >= 0:
            return amount * days * quantity
        return None

    @classmethod
    def get_service_quantity(cls, service, pax_qtty):
        if not hasattr(service, 'max_capacity'):
            return 1
        if service.max_capacity is None or (service.max_capacity < 1):
            return 1
        return int((pax_qtty + service.max_capacity - 1) / service.max_capacity)

    @classmethod
    def _get_transfer_amount(
            cls, service, detail, adults, children, quantity):
        quantity = cls.get_service_quantity(service, adults + children)
        if service.cost_type == TRANSFER_COST_TYPE_FIXED and detail.ad_1_amount:
            return detail.ad_1_amount * quantity
        if service.cost_type == TRANSFER_COST_TYPE_BY_PAX:
            if not service.grouping:
                adult_amount = 0
                if adults > 0:
                    if detail.ad_1_amount is None:
                        return None
                    adult_amount = adults * detail.ad_1_amount
                children_amount = 0
                if children > 0:
                    if detail.ch_1_ad_1_amount is None:
                        return None
                    children_amount = children * detail.ch_1_ad_1_amount
                amount = adult_amount + children_amount
            else:
                amount = cls._find_detail_amount(detail, adults, children)
            if amount and (amount >= 0):
                return amount * quantity
        return None

    @classmethod
    def _get_extra_amount(
            cls, service, detail, date_from, date_to, adults, children, quantity, parameter):
        if service.parameter_type == EXTRA_PARAMETER_TYPE_HOURS:
            # parameter hours mandatory
            if parameter is None:
                return None
        elif service.parameter_type == EXTRA_PARAMETER_TYPE_STAY:
            parameter = 1
        else:
            interval = date_to - date_from
            if service.parameter_type == EXTRA_PARAMETER_TYPE_DAYS:
                parameter = interval.days + 1
            elif service.parameter_type == EXTRA_PARAMETER_TYPE_NIGHTS:
                parameter = interval.days
            else:
                return None
        if quantity is None or quantity < 1:
            quantity = cls.get_service_quantity(service, adults + children)
        if service.cost_type == EXTRA_COST_TYPE_FIXED and detail.ad_1_amount:
            return detail.ad_1_amount * quantity * parameter
        if service.cost_type == EXTRA_COST_TYPE_BY_PAX:
            if not service.grouping:
                adult_amount = 0
                if adults > 0:
                    if detail.ad_1_amount is None:
                        return None
                    adult_amount = adults * detail.ad_1_amount
                children_amount = 0
                if children > 0:
                    if detail.ch_1_ad_1_amount is None:
                        return None
                    children_amount = children * detail.ch_1_ad_1_amount
                amount = adult_amount + children_amount
            else:
                amount = cls._find_detail_amount(detail, adults, children)
            if amount is not None and amount >= 0:
                return amount * quantity * parameter
        return None

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
        return None

    @classmethod
    def _get_provider_queryset(
            cls, manager, provider_id, service_id, date_from, date_to):
        return manager.select_related(
            'provider_service__service'
            ).filter(
                provider_service__provider_id=provider_id
            ).filter(
                provider_service__service_id=service_id
            ).filter(
                provider_service__date_to__gte=date_from,
                provider_service__date_from__lte=date_to
            ).order_by(
                'provider_service__date_from', '-provider_service__date_to'
            )

    @classmethod
    def _get_agency_queryset(
            cls, manager, agency_id, service_id, date_from, date_to):
        if date_from is None:
            return manager.none()
        if date_to is None:
            return manager.none()
        return manager.select_related(
            'agency_service__service'
            ).filter(
                agency_service__agency_id=agency_id
            ).filter(
                agency_service__service_id=service_id
            ).filter(
                agency_service__date_to__gte=date_from,
                agency_service__date_from__lte=date_to
            ).order_by(
                'agency_service__date_from', '-agency_service__date_to'
            )
